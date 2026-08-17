# W5 / BT-9 — Proteção de `main` + release gates

**Data:** 2026-08-17  
**Hora local (medida):** `17/08/26 - 00:14:09` (`date '+%d/%m/%y - %H:%M:%S'`)  
**Item:** `BT-9` (proteção remota GitHub de `main` + gates de status checks do CI)  
**Repo:** `petrinhu/bigtech_plugin`  
**Branch protegida:** `main`  
**API:** classic Branch Protection (`PUT/GET …/branches/main/protection`) — **não** rulesets (lista de rulesets estava vazia `[]`).

**Decisão autônoma (modo yolo do líder; confirmar retroativamente):** habilitar proteção de `main` **sem** exigir review de PR (solo maintainer se auto-bloqueava), com status checks estritos do CI multi-OS (BT-4), force-push e delete **desligados**, e `enforce_admins: false` para hotfix administrativo documentado.

---

## O que foi ligado

| Controle | Valor aplicado | Notas |
|---|---|---|
| Classic branch protection em `main` | **ON** (`protected: true`) | `GET` HTTP 200 (antes: 404 "Branch not protected") |
| `required_status_checks.strict` | `true` | branch do PR deve estar up-to-date com a base |
| Contexts / checks exigidos | 8 (lista abaixo) | nomes = `jobs[].name` do workflow CI (Actions app_id `15368`) |
| `required_pull_request_reviews` | `null` (desligado) | solo maintainer: não exigir review de si mesmo |
| `enforce_admins` | `false` | admin pode bypassar em hotfix (ver § Bypass) |
| `allow_force_pushes` | `false` | force-push em `main` bloqueado para não-admin |
| `allow_deletions` | `false` | apagar a branch `main` bloqueado |
| `restrictions` (push actors) | `null` | sem restrição de quem pusha (API exige null em repo pessoal público sem teams) |
| `required_signatures` | `false` (default) | não exigido nesta fatia |
| Rulesets | não criados | classic API bastou no plano free/public |

### Contexts exigidos (release gates de CI)

Fonte: último run **success** em `main` antes desta fatia — run id `31990067211` (`docs(bt-6): inventário dual-authority + plano de cutover`), e nomes de job no [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml):

1. `validate (ubuntu-latest, py3.11)`
2. `validate (ubuntu-latest, py3.12)`
3. `validate (windows-latest, py3.11)`
4. `validate (windows-latest, py3.12)`
5. `validate (debian via container)`
6. `validate (fedora via container)`
7. `validate (archlinux via container)`
8. `gitleaks (secrets)`

Todos resolvidos com `app_id: 15368` (GitHub Actions) no GET pós-PUT.

### Comando aplicado (reproduzível)

```bash
gh api --method PUT repos/petrinhu/bigtech_plugin/branches/main/protection --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "validate (ubuntu-latest, py3.11)",
      "validate (ubuntu-latest, py3.12)",
      "validate (windows-latest, py3.11)",
      "validate (windows-latest, py3.12)",
      "validate (debian via container)",
      "validate (fedora via container)",
      "validate (archlinux via container)",
      "gitleaks (secrets)"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": false
}
JSON
```

### Verificação (DoD de status)

```bash
gh api repos/petrinhu/bigtech_plugin/branches/main/protection
# HTTP 200; strict=true; 8 contexts; enforce_admins=false;
# allow_force_pushes=false; allow_deletions=false;
# required_pull_request_reviews=null
```

Resumo `GET` medido nesta fatia:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "validate (ubuntu-latest, py3.11)",
      "validate (ubuntu-latest, py3.12)",
      "validate (windows-latest, py3.11)",
      "validate (windows-latest, py3.12)",
      "validate (debian via container)",
      "validate (fedora via container)",
      "validate (archlinux via container)",
      "gitleaks (secrets)"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

`gh api …/branches/main` → `"protected": true`.

---

## Decisão autônoma (confirmar retroativamente)

| Tema | Escolha | Por quê |
|---|---|---|
| PR reviews obrigatórios | **Não** | Maintainer solo: review de si mesmo trava o fluxo sem ganho real |
| Status checks | **Sim, 8 jobs CI** | Release gate = matrix BT-4 + gitleaks; espelho do run verde |
| `strict: true` | **Sim** | evita merge de PR atrasado em relação a `main` |
| `enforce_admins` | **false** | permite hotfix de admin sem desligar proteção inteira |
| Force-push / delete | **false / false** | protege histórico e existência de `main` |
| Rulesets vs classic | **classic** | PUT classic funcionou; rulesets vazios; sem feature-gate do plano |

Confirmar com o líder se quiser endurecer depois (ex.: `require PR` + 0 reviews ainda bloqueia push direto em alguns planos; ou `enforce_admins: true` em janelas estáveis).

---

## Como bypassar (admin)

Com `enforce_admins: false`, a conta **admin** do repositório (`petrinhu`, permissões medidas: `admin: true`) pode:

1. **Hotfix direto em `main`** via push normal (não há “require PR before merging”).  
   - Force-push continua **desaconselhado** e a UI/API trata force-push como desabilitado para não-admins; admin com bypass pode forçar em emergência — **só com ordem explícita do líder**.
2. **UI GitHub:** Settings → Branches → Branch protection rule de `main` → desmarcar temporariamente um check ou a regra inteira → aplicar hotfix → **religar** (e re-correr o `GET` de verificação).
3. **API:**
   ```bash
   # ler estado atual
   gh api repos/petrinhu/bigtech_plugin/branches/main/protection > /tmp/main-protection.json
   # desligar (emergência)
   gh api --method DELETE repos/petrinhu/bigtech_plugin/branches/main/protection
   # religar = reaplicar o PUT deste doc
   ```
4. **Não** usar bypass para “passar CI vermelho em silêncio”. CI vermelho bloqueia release/tag de produto (regra da casa). Bypass é para incidente operacional (ex.: reverter um commit que quebrou o runner), não para contornar gates de qualidade.

---

## O que isto **não** é

- **Não** é tag de release semântica de produto (`vX.Y.Z`). Tag desta fatia = campanha `campanha/w5-bt9-branch-protection`.
- **Não** cutover de `~/.claude` / `~/.grok`.
- **Não** exige CODEOWNERS nem review humano (solo).
- **Não** ruleset enterprise-only; classic protection basta e foi o que a API aceitou.
- **Não** fecha `TST-BT-1` / `AUD-BT-1` (ondas W6/W7 de revalidação e auditoria de campanha).

---

## Impacto operacional no fluxo da casa

| Fluxo | Efeito |
|---|---|
| Push direto em `main` (write) | Ainda possível (sem “require PR”); force-push não |
| Merge de PR em `main` | Exige os 8 checks verdes + branch atualizada (`strict`) |
| Apagar `main` | Bloqueado |
| Admin hotfix | Possível (`enforce_admins: false`); documentar e repor proteção se alterada |
| CI vermelho em PR | Merge bloqueado pelos required checks |

---

## Prova e artefatos

| Artefato | Valor |
|---|---|
| Remote | `https://github.com/petrinhu/bigtech_plugin.git` (`origin`) |
| Pré-estado | `GET …/protection` → 404 Branch not protected |
| Pós-estado | `GET …/protection` → 200, 8 contexts, flags acima |
| Run CI de referência (nomes) | `31990067211` success |
| Workflow | `.github/workflows/ci.yml` jobs `test`, `test-distros`, `secrets-scan` |
| Token scopes usados | `repo` + `workflow` (conta `petrinhu` via `gh`) |

---

## Status do item

| Campo | Valor |
|---|---|
| ID | BT-9 |
| Status após fatia | ✅ Concluído |
| Estado Auditado | ✓ (prova = `GET` protection API HTTP 200 com payload esperado) |
| Tag campanha | `campanha/w5-bt9-branch-protection` |
