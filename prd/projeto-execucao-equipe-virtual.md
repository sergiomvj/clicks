# Projeto de Execucao para Equipe de Agentes Virtuais

Data de referencia: 2026-04-22
Projeto: FBR-CLICK
Base de planejamento: `prd/plano-batches-finalizacao-algoritmico.md`, `prd/tasklist-alinhamento-conceito-original.md`, `prd/status-alinhamento-conceito.md`

## Objetivo do documento

Transformar a finalizacao do FBR-CLICK em um sistema de execucao delegavel para uma equipe de agentes virtuais, de forma que modelos de baixo custo consigam executar com qualidade alta porque:

- cada tarefa tem objetivo unico e claro
- cada tarefa tem escopo pequeno e verificavel
- cada tarefa tem entregaveis obrigatorios
- cada tarefa diz exatamente como documentar o trabalho
- cada papel da equipe sabe o que pode pegar e o que nao pode pegar

## Principios para usar LLMs de baixo custo sem perder qualidade

- nunca delegar uma tarefa com objetivo ambiguo
- nunca delegar uma tarefa com escopo de escrita indefinido
- cada tarefa deve ter no maximo um objetivo principal
- cada tarefa deve produzir artefato tecnico e artefato de rastreabilidade
- toda tarefa deve dizer quais arquivos pode tocar
- toda tarefa deve dizer como validar
- toda tarefa deve dizer como documentar
- tarefas de Junior devem ser menores que tarefas de Senior
- tarefas de integracao, arquitetura e seguranca ficam com Senior ou Revisor
- nenhuma tarefa e considerada pronta sem nota de handoff

## Estrutura da equipe

### 1. Coordenacao Geral
Responsabilidade:
- quebrar batches em tasks
- ordenar prioridades
- destravar dependencias
- decidir sequencia de execucao
- consolidar status diario
- validar se a task foi atribuida para o papel certo

Nao deve fazer:
- implementar codigo grande diretamente quando houver Dev disponivel
- revisar o proprio trabalho como aceite final

### 2. Revisor
Responsabilidade:
- revisar codigo, risco, regressao e docs
- aprovar ou rejeitar entregas
- exigir evidencias e testes
- garantir coerencia entre implementacao e conceito
- validar se a documentacao foi atualizada

Nao deve fazer:
- virar implementador principal de todas as tasks
- aprovar task sem criterio de pronto visivel

### 3. Dev Senior A
Foco:
- backend
- banco
- seguranca
- RLS
- auth
- integracoes
- stack LLM

### 4. Dev Senior B
Foco:
- frontend
- UX final
- realtime
- painel de agentes
- monitoramento visual
- experiencia operacional

### 5. Dev Junior 1
Foco:
- migrations pequenas
- scripts locais
- seeds
- ajustes controlados de schema

### 6. Dev Junior 2
Foco:
- endpoints pequenos
- validacoes simples
- testes negativos
- contratos e payloads

### 7. Dev Junior 3
Foco:
- componentes de UI
- estilos
- copy operacional
- refinamentos de telas

### 8. Dev Junior 4
Foco:
- documentacao
- checklists
- evidencias
- runbook
- scripts de validacao

## Regra de atribuicao por papel

- Coordenacao Geral pega tasks de sequenciamento, desbloqueio e consolidacao
- Revisor pega tasks de analise critica, aceite, regressao e coerencia final
- Senior A pega tasks de arquitetura, seguranca, banco, auth, integracoes e LLM
- Senior B pega tasks de UX, painel, navegacao, monitoracao visual e handoff operacional de UI
- Juniors pegam tasks limitadas, com escopo pequeno e apoio de um Senior dono da frente

## Protocolo de execucao por task

Toda task deve seguir este algoritmo:

1. ler objetivo da task
2. confirmar arquivos permitidos
3. executar apenas o escopo definido
4. validar localmente o que for possivel
5. registrar o que foi alterado
6. atualizar documentacao definida na propria task
7. escrever handoff em 5 linhas: contexto, mudanca, validacao, risco, proximo passo
8. enviar para revisao

## Formato obrigatorio de task

Use sempre este formato:

```text
Task: <ID + nome>
Objetivo: <o elemento a ser construido ou ajustado>
Escopo de escrita: <arquivos ou modulo>
Entregaveis: <artefatos obrigatorios>
Validacao: <como provar que funcionou>
Como documentar: <arquivo que precisa ser atualizado>
Owner primario: <papel>
Apoio: <outro papel se existir>
Revisao final: <Revisor ou Senior>
```

## Regras de qualidade por task

- task sem criterio de validacao nao pode ser delegada
- task sem arquivo de documentacao definido nao pode ser encerrada
- task que tocar autenticacao, approval ou banco exige revisao do Revisor
- task que tocar UX critica exige revisao do Senior B
- task que tocar integracao externa exige revisao do Senior A
- task que tocar go-live exige revisao do Revisor e aceite da Coordenacao Geral

## Projeto de execucao por batches e tasks

## Batch 0 - Preparacao de Fechamento

Task: B0-T01 Baseline de finalizacao
Objetivo: congelar o baseline do projeto e consolidar a lista unica de pendencias reais.
Escopo de escrita: `prd/status-alinhamento-conceito.md`, `prd/plano-batches-finalizacao-algoritmico.md`
Entregaveis: status atualizado, backlog unico, bloqueios externos listados.
Validacao: documentos refletem o estado atual do repositorio.
Como documentar: atualizar `prd/status-alinhamento-conceito.md`.
Owner primario: Coordenacao Geral
Apoio: Dev Junior 4
Revisao final: Revisor

Task: B0-T02 Matriz de responsaveis externos
Objetivo: registrar quem responde por `1FBR-Leads`, `1FBR-Dev`, `1FBR-Suporte`, VPS, DNS, SSL e secrets.
Escopo de escrita: `prd/status-alinhamento-conceito.md`
Entregaveis: tabela de responsaveis e dependencias externas.
Validacao: nenhum bloqueio externo fica sem dono.
Como documentar: adicionar secao de owners externos.
Owner primario: Coordenacao Geral
Apoio: Dev Junior 4
Revisao final: Revisor

## Batch 1 - Banco e modelo conceitual

Task: B1-T01 Mapa final de modelagem
Objetivo: fechar a decisao entre modelo conceitual e modelo implementado.
Escopo de escrita: `prd/matriz-alinhamento-conceito.md`, docs tecnicas de schema.
Entregaveis: mapa definitivo de equivalencias e divergencias aceitas.
Validacao: cada tabela critica do conceito tem destino claro.
Como documentar: atualizar `prd/matriz-alinhamento-conceito.md`.
Owner primario: Dev Senior A
Apoio: Dev Junior 1
Revisao final: Revisor

Task: B1-T02 Consolidacao de migrations estruturais
Objetivo: garantir que migrations de alinhamento sejam consistentes e reaplicaveis.
Escopo de escrita: `db/migrations/003_concept_alignment.sql`, `db/migrations/004_operational_alignment.sql`
Entregaveis: migrations revisadas, consistentes e comentadas.
Validacao: banco sobe limpo do zero no ambiente local ou controlado.
Como documentar: registrar evidencias em `prd/status-alinhamento-conceito.md`.
Owner primario: Dev Junior 1
Apoio: Dev Senior A
Revisao final: Revisor

Task: B1-T03 Normalizacao de canais e prioridades
Objetivo: fechar semantica de `channels` e `tasks` conforme o conceito.
Escopo de escrita: schema, backend e UI relacionada.
Entregaveis: tipos de canal corretos e prioridade `p0` a `p3` consistentes.
Validacao: API e frontend exibem os valores finais sem alias quebrado.
Como documentar: atualizar `prd/status-alinhamento-conceito.md`.
Owner primario: Dev Junior 1
Apoio: Dev Senior A e Dev Senior B
Revisao final: Revisor

## Batch 2 - Seguranca profunda

Task: B2-T01 Estrategia de RLS
Objetivo: definir a estrategia segura de contexto por workspace no banco sem quebrar `asyncpg`.
Escopo de escrita: doc tecnico e, se aprovado, base de implementacao no backend.
Entregaveis: documento de estrategia, risco, tradeoff e abordagem escolhida.
Validacao: existe estrategia clara antes de escrever policies reais.
Como documentar: criar ou atualizar documento tecnico em `prd/`.
Owner primario: Dev Senior A
Apoio: Revisor
Revisao final: Revisor

Task: B2-T02 Implementacao de RLS real
Objetivo: aplicar `ENABLE ROW LEVEL SECURITY` e policies reais por `workspace_id`.
Escopo de escrita: migrations, backend de acesso ao banco, testes de isolamento.
Entregaveis: migrations de RLS, codigo de contexto, validacoes de isolamento.
Validacao: tenant A nao enxerga tenant B em nenhum caminho coberto.
Como documentar: atualizar `prd/status-alinhamento-conceito.md` e runbook.
Owner primario: Dev Senior A
Apoio: Dev Junior 2
Revisao final: Revisor

Task: B2-T03 Hardening de auth humana
Objetivo: confirmar cookie, sessao e headers no contrato final.
Escopo de escrita: frontend auth, backend auth, middleware.
Entregaveis: sessao humana endurecida e validada.
Validacao: sem dependencia insegura de storage no navegador.
Como documentar: atualizar docs de auth e runbook.
Owner primario: Dev Senior A
Apoio: Dev Junior 2
Revisao final: Revisor

Task: B2-T04 Escopo e approval de agentes
Objetivo: garantir que a autorizacao do agente cruza token, banco e configuracao versionada.
Escopo de escrita: `app/agents`, `app/api`, docs de agentes.
Entregaveis: enforcement de escopo, approval e logs.
Validacao: payload invalido ou fora do escopo deve falhar de forma rastreavel.
Como documentar: atualizar `prd/status-alinhamento-conceito.md`.
Owner primario: Dev Senior A
Apoio: Dev Junior 2
Revisao final: Revisor

Task: B2-T05 Kill switch e testes negativos
Objetivo: medir SLA e ampliar testes de webhook, prompt injection e rate limit.
Escopo de escrita: scripts, testes, docs de seguranca.
Entregaveis: evidencias de tempo de corte e cenarios negativos.
Validacao: kill switch com tempo registrado e testes negativos documentados.
Como documentar: anexar evidencias no runbook e status.
Owner primario: Dev Junior 2
Apoio: Dev Senior A
Revisao final: Revisor

## Batch 3 - UX final

Task: B3-T01 Diferenciacao humano vs agente
Objetivo: deixar autoria, avatar, badge e estado imediatamente legiveis.
Escopo de escrita: componentes de mensagens e cards relacionados.
Entregaveis: UI diferenciada para humano e agente.
Validacao: leitura visual sem ambiguidade em canal e painel.
Como documentar: atualizar checklist visual em `prd/`.
Owner primario: Dev Junior 3
Apoio: Dev Senior B
Revisao final: Revisor

Task: B3-T02 Sidebar e navegacao semantica
Objetivo: refletir o FBR-CLICK como hub central por tipo de canal e funcao operacional.
Escopo de escrita: `frontend/components/layout/Sidebar.tsx` e estilos relacionados.
Entregaveis: navegacao alinhada ao conceito.
Validacao: canais agrupados e linguagem consistente com a operacao.
Como documentar: atualizar `prd/status-alinhamento-conceito.md`.
Owner primario: Dev Junior 3
Apoio: Dev Senior B
Revisao final: Revisor

Task: B3-T03 Painel operacional final de agentes
Objetivo: consolidar heartbeat, pausado, approvals, watchers e estado visual final.
Escopo de escrita: tela de agentes, monitor e controles.
Entregaveis: painel final de agentes.
Validacao: operacao de agentes e legivel sem depender de logs brutos.
Como documentar: capturas e nota de aceite visual.
Owner primario: Dev Senior B
Apoio: Dev Junior 3
Revisao final: Revisor

## Batch 4 - Operacao real dos 6 agentes

Task: B4-T01 Ownership final dos 6 agentes
Objetivo: fechar owner, escopo e politica de approval por agente.
Escopo de escrita: docs de agentes e configuracao relacionada.
Entregaveis: matriz final por agente.
Validacao: nenhum agente fica sem owner e sem politica de approval.
Como documentar: atualizar docs dos agentes e status.
Owner primario: Coordenacao Geral
Apoio: Dev Senior A
Revisao final: Revisor

Task: B4-T02 Heartbeat e registro operacional
Objetivo: garantir operacao visivel e rastreavel dos 6 agentes.
Escopo de escrita: `app/agents`, scripts e docs.
Entregaveis: heartbeat funcional para todos os agentes.
Validacao: os 6 agentes aparecem com ultimo sinal registrado.
Como documentar: registrar evidencia em `prd/status-alinhamento-conceito.md`.
Owner primario: Dev Senior A
Apoio: Dev Junior 2
Revisao final: Revisor

Task: B4-T03 Triggers reais por agente
Objetivo: implementar pelo menos um trigger automatico coerente para cada agente.
Escopo de escrita: backend, scripts de execucao, docs dos agentes.
Entregaveis: 6 fluxos reais controlados.
Validacao: cada agente executa um trigger auditavel.
Como documentar: atualizar docs de cada agente e status geral.
Owner primario: Dev Senior B
Apoio: Dev Junior 2 e Dev Junior 3
Revisao final: Revisor

## Batch 5 - Stack LLM

Task: B5-T01 Matriz de uso por camada
Objetivo: definir qual camada responde a qual tipo de carga.
Escopo de escrita: docs e `app/core/llm.py`.
Entregaveis: matriz de decisao e payload de health coerente.
Validacao: modelo ativo e fallback ficam explicitos.
Como documentar: registrar em doc de stack LLM.
Owner primario: Dev Senior A
Apoio: Dev Junior 4
Revisao final: Revisor

Task: B5-T02 Publicacao de saude em Redis
Objetivo: refletir a saude das 3 camadas em Redis e no `/health`.
Escopo de escrita: backend e scripts de apoio.
Entregaveis: estado por camada e health enriquecido.
Validacao: `/health` e Redis refletem o estado esperado.
Como documentar: atualizar runbook e status.
Owner primario: Dev Junior 2
Apoio: Dev Senior A
Revisao final: Revisor

Task: B5-T03 Observabilidade e failover
Objetivo: registrar fallback, falha, latencia e indisponibilidade por camada.
Escopo de escrita: backend, logs e docs.
Entregaveis: rastreabilidade da cascata.
Validacao: existe evidencia de failover controlado.
Como documentar: atualizar runbook e plano de batches.
Owner primario: Dev Senior A
Apoio: Dev Junior 4
Revisao final: Revisor

## Batch 6 - Integracoes reais

Task: B6-T01 Pack de homologacao de integracoes
Objetivo: preparar a execucao real com `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte`.
Escopo de escrita: scripts, contratos, checklist e docs.
Entregaveis: pacote de homologacao pronto para uso externo.
Validacao: todos os passos para entrada e callback estao descritos.
Como documentar: atualizar `prd/status-alinhamento-conceito.md` e contratos.
Owner primario: Dev Junior 4
Apoio: Dev Senior A
Revisao final: Revisor

Task: B6-T02 Validacao real de payloads e callbacks
Objetivo: executar testes com endpoints e secrets finais.
Escopo de escrita: configuracao e docs de evidencias.
Entregaveis: evidencias por sistema externo.
Validacao: entrada e saida comprovadas para os 3 sistemas.
Como documentar: registrar evidencias no status e runbook.
Owner primario: Dev Senior A
Apoio: Coordenacao Geral
Revisao final: Revisor

## Batch 7 - Producao, observabilidade e restore

Task: B7-T01 Pack de producao
Objetivo: consolidar deploy, dashboards, smoke e restore em uma trilha unica.
Escopo de escrita: docs e scripts operacionais.
Entregaveis: pacote de producao pronto para execucao na VPS.
Validacao: go-live checklist cobre tudo o que a operacao precisa.
Como documentar: atualizar `docs-go-live-checklist.md` e runbook.
Owner primario: Dev Junior 4
Apoio: Dev Senior A
Revisao final: Revisor

Task: B7-T02 Execucao em ambiente alvo
Objetivo: subir stack real, validar monitoracao, backup e restore.
Escopo de escrita: ambiente real, logs e docs de evidencia.
Entregaveis: producao validada tecnicamente.
Validacao: smoke, dashboard, backup e restore completos.
Como documentar: atualizar runbook com horario, evidencias e riscos residuais.
Owner primario: Dev Senior A
Apoio: Coordenacao Geral
Revisao final: Revisor

## Batch 8 - Homologacao controlada final

Task: B8-T01 Roteiro de homologacao humana
Objetivo: transformar a homologacao final em execucao procedimental simples.
Escopo de escrita: checklist, roteiro e formulario de aceite.
Entregaveis: kit de homologacao controlada.
Validacao: uma pessoa humana consegue seguir o roteiro sem depender de memoria tribal.
Como documentar: atualizar docs de homologacao.
Owner primario: Dev Junior 4
Apoio: Coordenacao Geral
Revisao final: Revisor

Task: B8-T02 Janela controlada ponta a ponta
Objetivo: executar lead, approval, callback e triggers em sequencia real.
Escopo de escrita: logs, evidencias e notas de aceite.
Entregaveis: homologacao completa registrada.
Validacao: janela sem defeito P0 ou P1.
Como documentar: registrar em `prd/status-alinhamento-conceito.md` e runbook.
Owner primario: Coordenacao Geral
Apoio: Dev Senior A e Dev Senior B
Revisao final: Revisor

## Batch 9 - Go-live e encerramento

Task: B9-T01 Go-live controlado
Objetivo: liberar o sistema com observacao ativa.
Escopo de escrita: ambiente alvo, checklist e runbook.
Entregaveis: go-live executado e registrado.
Validacao: sistema saudavel apos a liberacao.
Como documentar: atualizar `docs-go-live-checklist.md` e `docs-runbook.md`.
Owner primario: Coordenacao Geral
Apoio: Dev Senior A
Revisao final: Revisor

Task: B9-T02 Handoff final do projeto
Objetivo: consolidar o encerramento e deixar a operacao transferivel.
Escopo de escrita: PRDs, tasklists, runbook e documento final.
Entregaveis: handoff final e checklist final de aderencia.
Validacao: qualquer novo membro entende o estado final sem depender de contexto oral.
Como documentar: consolidar tudo em `prd/` e `docs-runbook.md`.
Owner primario: Revisor
Apoio: Dev Junior 4
Revisao final: Coordenacao Geral

## Regras de handoff entre membros

- Junior nunca entrega direto para producao, sempre entrega para Senior ou Revisor
- Senior entrega para Revisor quando a task tocar seguranca, arquitetura, integracao ou ambiente real
- Revisor devolve a task se faltar validacao, documentacao ou criterio de pronto
- Coordenacao Geral so considera a task concluida quando o handoff estiver registrado

## Como a Coordenacao deve distribuir o trabalho

- distribuir batches 1, 2 e 5 prioritariamente para Senior A
- distribuir batches 3 e 4 prioritariamente para Senior B
- usar os 4 Juniors como camada de execucao assistida, nunca como dono de arquitetura
- sempre colocar um Junior apoiando um Senior na mesma frente para reduzir custo e manter qualidade
- manter o Revisor fora do fluxo de implementacao principal para preservar independencia critica

## Regra final para manter qualidade com custo baixo

Se a task for pequena, com escopo bem definido, artefato obrigatorio e validacao objetiva, ela pode ir para um Junior ou uma LLM barata.

Se a task envolver arquitetura, seguranca, integracao externa, producao ou decisao sem retorno barato, ela deve subir para Senior, Revisor ou Coordenacao Geral.
