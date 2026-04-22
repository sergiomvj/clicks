# Tasklist FBR-CLICK

Fonte principal: `prd/plano-de-implementacao.md`, `prd/prd-backend-fbrsales.md` e `prd/prd-frontend-fbrsales.md`.

## Papel do sistema no ecossistema FBR

O `FBR-CLICK` opera como base comercial central do ecossistema FBR.

Fluxo principal esperado:

1. o `1FBR-Leads` capta, enriquece e aquece leads frios
2. o `1FBR-Leads` envia os leads qualificados para o `FBR-CLICK`
3. o `FBR-CLICK` transforma esse handoff em base operacional de vendas
4. o `FBR-CLICK` cria deal, canal, contexto comercial, tarefas e acompanhamento humano + agentes
5. o `FBR-CLICK` devolve feedback de conversao para o `1FBR-Leads`

## Status atual do projeto

- [x] Estrutura real de backend criada
- [x] Estrutura real de frontend criada
- [x] Docker Compose criado
- [x] Banco modelado e migrado localmente
- [x] OpenClaw Gateway scaffoldado
- [x] Nginx e ambiente local preparados
- [x] Painel web criado
- [x] Contrato de entrada de leads vindos do `1FBR-Leads` implementado
- [x] Integracoes base com `1FBR-Dev` e `1FBR-Suporte` implementadas
- [x] Frontend validado localmente com login e navegacao
- [x] Webhooks locais validados com HMAC
- [x] Approval flow e audit log iniciais validados
- [x] Contratos publicos de `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte` documentados e testados
- [x] JWT inicial de agentes e `agent-api` inicial implementados
- [x] `agent-api` com efeitos reais iniciais em CRM, mensagens e tarefas
- [x] Realtime inicial validado para canal comercial
- [x] Realtime expandido para workspace em approvals, kill switch, tarefas e pipeline
- [x] CTA operacional de approvals validada no frontend
- [ ] Payloads reais e secrets finais entre sistemas
- [ ] Deploy em VPS com dominio e SSL reais
- [ ] Operacao real de agentes nativos

## Batch 1 - Fundacao

- [x] Criar bootstrap do repositorio com `app/`, `frontend/`, `agents/`, `db/`, `docker/`, `nginx/`, `scripts/` e `monitoring/`
- [x] Criar `docker-compose.yml` com `postgres`, `redis`, `fastapi`, `frontend`, `openclaw-gateway`, `nginx`, `prometheus` e `grafana`
- [x] Criar `Dockerfile` do backend
- [x] Criar `frontend/Dockerfile`
- [x] Criar `.env.example` consolidado
- [x] Criar `.gitignore`
- [x] Criar `nginx/default.conf` inicial
- [x] Criar `README.md` base do sistema
- [x] Criar `docs-runbook.md` inicial
- [x] Validar `GET /health` local
- [ ] Provisionar VPS Hetzner real
- [ ] Instalar Docker e Docker Compose na VPS
- [ ] Configurar SSL real com Certbot e dominio final

## Batch 2 - Database

- [x] Criar pasta de migrations SQL
- [x] Implementar schema principal do PRD
- [x] Criar tabelas de `workspaces`, `spaces`, `channels`, `users`, `agents`, `messages`, `tasks`, `deals`, `deal_history`, `approvals` e `agent_action_logs`
- [x] Criar campos para origem do lead e rastreabilidade do handoff do `1FBR-Leads`
- [x] Habilitar isolamento por `workspace_id`
- [x] Criar triggers de `updated_at`
- [x] Criar indices de performance
- [x] Criar seed inicial de workspace, admin, canais, pipeline e agentes mockados
- [x] Validar queries basicas e health do banco
- [x] Endurecer append-only do `agent_action_logs` via regra de banco

## Batch 3 - Backend Core

- [x] Criar app FastAPI com lifespan
- [x] Criar `app/core/config.py`, `app/core/database.py`, `app/core/redis.py` e `app/core/security.py`
- [x] Criar `GET /health`
- [x] Implementar autenticacao humana via fluxo compativel com proxy Next.js e header `X-User-Id`
- [x] Construir leitura inicial de spaces
- [x] Construir leitura inicial de messages com `author_type`
- [x] Construir leitura inicial de tasks com `source`
- [x] Construir leitura inicial de deals e stages
- [x] Criar `PATCH /deals/{id}/stage` com gravacao em `deal_history`
- [x] Criar WebSocket inicial de usuarios por canal
- [x] Criar notificacoes em tempo real iniciais por canal
- [x] Criar servico de entrada de lead qualificado vindo do `1FBR-Leads`
- [x] Criar logica de criacao automatica de deal, canal e tarefas a partir do handoff
- [x] Criar feedback `deal.won` e `deal.lost` de volta para o `1FBR-Leads`
- [x] Tornar o handoff do `1FBR-Leads` idempotente por `external_reference`

## Batch 4 - OpenClaw Agents

- [x] Criar scaffold do registro de agentes
- [x] Implementar validacao dos 7 markdowns obrigatorios
- [x] Criar JWT inicial para agentes
- [x] Criar gateway WebSocket `/agents/ws`
- [x] Criar `agent-api` inicial com checagem de escopo
- [x] Criar audit log basico com consulta por API
- [x] Criar approval flow inicial com solicitante, aprovador e expiracao
- [x] Criar rate limiting por agente e por canal
- [x] Criar sanitizacao anti-prompt-injection
- [x] Criar base de `git_watcher`
- [x] Criar template de repositorio de agente em `agents/`
- [x] Priorizar `comercial-bot` e `report-bot` como agentes operacionais reais
- [x] Permitir efeitos reais controlados para `draft_message`, `create_follow_up_task` e `suggest_stage_change`
- [x] Permitir execucao real de `change_deal_stage` somente apos approval aprovado

## Batch 5 - Frontend Dashboard

- [x] Criar app Next.js em `frontend/`
- [x] Configurar TypeScript strict
- [x] Configurar login, sessao e middleware
- [x] Implementar proxy `/api/proxy/[...path]`
- [x] Implementar layout principal com sidebar, spaces, canais e agentes
- [x] Implementar tela de mensagens com dados reais
- [x] Implementar board de tarefas com dados reais
- [x] Implementar pipeline CRM com dados reais
- [x] Implementar painel admin de agentes
- [x] Validar `build`
- [x] Exibir no frontend tarefas e mensagens criadas por `agent-api`
- [x] Exibir approvals pendentes na area de agentes
- [x] Atualizar tela do canal sem refresh manual via websocket
- [x] Exibir CTA real de aprovar/rejeitar approvals no frontend
- [x] Refinar visual e reduzir o que ainda esta scaffold
- [x] Destacar visualmente deals originados do `1FBR-Leads`
- [x] Exibir approvals pendentes de `change_deal_stage` com CTA claro
- [x] Atualizar `tasks`, `pipeline` e `agents` sem refresh manual via websocket de workspace

## Batch 6 - Agentes nativos

- [x] Criar template dos 7 markdowns em `agents/_template`
- [x] Criar `comercial-bot`
- [x] Criar `report-bot`
- [x] Criar `onboarding-bot`
- [x] Criar `approval-bot`
- [x] Criar `content-bot`
- [x] Criar `ads-bot`
- [x] Preparar documentacao de owner, approvals e kill switch

## Batch 7 - Integracao com sistemas FBR

- [x] Criar webhook de handoff do `1FBR-Leads`
- [x] Transformar handoff em deal, canal, tarefa e mensagem
- [x] Criar retorno `deal.won` e `deal.lost` para o `1FBR-Leads`
- [x] Criar webhook do `1FBR-Dev`
- [x] Criar webhook do `1FBR-Suporte`
- [x] Aplicar HMAC-SHA256 em todos os webhooks
- [x] Validar fluxo local dos webhooks
- [x] Publicar contratos publicos `v1` para `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte`
- [x] Criar scripts dedicados de teste para cada integracao
- [ ] Validar payloads reais entre sistemas

## Batch 8 - Producao e Entrega

- [x] Adicionar Prometheus e Grafana ao compose
- [x] Criar rotina de backup
- [x] Documentar operacao basica em runbook
- [x] Preparar compose de producao, `.env` exemplo e smoke test
- [x] Preparar bootstrap da VPS e checklist de go-live
- [ ] validar deploy integrado em VPS real
- [ ] Executar teste de carga
- [ ] Executar checklist de seguranca
- [x] Finalizar handoff operacional local para homologacao controlada

## Proximo bloco autonomo mais valioso

- [ ] ligar payloads finais de `1FBR-Dev` e `1FBR-Suporte` com endpoints reais
- [ ] endurecer append-only do `agent_action_logs`
- [x] Criar base de `git_watcher`
- [x] preparar validacao final de deploy na VPS real

## Pontos que dependem de voce

- [x] naming final do produto
- [ ] payloads e endpoints reais dos sistemas FBR
- [ ] secrets finais do `.env`
- [ ] VPS, dominio e SSL
- [ ] owners humanos dos agentes
- [ ] regras finais de aprovacao e operacao comercial

## Marco mais recente

- [x] Nome oficial padronizado para `FBR-CLICK`
- [x] Regras formais de transicao de stage implementadas
- [x] `reason_code` obrigatorio em `closed_won` e `closed_lost`
- [x] Metadados de CRM expostos em `/api/deals/meta`
- [x] Contrato publico `/api/v1/leads/webhook` publicado com resposta apenas `accepted`
- [x] Callback `FBR-CLICK -> 1FBR-Leads` implementado com HMAC
- [x] `agents/comercial-bot` criado com 7 markdowns validos
- [x] `agents/report-bot` criado com 7 markdowns validos
- [x] Script de backup diario criado em `scripts/backup-postgres.ps1`
- [x] Configuracao Nginx de producao criada em `nginx/production.conf`
- [x] Guia de deploy criado em `docs-deploy-producao.md`
- [x] Script `scripts/register-agents.ps1` registra os agentes operacionais
- [x] Sanitizacao leve anti-prompt-injection aplicada em mensagens e webhooks
- [x] Rate limiting basico aplicado em mensagens, CRM e webhooks
- [x] Escopo por agente exposto pela API
- [x] Kill switch por workspace implementado via Redis e exibido no frontend
- [x] `.env.production.example` criado para a VPS
- [x] `docker-compose.production.yml` criado e validado
- [x] `scripts/smoke-deploy.ps1` criado para validacao pos-deploy
- [x] `scripts/bootstrap-vps.sh` criado para preparar a VPS
- [x] `docs-go-live-checklist.md` criado para execucao do go-live
- [x] Contratos publicos de `1FBR-Dev` e `1FBR-Suporte` publicados e validados com resposta `accepted`
- [x] `prd/contratos-integracoes.md` criado para consolidar os payloads e headers de integracao
- [x] JWT inicial de agentes publicado em `/api/agents/tokens`
- [x] `agent-api` inicial publicado em `/api/agent-api/actions/execute`
- [x] `scripts/test-agent-api.ps1` criado e validado localmente
- [x] `agent-api` agora cria rascunho real de mensagem no canal
- [x] `agent-api` agora cria tarefa real de follow-up
- [x] `agent-api` agora cria tarefa e mensagem ao sugerir mudanca de stage
- [x] `agent-api` agora executa `change_deal_stage` somente apos approval aprovado
- [x] websocket do canal agora emite `message_created`, `task_created` e `deal_stage_changed`
- [x] frontend do canal agora atualiza sozinho quando recebe evento realtime
- [x] CTA real de aprovar e rejeitar approvals validada pelo frontend via proxy
- [x] websocket de workspace agora emite `approval_created`, `approval_decided`, `kill_switch_updated`, `task_created`, `message_created` e `deal_stage_changed`
- [x] frontend de `tasks`, `pipeline` e `agents` agora atualiza sozinho quando recebe evento realtime de workspace
- [x] `onboarding-bot`, `approval-bot`, `content-bot` e `ads-bot` criados, validados e registrados\r\n- [x] migration `002_audit_and_git_watchers.sql` aplicada com sucesso no Postgres local\r\n- [x] `agent_action_logs` bloqueia `UPDATE` e `DELETE` por trigger append-only\r\n- [x] `git_watcher` ganhou tabela, API e script `scripts/register-git-watchers.ps1`\r\n- [x] frontend de agentes agora mostra estado do `git_watcher` por repositorio\r\n- [x] pacote de pre-validacao da VPS criado com `scripts/validate-production-env.ps1` e `docs-validacao-vps.md`\r\n- [x] callbacks de saida para `1FBR-Dev` e `1FBR-Suporte` preparados no backend com HMAC e payload normalizado\r\n- [x] `scripts/homologacao-controlada.ps1` criado e validado com `ok = true`\r\n- [x] `docs-homologacao-controlada.md` criado para conduzir o uso controlado amanha
- [x] sidebar, board de tarefas e pipeline receberam refinamento visual operacional




