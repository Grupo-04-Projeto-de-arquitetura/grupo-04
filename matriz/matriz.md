# Matriz de estilos arquiteturais

| Estilo Arquitetural | Serve para o meu caso e envelope? | Em qual subdomínio ele entraria, se entrar. | Por quê (em até três frases, citando a seção do livro) | Qual atributo de qualidade melhora e qual piora no meu contexto |
|---|---|---|---|---|
| Monólito em camadas | Não | Nenhum | Trata-se de um modelo de implantação em nó único e com forte acoplamento que não tolera indisponibilidade local nem falhas parciais. Conforme a seção 5.6, o estilo deve ser evitado quando o domínio exige escalabilidade seletiva, isolamento de falhas ou alta disponibilidade sob infraestrutura de rede instável. Como a rede municipal possui 70 UBSs sofrendo com quedas diárias de internet, aplicar esse estilo paralisaria as unidades remotas a cada desconexão. **(Monolito em camadas ) (Cap. 5, Seções 5.1 a 5.6)** | Melhora: Testabilidade (devido ao isolamento de regras técnicas). Piora: Disponibilidade e escalabilidade. |
| Monolito modular | Em partes | Agendamento e cidadão | O estilo consolida fronteiras de módulos bem definidas sob uma única unidade de implantação, reduzindo drasticamente o custo de distribuição e complexidade operacional. Conforme a seção 6.5, é ideal para domínios centrais em ambientes de nuvem com times que precisam de forte coesão e baixo custo de infraestrutura. Contudo, não serve diretamente para as UBSs remotas sem resiliência local a desconexões. **(Monólito modular) (Cap. 6, Seções 6.1 a 6.5)** | Melhora: Modificabilidade (manutenção de fronteiras claras de código). Piora: Disponibilidade local (depende do link central operante). |
| Hexagonal (Ports and Adapters) | Sim | Triagem, atendimento, integração com legado e APIs federais | Isolando o domínio de negócio dos detalhes de infraestrutura e conectores externos por meio de portas e adaptadores, o estilo atende às demandas de alta variabilidade e desacoplamento. Conforme a seção 7.5, é recomendado quando o núcleo da aplicação precisa funcionar de forma independente de bancos de dados, interfaces ou APIs com instabilidade de terceiros. Isso permite trocar e integrar adaptadores do sistema legado de regulação ou dos serviços federais sem alterar a lógica clínica interna.  **(Arquitetura hexagonal / Ports and Adapters (Ports and Adapters)) (Cap. 7, Seções 7.1 a 7.5)** | Melhora: Testabilidade e modificabilidade. Piora: Custo de implementação pelo excesso de código boilerplate e mapeamento de adaptadores. |
| Microkernel | Não | Nenhum | O estilo é voltado para aplicações com um fluxo principal fixo e expansões customizadas dinâmicas por plugins. Conforme a seção 8.6, deve ser evitado quando a aplicação demanda comunicação intensa e de alta frequência entre as extensões ou quando o domínio é altamente distribuído. O sistema municipal requer forte consistência de dados transacionais cruzados e sincronização, e não extensibilidade por plugins de terceiros. **(Microkernel / Núcleo e plugins)  (Cap. 8, Seções 8.1 a 8.6)** | Melhora: Extensibilidade e isolamento de regras locais. Piora: Desempenho (overhead na troca de mensagens entre plugins). |
| Microsserviços | Sim | Agendamento e cidadão; Farmácia e estoque; Prontuário eletrônico | Permite a implantação e a escalabilidade independentes de cada unidade funcional, acomodando times distintos com autonomia de publicação. Conforme a seção 9.5, é indicado para organizações que possuem múltiplos times e necessidades acentuadas de escalabilidade seletiva, como nos picos de campanhas de vacinação (20x). Encaixa-se perfeitamente na capacidade do consórcio BB (40 desenvolvedores, 5 times, nuvem pública). **(Microsserviços) (Cap. 9, Seções 9.1 a 9.5)** | Melhora: Escalabilidade e deploy independente. Piora: Custo operacional, latência e consistência distribuída. |
| SOA / ESB | Em parte | Integração federal e legado | Focado na integração corporativa heterogênea por meio de um barramento intermediário que traduz protocolos e centraliza barramentos de serviços. Conforme a seção 10.5, é indicado quando há necessidade de orquestrar múltiplos sistemas legados e terceiros sem alterar suas arquiteturas internas. Auxilia no isolamento da regulação antiga por até 2 anos, embora adicione complexidade corporativa e risco de ponto único de falha. **(Arquitetura orientada a serviços (SOA))  (Cap. 10, Seções 10.1 a 10.5)** | Melhora: Compatibilidade / Integrabilidade (orquestração corporativa). Piora: Desempenho (latência acumulada pelo barramento). |
| Arquitetura orientada a eventos | Sim | Vigilância epidemiológica; Triagem e atendimento na UPA | Permite o desacoplamento temporal e espacial completo entre produtores e consumidores via corretores de mensagens assíncronos. Conforme a seção 11.5, o estilo é ideal para tolerar indisponibilidades de destinos (sistemas federais/vigilância) e processar cargas assíncronas em disparos de alertas. As UBSs e UPAs registram e publicam os fatos locais que serão enfileirados e consumidos na nuvem assim que a conectividade for restabelecida. **(Arquitetura orientada a eventos (EDA)) (Cap. 11, Seções 11.1 a 11.5)** | Melhora: Disponibilidade (tolerância a falhas temporárias de rede). Piora: Confiabilidade / Consistência (passa a adotar consistência eventual). |

## Análise de Estilos: Considerados vs. Descartados

### 1. Estilos Considerados

#### Microsserviços (Capítulo 9)

O estilo permite a implantação, manutenção e escalabilidade independentes de cada unidade funcional (Seção 9.1). Conforme a Seção 9.5 (Quando Usar), é altamente recomendado para cenários com múltiplos times de desenvolvimento e demandas de escalabilidade seletiva.

Encaixa-se perfeitamente no envelope do consórcio de 40 desenvolvedores divididos em 5 times autônomos. Permite absorver os picos sazonais de até 20x no subdomínio de Agendamento e Vacinação escalando apenas esses serviços na nuvem pública, sem a necessidade de provisionar recursos para os demais módulos.

#### Arquitetura Baseada em Células / Cell-Based (Capítulo 13)

Agrupa serviços, dados e regras em unidades autossuficientes e isoladas (cells) para mitigar o raio de impacto de falhas (Seção 13.1). Conforme a Seção 13.5 (Quando Usar), é a solução ideal quando ambientes locais precisam operar com 100% de autonomia e resiliência em relação ao ponto central.

Resolve a principal restrição física do projeto: as 70 UBSs e UPAs com quedas diárias de internet. Cada unidade de saúde opera como uma "célula local" independente com seu próprio banco de dados temporário, garantindo a continuidade da triagem e prescrição médica mesmo sem conexão, sincronizando com a nuvem assincronamente assim que a rede restabelece.

### 2. Estilos Descartados

#### Monolito em Camadas (Capítulo 5)

O monolito em camadas é uma aplicação centralizada sob uma única unidade de implantação (single deployment unit) que possui forte acoplamento e não tolera falhas parciais (Seção 5.1). Conforme a Seção 5.6 (Quando Evitar), o estilo deve ser expressamente descartado quando o domínio exige isolamento de falhas, escalabilidade seletiva ou resiliência sob rede instável.

Como as 70 UBSs sofrem com instabilidade diária de conexão, implantar um monolito centralizado paralisaria o atendimento das unidades de saúde a cada queda de internet. Além disso, a arquitetura impediria a escalabilidade seletiva necessária para as campanhas de vacinação.

#### Microkernel / Núcleo e Plugins (Capítulo 8)

O estilo baseia-se em um núcleo estático com fluxo transacional fixo estendido por rotinas customizadas via plugins (Seção 8.1). Conforme a Seção 8.6 (Quando Evitar), ele deve ser descartado quando a aplicação exige comunicação frequente entre as extensões ou quando o domínio é altamente distribuído por natureza.

O sistema municipal exige forte consistência de dados transacionais cruzados em tempo real (ex.: verificação de estoque da farmácia e leitos durante o atendimento clínico). O overhead de comunicação contínua entre plugins inviabilizaria a operação distribuída e de alta resiliência exigida entre os nós locais e a nuvem.
