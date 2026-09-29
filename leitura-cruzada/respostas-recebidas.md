Objeção 1 — Microsserviços não se encaixam perfeitamente no envelope

Decisão/trecho atacado:
Matriz de estilos arquiteturais / Microsserviços, Cap. 9, Seção 9.5: “Encaixa-se perfeitamente na capacidade do consórcio BB (40 desenvolvedores, 5 times, nuvem pública).”

Argumento:
A quantidade de desenvolvedores e times justifica a possibilidade de adoção de microsserviços, mas não significa que o estilo se encaixe “perfeitamente” no envelope. O sistema ainda precisa operar em 70 UBSs/UPAs com conectividade instável, o que aumenta significativamente a complexidade de descoberta de serviços, observabilidade, sincronização, implantação e tratamento de falhas distribuídas. O custo operacional de dezenas de serviços distribuídos pode superar o ganho de escalabilidade seletiva, principalmente nos subdomínios que não apresentam o mesmo pico de demanda.

O que nosso grupo faria no lugar:
Usaríamos microsserviços apenas nos subdomínios que realmente apresentam necessidade de escalabilidade e autonomia de implantação, mantendo os demais componentes mais consolidados. Dessa forma, reduziríamos a quantidade de comunicação distribuída sem perder a capacidade de escalar especificamente Agendamento e Vacinação.

## Resposta à Objeção 1 — Adequação de Microsserviços ao Envelope
**Posição:** Discordamos.

O argumento da objeção é procedente ao criticar o termo "encaixa-se perfeitamente", pois a simples disponibilidade de 40 desenvolvedores, 5 times e nuvem pública não elimina os custos operacionais de uma arquitetura amplamente distribuída (como *tracing*, *service discovery* e tratamento de falhas parciais) em um cenário com 70 unidades de saúde sob conectividade instável. A estrutura de times viabiliza a governança, mas não torna o estilo isento de complexidade na ponta. No entanto, a objeção assume erroneamente que a decisão previa a pulverização do sistema em dezenas de pequenos serviços homogêneos para todos os subdomínios, quando a premissa de ter 5 times visa ao alinhamento por limites de contextos do negócio (*Conway's Law*). Aceitamos que a redação original foi imprecisa ao transmitir uma visão simplista do estilo, devendo explicitar o caráter seletivo e pragmático da decomposição.

---

Objeção 2 — Arquitetura celular não garante, por si só, consistência para recursos compartilhados

Decisão/trecho atacado:
Matriz de estilos arquiteturais / Arquitetura celular, Cap. 13, Seção 13.5: “Permite que a UPA funcione como uma ‘célula local’ com banco próprio durante a queda da internet e sincronize assincronamente ao reconectar.”

Argumento:
A autonomia local resolve a disponibilidade, mas cria um problema justamente no caso mais crítico do envelope: duas unidades podem tentar modificar simultaneamente o mesmo recurso compartilhado, como um leito. Bancos independentes por célula não conseguem, isoladamente, garantir exclusão mútua entre 70 unidades desconectadas. Assim, a decisão melhora a disponibilidade, mas transfere o problema para a reconciliação de conflitos e pode comprometer a consistência exigida pela regulação.

O que nosso grupo faria no lugar:
Manteríamos a autonomia das células para os dados locais, mas centralizaríamos ou coordenaríamos explicitamente os recursos realmente globais, como leitos. Para esses recursos, usaríamos uma autoridade transacional única ou um mecanismo de reserva distribuída com identificador de versão, expiração e reconciliação de conflitos.

## Resposta à Objeção 2 — Arquitetura celular e consistência de recursos compartilhados
**Posição**: Discordamos.

O argumento da objeção está correto ao apontar que bancos de dados independentes e desconectados não conseguem, por si só, garantir exclusão mútua sobre recursos globais. No entanto, ele parte de uma premissa incorreta sobre a nossa modelagem de domínios: a arquitetura celular (Cell-Based + EDA) foi adotada exclusivamente para o subdomínio de Triagem e Atendimento da UPA/UBS, que prioriza alta disponibilidade (modelo AP no Teorema CAP) para garantir que o médico continue registrando atendimentos mesmo sem internet. O subdomínio de Regulação de Leitos, ao contrário do que a objeção assumiu, é mantido deliberadamente como um serviço centralizado único, operando fora da arquitetura celular sob uma única autoridade transacional. Não existem "bancos locais de leitos" por unidade. Aceitamos, contudo, que a redação original foi omissa ao não descrever explicitamente como o sistema se comporta quando a UPA perde a conectividade com esse serviço central.

O que vamos mudar:
Ajustar a resposta à pergunta obrigatória #2 para detalhar a separação estrita dos subdomínios e a política de degradação graciosa (*fail-safe*) durante instabilidade de rede:

* **Segregação explícita de subdomínios:** deixar claro que a autonomia celular e a sincronização assíncrona pertencem apenas ao fluxo de Atendimento e Triagem Local. A Regulação de Leitos permanece como uma autoridade transacional única e centralizada.
* **Comportamento *fail-safe* para reservas off-line:** esclarecer que a reserva de leitos **nunca é confirmada localmente** por uma unidade desconectada. Se a UPA perder comunicação com o Serviço Central de Leitos, a operação de reserva é imediatamente bloqueada/negada (ou retida em estado *Pendente de Conectividade*). Trata-se de uma escolha consciente de design: prefere-se falhar a reserva síncrona a arriscar uma dupla alocação de leito por inconsistência.
* **Papel da integração com o legado:** explicitar que o sistema legado de leitos (acessado via Adaptador/ACL) atua exclusivamente para sincronização de estado, e não como autoridade concorrente de decisão.

Substituir qualquer menção genérica a "sincronização posterior de leitos" por uma descrição precisa da abordagem híbrida: modelo celular e de consistência eventual para o Atendimento Clinical local, combinado com modelo centralizado de consistência estrita (*Fail-Safe*) para a Regulação de Leitos.

---

Objeção 3 — A resposta sobre reserva de leitos apresenta uma garantia maior do que a arquitetura demonstrada

Decisão/trecho atacado:
Perguntas e respostas / “Como duas unidades disputando o mesmo leito nunca conseguem reservá-lo ao mesmo tempo, com o sistema legado ainda no circuito?”

Argumento:
A resposta afirma que “duas reservas concorrentes não conseguem ser aceitas ao mesmo tempo”, mas o restante da arquitetura descreve bancos locais independentes e sincronização posterior. Um controle transacional local impede conflitos dentro de uma célula, mas não necessariamente entre células que estão desconectadas. O envelope possui exatamente a condição que torna o problema difícil: várias unidades podem continuar operando enquanto a rede está indisponível.

O que nosso grupo faria no lugar:
Não afirmaríamos “nunca” sem especificar o mecanismo de coordenação. Definiríamos explicitamente que a reserva de leitos é um recurso compartilhado, com uma autoridade de decisão central ou um protocolo de concessão de reserva, deixando claro o comportamento quando uma célula perde conectividade.

## Resposta à Objeção 3 — Reserva de leitos e garantia "nunca"

**Posição:** parcialmente aceita — rebatemos o argumento central, mas corrigimos a redação da resposta.

**Rebatemos** o ponto de que a arquitetura de células com sincronização posterior se aplica ao subdomínio de Regulação de Leitos. Essa arquitetura (Cell-Based + EDA) foi desenhada especificamente para o subdomínio de Triagem e Atendimento na UPA/UBS, que tolera consistência eventual porque o requisito ali é "não perder nem duplicar" o atendimento local — não "nunca conflitar entre unidades". A Regulação de Leitos, ao contrário, foi deliberadamente mantida como um serviço centralizado único (o Serviço de Leitos e Regulação, na nuvem, com CQRS e lock otimista no modelo de comando), justamente porque o requisito ali é consistência forte e disputa em tempo real. Não existem "bancos locais independentes" de leito por unidade — cada UBS/UPA/hospital consulta e reserva sempre contra essa mesma autoridade central. Portanto, a garantia "nunca duas reservas simultâneas" é sustentada pela decisão de manter esse subdomínio fora do modelo de células, e não uma promessa contraditória com ele.

**Aceitamos**, porém, que a resposta original foi imprecisa ao não descrever explicitamente o que acontece quando uma unidade perde conectividade com esse serviço central. Vamos corrigir o texto para deixar claro que:

- A reserva de leito nunca é aceita localmente por uma unidade desconectada — se a unidade não alcança o Serviço de Leitos e Regulação, a operação de reserva falha (ou fica pendente/bloqueada) em vez de ser confirmada offline.
- Isso é uma escolha consciente de fail-safe (preferir negar a reserva a arriscar duplicidade), diferente do modelo de Triagem, que prioriza disponibilidade sobre consistência imediata.
- O papel do sistema legado nesse fluxo (via Adaptador/ACL) é apenas de sincronização de estado, não de autoridade concorrente de decisão — a autoridade de reserva permanece única.

**O que muda no texto:** vamos reescrever a resposta à pergunta obrigatória #2, trocando "nunca conseguem reservá-lo ao mesmo tempo" por uma descrição explícita do mecanismo (single writer + lock otimista) e do comportamento degradado em caso de perda de conectividade com a autoridade central.

---

Objeção 4 — Event Sourcing não garante sozinho uma auditoria completa

Decisão/trecho atacado:
Matriz de estilos arquiteturais / Event Sourcing, Cap. 15, Seção 15.5: “Garante a auditoria exata de quem acessou, modificou ou visualizou cada dado sensível do prontuário.”

Argumento:
Event Sourcing registra a evolução do estado por eventos de domínio, mas isso não significa automaticamente que toda visualização ou acesso ao prontuário será registrado. Uma consulta de leitura pode não alterar o estado do domínio e, portanto, precisa de eventos de auditoria próprios. Além disso, armazenar todo esse histórico por 20 anos gera um custo considerável de armazenamento, retenção, projeções e gerenciamento de dados sensíveis.

O que nosso grupo faria no lugar:
Separaríamos claramente os eventos de domínio do log de auditoria. Registraríamos explicitamente acessos, alterações, consultas e ações autorizadas, aplicando políticas específicas de retenção e proteção aos eventos de auditoria e utilizando Event Sourcing somente onde o histórico completo de mudanças realmente trouxesse valor.

## Resposta à Objeção 4 — Event Sourcing e Log de Auditoria
**Posição:** aceita.

O argumento da objeção está tecnicamente correto. O padrão *Event Sourcing* tem como propósito a persistência e reconstrução do estado do domínio a partir de eventos de mutação (*state-changing events*, como `PrescreverMedicamento` ou `AtualizarDiagnostico`). Ele não captura, por natureza, operações puras de leitura e consulta (`VisualizarProntuario`), as quais não alteram o estado do sistema, mas são exigidas pela LGPD e pela regulação de saúde. Tratar visualizações de dados como eventos de domínio no *Event Store* é um anti-pattern que infla desnecessariamente a fila de eventos e compromete o desempenho de reconstrução de estado. Além disso, estender o *Event Sourcing* indistintamente para fins de conformidade legal de 20 anos gera um custo injustificado de armazenamento, gerenciamento de *snapshots* e evolução de *schema* ao longo das décadas.

O que vamos mudar:
Corrigir a imprecisão técnica na matriz de estilos arquiteturais (Capítulo 15, Seção 15.5), separando explicitamente a persistência do domínio da camada de auditoria de acessos:

* **Desacoplamento entre Event Sourcing e Audit Log:** restringir o uso de *Event Sourcing* estritamente à gestão de estado e histórico de mutações clínicas do Prontuário Eletrônico, removendo a declaração de que o padrão registra "visualizações".
* **Camada dedicada de Log de Acesso (Read/Query Audit):** especificar que visualizações e consultas a dados sensíveis serão capturadas por um componente de auditoria dedicado (*AuditLogger* via *Interceptors* / *Middleware* da API), gravando registros imutáveis de acesso de leitura em uma tabela *Append-Only* separada, otimizada para consulta de auditoria e conformidade com a LGPD.
* **Racionalização do escopo do Event Sourcing:** delimitar o *Event Sourcing* apenas aos contextos onde a reconstrução temporal e a imutabilidade do histórico clínico agregado agregam valor real ao negócio, aplicando políticas de retenção e expurgo diferenciadas para os logs de auditoria de leitura.

---

Objeção 5 — A guarda de 20 anos e a LGPD não são resolvidas apenas pela arquitetura

Decisão/trecho atacado:
Perguntas e respostas / “Como o prontuário garante que se saiba quem acessou cada registro, e como convive a guarda de 20 anos com os direitos do paciente sob a LGPD?”

Argumento:
A arquitetura pode fornecer rastreabilidade e mecanismos de controle, mas não determina sozinha a base legal, o prazo de retenção aplicável a cada categoria de dado ou a forma como os direitos do titular serão operacionalizados. A afirmação de que a retenção de 20 anos “aplica-se ao histórico de auditoria e aos eventos de domínio relevantes” também precisa ser fundamentada juridicamente e não apenas arquiteturalmente. Nesse envelope, segurança, retenção e privacidade representam requisitos independentes que precisam de políticas próprias.

O que nosso grupo faria no lugar:
Separaríamos a decisão arquitetural da decisão de governança de dados. A arquitetura implementaria autenticação, autorização, trilha de auditoria, criptografia e controles de retenção configuráveis, enquanto os prazos e hipóteses de tratamento seriam definidos pelas regras legais e institucionais aplicáveis.

## Resposta à Objeção 5 — Guarda de 20 anos e LGPD

**Posição:** aceita.

O argumento está correto: a arquitetura pode implementar rastreabilidade, controle de acesso e retenção configurável, mas não pode, por si só, definir a base legal do tratamento, o prazo correto por categoria de dado, nem operacionalizar os direitos do titular (acesso, correção, portabilidade, eventual anonimização). Isso são decisões de governança e compliance, não decisões arquiteturais, e misturar as duas categorias na resposta original passou a falsa impressão de que a escolha de Event Sourcing "resolve" a LGPD sozinha.

**O que vamos mudar:**

Separar claramente, na resposta à pergunta obrigatória #3, o que é capacidade técnica fornecida pela arquitetura do que é decisão de política/jurídica:

- **Arquitetura fornece:** autenticação e autorização (quem pode acessar o quê), trilha de auditoria imutável de todo acesso e alteração (via Event Sourcing + AuditLogger), criptografia de dados sensíveis em repouso e em trânsito, e retenção configurável por categoria de evento.
- **Fora do escopo da arquitetura**, a ser definido por política institucional/jurídica: a base legal do tratamento (ex.: cumprimento de obrigação legal x consentimento), o prazo de retenção aplicável a cada categoria específica de dado clínico, e o processo formal de atendimento às solicitações do titular sob a LGPD (que pode, inclusive, ser parcialmente restringido pela obrigação legal de guarda de 20 anos — essa é uma decisão de governança, não uma decisão técnica).

Retirar a frase "aplica-se ao histórico de auditoria e aos eventos de domínio relevantes" como se fosse uma conclusão arquitetural fechada, e substituí-la por algo como: "os prazos de retenção por categoria de dado são parametrizáveis na arquitetura, mas definidos pela área jurídica/institucional responsável pela política de dados da secretaria."

---

Objeção 6 — EDA melhora a disponibilidade, mas pode entrar em conflito com requisitos de consistência

Decisão/trecho atacado:
Matriz de estilos arquiteturais / Arquitetura orientada a eventos, Cap. 11, Seção 11.5: “As UBSs e UPAs registram e publicam os fatos locais que serão enfileirados e consumidos na nuvem assim que a conectividade for restabelecida.”

Argumento:
O mecanismo é adequado para notificações e alertas que podem ser processados de forma assíncrona, mas o envelope também contém operações cujo resultado pode depender do estado atual de outro recurso. Se o mesmo padrão assíncrono for aplicado indiscriminadamente, haverá atrasos entre o estado local e o central. Isso é especialmente problemático para informações operacionais que precisam refletir uma situação atual, e não apenas eventual convergência.

O que nosso grupo faria no lugar:
Usaríamos EDA principalmente para notificações, vigilância e integração assíncrona. Para operações críticas e transacionais, definiríamos explicitamente quais dados precisam de consistência forte e quais podem aceitar consistência eventual.

## Resposta à Objeção 6 — Arquitetura Orientada a Eventos (EDA) e modelos de consistência
**Posição:** parcialmente aceita.

O argumento da objeção é correto ao alertar sobre os riscos da aplicação indiscriminada do modelo de consistência eventual via EDA para operações que dependem de estado validado em tempo real. No entanto, a objeção parte da premissa incorreta de que a Arquitetura Orientada a Eventos foi proposta de forma homogênea e irrestrita para todas as transações do sistema. A arquitetura adota um modelo híbrido: o barramento de eventos assíncronos (*Domain Events*) é utilizado estritamente para fluxos que toleram diferimento temporal (como a persistência de atendimentos clínicos já concluídos na UPA, notificações de vigilância epidemiológica, telemetria e auditoria), enquanto transações sobre recursos globais concorrentes utilizam chamadas de comandos síncronos com garantia de consistência forte. Aceitamos, contudo, que a redação original foi genérica e deu a falsa impressão de que *qualquer* operação local dependia de enfileiramento assíncrono para validação de estado.

O que vamos mudar:
Refinar a seção sobre a Arquitetura Orientada a Eventos (Capítulo 11, Seção 11.5) para explicitar a fronteira e o contrato de consistência de cada tipo de operação:

* **Classificação explícita dos fluxos via EDA:** delimitar que a publicação e enfileiramento de fatos locais abrangem apenas registros imutáveis e eventos do histórico clínico/epidemiológico — cenários em que o fato médico já ocorreu na ponta e a disponibilidade da UPA/UBS deve ser preservada.
* **Isolamento de operações transacionais críticas:** deixar claro que operações que exigem consulta ou alteração de estado concorrente em tempo real (como checagem de disponibilidade de leitos e vagas globais) não utilizam o pipeline assíncrono de eventos para tomada de decisão, exigindo requisições síncronas diretas contra o serviço central (com tratamento de bloqueio em caso de queda de link).
* **Ajuste de redação na matriz:** substituir a declaração genérica por uma especificação precisa: "As UBSs e UPAs registram e publicam assincronamente os *fatos clínicos imutáveis e eventos de auditoria* para consumo e consolidação na nuvem via EDA, enquanto transações sobre recursos compartilhados mantêm contratos síncronos de consistência forte."
