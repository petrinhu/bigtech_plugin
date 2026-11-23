# docs/house: manuais canônicos da casa (cópia de distribuição)

Sincronizado a partir do **vault claudebrain** (autoridade) pelo script `scripts/sync_house.py`. Se o usuário tiver o vault na máquina, **o vault prevalece** em conflito material; senão use esta cópia.

Esta pasta é **gerada**: não editar à mão. Para regenerar, rode `python3 scripts/sync_house.py --vault <raiz do vault> --write`; para conferir, `--check` (sai 1 se algum arquivo divergir do vault).

| Campo | Valor |
|---|---|
| Origem | raiz do vault claudebrain (caminho omitido por privacidade; informe `--vault`) |
| Gaps no vault | **nenhum** (12/12 presentes) |
| Segredos | sem tokens/credenciais reais (ver scan abaixo) |
| Data de sync | `sync_date` no cabeçalho de cada arquivo |

## Lista dos 12 arquivos (10 manuais, `audit-seo` e o CLAUDE do vault)

| # | Arquivo house | Origem vault | Status |
|---|---|---|---|
| 1 | [CONTRACT.md](CONTRACT.md) | `CONTRACT.md` | OK |
| 2 | [TESTES.md](TESTES.md) | `TESTES.md` | OK |
| 3 | [TOOLING.md](TOOLING.md) | `TOOLING.md` | OK |
| 4 | [pipeline_release_1.0.md](pipeline_release_1.0.md) | `pipeline_release_1.0.md` | OK |
| 5 | [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) | `DEPLOY_CHECKLIST.md` | OK |
| 6 | [lideranca_pipeline_release.md](lideranca_pipeline_release.md) | `lideranca_pipeline_release.md` | OK |
| 7 | [ORG.md](ORG.md) | `ORG.md` | OK |
| 8 | [Standards.md](Standards.md) | `Standards.md` | OK (**ausente** no plugin antes da CONS-04B) |
| 9 | [AGILE.md](AGILE.md) | `AGILE.md` | OK |
| 10 | [AUDITORIAS.md](AUDITORIAS.md) | `AUDITORIAS.md` | OK |
| 11 | [audit-seo.md](audit-seo.md) | `audit-seo.md` | OK (domínio pessoal vira `{{DOMINIO_PRODUCAO}}`, T4) |
| 12 | [CLAUDE-vault.md](CLAUDE-vault.md) | `CLAUDE.md` do vault | OK (nome diferente de propósito: não é CLAUDE.md do plugin nem carregado de subpasta; caminho virou "na raiz do vault", T3a) |

Cada arquivo começa por um bloco HTML comment (`docs/house sync`) com origem, data, contagem de transformações e a regra de precedência. O **corpo** (após `-->\n`) é o do vault com as transformações de privacidade listadas abaixo. Sem transformação aplicada, o corpo é byte-idêntico ao vault.

## Transformações (todas de privacidade ou estruturais)

| Id | O que faz |
|---|---|
| T1 | Sai a linha que contém wikilink de `Projects/` ou `Areas/` (nomes de projetos e áreas pessoais). |
| T2 | A linha de autoridade pessoal vira o parágrafo padrão do plugin: "Quem opera este plugin é o líder supremo e soberano desta organização." |
| T3a | Caminho do vault na frase "cuja CWD esteja dentro de" vira "na raiz do vault". Roda antes da T3. |
| T3 | Caminho que começa na raiz de usuário vira `<caminho local removido>`. |
| T4 | Linha "- Dominio previsto em producao:" vira `{{DOMINIO_PRODUCAO}}`. |
| T5 | Link markdown relativo cujo alvo não existe em `docs/house` (marca `link-externo`, separada das de privacidade) vira só o nome do arquivo, sem link. Ex.: o link para um arquivo fora desta pasta vira o nome dele como texto simples. |

Nenhuma transformação altera o conteúdo do texto; T5 só tira o link de alvos fora de `docs/house`. Wikilinks `[[X]]` de outros tipos, URLs, âncoras e os links para arquivos desta pasta ficam como estão no vault.

Caminho do vault para o `--check` local: `--vault`, depois a variável `BIGTECH_VAULT`, depois o arquivo local `~/.config/bigtech/vault_path` (uma linha, fora do repo).

## SHA-256

- **`hmac_vault_sha256`**: HMAC-SHA256 do texto do vault com uma chave local que não está no repo (`~/.config/bigtech/sync_house.key`, modo 600). Autentica a versão do vault sincronizada. Não há sha256 do texto do vault em lugar nenhum desta pasta: o texto antes da redação tem pouca entropia (nomes de projeto, caminhos), e um hash cru permitiria testar palpites até desfazer a redação. Sem a chave, `--check` sai 3 e avisa que não conferiu a versão do vault.
- **`sha256_corpo_transformado`**: hash do corpo depois das transformações, com prefixo de domínio `corpo-transformado`. É o que está no arquivo; não é o hash do vault.

<!-- sync:tabela inicio -->
| Arquivo | hmac_vault_sha256 (chave local) | sha256_corpo_transformado | Transformações aplicadas |
|---|---|---|---|
| CONTRACT.md | `b3c02c12aafcbe6b03d1d261c260595dfff8f213b482aa69f6ef0255ada3cacc` | `497c40b6140e77faf2958fc0a887656211f42e556515264d59b053c4082bba47` | T1 |
| TESTES.md | `f5104865913bf9c3d51f0df893e0c2dd97cda9e99ada1118bdd04a11afe87b7a` | `5e31e3aeeecc8d839298f6c39fabc56e1a50b9e1c46e528e78d3a12a205dc10c` | T1 |
| TOOLING.md | `a72de16aca5daf160901d0214e170c5ae4974c0dc0fd1704d4ddaa8e93ccd08e` | `8d0fc96efffa0664a0defa633c7b1181f1c6e00e1666b3c9855728e7d1cb408c` | nenhuma |
| pipeline_release_1.0.md | `38bb7c8f7cea5ee6820dc3e0696136e74382999484b3f010a865d1e21a3ec538` | `16b7c38f136edd6f4714cd1b09b59100f1b8e57e354c7df0b149d76f6a8a998e` | nenhuma |
| DEPLOY_CHECKLIST.md | `51414fc76586eb2c39a92ce368b0f36687ff645b56a9ee7d42fd2d0117d30f9a` | `5c926bdffdaa94e300728ac647c1d2daaf6249121031ce49dcb4707d2e184424` | T1 |
| lideranca_pipeline_release.md | `6fa88b4477e725fe51d666387e05572eabebf28223e1819e31f6a53efbe9257d` | `20cd774f42b11fc20bb65d9d6c3912b9b666c39aa6133eb23ac81486250f4b89` | nenhuma |
| ORG.md | `eccb8911769d3a240c1a4e2bb1dedc6de35b4a6565fa7fbdd75820a781677af1` | `47142e37b0c1ca3d61480a9ceadb98810d2e4515383890b102872ed29a18f203` | T2 |
| Standards.md | `6d73c4c246498ae8027a59166408393f0a42d3fe00bba40b5a6d0ec59af25eaf` | `dec4bc0c1297c03f050356b45305bad9aa4a0c44f696b5a02d735a5d45d5cad4` | T1 |
| AGILE.md | `8395187d0c06dfc5ba3f4c51bcc0efaca65ad571ab858fae5c725d001f3e1ce9` | `35e63eaa5d76e987717b20fa102243a23b0ad5537bd87c5ae7619fa2ab781165` | T1 |
| AUDITORIAS.md | `6782751c19f404353a43cc9e2c3db22760df2c7b4417d6c493bc9790673591b2` | `1126051a179c726cfb2533cb01cbd1272ce30fabe8cefa0ac4140cf591642030` | T1 |
| audit-seo.md | `d0ce5704cbec73a320f2ecba5a967f680d1d7d465da35553cfbbf860f5cd01f1` | `491b79f3443e7f554219ce6f463edb1af6e14a4963764d63f87c078c1935e1e3` | T4 |
| CLAUDE-vault.md | `180eea1f2660709cf40f330f0eaee9e4a0abefa1d43e8ebfafd26f75a8901c5b` | `2e7d2615f60cc0b86aec250a3e46fb2a3d9c7b3420c77a189681a32e60cb68f3` | T3a, T5 |
<!-- sync:tabela fim -->

## Caminhos antigos (removidos)

As cópias antigas dos manuais, que ficavam na pasta de manuais legada e nos arquivos soltos de `docs/` (raiz), saíram do plugin na CONS-13. A cópia canônica é esta pasta, `docs/house/`. Os históricos das cópias antigas ficam no git e nos relatórios de `docs/campanha/`.

**Canônico de distribuição:** `docs/house/`.  
**Autoridade com vault local:** vault claudebrain na raiz.

## Scan de segredos (2026-08-16)

Comando: `rg -i 'password|token|api_key|secret' docs/house/`

**Veredito: LIMPO de credenciais reais.** Hits são falso-positivos documentais:

| Classe | Exemplos |
|---|---|
| Header de sync | `sem segredos: não incluir tokens/credenciais` (12×) |
| Política / checklist | T8 secrets scan, "No hardcoded secrets", gitleaks, age+sops |
| Design tokens | "design token system", "theme tokens", "Tokens (cores, tipografia…)" |
| Anti-exemplos no CONTRACT §8.2 | strings fictícias `sk-live-abc123xyz789`, `token=mypassword`, `limitless_api_key` (ilustram o que **não** fazer) |

## Re-sync

Quando o vault mudar materialmente:

1. Rodar `python3 scripts/sync_house.py --vault <raiz do vault> --write` (regenera os 12 arquivos e a tabela acima; exige a chave local e o vault).
2. Rodar `python3 scripts/sync_house.py --vault <raiz do vault> --check` antes de commitar (saída 0 = em dia; 3 = sem chave, não conferido).
3. Commit local; push só com autorização do líder.
