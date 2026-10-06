# Changelog — 0001

## Objeção

Foi apontado que a afirmação de que **"duas reservas concorrentes não conseguem ser aceitas ao mesmo tempo"** apresentava uma garantia maior do que a arquitetura demonstrava, principalmente diante do uso de bancos locais e sincronização posterior em outras partes do sistema.

## A onde mudou: ADR0003

## Decisão

**Parcialmente aceita.**

A objeção foi parcialmente rebatida porque a **Regulação de Leitos não utiliza o modelo Cell-Based com bancos locais independentes**. As reservas são realizadas contra um **Serviço de Leitos e Regulação centralizado**, que atua como autoridade única e utiliza **single writer + lock otimista**.

Entretanto, a redação original foi considerada imprecisa por não explicar o comportamento em caso de perda de conectividade.

## O que vai mudar

A resposta será reescrita para:

- Explicitar o **Serviço de Leitos e Regulação como autoridade central única**.
- Explicar o uso de **single writer e lock otimista** para evitar reservas concorrentes.
- Deixar claro que uma unidade **desconectada não poderá confirmar uma reserva localmente**.
- Especificar que, sem acesso ao serviço central, a reserva **falha ou permanece pendente/bloqueada**.
- Esclarecer que o **sistema legado atua apenas na sincronização/integração**, não como autoridade concorrente.

# Changelog — 0002

## Objeção

Foi apontado que o **Event Sourcing não garante, por si só, uma auditoria completa**, pois registra principalmente eventos que alteram o estado do domínio. Visualizações e consultas ao prontuário não necessariamente geram eventos de domínio e, portanto, precisam de um mecanismo específico de auditoria.

## A onde mudou: ADR0004

## Decisão

**Aceita.**

A objeção foi considerada tecnicamente correta. O **Event Sourcing** será utilizado para registrar o histórico de mutações do estado clínico, mas não será responsável por registrar acessos e visualizações dos dados sensíveis.

## O que vai mudar

A arquitetura será ajustada para:

- Separar o **Event Sourcing** do **Log de Auditoria**.
- Utilizar uma camada dedicada de **Audit Log** para registrar visualizações, consultas, acessos e outras ações sobre dados sensíveis.
- Armazenar os registros de auditoria em uma estrutura **Append-Only** separada do Event Store.
- Limitar o uso de **Event Sourcing** aos contextos em que o histórico e a reconstrução temporal do estado agreguem valor ao domínio.
- Definir políticas específicas de **retenção e gerenciamento** para os logs de auditoria, considerando os requisitos de conformidade e proteção de dados.

# Changelog — 0003

## Objeção

Foi apontado que a arquitetura, por si só, não define a **base legal, os prazos de retenção ou o atendimento aos direitos do titular previstos na LGPD**. Esses pontos dependem de decisões de governança e jurídicas, não apenas de decisões arquiteturais.

## A onde mudou: ADR0005

## Decisão

**Aceita.**

A arquitetura fornece mecanismos técnicos de segurança, rastreabilidade e retenção configurável, mas não deve determinar sozinha os requisitos legais e institucionais relacionados à retenção e ao tratamento dos dados.

## O que vai mudar

A resposta será reescrita para:

- Separar as **capacidades técnicas da arquitetura** das decisões de **governança e compliance**.
- Explicitar que a arquitetura fornece **autenticação, autorização, auditoria, criptografia e retenção configurável**.
- Remover a afirmação de que a guarda de 20 anos se aplica automaticamente ao histórico de auditoria e eventos de domínio.
- Deixar claro que os **prazos de retenção por categoria de dado** serão definidos pela área jurídica/institucional responsável.
- Esclarecer que a **base legal e o atendimento aos direitos do titular** são decisões de governança, não resolvidas exclusivamente pela arquitetura.
