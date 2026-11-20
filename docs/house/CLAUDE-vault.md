<!--
  docs/house sync
  origem: vault claudebrain / CLAUDE.md
  sync_date: 2026-11-20
  hmac_vault_sha256: 180eea1f2660709cf40f330f0eaee9e4a0abefa1d43e8ebfafd26f75a8901c5b
  transformacoes: T1=0 T2=0 T3a=1 T3=0 T4=0 T5=4
  regra: As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário. Se o usuário tiver o vault, o vault prevalece em conflito material; senão use esta cópia.
  sem segredos: não incluir tokens/credenciais
-->
# CLAUDE.md — Vault segundo cérebro

Auto-carrega em qualquer sessão Claude Code cuja CWD esteja na raiz do vault. Conteúdo em docs separados.

## Docs

- perfil.md — perfil dev, stacks, foco.
- vault-rules.md — escopo do vault, estilo de nota, exceções `/Projects/`.
- wikilinks-manuais.md — resolução `[[X]]` + 5 manuais canônicos (CONTRACT, TESTES, AGILE, DEPLOY_CHECKLIST, AUDITORIAS).
- para-structure.md — Projects/Areas/Resources/Inbox/Journal/Archive + pendências + permissões.

## Organização tipo bigtech (constelação de agents)

- [`ORG.md`](ORG.md) — manual de governança: constelação C-level (Celso/Capitolino/Caetano/Camilo/Cosmo/Narciso/Cândido/Confúcio/Cícero/Cláudio + Cósimo/Chief of Staff), RACI, variantes de pipeline por porte, política de ferramentas dos agents (secao 8), tabela de pendências ORG.
- [`pipeline_release_1.0.md`](pipeline_release_1.0.md) — pipeline de 12 fases (ideia ao 1.0) com agent e C-level por fase.
- [`lideranca_pipeline_release.md`](lideranca_pipeline_release.md) — teoria de liderança C-level e a constelação nomeada.
- [`TOOLING.md`](TOOLING.md) — 6º manual: ferramentas FOSS automatizáveis por agent (catálogo + status temos/baixar + comando de instalar + kit canônico). Agents operacionais têm seção "Ferramentas (usar SEMPRE)".
- Skill `/bigtech` monta o time via Cósimo (classifica porte, anti over-engineering); delega engenharia ao `/proj_software`.
