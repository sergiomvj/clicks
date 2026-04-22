# Documentacao de Ajuda por Menu - FBR-CLICK

## Visao Geral

**Rota:** `/spaces`

### Objetivo da tela
Centralizar a entrada para a operacao comercial do FBR-CLICK, redirecionando o usuario para o primeiro canal disponivel do workspace.

### Elementos principais
- resolucao do primeiro space e canal valido
- redirecionamento automatico para a operacao ativa

### Como interpretar os elementos
Se houver estrutura operacional cadastrada, o sistema leva o usuario diretamente para a area comercial mais relevante.

### Uso pratico
Serve como ponto de entrada rapido do sistema, evitando tela vazia antes do trabalho comercial.

### Relacao com outras telas ou modulos
Conecta o usuario ao canal comercial principal do workspace.

### Observacoes de homologacao
Validar se existem spaces e canais cadastrados; caso contrario, o sistema informa ausencia de estrutura.

## Canal Comercial

**Rota:** `/spaces/[spaceId]/channels/[channelId]`

### Objetivo da tela
Operar o deal no contexto do canal comercial, reunindo mensagens, pipeline, tarefas, approvals e visao de agentes.

### Elementos principais
- cabecalho com metricas da operacao
- lista de mensagens
- quadro de pipeline
- board de tarefas
- monitor de agentes
- fila de approvals

### Como interpretar os elementos
A tela mostra o estado vivo do deal e do workspace comercial, incluindo acoes humanas e automatizadas.

### Uso pratico
Usada para acompanhar o lead aquecido, revisar rascunhos, validar tarefas, acompanhar stage e operar approvals.

### Relacao com outras telas ou modulos
Se conecta diretamente com pipeline, tarefas, agentes e handoff do `1FBR-Leads`.

### Observacoes de homologacao
Validar atualizacao por websocket e exibir corretamente tarefas e mensagens originadas por agentes.

## Pipeline

**Rota:** `/spaces/[spaceId]/pipeline`

### Objetivo da tela
Visualizar o funil comercial por stage, com destaque operacional para deals vindos do `1FBR-Leads`.

### Elementos principais
- metricas resumidas do pipeline
- colunas por stage
- cards de deals
- fila de approvals

### Como interpretar os elementos
Cada coluna representa uma etapa comercial. Cards destacados indicam origem aquecida do `1FBR-Leads`.

### Uso pratico
Usada para leitura executiva do funil, priorizacao e deteccao de gargalos de operacao.

### Relacao com outras telas ou modulos
Se conecta com CRM, approvals e feedback para `1FBR-Leads`.

### Observacoes de homologacao
Validar transicoes de stage, destaque visual e atualizacao em tempo real.

## Tarefas

**Rota:** `/spaces/[spaceId]/tasks`

### Objetivo da tela
Concentrar tarefas do workspace, incluindo tarefas humanas e tarefas originadas por agentes.

### Elementos principais
- metricas de tarefas
- cards de tarefa
- origem, prioridade, status e vencimento

### Como interpretar os elementos
Cards marcados como `agent-api` indicam automacao controlada. As metricas resumem pendencias e carga operacional.

### Uso pratico
Usada para acompanhar follow-ups, revisoes e acao comercial diaria.

### Relacao com outras telas ou modulos
Relaciona-se com deals, agentes e canal comercial.

### Observacoes de homologacao
Validar criacao de tarefas por agentes e reflexo no board sem refresh manual.

## Agentes e Governanca

**Rota:** `/spaces/[spaceId]/settings/agents`

### Objetivo da tela
Gerenciar agentes, kill switch, approvals e estado de observacao dos repositorios pelo git watcher.

### Elementos principais
- painel de kill switch
- monitor de agentes
- owners e escopos
- approvals pendentes
- estado do git watcher

### Como interpretar os elementos
Cada agente possui escopo, acoes sensiveis e owners definidos. O watcher mostra o estado observado do repositorio associado.

### Uso pratico
Usada para governanca operacional, homologacao assistida e controle de automacoes.

### Relacao com outras telas ou modulos
Relaciona-se com approvals, JWT de agentes, `agent-api` e operacao comercial do workspace.

### Observacoes de homologacao
Validar approve/reject, kill switch e associacao correta entre agente e watcher.
