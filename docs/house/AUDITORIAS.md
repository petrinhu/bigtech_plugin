<!--
  docs/house sync
  origem: vault claudebrain / AUDITORIAS.md
  path_vault: /home/petrus/IDrive/Documentos/projetos_claudebrain/AUDITORIAS.md
  sync_date: 2026-08-16
  regra: se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
# Auditorias Técnicas  -  Referência Completa

> **Cópia canônica** na raiz do vault. Versão estável espelhada em [[Resources/Standards/AUDITORIAS]].

## Referências cruzadas

- Manuais irmãos: [[CONTRACT]] · [[TESTES]] · [[AGILE]] · [[DEPLOY_CHECKLIST]]
- Hub: [[Standards]] · [[CLAUDE]]
- Alvos C++/Qt: [[Projects/PokemonTCGViewer]] · [[Projects/astrometrica]] · [[Projects/transcritor]] · [[Projects/driver_brother_hl_l1222]]
- Alvos Python: [[Projects/rag_maker]] · [[Projects/orcamento-pessoal]] · [[Projects/my_comp]]
- Alvos Web: [[Projects/site_consultorio]] · [[Projects/my_comp]]
- Reports históricos: [[Projects/PokemonTCGViewer/reports]] · [[Projects/transcritor/reports]] · [[Projects/my_comp/reports]]

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
