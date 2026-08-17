# PHASE 0 — intake TODO `BT-*` (campanha 2026-08-16)

Data: 2026-08-16. Motor: `tab_pendencias/tools/todo_intake.py` (`run_intake`, `LOCAL_INTEGRATION`).

## IDs criados

| ID | Onda | Status pós-intake | Rota |
|---|---|---|---|
| BT-0 | W-BT0 | 🔍 Pendente verificação | LOCAL_INTEGRATION (L0) |
| BT-1 | W-BT1 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-2 | W-BT1 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-3 | W-BT2 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-4 | W-BT2 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-5 | W-BT3 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-6 | W-BT3 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-7 | W-BT4 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-8 | W-BT4 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |
| BT-9 | W-BT5 | ⏳ Pendente | LOCAL_INTEGRATION (L0) |

Flags de julgamento (todos): `fields_complete=True`, `authority_ok=True`, `is_local=True`, `is_foundation=False`, `is_scoped=False`.

Justificativa L0 (não FULL/SCOPED): anti-OE — tabela legada com 69 itens; append puro evita reordenação massiva e não mexe em N9/`WIP` legado. Foundation-ish (BT-0/BT-1/BT-6) entrou como **local** com onda/prereq explícitos na linha, não como `FULL_REORDER`.

BT-0 em 🔍: baseline de docs/campanha já em `8076cd1` + artefatos PHASE 0; **não** ✅ (falta TST/AUD da DoD).

BT-9: go/no-go do líder fica na descrição; item planejado na tabela (não residual INBOX).

## Health depois

```
Saude da TODO.md (79 itens):
  ✅ concluidos: 59
  ⏳/🔄 pendentes (nao entregues): 10
  🔍 aguardando verificacao: 10  (9 legados OS/TOOL + BT-0)
  INBOX: 0 (classificaveis=0)
```

Legados ✅/🔍 intocados. N9 permanece 🔄. Sem full reorder.

## Audit (diagnóstico, sem auto-fix destrutivo)

- **CHK-11 CRÍTICO [julgamento]**: `todo_health` conta a tabela principal (79); contagem independente sobe ~19 por **tabelas auxiliares** no mesmo `TODO.md` (scoring WSJF pai + scoring qualitativo N8–N10 com layout diferente). Divergência estável (~19) antes e depois do intake (69→88, 79→98). **Não auto-fixável** sem reestruturar seções legadas; não corrompe IDs. Documentado; sem `todo_fix`.
- CHK-05/07/12: legados pré-existentes (abreviações `D1*`, ondas iguais a prereq, AUD-R* sem prereq).
- CHK-14 cosmético: última onda agora `W-BT5` (BT-9); item Wiki+iniciante legado `W-WIKI` já ✅ em onda anterior — residual cosmético de perfil casa.
- `.tab_pendencias.ini` criado: `[profile] name = casa` (sem paths de máquina).

## O que ficou para PHASE 1

1. Fechar verificação de **BT-0** (DoD PHASE 0: re-medir SHAs, inventário, modelos; TST/AUD → só então ✅).
2. Executar **BT-1** (ADR source-of-truth / FABLE-ORG-ARCH) e **BT-2** (`docs/house` sync dos 10 manuais) na onda W-BT1.
3. Não cutover de `~/.claude`; não push/tag sem líder.
4. Demais BT-* seguem ondas W-BT2…W-BT5 conforme prereqs na tabela.

## Artefatos tocados

- `TODO.md` — +10 linhas BT-0..BT-9
- `.tab_pendencias.ini` — perfil casa
- este relatório

Sem push.
