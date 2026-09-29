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
