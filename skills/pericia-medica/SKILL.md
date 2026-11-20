---
name: pericia-medica
description: "Orquestra um CASO médico-jurídico acionando o QUARTETO dr-medico-perito (perícia geral) + dr-medico-trabalho (ocupacional) + dr-medico-psiquiatra (psiquiátrica) + dr-advogado (jurídico), roteando pela natureza do caso. Psiquiátrico/saúde mental (imputabilidade, interdição, capacidade, dano psíquico, incapacidade por transtorno mental, Burnout) → dr-medico-psiquiatra; ocupacional (acidente de trabalho, doença ocupacional, insalubridade, LER/DORT) → dr-medico-trabalho; demais (previdenciário físico, erro médico, dano corporal, medicina legal) → dr-medico-perito. Caso misto mental-ocupacional aciona psiquiatra + médico do trabalho. O médico fornece a base técnico-científica verificada; o advogado converte em tese, peça e estratégia. Por padrão integra médico + advogado; com --med_only o escopo INICIAL fica só no(s) médico(s) e o advogado vira passo opcional. Use quando o usuário disser \"monte o caso\", \"impugne o laudo e faça a petição\", \"caso de doença ocupacional/insalubridade\", \"caso previdenciário/psiquiátrico completo\", \"perícia + jurídico\", ou invocar /bigtech:pericia-medica. Para tarefa só médica use /bigtech:dr-medico-perito, /bigtech:dr-medico-trabalho ou /bigtech:dr-medico-psiquiatra; só jurídica use /bigtech:dr-advogado."
argument-hint: "[caso/objetivo] [--med_only] [--objetivo impugnar-laudo|erro-medico-autor|defesa-medico|formular-quesitos|viabilidade|doenca-ocupacional|insalubridade|acidente-trabalho|ler-dort|imputabilidade|capacidade-civil|incapacidade-psiquica|dano-psiquico|burnout] [--arquivo caminho/dos/autos.pdf]"
allowed-tools: [Read, Grep, Glob, Agent, AskUserQuestion, TodoWrite, Write]
---

# pericia-medica: caso médico-jurídico (quarteto: perito + médico do trabalho + psiquiatra + advogado)

Orquestrador que aciona o quarteto **`bigtech:dr-medico-perito`** (perícia geral), **`bigtech:dr-medico-trabalho`** (ocupacional) ou **`bigtech:dr-medico-psiquiatra`** (psiquiátrica) + **`bigtech:dr-advogado`** (direito), conforme a natureza do caso. O médico dá a base técnico-científica verificada; o advogado dá a tese, a peça e a estratégia. Cada um no seu papel: os médicos não dão direito, o advogado não diagnostica.

> A perícia médica é o núcleo; o jurídico é a camada integrável. Com `--med_only`, entrega-se primeiro só a perícia e o advogado fica como próximo passo **opcional**.

Argumentos recebidos: $ARGUMENTS

## O que fazer

1. **Identifique o objetivo e a natureza do caso** em `$ARGUMENTS` (e a flag `--objetivo`). Se não estiver claro, pergunte via **AskUserQuestion** (1 a 3 itens: objetivo, polo, documentos), opção recomendada primeiro. Detecte a flag `--med_only`.
2. **Escolha o(s) especialista(s) médico(s) pela natureza do caso:**
   - **Psiquiátrica/saúde mental** (imputabilidade, periculosidade, interdição/curatela, capacidade civil, dano psíquico, incapacidade por transtorno mental, Burnout, simulação) → **`bigtech:dr-medico-psiquiatra`**.
   - **Ocupacional/trabalhista** (acidente de trabalho/trajeto, doença ocupacional, insalubridade, periculosidade, LER/DORT, nexo ocupacional, LTCAT/PPP/PCMSO) → **`bigtech:dr-medico-trabalho`**.
   - **Demais** (previdenciário físico, erro médico, dano corporal/DPVAT, medicina legal) → **`bigtech:dr-medico-perito`**.
   - **Caso misto** (ex.: **transtorno mental relacionado ao trabalho** / Burnout) → aciona **`bigtech:dr-medico-psiquiatra` (diagnóstico/nexo psíquico) + `bigtech:dr-medico-trabalho` (ambiente/exposição, fluxograma do Limbo)**.
   - Na dúvida, pergunte via **AskUserQuestion**.
3. **Defina a sequência** conforme o objetivo (o "médico" abaixo = o(s) especialista(s) do passo 2):
   - **impugnar-laudo / insalubridade / doenca-ocupacional / ler-dort / burnout / dano-psiquico / incapacidade-psiquica:** o médico disseca o laudo/documento (falhas técnicas + quesitos) → `bigtech:dr-advogado` redige a impugnação/petição com fundamento jurídico + os pontos técnicos.
   - **erro-medico-autor:** o `bigtech:dr-medico-perito` avalia nexo/dano/culpa técnica → advogado monta a tese de responsabilidade civil.
   - **defesa-medico:** o `bigtech:dr-medico-perito` refuta nexo/culpa e demonstra a *lex artis* → advogado monta a defesa.
   - **acidente-trabalho:** o `bigtech:dr-medico-trabalho` avalia nexo (CAT, NTEP, Schilling) e dano → advogado monta a tese.
   - **imputabilidade / capacidade-civil:** o `bigtech:dr-medico-psiquiatra` avalia (EEM, diagnóstico, critério biopsicológico) → advogado monta a tese (penal/civil).
   - **formular-quesitos:** advogado define o que precisa provar (tese) → o médico redige os quesitos técnicos.
   - **viabilidade:** o médico estima a robustez técnica → advogado estima o prognóstico jurídico → síntese.
4. **Dispare os subagents em sequência** via a ferramenta `Agent`, **um de cada vez**, passando o resultado do anterior como contexto do seguinte:
   - comece pelo(s) especialista(s) médico(s) escolhido(s) (`subagent_type: bigtech:dr-medico-perito`, `subagent_type: bigtech:dr-medico-trabalho` ou `subagent_type: bigtech:dr-medico-psiquiatra`); em caso misto, dispare os dois médicos antes do advogado. Exceção: em *formular-quesitos*, o `bigtech:dr-advogado` vem primeiro para definir a tese.
   - **Se `--med_only`:** dispare **apenas** o(s) médico(s); ao final, **ofereça** acionar o `bigtech:dr-advogado` como próximo passo opcional (não dispare sem o ok do usuário).
5. **Sintetize** o produto conjunto numa resposta única e clara, preservando as marcações de verificação do médico e a nota de revisão (CRM/RQE/OAB) de cada lado.
6. Para iterações, faça novo despacho ao mesmo agente com o resultado anterior no prompt (subagent não tem SendMessage).

## Papéis (não misturar)

- **`bigtech:dr-medico-perito`**: perícia geral: nexo, dano corporal, incapacidade física, erro médico, medicina legal, quesitos, literatura verificada (ABNT). Nunca dá tese jurídica.
- **`bigtech:dr-medico-trabalho`**: perícia ocupacional: nexo ocupacional, insalubridade/periculosidade, LER/DORT, NR, LTCAT/PPP/PCMSO, fluxograma do **Limbo**, quesitos, normas verificadas (ABNT). Nunca dá tese jurídica.
- **`bigtech:dr-medico-psiquiatra`**: perícia psiquiátrica: imputabilidade, capacidade civil, interdição, incapacidade por transtorno mental, dano psíquico, EEM, **vigilância de Burnout**, laudo de 15 seções, quesitos (ABNT). Nunca dá tese jurídica.
- **`bigtech:dr-advogado`**: enquadramento, tese, peça, recurso, prazos, jurisprudência verificada, nota OAB. Nunca diagnostica.

## Quando NÃO usar

- Tarefa só médica → `/bigtech:dr-medico-perito`, `/bigtech:dr-medico-trabalho` ou `/bigtech:dr-medico-psiquiatra`. Só jurídica → `/bigtech:dr-advogado`.
- Conduta clínica de paciente real → recusada; oriente atendimento (risco psíquico → emergência).

## Autoridade

O usuário é o líder supremo e soberano desta organização (o CEO da sua bigtech). Diante de dúvida ou de mais de uma opção, perguntar via **AskUserQuestion** (recomendada primeiro), nunca decidir sozinho.

As instruções do usuário (o CLAUDE.md global e o do projeto, e as regras que eles referenciam) prevalecem sobre os manuais, agents e lembretes deste plugin em qualquer conflito. Onde divergirem, siga as do usuário.
