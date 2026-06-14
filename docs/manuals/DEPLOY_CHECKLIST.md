# DEPLOY CHECKLIST - Alterações Irreversíveis em Produção

Manual de governança que acompanha o plugin. Manuais irmãos: [CONTRACT](CONTRACT.md) · [TESTES](TESTES.md) · [AUDITORIAS](AUDITORIAS.md) · [AGILE](AGILE.md). Pré-deploy obrigatório: rodar [TESTES](TESTES.md) T8 (gitleaks/secrets) + T10 (SQL Injection) + T12 (CVEs).

---

> Antes de executar qualquer operação marcada como irreversível percorra **todos** os itens abaixo.
>
> Checklist condensado em 5 fases contíguas (0 a 4), do gate de classificação ao cutover. Cobre o caminho crítico de uma mudança irreversível: o seu projeto pode acrescentar fases conforme o stack (por exemplo, janela de manutenção ou aprovação formal).

---

## FASE 0 - Classificação da Mudança
- Migração ou alteração de schema de banco de dados
- Implementação ou modificação de autenticação (2FA, OAuth, SSO)
- Rotação de chaves criptográficas
- Operação DROP, TRUNCATE ou ALTER TABLE sem rollback trivial

---

## FASE 1 - Pré-Condições de Ambiente
- Backup completo (dados + schema) realizado nas últimas 2 horas
- Hash SHA-256 do backup registrado
- Restauração do backup testada em ambiente isolado

---

## FASE 2 - Database Migration (Dual Writes)
- A aplicação está configurada para escrever simultaneamente no banco legado e no novo schema
- Backfill de dados históricos concluído
- Validação de consistência lógica 100%

---

## FASE 3 - Validação de Segurança
- Bibliotecas criptográficas de fontes oficiais
- Cabeçalhos de Segurança HTTP (HSTS, CSP, X-Frame)
- Fluxo de 2FA validado (Passou)

---

## FASE 4 - Blue-Green Cutover
- Rollback plan documentado e testado
- Health check retornando 200 OK por 5 minutos consecutivos
- Taxa de erro pós-cutover < 0,5%
