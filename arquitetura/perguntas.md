# Perguntas e respostas

## Como a UPA continua triando e atendendo com a internet fora do ar, e o que acontece quando ela volta?

**Resposta:** Por ser uma arquitetura cell-based, cada UPA é tratada como uma célula, onde o banco local, a triagem e os demais processos acontecem localmente. Quando a internet cai, a unidade continua operando com autonomia, armazenando as operações em fila local e mantendo a continuidade do atendimento. Quando a rede volta, a célula sincroniza os dados com o ambiente central, reconciliando o estado local com o sistema principal sem interromper o atendimento em andamento.

**Sustentação nos ADRs e diagramas:** essa resposta é sustentada pelo ADR 0002, que define a arquitetura baseada em células como a forma de manter a operação local mesmo sob falha de rede, e pela análise da matriz, que aponta a resiliência local como principal diferencial da arquitetura cell-based. Os diagramas C4 de contexto, contêineres e componentes reforçam essa visão ao mostrar a UPA como unidade autônoma que interage com o sistema central de forma desacoplada e tolerante a falhas.

## Como duas unidades disputando o mesmo leito nunca conseguem reservá-lo ao mesmo tempo, com o sistema legado ainda no circuito?

Resposta: A garantia de exclusão mútua é obtida pelo Serviço de Leitos e Regulação. O serviço reside fora do modelo celular, atuando como autoridade central para o recurso. A reserva é tratada como uma operação single writer, com controle de concorrência por versão do recurso e lock otimista. Antes de confirmar a reserva, o sistema verifica o status atual do leito e aceita apenas a primeira confirmação válida. Uma segunda tentativa é rejeitada ou marcada como pendente, impedindo a reserva por duas unidades.
Quando uma unidade perde a conectividade com o sistema central, a reserva não passa pela confirmação local, falhando ou entrando em pendência, evitando a geração de confirmação online, já que pode resultar na dupla alocação.
Quanto ao sistema legado, ainda presente, atua apenas como mecanismo de integração e sincronização de estado durante a transição, sem presença na decisão sobre a reserva.

Sustentação nos ADRs e diagramas: essa resposta está alinhada ao ADR de arquitetura baseada em células, pois a autonomia local exige consistência local e controle de exclusão para recursos compartilhados. A matriz também reforça a necessidade de isolamento e consistência operacional ao tratar a regulação de leitos como um ponto sensível do domínio. O diagrama de componentes evidencia a presença do módulo de regulação e o desacoplamento entre a unidade local e os sistemas externos, permitindo que a reserva seja tratada de forma segura mesmo com o legado ainda no circuito. 

## Como o prontuário garante que se saiba quem acessou cada registro, e como convive a guarda de 20 anos com os direitos do paciente sob a LGPD?

**Resposta:** O prontuário oferece rastreabilidade através de mecanismos da arquitetura: autenticação e autorização para cada acesso, trilha de auditoria imutável de todo acesso e alteração, criptografia de dados sensíveis em repouso e em trânsito, e retenção configurável por categoria de evento. O sistema registra quem e quando acessou, o que foi alterado e se a ação foi autorizada.
No entanto, a base legal do tratamento, o prazo de retenção aplicável a cada categoria de dado clínico e o atendimento aos direitos do titular sob a LGPD são decisões de política institucional e jurídica.
A guarda de 20 anos e os direitos do paciente convivem com a LGPD por políticas de acesso, minimização e retenção definidas pela organização, enquanto a arquitetura fornece a rastreabilidade e a proteção técnica dos dados.

**Sustentação nos ADRs e diagramas:** esse ponto é suportado pela decisão de arquitetura que prioriza integridade, rastreabilidade e proteção dos dados sensíveis, especialmente no contexto de prontuário eletrônico e auditoria. O ADR de arquitetura celular não elimina os requisitos de segurança e conformidade; ele os torna mais evidentes na operação local e no sincronismo com o centro. Os diagramas C4 de componentes e de contexto ajudam a mostrar a separação entre o subsistema local, os módulos de autenticação e auditoria e os sistemas externos, tornando explícita a necessidade de controle de acesso e rastreabilidade.



## Como a notificação compulsória chega à vigilância em até 24 horas mesmo se o sistema federal estiver indisponível?

**Resposta:** A notificação compulsória é registrada no armazenamento local da célula assim que é criada. Como a unidade opera com autonomia, o evento fica em fila local como pendente enquanto a rede ou o sistema federal estiverem indisponíveis. Quando a conexão retorna, a célula sincroniza esse evento com o ambiente central, que encaminha a notificação para a vigilância. Dessa forma, a notificação não é perdida e pode ser entregue dentro do prazo de 24 horas mesmo com indisponibilidade temporária do sistema externo.

**Sustentação nos ADRs e diagramas:** essa resposta é diretamente sustentada pelo ADR 0002 e pelo desenho de resiliência local da arquitetura cell-based. A matriz e o caso demonstram que o problema dos sistemas externos indisponíveis precisa ser contornado por mecanismo de fila local e sincronização eventual. Os diagramas C4 mostram a célula operando autonomamente e enviando eventos para o núcleo central quando a infraestrutura externa volta, preservando a continuidade do fluxo de notificação compulsória.

## Como o sistema legado de regulação é substituído aos poucos sem interromper o serviço?

**Resposta:** A substituição do sistema legado ocorre de forma gradual em fases. A arquitetura cell-based permite que cada unidade opere localmente enquanto o novo sistema está sendo implantado em paralelo, reduzindo o risco de interrupção. O legado e o novo sistema convivem por meio de adaptadores e interfaces de integração, que permitem a troca incremental de responsabilidades sem quebrar o fluxo de atendimento. Conforme o novo sistema assume as operações críticas, o legado é retirado de forma controlada, mantendo o serviço ininterrupto durante a migração.
