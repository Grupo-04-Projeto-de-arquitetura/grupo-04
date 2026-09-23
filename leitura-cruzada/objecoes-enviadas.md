## Objeções relacionadas aos diagramas

### Objeção 1 — Acoplamento direto ao banco do legado via "SQL Direct" apesar do nome "ACL"

**Trecho atacado:** Diagrama de Contexto (Nível 1), relação "Consulta e reserva leitos em tempo real [Database Link / REST / ACL]"; Diagrama de Componentes (Nível 3), `LegacyBedSystemAdapter (ACL)` → Sistema Legado de Leitos, relação "Atualiza estado do leito no sistema antigo [SQL Direct / REST]".

**Argumento:** A pergunta central do Envelope C é "como vocês substituem o legado aos poucos, com pouca gente e sem nuvem?". Um componente rotulado como Anti-Corruption Layer que acessa o banco do legado via SQL direto contradiz o próprio propósito do padrão: ele expõe o schema interno do sistema antigo ao novo sistema, em vez de isolar um do outro atrás de um contrato estável. Com apenas 10 desenvolvedores (sem times dedicados de integração), qualquer mudança de coluna ou tabela no legado — algo comum em um sistema de até 2 anos ainda em produção — quebra silenciosamente o novo sistema, e a equipe pequena não tem folga para depurar esse tipo de acoplamento oculto continuamente.

**O que faríamos no lugar:** Restringir toda comunicação com o legado à API/contrato formal já existente (mesmo que mais lenta), mantendo o adaptador apenas como tradutor de protocolo. Isso é o que de fato permite migrar funcionalidades do legado aos poucos sem risco de quebra por acesso direto ao schema.

### Objeção 2 — RabbitMQ como peça adicional de infraestrutura stateful

**Trecho atacado:** Diagrama de Contêineres (Nível 2), container "Message Broker [RabbitMQ]", com a relação "Publica e consome eventos de atendimento, vigilância e auditoria [AMQP / Port 5672]".

**Argumento:** O sistema já introduz PostgreSQL e Redis como stores próprios; adicionar um terceiro sistema stateful (cluster de mensageria) eleva ainda mais a carga operacional de uma equipe de apenas 2 pessoas de infraestrutura, sem apoio de serviço gerenciado de nuvem (proibido pelo envelope). O próprio diagrama já usa um padrão de Outbox transacional no PostgreSQL para a integração com o e-SUS/CADSUS ("Envia notificações... via Outbox + Circuit Breaker") — ou seja, o grupo já tem uma solução de entrega assíncrona resiliente sem broker dedicado, mas não a reaproveitou para os eventos internos de atendimento/vigilância/auditoria, preferindo introduzir uma tecnologia nova para o mesmo tipo de problema.

**O que faríamos no lugar:** Usar o mesmo padrão de tabela Outbox no PostgreSQL já existente para os eventos internos (atendimento, vigilância, auditoria), processados por um worker agendado — evitando manter um cluster RabbitMQ adicional com a equipe reduzida do envelope.

### Objeção 3 — Monólito único concentrando 5 módulos de naturezas muito diferentes

**Trecho atacado:** Diagrama de Contêineres (Nível 2), container "Monólito Modular (API Core)", descrito como "Aplicação central contendo os módulos de Atendimento, PEC, Agendamento, Leitos, Vigilância e Farmácia."

**Argumento:** O enunciado descreve subdomínios com naturezas e ritmos de mudança muito distintos — Regulação de Leitos exige consistência forte e é o alvo direto da substituição gradual do legado; Vigilância é analítico/em lote; Agendamento tem pico sazonal de 20x. Colocar todos em uma única unidade de implantação (ainda que "modular" internamente) significa que qualquer deploy relacionado à Regulação de Leitos — justamente o módulo que precisa evoluir aos poucos para substituir o legado — exige recompilar e reimplantar o sistema inteiro, incluindo Farmácia, PEC e Vigilância. Isso vai contra a resposta que o próprio envelope pede: uma substituição incremental e de baixo risco do legado, com equipe pequena que não pode se dar ao luxo de re-testar o sistema inteiro a cada mudança pontual no módulo de leitos.

**O que faríamos no lugar:** Manter o monólito modular para a maior parte dos módulos (justificável pelo orçamento e equipe de 10 devs), mas isolar o módulo de Regulação de Leitos como um serviço deployável separadamente (mesmo dentro do mesmo ambiente on-premises), permitindo evoluir e substituir a integração com o legado sem redeploy do restante do sistema.

---

**Observação (não é objeção de arquitetura):** O grupo não entregou o Mapa de Restrições e Decisões (segunda entrega solicitada no enunciado), o que impede avaliar se as justificativas textuais para cada decisão — especialmente para o Envelope C — de fato endereçam a pergunta obrigatória "como vocês substituem o legado aos poucos, com pouca gente e sem nuvem?". As objeções acima se baseiam apenas no que os diagramas comunicam.
