# Runbook Inicial - FBR-CLICK

## Subida local

1. Copie `.env.example` para `.env`.
2. Rode `docker compose up --build -d`.
3. Valide os healthchecks:
   - frontend: `http://localhost:3000`
   - backend: `http://localhost:8000/health`
   - OpenClaw gateway: `http://localhost:3500/health`

## Credenciais locais

- email: `admin@fbr.local`
- senha: `change-me-now`
- workspace: `00000000-0000-0000-0000-000000000001`
- user id: `11111111-1111-1111-1111-111111111111`

## Endpoints principais locais

- handoff publico do `1FBR-Leads`: `http://localhost:8000/api/v1/leads/webhook`
- webhook publico do `1FBR-Dev`: `http://localhost:8000/api/v1/dev/events/webhook`
- webhook publico do `1FBR-Suporte`: `http://localhost:8000/api/v1/suporte/handoff/webhook`
- webhook legado detalhado: `http://localhost:8000/api/webhooks/fbr-leads/handoff`
- CRM meta: `http://localhost:8000/api/deals/meta`
- validacao de agentes: `http://localhost:8000/api/agents/validate`
- controle de agentes: `http://localhost:8000/api/agents/control`
- emissao de token de agente: `http://localhost:8000/api/agents/tokens`
- agent api inicial: `http://localhost:8000/api/agent-api/actions/execute`
- websocket do canal: `ws://localhost:8000/api/messages/ws/channels/{channel_id}`
- websocket do workspace: `ws://localhost:8000/api/agents/ws/workspaces/{workspace_id}`
- git watcher: `http://localhost:8000/api/git-watcher`

## Scripts operacionais

- registrar agentes: `scripts/register-agents.ps1`
- registrar git watchers: `scripts/register-git-watchers.ps1`
- backup diario: `scripts/backup-postgres.ps1`
- testar webhooks: `scripts/test-webhooks.ps1`
- testar `1FBR-Leads`: `scripts/test-fbr-leads-webhook.ps1`
- testar `1FBR-Dev`: `scripts/test-fbr-dev-webhook.ps1`
- testar `1FBR-Suporte`: `scripts/test-fbr-suporte-webhook.ps1`
- testar `agent-api`: `scripts/test-agent-api.ps1`
- validar ambiente de producao: `scripts/validate-production-env.ps1`
- smoke test de producao: `scripts/smoke-deploy.ps1`
- bootstrap de VPS: `scripts/bootstrap-vps.sh`
- homologacao controlada: `scripts/homologacao-controlada.ps1`

## Agentes operacionais

Repositorios locais prontos:
- `agents/comercial-bot`
- `agents/report-bot`
- `agents/onboarding-bot`
- `agents/approval-bot`
- `agents/content-bot`
- `agents/ads-bot`

Todos possuem os 7 markdowns obrigatorios, passam na validacao da API e podem ser registrados com `scripts/register-agents.ps1`.

## Help padronizado FBR

Entrou no FBR-CLICK o modulo `Preciso de Ajuda` seguindo o padrao corporativo:
- item visivel no menu lateral
- drawer lateral sem troca de rota
- ajuda automatica baseada na rota atual
- checklist rapido por tela
- proximas acoes com atalhos contextuais
- perguntas sugeridas por pagina
- chat contextual com o agente `Leon Guavamango`
- reset de contexto ao trocar de pagina
- knowledge base estruturada por rota em `frontend/lib/help/leon-knowledge.ts`
- documentacao por menu em `prd/documentacao-ajuda-menu-fbr-click.md`

## Frontend de agentes

Telas validadas:
- `/spaces/[spaceId]/settings/agents`
- `/spaces/[spaceId]/pipeline`
- `/spaces/[spaceId]/channels/[channelId]`
- `/spaces/[spaceId]/tasks`

O painel agora mostra:
- kill switch real do workspace
- owners por agente
- escopo permitido por agente
- acoes que exigem approval
- fila de approvals com CTA real de aprovar e rejeitar
- cards do pipeline com destaque visual para origem `1FBR-Leads`
- atualizacao automatica por websocket em canal e workspace
- sidebar com leitura mais operacional de spaces, canais e agentes ativos
- board de tarefas em cards com metricas de prioridade e origem
- monitor de agentes com estado do git watcher por repositorio

## Producao

Artefatos preparados:
- compose dedicado: `docker-compose.production.yml`
- ambiente exemplo: `.env.production.example`
- Nginx de producao: `nginx/production.conf`
- runbook de deploy: `docs-deploy-producao.md`
- checklist de go-live: `docs-go-live-checklist.md`
- bootstrap da VPS: `scripts/bootstrap-vps.sh`
- backup diario: `scripts/backup-postgres.ps1`
- smoke test: `scripts/smoke-deploy.ps1`

## Validacoes ja confirmadas

- `GET /health` retorna `ok`
- frontend sobe e responde em `http://localhost:3000`
- login local funciona
- telas de `spaces`, `channels`, `tasks`, `pipeline` e `agents` respondem com dados reais
- approvals criam, aprovam e registram auditoria
- handoff do `1FBR-Leads` e idempotente por `external_reference`
- webhooks de `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte` passam localmente
- contratos publicos de `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte` respondem `accepted`
- `1FBR-Dev` e `1FBR-Suporte` tem callback de saida preparado no backend, pendente apenas da URL real
- CRM expoe stages, transicoes e motivos padrao em `/api/deals/meta`
- mudanca de stage invalida retorna `422`
- fechamento de deal exige `reason_code`
- `FBR-CLICK -> 1FBR-Leads` dispara callback HTTP assinado em cada mudanca de stage e fechamento
- os 6 bots atuais passam na validacao dos 7 markdowns
- `agent_action_logs` e append-only no Postgres
- `git_watcher` possui tabela, API e bootstrap local validado
- `scripts/register-agents.ps1` registra os agentes no banco
- mensagens humanas passam por sanitizacao leve contra prompt injection
- rotas sensiveis possuem rate limiting basico e retornam `429` quando excedidas
- mensagens, tarefas e `agent-api` tambem possuem limite adicional por canal e por agente quando aplicavel
- kill switch e escopo por agente aparecem no frontend
- emissao de JWT de agentes validada via `/api/agents/tokens`
- `agent-api` valida escopo, executa acoes permitidas e abre approval quando necessario
- `agent-api` cria tarefas reais de follow-up e tarefas de revisao de stage
- `agent-api` registra mensagem de contexto no canal ao sugerir mudanca de stage
- `agent-api` registra rascunho real de mensagem no canal
- `agent-api` executa `change_deal_stage` apos approval aprovado
- websocket do canal entrega `message_created`, `task_created` e `deal_stage_changed`
- websocket do workspace entrega `approval_created`, `approval_decided`, `kill_switch_updated`, `task_created`, `message_created` e `deal_stage_changed`
- a tela do canal tem bridge realtime e atualiza via `router.refresh()` sem refresh manual
- as telas de `tasks`, `pipeline` e `agents` atualizam via websocket de workspace sem refresh manual
- CTA de aprovar e rejeitar funciona no frontend via `/api/proxy`
- `docker-compose.production.yml` valida corretamente no Docker Compose
- `scripts/homologacao-controlada.ps1` passou com `ok = true` na validacao local final do MVP
- o modulo `Preciso de Ajuda` abre sem troca de rota e responde com contexto da pagina atual
