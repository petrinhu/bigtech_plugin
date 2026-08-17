# docs/house — manuais canônicos da casa (cópia de distribuição)

Sincronizado a partir do **vault claudebrain** (autoridade). Se o usuário tiver o vault na máquina, **o vault prevalece** em conflito material; senão use esta cópia.

| Campo | Valor |
|---|---|
| Sync date | **2026-08-16** |
| Origem | `/home/petrus/IDrive/Documentos/projetos_claudebrain/` |
| Gaps no vault | **nenhum** (10/10 presentes) |
| Segredos | sem tokens/credenciais reais (ver scan abaixo) |

## Lista dos 10 manuais

| # | Arquivo house | Origem vault | Status |
|---|---|---|---|
| 1 | [CONTRACT.md](CONTRACT.md) | `CONTRACT.md` | OK |
| 2 | [TESTES.md](TESTES.md) | `TESTES.md` | OK |
| 3 | [TOOLING.md](TOOLING.md) | `TOOLING.md` | OK |
| 4 | [pipeline_release_1.0.md](pipeline_release_1.0.md) | `pipeline_release_1.0.md` | OK |
| 5 | [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) | `DEPLOY_CHECKLIST.md` | OK |
| 6 | [lideranca_pipeline_release.md](lideranca_pipeline_release.md) | `lideranca_pipeline_release.md` | OK |
| 7 | [ORG.md](ORG.md) | `ORG.md` | OK |
| 8 | [Standards.md](Standards.md) | `Standards.md` | OK (**ausente** no plugin antes desta fatia) |
| 9 | [AGILE.md](AGILE.md) | `AGILE.md` | OK |
| 10 | [AUDITORIAS.md](AUDITORIAS.md) | `AUDITORIAS.md` | OK |

Cada arquivo em `docs/house/` começa com um bloco HTML comment (`docs/house sync`) com origem, path do vault, data e regra de prevalência. O **corpo** (após `-->\n`) é **byte-idêntico** ao vault na data de sync.

## SHA-256

O header de sync quebra o hash do arquivo completo em relação ao vault. Use:

- **`sha256_vault` / `sha256_body`**: conteúdo canônico (sem header) — devem ser iguais.
- **`sha256_house_file`**: arquivo em `docs/house/` (header + body).

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

Verificação local (body = vault):

```bash
# exemplo: CONTRACT
python3 -c "
from pathlib import Path, hashlib
t = Path('docs/house/CONTRACT.md').read_bytes()
body = t[t.find(b'-->\\n')+4:]
print(hashlib.sha256(body).hexdigest())
"
```

## Dual path legado (NÃO apagar nesta fatia)

Cópias **anteriores e possivelmente defasadas** ainda existem no plugin. Cutover de links/paths é fase posterior (ver `docs/campanha/2026-08-16-phase0-house-plan.md`).

| Path legado | Manuais |
|---|---|
| `docs/manuals/` | CONTRACT, TESTES, DEPLOY_CHECKLIST, AGILE, AUDITORIAS |
| `docs/` (raiz) | TOOLING, ORG, pipeline_release_1.0, lideranca_pipeline_release |
| *(antes ausente)* | Standards.md |

**Canônico de distribuição após esta fatia:** `docs/house/`.  
**Autoridade com vault local:** vault claudebrain na raiz.

## Scan de segredos (2026-08-16)

Comando: `rg -i 'password|token|api_key|secret' docs/house/`

**Veredito: LIMPO de credenciais reais.** Hits são falso-positivos documentais:

| Classe | Exemplos |
|---|---|
| Header de sync | `sem segredos: não incluir tokens/credenciais` (10×) |
| Política / checklist | T8 secrets scan, “No hardcoded secrets”, gitleaks, age+sops |
| Design tokens | “design token system”, “theme tokens”, “Tokens (cores, tipografia…)” |
| Anti-exemplos no CONTRACT §8.2 | strings fictícias `sk-live-abc123xyz789`, `token=mypassword`, `limitless_api_key` (ilustram o que **não** fazer) |

## Re-sync

Quando o vault mudar materialmente:

1. Re-copiar os 10 a partir do vault.
2. Reaplicar o bloco `docs/house sync` (atualizar `sync_date`).
3. Atualizar esta tabela de SHA.
4. Commit local; push só com autorização do líder.
