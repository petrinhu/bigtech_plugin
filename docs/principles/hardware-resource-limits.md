---
title: Limites de recursos de hardware
description: Como rodar workloads pesados (ML, RAG, build, transcoding, render, big-data) sem esgotar CPU, RAM ou GPU da máquina do usuário.
---

# Limites de recursos de hardware

> Regra para todos os agents: ao disparar qualquer workload pesado, **respeite os limites
> de hardware da máquina onde o plugin roda**. Não sature CPU, RAM nem GPU a ponto de
> travar o desktop, o IO ou outras tarefas do usuário. Quando um workload puder estourar
> esses limites, **avise antes** e, em dúvida, peça confirmação (opção recomendada primeiro).

Este documento é referência transversal: vários agents apontam para ele antes de executar
trabalho intensivo. O objetivo é dar **padrões genéricos e portáveis**: você ajusta os
números ao **seu** hardware com os comandos da seção seguinte.

> Os comandos de diagnóstico usam utilitários comuns de Linux (`nproc`, `free`, `nvidia-smi`).
> Em outros sistemas, adapte ao equivalente (`sysctl`/Activity Monitor no macOS;
> Task Manager/`Get-CimInstance` no Windows). A lógica dos caps é a mesma em qualquer plataforma.

---

## Quando aplicar

Estes limites valem **sempre** que um comando puder consumir CPU/RAM/GPU de forma agressiva:

- Treino ou inferência de ML local (PyTorch, TensorFlow, JAX, Hugging Face Transformers).
- RAG, geração de embeddings, reranking.
- Builds paralelos (`make -j`, `cmake --build -j`, `cargo build -j`, `ninja`, importação em lote).
- Transcoding de áudio/vídeo (`ffmpeg -threads`).
- Compressão/descompressão massiva (`zstd -T`, `xz -T`, pipelines de `tar`).
- Big-data / processamento em lote (Spark local, pandas/polars em datasets grandes).
- **Qualquer comando com flag `-j N`, `--threads N`, `--jobs N` ou equivalente.**

---

## 1. Descubra os limites do seu hardware

Antes de definir caps, meça a máquina. Rode:

```bash
# Núcleos de CPU (lógicos)
nproc

# Memória total e livre, em formato legível
free -h

# GPU NVIDIA: modelo, VRAM total e VRAM em uso
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv

# Swap configurado (tamanho e uso atual)
swapon --show
```

Anote três números:

- **Cores totais** (saída de `nproc`).
- **RAM total** e **RAM tipicamente livre** com o desktop e apps abertos (de `free -h`).
- **VRAM total** e **VRAM já ocupada** por outros processos de GPU (de `nvidia-smi`).

> Sem GPU NVIDIA (CPU-only, GPU integrada, ou AMD/Intel)? `nvidia-smi` não existirá: ignore
> as seções de GPU e force execução em CPU (ver §4).

---

## 2. Defina seus caps (fórmulas portáveis)

Use estas regras de bolso para não monopolizar a máquina. Os valores são **derivados do seu
hardware**, não fixos.

### CPU: deixe folga para o desktop e o IO

- **Threads de workload = ~80% dos cores**, deixando pelo menos **2–3 cores livres**.
- Fórmula: `cores * 0.8`, com piso de "total − 2".

```bash
# Threads recomendadas para workloads paralelos (80% dos cores)
THREADS=$(( $(nproc) * 8 / 10 ))
echo "Usar no máximo $THREADS threads"
```

| Cores totais (`nproc`) | Threads sugeridas (~80%) | Cores livres |
|---|---|---|
| 4  | 3  | 1 |
| 8  | 6  | 2 |
| 12 | 9  | 3 |
| 16 | 13 | 3 |
| 32 | 25 | 7 |

### RAM: nunca encoste no total

- **Mantenha um colchão livre** (sugestão: ~30% da RAM total, ou no mínimo alguns GB) para o
  desktop, navegador e cache de IO.
- **Cap soft do workload = RAM total − colchão.** Exemplo: numa máquina de 32 GB com colchão de
  ~10 GB, o teto do workload fica em ~20 GB.
- **Não conte com swap** para caber o workload (ver §3).

### GPU / VRAM: conte só o que sobra

- **VRAM útil = VRAM total − VRAM já ocupada** por outros processos (servidores de modelo,
  compositor gráfico, etc.).
- Dimensione *batch size*, *contexto* e precisão do modelo para caber na VRAM útil, não na
  total. Em GPUs pequenas (p.ex. 4–6 GB), prefira **uma carga de GPU por vez** (ver §5) e
  reduza *batch* antes de assumir que vai caber.

---

## 3. Swap não é recurso de workload

Swap costuma já estar parcialmente ocupado e é ordens de magnitude mais lento que RAM. **Não
dimensione um workload para "caber no swap"**: se o trabalho só fecha contando com swap, ele
vai travar a máquina inteira (thrashing). Trate o swap como rede de segurança do SO, não como
memória extra disponível.

---

## 4. Padrões obrigatórios: limitar threads (env vars)

Bibliotecas numéricas (BLAS, OpenMP, MKL, NumExpr) ignoram seu cap e tentam usar **todos** os
cores por padrão. Exporte estas variáveis para conter a paralelização ao seu `THREADS`:

```bash
# Calcule uma vez a partir dos seus cores (§2)
THREADS=$(( $(nproc) * 8 / 10 ))

export OMP_NUM_THREADS="$THREADS"       # OpenMP (PyTorch, NumPy, SciPy, ...)
export MKL_NUM_THREADS="$THREADS"       # Intel MKL
export OPENBLAS_NUM_THREADS="$THREADS"  # OpenBLAS
export NUMEXPR_NUM_THREADS="$THREADS"   # NumExpr (pandas eval)
export TOKENIZERS_PARALLELISM=false     # tokenizers do HF: evita fork-bomb de threads
```

> Substitua `"$THREADS"` por um número fixo apenas se quiser travar o valor; o cálculo dinâmico
> mantém o padrão portável entre máquinas.

---

## 5. Padrões obrigatórios: GPU / PyTorch

```bash
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True  # reduz fragmentação de VRAM
export CUDA_VISIBLE_DEVICES=0                             # fixa a GPU usada (ajuste o índice)
```

- **Fallback para CPU:** ao carregar um modelo na GPU, trate `CUDA out of memory` (OOM) com
  fallback automático para CPU em vez de deixar o processo morrer. Para forçar CPU:
  `export CUDA_VISIBLE_DEVICES=""`.
- **Uma carga de GPU por vez** em GPUs pequenas: serialize com lock (ver §6). Dois processos
  pesados disputando a mesma VRAM resultam em OOM mesmo que individualmente coubessem.
- **Não use `ulimit -v` rígido** para conter memória: um teto agressivo de memória virtual
  bloqueia o `mmap` de modelos grandes (que mapeiam arquivos sem alocar tudo de fato) e quebra
  o carregamento. Para limitar memória física, prefira *cgroups* (`systemd-run --user -p
  MemoryMax=...`) a um `ulimit -v` baixo.

---

## 6. Prioridade e serialização

Para que um workload pesado não disputizar de igual com o desktop, e para evitar concorrência
por GPU/RAM:

```bash
# Roda em prioridade mais baixa (cede CPU ao restante do sistema)
nice -n 5 <comando pesado>

# Garante UMA instância por vez quando o workload satura GPU ou RAM.
# A trava é liberada quando o comando termina.
flock -x /tmp/<workload>.lock <comando pesado>
```

- **`nice -n 5`** (ou maior) em qualquer comando intensivo de CPU.
- **`flock`** quando o workload satura um recurso compartilhado (VRAM, RAM): garante **uma
  execução por vez** e evita que duas chamadas se atropelem.

---

## 7. Receita: wrapper "safe" para workloads recorrentes

Para tarefas que você repete (RAG, transcoding, builds), em vez de lembrar das env vars toda
vez, crie um wrapper único no seu `PATH` que combine **env vars + `nice` + `flock`**:

```bash
#!/usr/bin/env bash
# Exemplo: wrapper "safe" para uma ferramenta hipotética `minha-tool`.
# Salve em um diretório do seu PATH, dê permissão de execução (chmod +x) e chame o wrapper
# no lugar do comando cru.
set -euo pipefail

THREADS=$(( $(nproc) * 8 / 10 ))
export OMP_NUM_THREADS="$THREADS"
export MKL_NUM_THREADS="$THREADS"
export OPENBLAS_NUM_THREADS="$THREADS"
export NUMEXPR_NUM_THREADS="$THREADS"
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

exec flock -x /tmp/minha-tool.lock nice -n 5 minha-tool "$@"
```

> Comandos one-shot: exporte as env vars inline na mesma linha, ou reaproveite um wrapper que
> já exista. Comandos recorrentes: padronize no wrapper.

---

## 8. Exemplo aplicado: RAG / embeddings em GPU pequena

Cenário comum em que os caps importam: um pipeline de RAG com modelos de embedding e reranking
rodando localmente em uma GPU de **VRAM modesta** (4–6 GB), compartilhada com um servidor de
modelos.

- **Serialize as queries:** processe **uma por vez** com `flock`. Disparar várias em paralelo
  satura a VRAM e faz as queries falharem (retornam avisos sem resultado válido).
- **Reduza o *batch* do reranker:** baixe o `top_n` do estágio de recuperação (p.ex. de ~100
  para ~25 candidatos) para o lote de reranking caber na VRAM útil.
- **Device do reranker = GPU com fallback CPU automático** ao detectar OOM.
- **Padronize via wrapper** (§7): chame o comando "safe" em vez do binário cru.

A lição é geral: em GPU pequena, **menos paralelismo + *batch* menor + serialização** vence
"rodar tudo de uma vez".

---

## 9. Falhas típicas que estes limites previnem

Padrões de incidente reais que estes caps evitam (use-os como sinal de alerta):

- **OOM de VRAM:** disparar várias cargas de GPU em paralelo (ex.: queries de RAG 2-a-2 ou
  3-a-3) satura a VRAM e derruba o lote: os processos retornam só avisos, sem saída válida.
  *Mitigação:* serializar com `flock` (§6).
- **Falha de `mmap`:** um `ulimit -v` rígido demais bloqueia o `mmap` de um modelo de vários GB
  e impede o carregamento. *Mitigação:* não usar `ulimit -v` baixo; preferir cgroups (§5).
- **Sistema lento / thrashing:** RAM perto de 100% e swap muito ocupado deixam todos os outros
  apps lentos durante um lote pesado. *Mitigação:* respeitar o colchão de RAM e não contar com
  swap (§2, §3).

---

## 10. Procedimento antes de disparar trabalho pesado

1. **Meça** o hardware (§1) se ainda não conhece os números da máquina.
2. **Exporte** as env vars de threads (§4) e, se houver GPU, as de GPU (§5).
3. **Envolva** o comando em `nice` e, se ele saturar GPU/RAM, em `flock` (§6); ou use um
   wrapper "safe" (§7).
4. **Avise o usuário antes** de qualquer lote que possa estourar os limites: **≥3 processos
   pesados em paralelo** ou **um novo processo de GPU** numa máquina de VRAM apertada.
5. **Em dúvida, peça confirmação** ao usuário antes de executar, apresentando a opção
   recomendada primeiro. A palavra final sobre disparar uma carga arriscada é sempre dele.

---

## Checklist rápido

- [ ] Caps derivados do hardware real (`nproc`, `free -h`, `nvidia-smi`), não chutados.
- [ ] `OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS` exportadas; `TOKENIZERS_PARALLELISM=false`.
- [ ] Pelo menos 2–3 cores e um colchão de RAM deixados livres.
- [ ] Workload não depende de swap para caber.
- [ ] Env de GPU exportada; fallback CPU no OOM; **sem** `ulimit -v` rígido.
- [ ] `nice` em comando pesado; `flock` quando satura GPU/RAM (1 instância por vez).
- [ ] Usuário avisado antes de lote arriscado; confirmação pedida em caso de dúvida.
