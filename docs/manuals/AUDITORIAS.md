# Auditorias Técnicas - Referência Completa

Manual de governança que acompanha o plugin. Manuais irmãos: [CONTRACT](CONTRACT.md) · [TESTES](TESTES.md) · [AGILE](AGILE.md) · [DEPLOY_CHECKLIST](DEPLOY_CHECKLIST.md). O `CLAUDE.md` na raiz do seu projeto define as preferências locais; estes manuais são seus padrões de engenharia.

---

> Checklists operacionais de auditoria para projetos C++ · Python · Web (PHP/JS/HTML).
> Cada item tem prioridade **🔴 CRÍTICO · 🟠 IMPORTANTE · 🟢 COSMÉTICO**.

> **Como usar este manual.** Este é o catálogo de referência dos temas de auditoria por stack. O conjunto de auditorias aplicável a um projeto concreto é materializado no `AUDITORIAS.md` da raiz daquele projeto, gerado e podado pela skill `/tab_pendencias` conforme o stack detectado (cada tema vira um item `AUD-*` na tabela de pendências). Consulte aqui o escopo de cada tema; rode lá a auditoria do seu projeto.

> **Política - ferramenta ausente.** Ao executar um item de auditoria (`AUD-*` / `A*`) cuja ferramenta requerida não está instalada, siga a [política de ferramenta ausente](../principles/missing-tool-policy.md) (fonte única do protocolo, agnóstica de SO): detecte conforme o SO; instale sozinho se a ferramenta for de userland (`pip`/`uv`, `cargo`, `npm`, binário no `$HOME`) ou OFEREÇA antes via AskUserQuestion se a instalação exigir `sudo`/gerenciador do sistema; nunca falhe por falta de ferramenta nem fique silencioso. O comando de instalação de cada ferramenta está no [TOOLING](../TOOLING.md); os pré-requisitos básicos do ambiente seguem o T15.0 do [TESTES](TESTES.md).

---

## Catálogo de temas por stack

### Parte I - C++ / Qt6 / MySQL

1. Índice Mestre e Roadmap
2. Arquitetura: 4 camadas, SOLID, DRY, TDD
3. Segurança: memory safety, SQL injection, binário, LGPD
4. C++23 moderno: tipos, concorrência, move semantics
5. Qt6 específico: signals/slots, model/view, QML, i18n
6. MySQL: schema, queries, EXPLAIN, migrations, LGPD
7. Qualidade de código: god classes, complexidade, dead code

### Parte II - Python / Qt6 / SQLite

1. Arquitetura Python: 4 camadas, SOLID, DRY, TDD
2. Segurança Python: SQL injection, senhas, LGPD

### Parte III - Web (PHP / JS / HTML)

1. Arquitetura web: 4 camadas, SOLID, DRY, TDD (com PHPUnit)
2. API design REST: verbos, status codes, auth, OpenAPI
3. Hardening PHP + LGPD: pipeline OWASP ZAP, incidentes

---

## Classificação de severidade

| Prioridade | Símbolo | Significado |
|---|---|---|
| Crítico | 🔴 | Bloqueia release: falha de segurança, perda de dado, violação de arquitetura grave |
| Importante | 🟠 | Corrigir antes do próximo marco: dívida técnica relevante, risco médio |
| Cosmético | 🟢 | Melhoria incremental: estilo, consistência, baixo impacto |

---

## Ver também

- [TESTES](TESTES.md): os procedimentos de teste (T1-T15) que precedem e alimentam a auditoria.
- [DEPLOY_CHECKLIST](DEPLOY_CHECKLIST.md): gates pré-deploy que dependem das auditorias de segurança.
- O `AUDITORIAS.md` na raiz do seu projeto traz o subconjunto aplicável ao seu stack.
