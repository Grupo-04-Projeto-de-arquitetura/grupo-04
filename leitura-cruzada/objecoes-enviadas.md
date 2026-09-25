## Objeções relacionadas aos diagramas

### Objeção 1  Acoplamento direto ao banco do legado via "SQL Direct" apesar do nome "ACL"

**Trecho atacado:** Diagrama de Contexto (Nível 1), relação "Consulta e reserva leitos em tempo real [Database Link / REST / ACL]"; Diagrama de Componentes (Nível 3), `LegacyBedSystemAdapter (ACL)` → Sistema Legado de Leitos, relação "Atualiza estado do leito no sistema antigo [SQL Direct / REST]".

**Argumento:** A pergunta central do Envelope C é "como vocês substituem o legado aos poucos, com pouca gente e sem nuvem?". Um componente rotulado como Anti-Corruption Layer que acessa o banco do legado via SQL direto contradiz o próprio propósito do padrão: ele expõe o schema interno do sistema antigo ao novo sistema, em vez de isolar um do outro atrás de um contrato estável. Com apenas 10 desenvolvedores (sem times dedicados de integração), qualquer mudança de coluna ou tabela no legado  algo comum em um sistema de até 2 anos ainda em produção  quebra silenciosamente o novo sistema, e a equipe pequena não tem folga para depurar esse tipo de acoplamento oculto continuamente.

**O que faríamos no lugar:** Restringir toda comunicação com o legado à API/contrato formal já existente (mesmo que mais lenta), mantendo o adaptador apenas como tradutor de protocolo. Isso é o que de fato permite migrar funcionalidades do legado aos poucos sem risco de quebra por acesso direto ao schema.

### Objeção 2  RabbitMQ como peça adicional de infraestrutura stateful

**Trecho atacado:** Diagrama de Contêineres (Nível 2), container "Message Broker [RabbitMQ]", com a relação "Publica e consome eventos de atendimento, vigilância e auditoria [AMQP / Port 5672]".

**Argumento:** O sistema já introduz PostgreSQL e Redis como stores próprios; adicionar um terceiro sistema stateful (cluster de mensageria) eleva ainda mais a carga operacional de uma equipe de apenas 2 pessoas de infraestrutura, sem apoio de serviço gerenciado de nuvem (proibido pelo envelope). O próprio diagrama já usa um padrão de Outbox transacional no PostgreSQL para a integração com o e-SUS/CADSUS ("Envia notificações... via Outbox + Circuit Breaker")  ou seja, o grupo já tem uma solução de entrega assíncrona resiliente sem broker dedicado, mas não a reaproveitou para os eventos internos de atendimento/vigilância/auditoria, preferindo introduzir uma tecnologia nova para o mesmo tipo de problema.

**O que faríamos no lugar:** Usar o mesmo padrão de tabela Outbox no PostgreSQL já existente para os eventos internos (atendimento, vigilância, auditoria), processados por um worker agendado  evitando manter um cluster RabbitMQ adicional com a equipe reduzida do envelope.

### Objeção 3  Monólito único concentrando 5 módulos de naturezas muito diferentes

**Trecho atacado:** Diagrama de Contêineres (Nível 2), container "Monólito Modular (API Core)", descrito como "Aplicação central contendo os módulos de Atendimento, PEC, Agendamento, Leitos, Vigilância e Farmácia."

**Argumento:** O enunciado descreve subdomínios com naturezas e ritmos de mudança muito distintos  Regulação de Leitos exige consistência forte e é o alvo direto da substituição gradual do legado; Vigilância é analítico/em lote; Agendamento tem pico sazonal de 20x. Colocar todos em uma única unidade de implantação (ainda que "modular" internamente) significa que qualquer deploy relacionado à Regulação de Leitos  justamente o módulo que precisa evoluir aos poucos para substituir o legado  exige recompilar e reimplantar o sistema inteiro, incluindo Farmácia, PEC e Vigilância. Isso vai contra a resposta que o próprio envelope pede: uma substituição incremental e de baixo risco do legado, com equipe pequena que não pode se dar ao luxo de re-testar o sistema inteiro a cada mudança pontual no módulo de leitos.

**O que faríamos no lugar:** Manter o monólito modular para a maior parte dos módulos (justificável pelo orçamento e equipe de 10 devs), mas isolar o módulo de Regulação de Leitos como um serviço deployável separadamente (mesmo dentro do mesmo ambiente on-premises), permitindo evoluir e substituir a integração com o legado sem redeploy do restante do sistema.

### Objeção 4  Vulnerabilidade crítica no Lock Distribuído (Redlock) para prevenção de overbooking de leitos

**Trecho atacado:** ADR-003, seção "Decisão" ("travamento temporário de leitos utilizando Lock Distribuído via Redis (Redlock)") e "Consequências Negativas" ("o Redlock oferece garantias fortes apenas com múltiplas instâncias Redis independentes; rodando sobre uma única instância, a proteção contra *split-brain* é mais fraca").

**Argumento:** O algoritmo Redlock exige matematicamente um cluster de pelo menos 5 instâncias de Redis totalmente independentes para garantir a exclusão mútua contra falhas de rede e *split-brain*. Como a solução opera em um ambiente *On-Premises* mantido por apenas 2 profissionais de infraestrutura (Envelope C), a implantação prática tenderá a rodar sobre uma única instância ou réplica simples no Docker Swarm. Em caso de partição de rede, degradação de I/O ou reinicialização do nó de Redis, a garantia de exclusão mútua é violada. Isso resultará na dupla alocação real de um leito hospitalar  exatamente o risco mais crítico do projeto que a arquitetura deveria mitigar. Delegar a consistência transacional mais sensível do sistema a uma ferramenta de coordenação externa complexa fere a premissa de simplicidade do Envelope C.

**O que faríamos no lugar:** Implementar a reserva temporária de leitos com garantia de concorrência ACID diretamente no banco de dados relacional (PostgreSQL), utilizando *Pessimistic Lock* (`SELECT ... FOR UPDATE`) ou uma tabela de alocação temporária com *Constraint* e expiração no próprio banco. Isso elimina a dependência do Redis para coordenação transacional crítica e garante consistência estrita sem sobrecarregar a equipe de infraestrutura.

---

### Objeção 5  Perda silenciosa de notificações compulsórias devido ao uso de barramento de eventos puramente em memória

**Trecho atacado:** ADR-001, seção "Decisão" ("comunicação *In-Memory* (via Barramento de Eventos interno/Spring Application Events)") em articulação com a ADR-006 ("Pipes and Filters ... consumindo eventos do mesmo RabbitMQ ... `SurveillanceOutboxHandler`").

**Argumento:** A ADR-001 adota o envio de eventos *In-Memory* para a comunicação entre os módulos do monólito. Se a gravação de um atendimento clínico no módulo de Atendimento depende de um evento interno em memória do Spring para avisar o módulo de Vigilância Epidemiológica a gerar o registro na tabela de Outbox (ADR-006), cria-se uma janela de falha irrecuperável. Se a aplicação sofrer um *crash*, indisponibilidade de memória ou for reiniciada pelo Docker Swarm logo após o commit do atendimento, o evento em memória será volatilizado antes de ser processado. Como consequência, o registro no Outbox nunca será criado e a notificação de doença compulsória jamais será enviada ao e-SUS. Como a falha ocorre antes da escrita na tabela de Outbox, o job de monitoramento de pendências sequer detectará o atraso, causando perda silenciosa de dados e violação direta do prazo legal de 24 horas.

**O que faríamos no lugar:** Escrever o registro de intenção de notificação na tabela do *Transactional Outbox* dentro da própria transação de banco de dados do atendimento clínico (no módulo de Atendimento), em vez de delegar o disparo do Outbox a um evento volátil em memória entre subdomínios. Caso a comunicação modular exija desacoplamento, utilizar escuta transacional de eventos conectada ao commit da transação local (`@TransactionalEventListener`) com fallback de persistência direta.

### Objeção 6  Monólito único concentrando módulos com naturezas distintas

**Trecho atacado:** Diagrama de Contêineres (Nível 2), Redis descrito como “Verifica saldo de cotas e adquire locks”.

**Argumento:** Manter o contador de cotas como fonte de verdade no Redis (além do lock) é arriscado em produções on‑premises com pouca operação: keys podem ser perdidas por reinício sem persistência, evicção quando o cache enche, ou divergências durante failover/replica split‑brain. Isso dificulta a auditoria e a reconciliação automática do estado das quotas, já que desvios tendem a ser detectados muito tarde e muitas vezes exigem intervenção manual. Logo, a dependência do Redis para contadores críticos aumenta a probabilidade de indisponibilidade do serviço.

**O que faríamos no lugar:**

- Usar padrão "create‑if‑not‑exists" com constraint única: modelar uma tabela de alocações com `UNIQUE(leito_id)` e reservar tentando `INSERT`. Se o `INSERT` for bem‑sucedido, a reserva é concedida; se houver violação de chave, o recurso já está ocupado. Para reservas temporárias, combinar com um job que expira registros antigos. Essa abordagem evita locks pesados e é simples de operar On‑Premise.
  
- Se for necessário um caminho rápido (fast‑path) para latência, usar o Redis apenas como cache/fast‑path combinado com escrita de um evento na `Transactional Outbox` para reconciliação; um job periódico reconcilia e corrige divergências.

- Se o time optar por manter Redis como contador primário, exigir persistência (AOF), réplicas/HA, operações atômicas via scripts Lua e instrumentação/alertas (eviction, AOF desativado, latência), além de runbooks e testes de falha obrigatórios.

---

**Observação (não é objeção de arquitetura):** O grupo não entregou o Mapa de Restrições e Decisões (segunda entrega solicitada no enunciado), o que impede avaliar se as justificativas textuais para cada decisão  especialmente para o Envelope C  de fato endereçam a pergunta obrigatória "como vocês substituem o legado aos poucos, com pouca gente e sem nuvem?". As objeções acima se baseiam apenas no que os diagramas comunicam.
