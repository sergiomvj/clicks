# Tasklist de Finalizacao 100% Alinhada ao Conceito - FBR-CLICK

Atualizado em: 2026-03-27

Fontes usadas nesta avaliacao:
- `prd/fbr-click-conceito.html`
- `prd/matriz-alinhamento-conceito.md`
- `prd/status-alinhamento-conceito.md`
- `.agent/rules/fbr-arquitetura.md`

## Aviso de governanca antes da execucao

Esta tasklist foi alinhada ao conceito geral e a arquitetura FBR canonica disponivel no workspace.

Arquivos canonicos obrigatorios pelo padrao FBR que NAO foram encontrados com esses nomes no projeto:
- `securitycoderules.md`
- `DESIGN_STANDARDS.md`

Decisao pratica para esta tasklist:
- manter a execucao tecnica baseada na arquitetura canonica e no conceito atual
- tratar a ausencia desses dois documentos como bloqueio de governanca a ser resolvido no primeiro batch
- nao considerar o projeto 100% finalizado enquanto esses arquivos nao forem restaurados, validados ou substituidos por equivalentes canonicos aprovados

## Leitura executiva do estado atual

Ja esta substancialmente pronto e operacional em ambiente local, com MVP forte para homologacao.

O que ainda impede 100% de alinhamento conceitual:
- ausencia dos documentos canonicos de seguranca e design exigidos pelo padrao FBR
- RLS real e auditavel por `workspace_id` ainda nao fechado no banco inteiro
- stack LLM de 3 camadas ainda nao operacional ponta a ponta com health publish e fallback real
- n8n ainda nao esta fechado como camada de orquestracao efetiva dos triggers dos agentes
- operacao autonoma dos 6 agentes ainda nao esta completa no modelo do conceito
- deploy final real e integracoes reais externas ainda nao homologados no ambiente alvo

## Invariantes de finalizacao

Estas condicoes precisam ser verdadeiras para considerar o projeto finalizado e 100% alinhado:

- [ ] os documentos canonicos de arquitetura, seguranca e design estao presentes e aprovados
- [ ] toda tabela aplicavel possui enforcement real de isolamento por `workspace_id`
- [ ] nenhum fluxo critico depende de mock, alias transitorio ou bypass operacional
- [ ] todos os 6 agentes operam com owner definido, kill switch, approvals e triggers reais
- [ ] n8n esta presente como orquestrador efetivo dos triggers e handoffs do sistema
- [ ] a stack LLM em 3 camadas opera com fallback real e health publicado no Redis
- [ ] webhooks e callbacks externos estao homologados com payload real, URL real e secret real
- [ ] deploy em VPS, SSL, backup, restore e observabilidade foram validados no ambiente final

## Batch F0 - Fechar governanca canonica

Objetivo: eliminar lacunas documentais que impedem declarar alinhamento FBR pleno.

- [ ] localizar ou recriar `securitycoderules.md` no workspace com aprovacao explicita
- [ ] localizar ou recriar `DESIGN_STANDARDS.md` no workspace com aprovacao explicita
- [ ] revisar `prd/fbr-click-conceito.html` contra `.agent/rules/fbr-arquitetura.md` e registrar equivalencias finais
- [ ] consolidar um glossario final de equivalencias tecnicas do conceito vs implementacao real
- [ ] definir formalmente o criterio institucional de “100% alinhado” para este projeto

Criterio de done do batch:
- [ ] os tres documentos canonicos estao presentes no workspace
- [ ] nao existe duvida aberta sobre nomenclatura ou equivalencia de entidades
- [ ] a tasklist restante passa a refletir somente execucao, nao descoberta conceitual

## Batch F1 - Fechar isolamento de dados e seguranca estrutural

Objetivo: convergir a persistencia ao conceito e reduzir o maior gap tecnico remanescente.

- [ ] mapear todas as tabelas que exigem enforcement por `workspace_id`
- [ ] aplicar RLS real ou mecanismo equivalente aprovado em todas as tabelas aplicaveis
- [ ] provar que leitura cruzada entre workspaces retorna bloqueio observavel
- [ ] revisar endpoints FastAPI para garantir propagacao consistente de identidade e workspace
- [ ] revisar `agent-api` para negar execucao quando token, banco e escopo divergirem
- [ ] criar checklist de seguranca executavel para rotas humanas, rotas de agente e webhooks

Criterio de done do batch:
- [ ] isolamento entre workspaces validado com evidencia tecnica binaria
- [ ] nenhuma rota critica consegue operar sem contexto valido de workspace
- [ ] trilha de auditoria e controles de escopo foram revalidados apos o endurecimento

## Batch F2 - Fechar aderencia conceitual de dados e contratos

Objetivo: remover desvios residuais entre conceito e implementacao real.

- [ ] revisar a modelagem final de `channels`, `tasks`, `kpis`, `approvals`, `agent_markdown_cache`, `lead_intakes` e `git_watchers`
- [ ] documentar oficialmente que `approvals` e a equivalencia tecnica de `agent_approval_requests`
- [ ] consolidar os aliases legados de prioridade de tarefa e remover dependencias ambiguuas
- [ ] garantir que todos os tipos de canal finais sejam apenas `deal`, `task`, `system` e `agent-log` ou registrar excecoes aprovadas
- [ ] revisar os contratos REST e WebSocket e marcar claramente o que e canonico, legado ou compatibilidade

Criterio de done do batch:
- [ ] nao resta desvio estrutural sem decisao documentada
- [ ] contratos publicos e internos batem com a modelagem final aprovada
- [ ] a documentacao tecnica final nao depende de interpretacao informal

## Batch F3 - Operacionalizar n8n como sistema nervoso central

Objetivo: alinhar a execucao dos agentes ao pressuposto canonico da arquitetura FBR.

- [ ] definir os triggers de n8n necessarios para `comercial-bot`, `report-bot`, `onboarding-bot`, `approval-bot`, `content-bot` e `ads-bot`
- [ ] criar ou importar a instancia dedicada de n8n do sistema
- [ ] implementar os fluxos de chamada de agente via n8n em vez de disparos apenas locais ou manuais
- [ ] publicar eventos de negocio necessarios para n8n consumir com previsibilidade
- [ ] registrar falha de trigger, retry e fallback operacional no audit log ou monitoramento

Criterio de done do batch:
- [ ] n8n dispara fluxos criticos dos agentes em ambiente real
- [ ] os fluxos principais deixam de depender de acionamento manual para operar no modo previsto pelo conceito
- [ ] existe rastreabilidade do trigger ate o efeito no FBR-CLICK

## Batch F4 - Fechar stack LLM em 3 camadas com fallback real

Objetivo: cumprir o pressuposto canonico de resiliencia dos agentes.

- [ ] implementar health check recorrente das tres camadas de LLM
- [ ] publicar o status agregado no Redis a cada ciclo de verificacao
- [ ] ajustar a camada de execucao dos agentes para ler o status antes de cada chamada
- [ ] implementar fallback automatico `Ollama -> Claude -> GPT-4o`
- [ ] registrar eventos de degradacao e fallback para auditoria e observabilidade
- [ ] validar cenarios de indisponibilidade parcial sem interromper a operacao

Criterio de done do batch:
- [ ] o fallback real acontece sem intervencao manual
- [ ] a indisponibilidade de uma camada nao paralisa o sistema
- [ ] o owner consegue observar claramente qual camada esta sendo usada

## Batch F5 - Colocar os 6 agentes em operacao conceitualmente completa

Objetivo: sair do modo “agentes prontos no repositorio” para “agentes operando como atores reais do sistema”.

- [ ] definir owner humano final de cada um dos 6 agentes
- [ ] fechar approvals obrigatorios de cada agente em termos binarios e auditaveis
- [ ] ligar triggers reais do `comercial-bot` e `report-bot` nos fluxos principais
- [ ] ligar triggers reais do `onboarding-bot`, `approval-bot`, `content-bot` e `ads-bot`
- [ ] validar heartbeat, health e watchdog operacional de todos os agentes
- [ ] executar periodo de observacao controlada conforme a arquitetura FBR
- [ ] documentar criterio de promocao de cada agente para operacao plena

Criterio de done do batch:
- [ ] todos os agentes possuem owner, trigger, escopo, approval e kill switch operacionais
- [ ] todos os agentes conseguem ser observados e interrompidos sem ambiguidade
- [ ] nenhum agente permanece apenas como cadastro ou template estatico

## Batch F6 - Homologar integracoes reais do ecossistema FBR

Objetivo: trocar validacao local e contratos simulados por interoperabilidade real.

- [ ] homologar payload real do `1FBR-Leads -> FBR-CLICK`
- [ ] homologar payload real do `FBR-CLICK -> 1FBR-Leads`
- [ ] homologar payload real do `1FBR-Dev -> FBR-CLICK`
- [ ] homologar payload real do `FBR-CLICK -> 1FBR-Dev`
- [ ] homologar payload real do `1FBR-Suporte -> FBR-CLICK`
- [ ] homologar payload real do `FBR-CLICK -> 1FBR-Suporte`
- [ ] validar HMAC, idempotencia, retry e observabilidade de cada integracao

Criterio de done do batch:
- [ ] todos os contratos externos foram exercitados com URL real e secret real
- [ ] nao existe integracao critica pendente apenas de “ajustar depois”
- [ ] erros externos produzem comportamento previsivel e rastreavel

## Batch F7 - Fechar frontend final conforme conceito e padrao corporativo

Objetivo: remover os ultimos desvios de experiencia e consolidar a interface final.

- [ ] validar o dark mode final contra o conceito e contra o padrao visual corporativo aprovado
- [ ] revisar a navegacao do canal, pipeline, tarefas, agentes e help padronizado como fluxo unico
- [ ] garantir consistencia entre estados realtime, approvals e acoes humanas
- [ ] revisar copy operacional, naming e sinais visuais de origem, risco e aprovacao
- [ ] validar o modulo `Preciso de Ajuda` contra o padrao documental corporativo e ajustar lacunas visuais finais

Criterio de done do batch:
- [ ] nao resta superficie principal com comportamento de scaffold
- [ ] a interface final reflete o conceito sem contradicoes relevantes
- [ ] a operacao humana consegue usar o sistema sem recorrer a docs paralelas para tarefas basicas

## Batch F8 - Produzir ambiente final e operacao real

Objetivo: converter o projeto de homologado localmente para sistema finalizado em producao.

- [ ] provisionar a VPS final do sistema
- [ ] configurar dominio, DNS e SSL finais
- [ ] aplicar `.env` final sem secrets versionados
- [ ] validar compose e bootstrap no ambiente alvo
- [ ] executar backup real e restore real no ambiente alvo
- [ ] validar Prometheus, Grafana, logs e alertas no ambiente alvo
- [ ] executar smoke test real de deploy

Criterio de done do batch:
- [ ] o sistema sobe limpo na VPS final
- [ ] o restore funciona com evidencia tecnica
- [ ] o owner consegue operar e observar o ambiente sem dependencia do ambiente local

## Batch F9 - Encerrar com validacao final de confiabilidade

Objetivo: declarar finalizacao com evidencias, nao por percepcao.

- [ ] executar teste de carga com pelo menos 10 agentes simultaneos e usuarios humanos concorrentes conforme o conceito
- [ ] executar checklist de seguranca final aprovado
- [ ] executar rodada de homologacao ponta a ponta com os sistemas externos reais
- [ ] consolidar evidencias de auditoria, backup, restore, fallback LLM e kill switch
- [ ] registrar termo interno de aceite operacional do sistema

Criterio de done do batch:
- [ ] existe evidencia objetiva de estabilidade, seguranca e interoperabilidade
- [ ] nao resta bloqueio aberto para chamar o projeto de finalizado
- [ ] o projeto pode ser encerrado como 100% alinhado ao conceito geral

## Ordem recomendada de execucao

1. `F0` governanca canonica
2. `F1` seguranca estrutural e isolamento
3. `F2` aderencia de modelagem e contratos
4. `F3` n8n como orquestrador real
5. `F4` stack LLM em 3 camadas
6. `F5` operacao plena dos 6 agentes
7. `F6` integracoes reais externas
8. `F7` frontend final e UX conceitual
9. `F8` producao final
10. `F9` validacao conclusiva

## Leitura honesta de prioridade

Se o objetivo for “fechar o projeto tecnicamente” o centro de gravidade esta em `F1`, `F3`, `F4`, `F5`, `F6` e `F8`.

Se o objetivo for “poder afirmar 100% alinhamento conceitual” o bloqueio numero 1 continua sendo `F0`, porque sem os documentos canonicos faltantes a governanca FBR fica incompleta, mesmo com codigo forte.
