# Plano de ImplementaÃ§Ã£o â€” FBR-CLICK v1.0
> **Fonte de verdade:** `prd-backend-fbrclick.md` Â· `prd-frontend-fbrclick.md`
> **Regras obrigatÃ³rias:** `securitycoderules.md` Â· `fbr-arquitetura.md`
> **Prazo:** 60 dias Â· 8 batches Â· ~50 tasks de 5â€“15 min cada

---

## Como usar este plano

Para cada batch, disparar uma sessÃ£o com o contexto:
```
Execute o [Batch X â€” Nome].
Fonte de verdade: prd-backend-fbrclick.md e prd-frontend-fbrclick.md (seÃ§Ã£o do batch).
Regras obrigatÃ³rias: securitycoderules.md e fbr-arquitetura.md.
CritÃ©rio de conclusÃ£o: todas as verificaÃ§Ãµes da tabela do batch passando.
NÃ£o avanÃ§ar para o prÃ³ximo batch sem verificaÃ§Ã£o OK em todas as tasks.
```

---

## Batch 1 â€” FundaÃ§Ã£o de Infraestrutura
**Dias 1â€“7 Â· Objetivo:** VPS funcionando, Docker Compose subindo toda a stack, SSL ativo.

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 1.1 | Provisionar VPS Hetzner (8 vCores / 32GB / 200GB NVMe Â· Ubuntu 24.04) | â€” | SSH funciona. `df -h` mostra 200GB. |
| 1.2 | Instalar Docker + Docker Compose | â€” | `docker --version` retorna sem erro. |
| 1.3 | Criar `docker-compose.yml` com: postgres, redis, fastapi, nginx | `docker-compose.yml` | `docker compose up -d` sobe todos sem erro. |
| 1.4 | Configurar PostgreSQL 16 com extensÃµes `uuid-ossp` | `app/core/database.py` | `SELECT gen_random_uuid()` retorna UUID vÃ¡lido. |
| 1.5 | Criar `.env` e `.env.example` com todas as variÃ¡veis do PRD backend | `.env` Â· `.env.example` | FastAPI inicia sem erros de variÃ¡vel faltando. |
| 1.6 | Configurar Nginx como proxy reverso com SSL (Certbot) | `nginx/default.conf` | `https://fbr-click.com` retorna 200. |
| 1.7 | Adicionar OpenClaw Gateway ao `docker-compose.yml` (porta 3500) | `docker-compose.yml` | `curl localhost:3500/health` retorna `{status: ok}`. |

---

## Batch 2 â€” Database
**Dias 7â€“12 Â· Objetivo:** Schema completo com RLS, triggers e indexes em produÃ§Ã£o.

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 2.1 | Executar SQL de criaÃ§Ã£o de todas as tabelas (seÃ§Ã£o 4.2 do prd-backend) | â€” | `\dt` no psql lista todas as 13 tabelas. |
| 2.2 | Aplicar RLS em todas as tabelas (seÃ§Ã£o 4.3 do prd-backend) | â€” | SELECT com `workspace_id` diferente retorna 0 rows. |
| 2.3 | Criar funÃ§Ã£o `update_updated_at()` e triggers nas tabelas relevantes | â€” | UPDATE em `messages` atualiza `updated_at` automaticamente. |
| 2.4 | Criar todos os indexes de performance (seÃ§Ã£o 4.4 do prd-backend) | â€” | `EXPLAIN ANALYZE` usa index, nÃ£o seq scan em queries comuns. |
| 2.5 | Seed: workspace de teste + space + canal + usuÃ¡rio admin | `app/core/database.py` | Login com usuÃ¡rio seed funciona end-to-end. |

---

## Batch 3 â€” Backend Core
**Dias 12â€“20 Â· Objetivo:** FastAPI rodando com auth, mensagens, tasks, CRM e WebSocket de usuÃ¡rios.**

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 3.1 | FastAPI app factory com lifespan + `GET /health` | `app/main.py` | `GET /health` retorna `{status: ok}`. |
| 3.2 | Auth humano: `POST /api/auth/login`, `POST /api/auth/logout`, middleware iron-session â†’ `X-User-Id` | `app/auth/` | Rota protegida sem cookie â†’ 401. Com cookie â†’ 200. |
| 3.3 | Spaces e Channels: CRUD completo com isolamento por workspace | `app/spaces/` | POST cria space. GET de outro workspace retorna 0 resultados. |
| 3.4 | Messaging: CRUD de mensagens + distinÃ§Ã£o `author_type` human/agent | `app/messaging/` | POST mensagem retorna com `author_type` correto no payload. |
| 3.5 | Tasks: CRUD completo com `source` human/agent e filtros | `app/tasks/` | POST task com `source="agent"` salva e retorna corretamente. |
| 3.6 | CRM: deals, stages, `deal_history`, KPIs | `app/crm/` | `PATCH /deals/{id}/stage` cria registro em `deal_history`. |
| 3.7 | WebSocket de usuÃ¡rios: conexÃ£o em tempo real por canal (`/ws/channels/{id}`) | `app/messaging/websocket.py` | Abrir 2 conexÃµes no mesmo canal â€” msg enviada chega nas duas. |

---

## Batch 4 â€” Infraestrutura de Agentes
**Dias 20â€“32 Â· Objetivo:** Registro, autenticaÃ§Ã£o, WebSocket de agentes, audit log e approval flow operacionais.**

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 4.1 | Agent-service: registro de agente com validaÃ§Ã£o dos 7 markdowns obrigatÃ³rios | `app/agents/service.py` | `POST /api/agents` com repo vÃ¡lido â†’ agente registrado. Repo sem SOUL.md â†’ 422. |
| 4.2 | JWT de agente: geraÃ§Ã£o no registro, rotaÃ§Ã£o automÃ¡tica a cada 24h via Redis TTL | `app/agents/service.py` | Token expirado â†’ 401. Novo token gerado automaticamente. |
| 4.3 | Agent-gateway: WebSocket dedicado para OpenClaw em `/agents/ws` | `app/agents/gateway.py` | OpenClaw conecta via WS. Evento `message` chega no handler correto. |
| 4.4 | Agent-API: endpoints `/agent/*` com validaÃ§Ã£o de scope contra AGENTS.md | `app/agents/routes.py` | Agente tentando postar em canal fora do scope â†’ 403. |
| 4.5 | Git-watcher: receber push do GitHub, clonar, validar markdowns, recarregar | `app/agents/git_watcher.py` | Push no repo â†’ markdowns recarregados em < 30s. Canal de log recebe "âš™ï¸ ConfiguraÃ§Ã£o atualizada". |
| 4.6 | Audit log: `action_logger` como wrapper obrigatÃ³rio para toda action de agente | `app/agents/action_logger.py` | Toda action de agente â†’ `COUNT(*)` em `agent_action_logs` cresce. |
| 4.7 | Approval flow: agente solicita aprovaÃ§Ã£o, humano aprova/rejeita via API | `app/agents/approval.py` | Solicitar aprovaÃ§Ã£o â†’ aparece em `GET /api/agents/approvals`. Aprovar â†’ agente executa. |
| 4.8 | Rate limiting: 60 actions/min por agente, 5 mensagens/min por canal | `app/core/security.py` | 61Âª action em 1min â†’ 429. Backoff exponencial ativo. |
| 4.9 | Prompt injection: sanitizaÃ§Ã£o de input antes de enviar ao Gateway | `app/agents/gateway.py` | Input com tags HTML e instruÃ§Ãµes embutidas â†’ sanitizado antes de processar. |

---

## Batch 5 â€” Agentes Nativos
**Dias 32â€“42 Â· Objetivo:** 6 agentes nativos registrados e operacionais com seus repositÃ³rios Git.**

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 5.1 | Criar repositÃ³rio Git + 7 Markdowns do **Comercial Bot ðŸ’¼** | `agents/comercial-bot/` | Agente registrado no FBR-CLICK com badge ðŸ¤– na sidebar. |
| 5.2 | Testar trigger do Comercial Bot: deal movido â†’ cria tarefa + posta mensagem | `agents/comercial-bot/TASKS.md` | Mover deal no Kanban â†’ tarefa criada + mensagem no canal em â‰¤ 2min. |
| 5.3 | Criar e registrar **Report Bot ðŸ“Š** (relatÃ³rio sexta 17h) | `agents/report-bot/` | Heartbeat sexta 17h â†’ relatÃ³rio postado no canal #geral. |
| 5.4 | Criar e registrar **Onboarding Bot ðŸŽ“** (novo membro) | `agents/onboarding-bot/` | Adicionar membro ao workspace â†’ bot envia boas-vindas em â‰¤ 2min. |
| 5.5 | Criar e registrar **Approval Bot ðŸŽ¨** (fluxo de criativos) | `agents/approval-bot/` | Asset novo no canal de design â†’ bot inicia fluxo de aprovaÃ§Ã£o. |
| 5.6 | Criar e registrar **Content Bot âœï¸** e **Ads Bot ðŸ“¢** | `agents/content-bot/` Â· `agents/ads-bot/` | Ambos registrados com status online e heartbeat ativo. |

---

## Batch 6 â€” Frontend
**Dias 35â€“48 Â· Objetivo:** Interface completa com auth, sidebar, mensagens, tasks, pipeline e painel de agentes.**

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 6.1 | Next.js 15 + TypeScript strict + Tailwind v4 + shadcn/ui | `package.json` Â· `tsconfig.json` | `npx tsc` sem erros. `npm run dev` sobe na porta 3000. |
| 6.2 | Configurar `Inter` e `Outfit` via `next/font/google` no `layout.tsx` | `app/layout.tsx` Â· `globals.css` | Fontes carregam sem flash. Classes `font-sans` e `font-heading` funcionam. |
| 6.3 | iron-session: login, logout, middleware de proteÃ§Ã£o de rotas | `app/api/auth/` Â· `middleware.ts` | Rota `/spaces` sem cookie â†’ redireciona para `/login`. |
| 6.4 | Proxy Next.js obrigatÃ³rio para todas as chamadas ao backend | `app/api/proxy/[...path]/route.ts` | Fetch direto ao backend â†’ 401. Via proxy com cookie â†’ 200. |
| 6.5 | Layout principal: sidebar com spaces, canais e agentes com badges | `components/layout/Sidebar.tsx` | Sidebar lista spaces, canais e agentes com Ã­cone ðŸ¤– e badge "AGENTE" em roxo. |
| 6.6 | Tela de mensagens com WebSocket + distinÃ§Ã£o visual agente/humano | `components/messaging/` | Mensagem de agente tem fundo `#faf5ff` e badge "AGENTE". ReconexÃ£o automÃ¡tica funciona. |
| 6.7 | Kanban de deals com drag-and-drop entre stages | `components/crm/PipelineKanban.tsx` | Arrastar deal â†’ stage atualizado no backend + `deal_history` criado. |
| 6.8 | Board de tarefas com filtros por assignee, status, prazo, source | `components/tasks/TaskBoard.tsx` | Filtro por source="agent" retorna sÃ³ tarefas de agentes. |
| 6.9 | Painel de monitoramento de agentes (admin): status, logs, aprovaÃ§Ãµes, kill switch | `components/agents/AgentMonitor.tsx` | Agente offline â†’ badge vermelho em tempo real. Kill switch desconecta em < 5s. |

---

## Batch 7 â€” IntegraÃ§Ã£o com Sistemas FBR
**Dias 48â€“54 Â· Objetivo:** FBR-Leads, FBR-Dev e FBR-Suporte integrados via webhooks autenticados.**

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 7.1 | Webhook FBR-Leads: receber SQL handoff â†’ criar deal + canal + notificar vendedor | `app/webhooks/fbr_leads.py` | SQL do FBR-Leads â†’ deal criado no pipeline + canal do deal aberto + @menÃ§Ã£o ao vendedor. |
| 7.2 | Webhook FBR-Leads: enviar feedback deal.won/lost de volta ao FBR-Leads | `app/crm/service.py` | Fechar deal como ganho/perdido â†’ webhook enviado ao FBR-Leads em â‰¤ 1min. |
| 7.3 | Webhook FBR-Dev: receber eventos de sprint, deploys, blockers | `app/webhooks/fbr_dev.py` | Evento de blocker do FBR-Dev â†’ mensagem no canal #dev-sprints. |
| 7.4 | Webhook FBR-Suporte: receber leads qualificados e tickets escalados | `app/webhooks/fbr_suporte.py` | Lead do FBR-Suporte â†’ deal criado no pipeline de vendas. |
| 7.5 | Validar HMAC-SHA256 em TODOS os webhooks externos antes de processar | `app/webhooks/` | Webhook com secret errado â†’ 403. Secret correto â†’ processado normalmente. |

---

## Batch 8 â€” ProduÃ§Ã£o e Entrega
**Dias 54â€“60 Â· Objetivo:** Monitoramento, seguranÃ§a, testes de carga e handoff para o time.**

| Task | DescriÃ§Ã£o | Arquivos | VerificaÃ§Ã£o |
|---|---|---|---|
| 8.1 | Grafana + Prometheus: dashboards de infra (CPU, RAM, Redis, Postgres, WebSocket connections) | `docker-compose.yml` | Grafana acessÃ­vel. MÃ©tricas de todos os containers visÃ­veis em tempo real. |
| 8.2 | Backup automÃ¡tico do PostgreSQL para storage externo (diÃ¡rio Ã s 3h) | `scripts/backup.sh` | Restore a partir do backup â€” dados Ã­ntegros. |
| 8.3 | Teste de carga: 10 agentes simultÃ¢neos, 100 mensagens/min por 10min | â€” | Zero 429s. Zero mensagens perdidas. Audit log 100% completo. |
| 8.4 | Teste de seguranÃ§a: prompt injection, scope violation, kill switch, HMAC falso | â€” | Todos os vetores do checklist bloqueados. Kill switch desconecta em < 5s. |
| 8.5 | README: onboarding de agente, como registrar, como monitorar, como usar kill switch | `README.md` | README aprovado pelo gestor do projeto. |
| 8.6 | Handoff para o time: demo dos 6 agentes nativos, painel de monitoramento, fluxo de aprovaÃ§Ã£o | â€” | Todos os owners sabem registrar agente, pausar e aprovar aÃ§Ãµes sem assistÃªncia. |

---

## Resumo de prazos

| Batch | Nome | Dias | EntregÃ¡vel principal |
|---|---|---|---|
| 1 | FundaÃ§Ã£o de Infraestrutura | 1â€“7 | VPS + Docker + SSL rodando |
| 2 | Database | 7â€“12 | Schema completo com RLS e indexes |
| 3 | Backend Core | 12â€“20 | API REST + WebSocket de usuÃ¡rios |
| 4 | Infraestrutura de Agentes | 20â€“32 | OpenClaw integrado + audit log |
| 5 | Agentes Nativos | 32â€“42 | 6 agentes registrados e operacionais |
| 6 | Frontend | 35â€“48 | Interface completa com design system |
| 7 | IntegraÃ§Ã£o com Sistemas FBR | 48â€“54 | Webhooks FBR-Leads, Dev, Suporte |
| 8 | ProduÃ§Ã£o e Entrega | 54â€“60 | Monitoramento + testes + handoff |

> Batches 5 e 6 rodam em paralelo (dias 35â€“42 em overlap): o backend de agentes estarÃ¡ estÃ¡vel o suficiente para o frontend iniciar o painel de monitoramento enquanto os repositÃ³rios dos agentes sÃ£o criados.

---

## Checklist de seguranÃ§a â€” antes do go-live

- [ ] SESSION_SECRET com 64+ caracteres armazenado apenas no `.env`
- [ ] JWT_SECRET e OPENCLAW_AGENT_JWT_SECRET nunca commitados no Git
- [ ] `.env` no `.gitignore`. `.env.example` com valores em branco no repositÃ³rio
- [ ] RLS ativa em todas as 13 tabelas â€” testado com usuÃ¡rios de workspaces distintos
- [ ] Audit log append-only confirmado: nenhuma policy de UPDATE ou DELETE em `agent_action_logs`
- [ ] Kill switch testado e desconectando em < 5s
- [ ] HMAC-SHA256 validado em todos os 4 webhooks externos
- [ ] TypeScript strict sem `any` no frontend
- [ ] Nenhuma variÃ¡vel sensÃ­vel com prefixo `NEXT_PUBLIC_`
- [ ] Rate limiting ativo: 60 actions/min por agente, 5 mensagens/min por canal
- [ ] CORS configurado apenas para domÃ­nio do frontend
