<!--
  docs/house sync
  origem: vault claudebrain / DEPLOY_CHECKLIST.md
  sync_date: 2026-11-23
  hmac_vault_sha256: 51414fc76586eb2c39a92ce368b0f36687ff645b56a9ee7d42fd2d0117d30f9a
  transformacoes: T1=1 T2=0 T3a=0 T3=0 T4=0 T5=0
  regra: As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário. Se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
# DEPLOY CHECKLIST  -  Alterações Irreversíveis em Produção

> **Cópia canônica** na raiz do vault (resumo executivo das 7 fases). Versão estável espelhada em [[Resources/Standards/DEPLOY_CHECKLIST]]. Versão completa executável (sub-checklists, comandos de exemplo, tabela de status) em `~/.claude/templates/deploy-checklist.md` — diretiva normativa cross-project descrita em `~/.claude/docs/deploy-irreversivel.md`.

## Referências cruzadas

- Manuais irmãos: [[CONTRACT]] · [[TESTES]] · [[AUDITORIAS]] · [[AGILE]]
- Hub: [[Standards]] · [[CLAUDE]]
- Pré-deploy obrigatório: rodar [[TESTES]] T8 (gitleaks/secrets) + T10 (SQL Injection) + T12 (CVEs)

---

> O rito vale só para as sete classes da Fase 0. Antes de executar uma delas, percorra **todos** os itens abaixo.
>
> Cada item recebe `[PASSOU]`, `[FALHOU]` ou `[BLOQUEADO]`. Qualquer `[FALHOU]` ou `[BLOQUEADO]` aborta o deploy imediatamente, e o deploy só é autorizado com as 7 fases `[PASSOU]`. Se as instruções do usuário definem um processo próprio de deploy irreversível, ele prevalece por inteiro.

---

## FASE 0  -  Classificação da Mudança
- Login: implementação ou modificação de autenticação (2FA, OAuth, SSO)
- Permissão: alteração de RBAC/ACL
- Token: geração, rotação ou revogação de token em produção
- Segredo: geração ou troca de senha, credencial ou outro segredo em produção
- Apagar dado: DROP, TRUNCATE ou ALTER TABLE sem rollback trivial
- Schema de banco: migração ou alteração de schema de banco de dados
- Rotação de chave: rotação ou geração de chave criptográfica em produção

Fora destas sete, a mudança não passa por este rito e segue a publicação comum ([[pipeline_release_1.0]], Fase 11.2).

---

## FASE 1  -  Pré-Condições de Ambiente
- Backup completo (dados + schema) realizado nas últimas 2 horas
- Hash SHA-256 do backup registrado
- Restauração do backup testada em ambiente isolado

---

## FASE 2  -  Shadow Deployment (Validação de Tráfego em Sombra)
- Mirror de tráfego ativo: requisições reais duplicadas para o ambiente Green/Shadow; respostas ao usuário só do Blue (produção atual)
- Mínimo 30 min de tráfego espelhado; divergência de taxa de erro Blue x Green < 0,1%; latência P99 do Green não excede o Blue em mais de 15%
- Sem Load Balancer configurável (ex.: hospedagem compartilhada): substituir por dupla validação manual em staging, documentada no `CLAUDE.md` do projeto, e avançar para a Fase 3

---

## FASE 3  -  Database Migration (Dual Writes)
- A aplicação está configurada para escrever simultaneamente no banco legado e no novo schema
- Backfill de dados históricos concluído
- Validação de consistência lógica 100% (amostra mínima de 1.000 registros)

---

## FASE 4  -  Validação de Segurança
- Bibliotecas criptográficas de fontes oficiais
- Cabeçalhos de Segurança HTTP (HSTS, CSP, X-Frame)
- Fluxo de 2FA validado (Passou)

---

## FASE 5  -  Blue-Green Cutover
- Rollback plan documentado e testado
- Health check retornando 200 OK por 5 minutos consecutivos
- Taxa de erro pós-cutover < 0,5%
- **Sub-fase 5.3 (passo irreversível):** mínimo 48h de operação estável no novo ambiente + aprovação nominal registrada (Responsável + Data-Hora + Assinatura) + banco/estado legado desativado mas mantido offline por 30 dias adicionais antes do descarte definitivo

---

## FASE 6  -  Pós-Deploy e Documentação
- Incident report: o que mudou, quando, quem aprovou, métricas de validação
- Runbook de rollback atualizado com lições aprendidas
- Alertas de monitoramento ajustados para a nova arquitetura
- Time notificado da conclusão bem-sucedida do deploy
