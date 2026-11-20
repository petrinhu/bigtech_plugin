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
| CONTRACT.md | `0037f7a1fd787488f3cce7a00078c101baeb575693b7efad273ca884a2a562ed` | `c2f64ced18876520d9d988f43a696690c345e2963cc7da97f47d723bf6217005` | T1 |
| TESTES.md | `66b094fc2ae4d97252c8edb1a6476c8dd49349b2123184345098a30179dead5e` | `1e3db19b040492080fa3d76a68ae559b7e0274ffd610d40ef5872c761967262f` | T1 |
| TOOLING.md | `93d7abb6f16fbc61827f7131dd0a72c6d04d9a470302c439f5625c9885e050f1` | `412fc1c4c647ea10d0435a4dcc7c6dd998e2413386edfdc3e8a45360cfa225e6` | nenhuma |
| pipeline_release_1.0.md | `19a5c3aad4cbe5d3a32890e9d324e01780d30f9044c5b54c1309bf7f8591008d` | `6839afdf80fece62d7593be3978c0120d9e4ea348ceb581ac8921ef2b52dcd20` | nenhuma |
| DEPLOY_CHECKLIST.md | `ed548f1da52830cd85e39bd184d16f9686f70427019cd70f1ce50309b0f728ba` | `b4e3e9931af31c191541f83a90996855511ef449e0331f12106e2b056b5696a3` | T1 |
| lideranca_pipeline_release.md | `6fa88b4477e725fe51d666387e05572eabebf28223e1819e31f6a53efbe9257d` | `20cd774f42b11fc20bb65d9d6c3912b9b666c39aa6133eb23ac81486250f4b89` | nenhuma |
| ORG.md | `e99d55729b4e75c81c870c97ead8902f0481736e8bc73d785437af363cabe2ac` | `e73c595f10ee93c7a3d4eacaadbc645888ec593037bf1320a466f81ab3349d92` | T2 |
| Standards.md | `28a9d129ba72df0f943b1ebd9d6032840c65c9cddb585b9e9096ffdf040a1974` | `34f8283ada07a24a2bd983b96b8554b983ce276c9fd4b649cd29d16850435291` | T1 |
| AGILE.md | `2655cfc9058e35eb0a0baa040fcf3d0e52df4433a7f073d1dc11bb7a51fd95d7` | `e33ebf74074254ec6668fb2f472142cffbad7b0d6ea5cf2aafae64a190303260` | T1 |
| AUDITORIAS.md | `7210c74415749a6053d1af65b830ac701921403161808133ea85fadae48d3474` | `189ad565f2b854df57d9641b54e06ae2bb5a0c0d857abe3dbd8dbef1b232bef8` | T1 |
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
