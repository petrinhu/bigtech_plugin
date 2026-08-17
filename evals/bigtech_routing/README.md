# Evals de roteamento `/bigtech` (BT-8)

Harness **offline** e **determinístico** da política de classificação de porte da skill `/bigtech` / Cósimo, alinhado ao **pós-BT-5**.

Isto **não** substitui eval com LLM real (prompt da skill + mapa de ativação completo). Só trava a **política**:

| Invariante | Regra |
|---|---|
| Perfis canônicos | `early` \| `scale` \| `bigtech` |
| Piso | `early` (nunca abaixo) |
| Proibido como perfil | `solo` (alias deprecado → `early`) |
| Headcount / capacity | peso **0** no score de perfil (nota auxiliar) |
| Criticidade | eleva agents (CISO/CLO) e, com sinais sistêmicos, o porte |

## Layout

```text
evals/bigtech_routing/
  cases.json      # fixtures CASE-A..D + portes + alias solo + IA
  run_evals.py    # classificador determinístico + runner (stdlib)
  README.md       # este arquivo
```

## Como rodar

Na raiz do repositório (ou com path absoluto):

```bash
python3 evals/bigtech_routing/run_evals.py
```

- Exit **0** se todos os cases PASS.
- Exit **1** se algum FAIL (ou erro de IO/JSON).
- Imprime tabela `ID | STATUS | GOT | EXPECTED | DETAIL`.

Opcional: `python3 evals/bigtech_routing/run_evals.py /caminho/cases.json`.

## Cases (resumo)

| ID | Cenário | Perfil esperado |
|---|---|---|
| `CASE-A` | Script trivial local, capacity solo | `early` |
| `CASE-B` | Multi-repo + framework + consumidores, 1 humano | `scale` (ou `bigtech` se `allowed`) |
| `CASE-C` | App pequeno com saúde/PII | `early` + min CISO/CLO |
| `CASE-D` | Time grande, site estático simples | `early` (headcount não promove) |
| `PORTE-EARLY-PMF` | Early-stage / primeiros usuários | `early` + CPO |
| `PORTE-SCALE` | Crescimento + regulação | `scale` |
| `PORTE-BIGTECH` | Multi-produto + compliance pesado | `bigtech` |
| `FORBID-SOLO-ALIAS` | `legacy_porte_hint=solo` | `early` (nunca `solo`) |
| `CRIT-MONEY` | Pagamentos em escopo pequeno | `early` + CISO |
| `IA-CENTRAL` | IA como capability central | `early` + CAIO + applied-ai-engineer |

Origem narrativa: `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md` §2.6 (CASE-A..D), traduzida para a taxonomia **pós-BT-5** (`early|scale|bigtech`, não `lean|standard|critical` da rubrica futura de Phase 2).

## Modelo de score (determinístico)

Cada case declara `signals` com dimensões `0..3`.

**Porte (escala/complexidade)** - entram na soma:

`blast_radius`, `coupling`, `reversibility`, `complexity`, `distribution`, `maintenance`.

- **Soma** (0..18): `0..8` → `early`; `9..15` → `scale`; `16+` → `bigtech`.
- **Elevações sistêmicas**: multi-repo/consumidores → mínimo `scale`; multi-produto + criticidade/compliance no teto → `bigtech`.

**Risco (governança)** - `criticality`, `compliance`:

- **não** sobem o porte sozinhas (CASE-C saúde fica `early`, anti-OE de cerimônia);
- elevam agents: CISO e, se regulado/saúde, CLO.

**Outros:**

- **Agents base** por porte + overlays PMF early (CPO) e IA central (CAIO).
- `headcount` / `capacity` são lidos só para prova de que **não** alteram o perfil.

## Integração CI / pre-CI

- `scripts/preci.sh`  -  gate dedicado (stdlib, hard).
- GitHub Actions (job Ubuntu nativo e, quando aplicável, matrix Linux): `python3 evals/bigtech_routing/run_evals.py`.

## Manutenção

1. Novo cenário de política → case em `cases.json` (id estável, `expected_*` explícitos).
2. Mudança de regra de porte (BT-5+) → ajustar `classify()` em `run_evals.py` **e** os expectations no mesmo commit.
3. Não chamar API paga nem rede neste harness.
4. Não gravar `solo` como `expected_profile`.

## Relação com o produto

| Camada | Papel |
|---|---|
| Skill `/bigtech` + Cosimo | classificação com LLM + mapa de ativação |
| Hooks `bigtech_porte_*` | marcador `.bigtech-porte`, alias `solo`→`early` |
| **Este harness** | regressão da **política** sem LLM |

Se o harness e a prosa da skill divergirem em piso/alias/headcount, o harness falha de propósito: alinhar docs/skill/hooks antes de alargar o classificador.
