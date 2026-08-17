# BT-6 - Plano de cutover dual-authority (só plano)

**Item:** BT-6. **Não executa** PHASE 11.  
**Inventário que este plano consome:** [`2026-08-16-dual-authority-inventory.md`](2026-08-16-dual-authority-inventory.md) + [CSV](2026-08-16-dual-authority-inventory.csv).  
**Autoridade:** [`docs/adr/ADR-source-of-truth.md`](../adr/ADR-source-of-truth.md) D1–D8, D6 rollback.  
**Runbook-mãe:** `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md` PHASE 11.  
**Status desta fatia:** plano versionado. Instalação viva **intocada**.

## 0. Decisão autônoma (confirmar retroativamente)

**Canário futuro. Zero cutover real agora.**

Proibido nesta fatia (e até o go explícito da PHASE 11):

- apagar, mover, renomear `~/.claude/agents/*`
- desligar hooks globais homônimos
- substituir skills globais pelas do plugin
- tocar `~/.grok/agents/` como se fosse a SoT
- sync bidirecional / daemon / “espelho contínuo”
- publicar `VAULT_ONLY` no repo público

O estado transitório (51 homônimos ativos) **é aceite** até canário verde (ADR D2).

## 1. Estado-alvo (o que “cutover feito” significa)

Uma fonte de verdade para o núcleo distribuível: `bigtech_plugin`.

| Superfície | Depois do cutover |
|---|---|
| Agents core (51) | só o plugin; **0** ficheiros ativos em `~/.claude/agents/` com o mesmo `name:` |
| Agents `INTENTIONAL-EXCLUSION` (12) | continuam no vault |
| Agents `PERSONAL-OVERLAY` (8) | continuam no vault |
| Skills core | plugin (ou wrapper D4 curto que **só** encaminha) |
| `tab_pendencias` | produto standalone (pin/symlink); cópia embutida no plugin não é SoT |
| Hooks core (`bigtech_*`, `tdd_*`) | um registro (plugin); globais homônimos fora do `settings` ativo |
| Hooks pessoais | ficam |
| Grok | overlay de host (symlink/adapter); **não** 51 cópias core como terceira SoT |
| Rollback | executável a partir do histórico git + perfil isolado |

## 2. Pré-condições (não pular)

Ordem. Se uma falhar, **não** remover globais.

1. **ADR SoT aceite** (BT-1). Feito.
2. **Inventário classificado** (este BT-6). Feito nesta fatia; SHA do CSV no mesmo commit.
3. **Plugin canário publicado** (release / SHA instalável). Ainda **não**. `LAST_KNOWN_GOOD_PLUGIN_SHA` ainda não existe; HEAD de medição `77c1f9e` é só baseline de plano.
4. **BT-5 (porte) verificado** o suficiente para o canário não ensinar “solo/headcount” (vault Cosimo ainda ensina; o plugin já não).
5. **CI verde no SHA canário** (BT-4 no remoto; HEAD da medição pode não ser o canário).
6. **Evals de roteamento** (BT-8) e **drift gate** (BT-7) são desejáveis antes do cutover vivo, não desta fatia. Cutover **não** espera por eles para *planear*; espera para *executar* se o líder os mantiver no caminho crítico da PHASE 11.
7. **FABLE-CUTOVER** (papel teto do host) **antes** da primeira remoção. Este documento não substitui esse gate.
8. **Autorização explícita do líder** no contexto da PHASE 11. Plano ≠ ordem de apagar.

## 3. Passos ordenados (execução futura)

Cada passo prova o anterior. Nenhum `rm` no passo de canário.

### Passo A - Congelar e etiquetar

1. Registrar no runbook privado (não precisa republicar PII):
   - `LAST_KNOWN_GOOD_PLUGIN_SHA` = SHA do plugin que passou o canário.
   - SHA de `claude-memory` **antes** da remoção (hoje: `5b19b524`; re-medir na hora).
   - SHA Grok / adaptadores se a árvore versionada for afetada.
2. Exportar inventário ativo (nome, path, sha256) dos 51 que **vão sair do escopo ativo**. O CSV desta fatia é o modelo; re-hashear na hora (a árvore vault pode ter mudado).
3. Garantir que os 51 blobs existem no histórico git de `claude-memory`. Sem isso, não há rollback barato. Sem `rm` fora de git.

### Passo B - Canário em perfil **isolado**

Não na sessão viva do líder.

```text
CLAUDE_CONFIG_DIR=/caminho/para/perfil-limpo
# instalar marketplace + plugin no SHA canário
# NÃO copiar ~/.claude/agents core para o perfil
```

Provar, e gravar evidência:

- [ ] os 51 `name:` aparecem via plugin (não via `agents/` do perfil)
- [ ] as 4 skills resolvem no namespace do plugin
- [ ] hooks core disparam **uma** vez por evento (`SessionStart`, `UserPromptSubmit`, `PreToolUse`/`PostToolUse`)
- [ ] docs-bootstrap injeta `docs/` do plugin
- [ ] um agent de amostra reflete texto **exclusivo** do SHA canário (ex.: tabela early do Cósimo pós-BT-5, ausente no vault)
- [ ] `caveman` ausente / aviso se ambos ativos
- [ ] zero path de máquina / PII vazado no que o plugin carrega

Se o canário falhar: **parar**. Não ir ao Passo D. Registrar o gate. Overlay vivo fica como está.

### Passo C - Port residual (só se a re-medição achar gap)

Nesta medição (HEAD `77c1f9e` × vault `5b19b524`): **gap CORE-GENERIC = 0**.  
Na hora do cutover, repetir o diff semântico. Se aparecer texto vault reutilizável:

1. Classificar de novo (D8).
2. Portar só `CORE-GENERIC` para o plugin (commit no produto, com ID de item).
3. Overlay pessoal vai para `CLAUDE.md` / memória, **não** para o plugin.
4. `STALE` (wikilink, caveman, solo) **não** se porta.

Não inventar port “para ficar igual”.

### Passo D - Retirar sombreamento de agents (só após B verde)

No repo `claude-memory` (ou equivalente versionado), **não** no disco solto:

1. `git rm` dos 51 `~/.claude/agents/<core>.md` (lista = coluna INTERSECTION do CSV).
2. Commit local com a lista de nomes + SHA do plugin canário no corpo.
3. **Não** apagar os 20 `VAULT_ONLY`.
4. **Não** `git reset --hard`. **Não** `isolation: worktree` sob pasta IDrive/Dropbox.
5. Provar:
   - `/agents` (ou inventário do host) aponta o blob do plugin para um core amostrado;
   - editar (em perfil isolado) um agent do plugin muda o comportamento; o vault já não sombreia;
   - os 20 restantes ainda despacham.

Push de `claude-memory` só com autorização do líder nesse contexto.

### Passo E - Skills pessoais

1. Se a ergonomia `/bigtech` (e `/proj_software`) for necessária no overlay: **wrapper D4** (encaminha para `/bigtech:bigtech` ou namespace vigente). Sem rubrica de porte, sem lista de agents, sem segundo `SKILL.md` de produto.
2. Remover ou reduzir qualquer skill global que **reimplemente** o workflow (isso é `STALE`).
3. `tab_pendencias`: **não** usar a cópia embutida do plugin como SoT. Manter pin/submódulo (Claude) e symlink (Grok) para o produto. Atualizar pin quando o produto taggear; não “consertar” no fork do plugin.

### Passo F - Hooks globais

1. Tirar do `settings.json` **vivo** as entradas que duplicam o plugin:
   - `bigtech_session_init`, `bigtech_porte_reminder`, `bigtech_reinforce`
   - `tdd_guard`, `tdd_runner` (+ `tdd_common` se só existir para eles)
   - shim `tab_pendencias_reminder` se o produto já registrar o reminder
2. **Manter** overlay: `no_mdash`, `trash-guard`, `token_alert_*`, `pubmed_fda_crosslink`, `regua_glintfx`, `session_models_apply`, den-den / som, etc.
3. Prova: um `SessionStart` no perfil isolado **e** (depois) no vivo gera **uma** linha de hook core, não duas.
4. Backup do `settings.json` **não** vai para o repo do plugin (segredos).

### Passo G - Grok (segundo host)

Não é cutover de produto. É impedir terceira autoridade.

1. Depois do plugin canário existir no Grok (compat / marketplace / path do repo): os 51 `~/.grok/agents/<core>.md` **não** podem continuar como cópia ativa se o host os sombrear.
2. Preferir: host carrega o plugin; overlay Grok = adapter (hooks stdin, mapa de modelo, symlink de skill).
3. Os 20 `VAULT_ONLY` no Grok seguem a mesma classe (exclusão / overlay).
4. **Não** nesta fatia. **Não** apagar `~/.grok/agents` agora.

### Passo H - Verificar e só então chamar “cutover feito”

Checklist mínimo (espelha DoD PHASE 11):

- [ ] plugin habilitado em user scope no perfil vivo **depois** do canário
- [ ] 0 agents core user-scope sombreando
- [ ] 0 hooks core duplicados
- [ ] wrappers sem lógica duplicada
- [ ] 20 vault-only ainda presentes
- [ ] rollback ensaiado (Passo R) em perfil isolado
- [ ] medição (sha do agent ativo = plugin), não relatório de agente

## 4. Rollback (Passo R) - obrigatório **antes** do Passo D no vivo

Ensaio no perfil isolado, não na sessão do líder.

1. Restaurar os 51 blobs a partir do commit pré-D de `claude-memory` (`git checkout <sha-pre> -- agents/<lista>`).
2. Restaurar registros de hook/skill do backup de settings (fora do git se tiver segredo).
3. Desabilitar o plugin **ou** voltar ao SHA `LAST_KNOWN_GOOD` se o defeito for do plugin.
4. Provar: `/agents` volta a resolver o blob vault; hook global volta a disparar.
5. Registrar **qual gate** falhou (canário B, prova D, hook duplo, eval, CI).
6. Nenhum core sai do vault ativo de novo até existir equivalente testado no plugin (já existe hoje; o que pode faltar é o canário).

Não usar `git reset --hard` com outro agente na mesma árvore. Não `filter-repo` para “desfazer” cutover.

## 5. Mapa ação × classe (resumo operacional)

| Classe | Quem fica com o ficheiro | Ação no cutover |
|---|---|---|
| `CORE-GENERIC` (51) | plugin | plugin wins; `git rm` da cópia vault **após** canário |
| `PERSONAL-OVERLAY` (8) | vault | vault overlay; não publicar; não apagar |
| `INTENTIONAL-EXCLUSION` (12) | vault | keep intentional; não publicar; não apagar |
| Resíduo `STALE` *dentro* dos 51 vault | (some com o ficheiro) | não portar; caveman não se “preserva” |
| Skill wrapper D4 | overlay, se existir | só encaminhar |
| `tab_pendencias` embutida no plugin | produto standalone | tratar cópia do plugin como `STALE` (D5) |

Lista nominal: CSV. Não improvisar um 52º nome.

## 6. O que **não** fazer

1. **Não** cutover de `~/.claude` nesta fatia nem “porque o inventário já classificou”.
2. **Não** apagar diferença só para os dois lados parecerem iguais (D8 / plano § proibições).
3. **Não** daemon / timer / hook de sync vault ↔ plugin (D7).
4. **Não** união vault ∪ plugin como produto (publicaria perícia, jogo, PII).
5. **Não** publicar `revisor-textual` (paths) nem qualquer `dr-*`.
6. **Não** instalar o plugin no perfil **vivo** enquanto os 51+hooks globais estão ativos, a menos que o líder aceite risco ALTO de hook duplo. Caminho seguro = perfil isolado primeiro.
7. **Não** `CLAUDE_CONFIG_DIR` apontando para `~/.claude` e chamar isso de canário.
8. **Não** `isolation: worktree` neste repo (IDrive + concorrência).
9. **Não** push / merge em `main` / tag remota / GitHub Release sem ordem no contexto.
10. **Não** implementar BT-7 (gate de drift) nem BT-8 (evals) debaixo deste plano.
11. **Não** reescrever histórico para “limpar” os 51; o histórico **é** o backup.
12. **Não** confiar em `git grep` da árvore para provar ausência de sombreamento: medição é inventário de `name:` ativo no host + sha do blob servido.

## 7. Riscos residuais (declarados)

| Risco | Mitigação |
|---|---|
| Hook TDD/bigtech a correr duas vezes no vivo | canário isolado; só então desligar globais (F) |
| Operador usa Cósimo vault (solo/headcount) depois de BT-5 | some no Passo D; até lá, dual authority **mente** no host vivo |
| Grok continua com 51 cópias | Passo G; senão a métrica “1 SoT” falha no segundo host |
| Wrapper `/bigtech` volta a crescer | qualquer corpo além de encaminhar = `STALE` (D4) |
| Relatório de agente “já cortei os 51” | orquestrador re-mede `ls` + sha; relatório ≠ prova |
| Settings com token no commit de cutover | settings continua gitignored; backup fora do plugin |

## 8. Fora de escopo deste documento

- Executar os passos A–G.
- Escolher número de versão da release canário (PHASE 12).
- Redesenhar `tab_pendencias`.
- Mudar frontmatter `model:` dos 51 (literal de plataforma).
- FABLE-FINAL-AUDIT (PHASE 13).

## 9. DoD desta fatia (BT-6), distinto do DoD da PHASE 11

BT-6 fecha quando:

- [x] inventário classificado (51 + 20) com ação por linha
- [x] plano ordenado + canário + rollback + proibições
- [x] decisão de **não** mexer em `~/.claude` agora, escrita
- [ ] TODO `BT-6` → 🔍 (mesmo commit)
- [ ] tag local `campanha/w3-bt6-dual-authority`
- [ ] sem push

PHASE 11 só abre com FABLE-CUTOVER + canário + ordem do líder.
