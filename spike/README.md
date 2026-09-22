# Spike: prova de arquitetura baseada em células

## ADR provada

ADR #0002 — Utilização de arquitetura baseada em células.

## Objetivo

Este spike tem o objetivo demonstrar que a decisão mais arriscada do projeto funciona: manter a operação local dentro de cada célula quando a rede ou o sistema central ficam indisponíveis.

A simulação mostra que, mesmo com falha de infraestrutura externa, a célula continua processando localmente, registra os eventos como pendentes e, quando a conexão retorna, sincroniza os dados com o sistema legado.

## O que o programa prova

- Cada célula possui seu próprio banco local e operação isolada.
- A falha de uma célula não derruba todas as outras.
- A rede pode cair sem impedir que a operação continue localmente.
- Os eventos acumulados ficam em fila para sincronização posterior.
- A recuperação da infraestrutura permite a reconciliação dos dados sem perder continuidade.

## Como executar

1. Abra o terminal.
2. Acesse a pasta do spike:

   ```bash

   cd spike

   ```

3. Execute:

   ```bash
   python exemplo.py
   ```

4. O programa imprime a sequência da simulação e grava o resultado em `saida-esperada.txt`.

## O que aconteceria se a decisão estivesse errada?

Se a arquitetura não fosse baseada em células, uma falha de rede ou de sistema central poderia travar o processamento local, levando à indisponibilidade operacional, perda de continuidade clínica e atrasos na atualização dos dados. Em um ambiente com conectividade instável, isso tornaria o sistema sensível a interrupções e reduziria a efetividade o atendimento.

## Conclusão

O spike demonstra que, em cenários de conexão instável, a autonomia local é essencial para que o sistema continue funcionando e garantir eventual consistência quando a rede volta.

# Referências
- Código adaptado de: Abreu, Douglas H. S. Estilos Arquiteturais de Software: guia de consulta, Capítulo 13, “Arquitetura celular (cell-based)”, seção 13.4, “Exemplo executável”
