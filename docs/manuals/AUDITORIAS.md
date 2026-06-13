# Auditorias Técnicas  -  Referência Completa

Manual de governança que acompanha o plugin. Manuais irmãos: [CONTRACT](CONTRACT.md) · [TESTES](TESTES.md) · [AGILE](AGILE.md) · [DEPLOY_CHECKLIST](DEPLOY_CHECKLIST.md). O `CLAUDE.md` na raiz do seu projeto define as preferências locais; estes manuais são seus padrões de engenharia.

---

> Checklists operacionais de auditoria para projetos C++ · Python · Web (PHP/JS/HTML).
> Cada item tem prioridade **🔴 CRÍTICO · 🟠 IMPORTANTE · 🟢 COSMÉTICO**.

---

## Índice

### Parte I  -  C++ / Qt6 / MySQL
1. [Índice Mestre e Roadmap](#i1--índice-mestre-e-roadmap)
2. [Arquitetura  -  4 Camadas, SOLID, DRY, TDD](#i2--arquitetura--4-camadas-solid-dry-tdd)
3. [Segurança  -  Memory Safety, SQL Injection, Binário, LGPD](#i3--segurança--memory-safety-sql-injection-binário-lgpd)
4. [C++23 Moderno  -  Tipos, Concorrência, Move Semantics](#i4--c23-moderno--tipos-concorrência-move-semantics)
5. [Qt6 Específico  -  Signals/Slots, Model/View, QML, i18n](#i5--qt6-específico--signalsslots-modelview-qml-i18n)
6. [MySQL  -  Schema, Queries, EXPLAIN, Migrations, LGPD](#i6--mysql--schema-queries-explain-migrations-lgpd)
7. [Qualidade de Código  -  God Classes, Complexidade, Dead Code](#i9--qualidade-de-código--god-classes-complexidade-dead-code)

### Parte II  -  Python / Qt6 / SQLite
10. [Arquitetura Python](#ii2--arquitetura-python--4-camadas-solid-dry-tdd)
11. [Segurança Python](#ii3--segurança-python--sql-injection-senhas-lgpd)

### Parte III  -  Web
12. [Arquitetura Web](#iii1--arquitetura-4-camadas-web--solid-dry-tdd-com-phpunit)
13. [API Design REST](#iii5--api-design-rest--verbos-status-codes-auth-openapi)
14. [Hardening PHP + LGPD](#iii7--hardening-php--lgpd--pipeline-owasp-zap-incidentes)
