# W2 / BT-2 — verificação adversarial de `docs/house/`

**Data da verificação:** 2026-08-16  
**Hora local (medida):** `16/08/26 - 23:50:59` (`date '+%d/%m/%y - %H:%M:%S'`)  
**Papel:** verificador de campanha — host Grok, papel [grok][mais recente]  
**Item:** `BT-2` (`docs/house`: sync 10 manuais vault + README de navegação)  
**DoD desta fatia:** `TODO.md` BT-2 + `docs/campanha/2026-08-16-phase0-house-plan.md` (cópia/sync; **não** o cutover de paths)  
**HEAD do plugin no início desta auditoria:** `2ea32f52fd11780b7042c7afcb51cb51cee9351b` (working tree limpa)  
**Commit da entrega:** `24b1e8f9487cf2d979eddbc3e13c8086361bbc36` (`docs(house): sync 10 manuais canônicos do vault`)  
**Método:** re-medição em disco + objeto git + vault ao vivo. Prosa do README/house-plan **não** foi aceita sem prova.

**Veredito:** **PASS em todos os itens materiais do DoD da fatia.**  
**Decisão autônoma (confirmar retroativamente):** promover `BT-2` para **✅ Concluído** e Estado Auditado **✓**. Não é promoção de BT-1 / BT-3 / BT-4 (permanecem 🔍). Não fecha cutover de links (residual documentado).

---

## Escopo e o que isto não é

- Fecha a **cópia de distribuição** em `docs/house/`: 10 manuais + README, headers de sync, SHA body == vault, `Standards.md` presente, house-plan presente, sem secrets reais.
- **Não** fecha o cutover de paths (links em README/AGENTS/docs de produto; dual path legado). House-plan marca isso como residual explícito.
- **Não** é re-sync posterior do vault. SHA conferidos contra o vault **hoje** (ainda iguais).
- **Não** houve push. **Não** se tocou noutro ID BT-\*.

---

## Checklist DoD (item a item)

| # | Item | Veredito | Evidência âncora |
|---|---|:---:|---|
| 1 | 10 manuais + README existem em `docs/house/` | **PASS** | 11 arquivos, conjunto exato; nenhum extra |
| 2 | headers `docs/house sync` nos 10 manuais | **PASS** | 10/10 com origem, path_vault, sync_date, regra, sem-segredos |
| 3 | sem secrets reais | **PASS** | `rg` documental só; padrões de alta-sinal = 0 hits |
| 4 | `Standards.md` presente | **PASS** | `docs/house/Standards.md` (44 linhas + header); body SHA = vault |
| 5 | `docs/campanha/2026-08-16-phase0-house-plan.md` existe | **PASS** | tracked; nasceu em `24b1e8f`; 1 linha BT-3 depois |
| 6 | body byte-idêntico ao vault (prova de sync) | **PASS** | SHA-256 body == vault == tabela do README, 10/10 |

Nenhum FAIL material. Residuais abaixo **não** impedem ✅.

---

## 1. Inventário: 10 manuais + README

`find docs/house -maxdepth 1 -type f | wc -l` → **11**.  
Conjunto medido (ordem de listagem):

| # | Arquivo | Linhas (`wc -l`) | Papel |
|---|---|---:|---|
| 1 | `AGILE.md` | 518 | manual |
| 2 | `AUDITORIAS.md` | 47 | manual |
| 3 | `CONTRACT.md` | 987 | manual |
| 4 | `DEPLOY_CHECKLIST.md` | 74 | manual |
| 5 | `lideranca_pipeline_release.md` | 189 | manual |
| 6 | `ORG.md` | 199 | manual |
| 7 | `pipeline_release_1.0.md` | 500 | manual |
| 8 | `README.md` | 94 | navegação (não é um dos 10) |
| 9 | `Standards.md` | 44 | manual (gap P0 do plugin pré-fatia) |
| 10 | `TESTES.md` | 333 | manual |
| 11 | `TOOLING.md` | 235 | manual |

Os 10 nomes batem com a lista canónica do vault / house-plan / README (CONTRACT, TESTES, TOOLING, pipeline_release_1.0, DEPLOY_CHECKLIST, lideranca_pipeline_release, ORG, Standards, AGILE, AUDITORIAS).  
README lista os 10 com links relativos e marca `Standards.md` como o que faltava no plugin.

`git ls-files docs/house/` devolve os mesmos 11 paths. Nenhum untracked.

---

## 2. Headers de sync

Cada um dos **10** manuais começa com o bloco HTML:

```
<!--
  docs/house sync
  origem: vault claudebrain / <NOME>
  path_vault: /home/petrus/IDrive/Documentos/projetos_claudebrain/<NOME>
  sync_date: 2026-08-16
  regra: se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
```

Checagem mecânica: `docs/house sync` + `origem:` + `path_vault:` + `sync_date:` + `regra:` + `sem segredos:` presentes nos 10.  
`sync_date` = `2026-08-16` em todos.  
README **não** tem esse header (é índice de navegação, não cópia de um manual) — esperado.

Vault ao vivo existe nos 10 `path_vault` declarados (`VAULT_OK` × 10).

---

## 3. SHA-256: vault == body == tabela do README

Header quebra o hash do arquivo completo. O contrato do README é:

- `sha256_vault` / `sha256_body` = conteúdo após `-->\n` — devem ser iguais entre si e ao vault.
- `sha256_house_file` = arquivo inteiro (header + body).

Re-medição 16/08/26 23:49:59 (`hashlib.sha256` em Python 3):

| Arquivo | BODY==VAULT | BODY==README | FILE==README |
|---|:---:|:---:|:---:|
| CONTRACT.md | True | True | True |
| TESTES.md | True | True | True |
| TOOLING.md | True | True | True |
| pipeline_release_1.0.md | True | True | True |
| DEPLOY_CHECKLIST.md | True | True | True |
| lideranca_pipeline_release.md | True | True | True |
| ORG.md | True | True | True |
| Standards.md | True | True | True |
| AGILE.md | True | True | True |
| AUDITORIAS.md | True | True | True |

Valores (iguais nos três lados para body; file = header+body):

| Arquivo | sha256_vault (= body) | sha256_house_file |
|---|---|---|
| CONTRACT.md | `80cc659ed4633a29da9fc8e4fc9b851478d73424ffbdd0a40970c75af25c3b94` | `65fa239836f0ca58c8410dd08129c4c4e5e19a6ce219313ded7fd3a679eef989` |
| TESTES.md | `12728cd747b9df5cb01b8ea167a49666649bf8747c937f2ee2609d42cb099e5e` | `eadb448b8294f6687aaa2ad8d6b9515af9a3e81122dbd10a6f6449340590bc2b` |
| TOOLING.md | `8e1c870e427aa21d47825f408f20733e1e2288fc98431322f9e7a29c5dcbdfc3` | `37789d51bafc387aa52ea5b58d7e28c0db4b8c576a0e2c70ebf22a2707c5209e` |
| pipeline_release_1.0.md | `77ceee6f22e3ca31d27286595baadddb17ba51e07b49f1aaa30737c6dcdab759` | `3a7d901282d70d5124d567728b992bb7a61332eb60bfa98f25f70779daf66152` |
| DEPLOY_CHECKLIST.md | `9b7ca5fa65b38ebb223125e4d1810fbcb319c79263f011b75eeccb5daf428bdc` | `066c5e2be257a0469d31736b7d6ee001f088b609bb2fab90e4cffb4e74c00d6b` |
| lideranca_pipeline_release.md | `88457ef1728364a3419732b70acf4e8c83d713ce9be714dc104ff158fbb342ca` | `04bb02590616f7fc4751485aa226bc67655d964caf87f78c63ef2f229adfd3a8` |
| ORG.md | `7fc6c87c85cca67c3b5a6ae3c9b79be074b4646fe3d2ca2b0d0de9fffa7c3f18` | `0883522518b074cfacdc41bf2922fa8c971679d2cda653b450840b51e1ea9287` |
| Standards.md | `6e384fee46f0af7c56530bd2fc4ecff2df48aeedd94889905b60a9a7e20ab614` | `5b89aaa03c435ea2cf7731a63accac274f4ce655af1fa15433fe9e2d28fa4cc6` |
| AGILE.md | `9a96eaa08eb71b6196507516352c58ae0f71af44d9d88641ed95db2df6ab34c8` | `9286c2dfe876bd0365439bac883d09e68980ec2ddc2c6c18772256b0d554179e` |
| AUDITORIAS.md | `6cf4d3e55d9925a7b30eeedf12a54ce904aa8971c7457781338d6b014ceb6c43` | `608077399f90810d0a24a094e408132b698d54cd22e30a5d61090d82ad4603ad` |

Isto prova sync real, não só “os ficheiros existem”.

---

## 4. Secrets

### 4.1 Padrões de alta-sinal (0 hits)

```
rg -n --pcre2
  '-----BEGIN (RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----'
  '\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}'
  '\bxox[baprs]-[A-Za-z0-9-]{10,}'
  '\bAKIA[0-9A-Z]{16}\b'
  '\b(sk-ant-|sk-proj-|sk-live-)[A-Za-z0-9]{16,}'
  '\bAIza[0-9A-Za-z_-]{30,}'
  '\b(xai-|xai_)[A-Za-z0-9]{20,}'
  'Bearer [A-Za-z0-9._-]{20,}'
  docs/house/
```

Resultado: **NO_HIGH_SIGNAL_HITS**.  
Nota: `sk-live-abc123xyz789` no CONTRACT **não** casa o padrão `sk-live-` + 16+ alfanuméricos de chave — o sufixo é curto e fictício.

### 4.2 Scan documental (`password|token|api_key|secret`, case-insensitive)

Hits = só as classes já listadas no README:

| Classe | Onde | Julgamento |
|---|---|---|
| Header de sync | 10 manuais, linha `sem segredos:` | política, não credencial |
| T8 / gitleaks / age+sops / “No hardcoded secrets” | TESTES, DEPLOY_CHECKLIST, TOOLING, pipeline | doutrina |
| Design tokens | CONTRACT § tema; pipeline Storybook | vocabulário de UI |
| Anti-exemplo CONTRACT §8.2 | `sk-live-abc123xyz789`, `token=mypassword`, `limitless_api_key` | bloco `// INCORRECT  -  NEVER commit this` vs `// CORRECT` |

**Veredito: LIMPO de credenciais reais.**

---

## 5. `Standards.md`

Presente em `docs/house/Standards.md`.  
Header de sync OK; `path_vault` aponta para o vault; body SHA `6e384fee…` = vault ao vivo.  
README marca-o como o único dos 10 que **faltava** no plugin antes desta fatia (gap P0 do baseline PHASE 0). Confirmado: não há `Standards.md` em `docs/manuals/` nem na raiz de `docs/` (só em `docs/house/`).

---

## 6. House-plan

`docs/campanha/2026-08-16-phase0-house-plan.md` existe, tracked.

| Facto | Valor |
|---|---|
| Nasceu | `24b1e8f` (mesmo commit da cópia house) |
| Edição posterior | `1bfc800` (BT-3): 1 linha — AGENTS.md deixou de ser “Codeberg-oriented” |
| Status no próprio plano | “fatia de **cópia/sync** feita; **cutover de paths** pendente” |
| Checkboxes da cópia | 5/5 marcados (criar 10, prefixo, README+SHA, scan secrets, commit local) |

O residual do plano (atualizar links, classificar dual path, não apagar legados, re-sync, wikilinks) **não** faz parte do DoD de BT-2.

---

## 7. Entrega no histórico

```
git log --oneline -- docs/house/
24b1e8f docs(house): sync 10 manuais canônicos do vault (PHASE 0)
```

`git show --stat 24b1e8f`: 12 files, +3258 (10 manuais + README + house-plan).  
TODO BT-2 estava em 🔍 desde o intake; esta verificação promove só esse ID.

---

## Residuais (não-FAIL)

1. **Cutover de paths** ainda pendente: `docs/manuals/` e manuais soltos em `docs/{TOOLING,ORG,pipeline_*,lideranca_*}.md` continuam. House-plan § Residual; fora do escopo de BT-2.
2. **Wikilinks `[[…]]`** do vault nos corpos: no plugin são texto. Plano já declara opt-in posterior.
3. **`path_vault` é path de máquina** (`/home/petrus/IDrive/...`). Origem da cópia, não segredo; quem clona o produto usa o body, não o path.
4. **Re-sync futuro** se o vault andar. Hoje body ainda == vault (provado).
5. Nota WSJF em `TODO.md` (~L185) ainda diz “Itens 🔍 (BT-0/2/3/4)” — prosa velha após BT-0 ✅; **não** editada aqui (não tocar outros BT / não alargar escopo).

---

## Decisão

Todos os itens materiais de BT-2 **PASS**.  
Promover na tabela: Status **✅ Concluído**, Estado Auditado **✓**.  
Não promover BT-1 / BT-3 / BT-4. Sem push. Tag local `campanha/w2-bt2-house-verify` no SHA deste commit de verificação.
