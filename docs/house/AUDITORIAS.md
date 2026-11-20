<!--
  docs/house sync
  origem: vault claudebrain / AUDITORIAS.md
  sync_date: 2026-11-20
  hmac_vault_sha256: 7210c74415749a6053d1af65b830ac701921403161808133ea85fadae48d3474
  transformacoes: T1=4 T2=0 T3a=0 T3=0 T4=0 T5=0
  regra: As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário. Se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
# Auditorias Técnicas  -  Referência Completa

> **Cópia canônica** na raiz do vault. Versão estável espelhada em [[Resources/Standards/AUDITORIAS]].

## Referências cruzadas

- Manuais irmãos: [[CONTRACT]] · [[TESTES]] · [[AGILE]] · [[DEPLOY_CHECKLIST]]
- Hub: [[Standards]] · [[CLAUDE]]

---

> Checklists operacionais de auditoria para projetos C++ · Python · Web (PHP/JS/HTML).
> Cada item tem prioridade **CRÍTICO · IMPORTANTE · COSMÉTICO**.

> **Como usar este manual.** Este é o catálogo de referência dos temas de auditoria por stack. O conjunto de auditorias aplicável a um projeto concreto é materializado no `AUDITORIAS.md` da raiz daquele projeto, gerado e podado pela skill `tab_pendencias` conforme o stack detectado (cada tema vira um item `AUD-*` na tabela de pendências). Consulte aqui o escopo de cada tema; rode lá a auditoria do seu projeto.

> **Ferramenta ausente.** Siga a regra de [[TOOLING]] (legenda de status): ferramenta de linha de comando de uso geral pode ser instalada com aviso; biblioteca, dependência de projeto, modelo, extensão, navegador e serviço só com permissão do usuário; nunca falhar calado.

---

## Classificação de severidade

| Prioridade | Significado |
|---|---|
| CRÍTICO | Bloqueia release: falha de segurança, perda de dado, violação de arquitetura grave |
| IMPORTANTE | Corrigir antes do próximo marco: dívida técnica relevante, risco médio |
| COSMÉTICO | Melhoria incremental: estilo, consistência, baixo impacto |

Os ícones 🔴 (crítico), 🟠 (importante) e 🟢 (cosmético) só entram se o projeto ou o usuário pedir. Sem esse pedido, use o nome da severidade em texto.

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

---

## Ver também

- [[TESTES]]: os procedimentos de teste (T1-T15) que precedem e alimentam a auditoria.
- [[DEPLOY_CHECKLIST]]: gates pré-deploy que dependem das auditorias de segurança.
- O `AUDITORIAS.md` na raiz do seu projeto traz o subconjunto aplicável ao stack dele.
