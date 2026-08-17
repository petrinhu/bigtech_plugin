# PHASE 0.docs residual — cutover `docs/house/`

**Data:** 2026-08-16  
**Status:** fatia de **cópia/sync** feita; **cutover de paths** pendente  
**Relacionado:** `docs/house/README.md`, runbook `PLANO-MELHORIA-BIGTECH-CLAUDE-CODE-2026-08-16.md`

## Feito nesta fatia

- [x] Criar `docs/house/` com os **10** manuais a partir do **vault** (não das cópias antigas do plugin).
- [x] Prefixo `docs/house sync` em cada arquivo (origem, path_vault, sync_date, regra de prevalência).
- [x] `docs/house/README.md` com lista, SHA vault/body vs house_file, gaps (0), dual path legado.
- [x] Scan `rg -i 'password|token|api_key|secret' docs/house/` → limpo (só falso-positivos documentais).
- [x] Commit local `docs(house): …` — **sem push**.

## Residual (fase docs / cutover — NÃO nesta fatia)

1. **Atualizar links** em README, docs de produto e (quando autorizar) `AGENTS.md` para apontar a `docs/house/` como cópia de distribuição.
   - **Não editar AGENTS.md** só por esta fatia (manual de instalação; cutover explícito depois).
2. **Classificar dual path** legados (`docs/manuals/*`, `docs/{TOOLING,ORG,pipeline_*,lideranca_*}.md`):
   - opção A: deprecar com nota “use `docs/house/`” e manter por 1 release;
   - opção B: remover após canário + busca de referências zero.
3. **Não apagar legados** até inventário de referências (`rg 'docs/manuals|docs/ORG|docs/TOOLING|docs/pipeline_release|docs/lideranca'`) + decisão do líder.
4. **Re-sync periódico** quando vault mudar: procedimento em `docs/house/README.md`.
5. **Wikilinks `[[…]]` do vault** nos manuais: funcionam no Obsidian do vault; no plugin são texto — eventual glossário ou tabela de âncoras é opt-in posterior (não bloquear PHASE 0).
6. **README do plugin / marketplace**: mencionar `docs/house/` como manuais da casa sem vault.

## Fora de escopo desta fatia

- Push, tag, release, cutover destrutivo de `~/.claude`.
- Merge vault×plugin de conteúdo “melhor dos dois” (authority = vault; plugin legado não reabre revisão).
- Edição de `AGENTS.md` (install script reescrito para GitHub em BT-3/F1; fora desta fatia house).

## Critério de aceite do cutover futuro

- Zero links canônicos de produto apontando só para `docs/manuals/` ou manuais soltos em `docs/*.md` sem menção a `docs/house/`.
- `docs/house/README.md` SHA ainda batem com vault **ou** re-sync datado.
- AGENTS/README mencionam path de distribuição e regra vault-prevalece.
