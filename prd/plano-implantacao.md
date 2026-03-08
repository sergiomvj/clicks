# FBR-LEADS — Plano de Implementação v2.0
> **60 Dias · 8 Batches · ~50 Tasks de 5–15 min cada**  
> **Critério de avanço:** todas as verificações do batch anterior com status OK antes de iniciar o próximo  
> **Empresa:** Facebrasil · Fevereiro 2026 · Confidencial

---

## Como Usar Este Plano

Cada task tem duração de 5–15 minutos e inclui os arquivos envolvidos e como verificar que funcionou. O critério de avanço entre batches é: **todas as verificações do batch anterior com status OK**.

**Prompt padrão para disparar cada batch no Antigravity:**

> Execute o [Batch X — Nome]. Fonte de verdade: `docs/prd-backend.md`. Regras obrigatórias: `docs/securitycoderules.md`. Arquitetura: `docs/fbr-arquitetura.md`. Critério de conclusão: todas as verificações da tabela do batch passando. Não avançar para o próximo batch sem verificação OK em todas as tasks.

---

## Visão Geral dos Batches

| Batch | Nome | Período | Objetivo |
|-------|------|---------|----------|
| Batch 1 | Fundação | Dias 1–7 | VPS, Docker, Tailscale, PostgreSQL, Nginx |
| Batch 2 | Database | Dias 7–12 | Schema, RLS, Triggers, Indexes, Seed |
| Batch 3 | Backend Core | Dias 12–22 | FastAPI, LLM cascade, Webhooks, Audit log |
| Batch 4 | OpenClaw Agents | Dias 22–35 | 13 agentes configurados e registrados no FBR-Click |
| Batch 5 | Postal + Aquecimento | Dias 35–42 | Mail server, SPF/DKIM/DMARC, fase 1 de aquecimento |
| Batch 6 | Frontend Dashboard | Dias 35–45 | Next.js, iron-session, 6 páginas com design system |
| Batch 7 | Integração FBR-Click | Dias 45–52 | Handoff de SQLs, feedback loop, relatórios |
| Batch 8 | Produção e Entrega | Dias 52–60 | Grafana, backup, testes de carga e fallback |

> Batches 5 e 6 podem rodar em paralelo a partir do Dia 35.

---

## Batch 1 — Fundação
**Período:** Dias 1–7  
**Objetivo:** Infraestrutura base operacional — VPS, containers, rede Tailscale e banco de dados prontos

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 1.1 | Provisionar VPS Hetzner (8 vCores / 32GB / 200GB NVMe · Ubuntu 24.04) | — | SSH funciona. `df -h` mostra 200GB disponível. |
| 1.2 | Instalar Docker + Docker Compose na VPS | — | `docker --version` e `docker compose version` retornam sem erro. |
| 1.3 | Configurar Tailscale na VPS e no Mac Mini M4 — garantir visibilidade mútua | — | `ping [IP-tailscale-mac-mini]` responde da VPS. |
| 1.4 | Testar Ollama no Mac Mini via Tailscale | `app/core/llm.py` | `curl http://[tailscale-ip]:11434/api/tags` retorna lista de modelos com status 200. |
| 1.5 | Criar `docker-compose.yml` com serviços: postgres, redis, fastapi, n8n, nginx | `docker-compose.yml` | `docker compose up -d` sobe todos os containers sem erro. |
| 1.6 | Configurar PostgreSQL 16 com extensões `uuid-ossp` + `pg_cron` | `app/core/database.py` | `SELECT gen_random_uuid()` retorna UUID válido no psql. |
| 1.7 | Criar `.env` e `.env.example` com todas as variáveis documentadas (Seção 7.5 PRD Backend) | `.env` · `.env.example` | FastAPI inicia sem erros de variável faltando. |
| 1.8 | Configurar Nginx como proxy reverso com SSL (Certbot) | `nginx/default.conf` | `https://leads.fbr.internal` retorna 200 do health check. |

---

## Batch 2 — Database
**Período:** Dias 7–12  
**Objetivo:** Schema completo, RLS em todas as tabelas, triggers, indexes e seed de dados iniciais

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 2.1 | Executar SQL de criação de todas as tabelas (Seção 3.2 PRD Backend) | `docs/prd-backend.md` | `\dt` no psql lista todas as tabelas criadas. |
| 2.2 | Aplicar RLS em todas as tabelas (Seção 3.3 PRD Backend) | `docs/prd-backend.md` | `SELECT * FROM leads` com user diferente retorna 0 rows. |
| 2.3 | Criar triggers `updated_at` e `pg_cron` para reset de `sends_today` (Seção 3.4) | `docs/prd-backend.md` | `UPDATE` em leads atualiza `updated_at` automaticamente. |
| 2.4 | Criar todos os indexes de performance (Seção 3.4 PRD Backend) | `docs/prd-backend.md` | `EXPLAIN ANALYZE` em query de leads usa index (não seq scan). |
| 2.5 | Seed: criar workspace de teste + domínio de teste + ICP de teste | `app/core/database.py` | `SELECT count(*) FROM workspaces` retorna 1. |

---

## Batch 3 — Backend Core
**Período:** Dias 12–22  
**Objetivo:** FastAPI funcional com todos os endpoints, LLM cascade testado e audit log operacional

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 3.1 | FastAPI app factory com lifespan (startup/shutdown de conexões) | `app/main.py` | `GET /health` retorna `{status: ok, llm_layer: 1}`. |
| 3.2 | `app/core/llm.py` com cascade Ollama→Claude→GPT-4o e health check publicado no Redis | `app/core/llm.py` | Desligar Ollama → redireciona para Claude automaticamente em ≤ 30s. |
| 3.3 | Middleware JWT para agentes (header `X-Agent-Id` obrigatório em todas as rotas) | `app/core/security.py` | Sem header → 401. Token válido → passa. |
| 3.4 | Domínios: CRUD + service de saúde + dispatcher básico | `app/domains/` | `POST` cria domínio. `GET` retorna lista com métricas. |
| 3.5 | Leads: ingest em batch + enrichment pipeline + scorer | `app/leads/` | `POST /ingest` aceita array. Score calculado via Ollama. |
| 3.6 | Campaigns: criação + writer (Claude API) + dispatcher | `app/campaigns/` | `POST` cria campanha. Writer gera e-mail personalizado via Claude. |
| 3.7 | Webhook Postal (bounce/abertura/clique) com validação HMAC-SHA256 | `app/webhooks/postal.py` | Secret correto → lead atualizado. Secret errado → 403. |
| 3.8 | Webhook FBR-Click (deal.won/lost) com validação HMAC-SHA256 | `app/webhooks/fbr_click.py` | Feedback `deal.won` → `intelligence_reports` atualizado. |
| 3.9 | `action_logger.py` como wrapper para toda ação de agente (audit log append-only) | `app/agents/action_logger.py` | Após ação de agente, `count(*)` em `agent_action_logs` cresce. Nenhum DELETE funciona na tabela. |

---

## Batch 4 — OpenClaw Agents
**Período:** Dias 22–35  
**Objetivo:** 13 agentes configurados com os 7 Markdowns, aprovados via PR e operacionais no FBR-Click

> **⚠️ Lembrete obrigatório (Bíblia FBR):** Cada agente precisa dos **7 Markdowns** versionados em Git: `SOUL.md` · `IDENTITY.md` · `TASKS.md` · `AGENTS.md` · `MEMORY.md` · `TOOLS.md` · `USER.md`. Pull Request obrigatório antes de ativar. Período de observação de 7 dias com kill switch pronto.

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 4.1 | Configurar OpenClaw Gateway no docker-compose (porta 3500) | `docker-compose.yml` | `curl localhost:3500/health` retorna `{status: ok}`. |
| 4.2 | Criar repositório Git e 7 Markdowns para os 4 Guardiões do Mail Server | `agents/guardiao-dominios/` | Agentes registrados no FBR-Click com badge 🤖. |
| 4.3 | Criar e registrar Garimpeiro LinkedIn + testar coleta via Apify | `agents/garimpeiro-linkedin/` | Heartbeat a cada 2h insere leads na tabela `leads`. |
| 4.4 | Criar e registrar Garimpeiro CNPJ + testar consulta à Receita Federal | `agents/garimpeiro-cnpj/` | Lead com CNPJ tem campos `company_*` preenchidos após enriquecimento. |
| 4.5 | Criar e registrar Analista Enriquecedor + Validador de E-mail (ZeroBounce) | `agents/analista-enriquecedor/` | Lead com e-mail inválido → `funnel_stage='discard'` automaticamente. |
| 4.6 | Criar e registrar Scorer + testar pipeline completo de qualificação | `agents/scorer/` | Lead recebe score 0-100. Log mostra qual camada LLM foi usada. |
| 4.7 | Criar e registrar Redator Principal + Revisor + Testador A/B | `agents/redator-principal/` | E-mail gerado sem links, sem spam words. 2 variações de assunto. |
| 4.8 | Criar e registrar Dispatcher + Monitor de Respostas + Agendador | `agents/cadenciador/` | Dispatcher respeita `daily_limit`. Resposta positiva aciona handoff. |
| 4.9 | Criar e registrar os 4 agentes do Time de Inteligência | `agents/inteligencia/` | Heartbeat domingo 18h UTC-5 gera relatório e posta no FBR-Click. |

---

## Batch 5 — Postal + Aquecimento
**Período:** Dias 35–42  
**Objetivo:** Mail server ativo com domínios configurados e iniciando fase 1 de aquecimento

> Pode rodar em paralelo com o Batch 6 a partir do Dia 35.

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 5.1 | Instalar e configurar Postal no docker-compose com banco dedicado | `docker-compose.yml` | Interface web do Postal acessível. API key funcional. |
| 5.2 | Migrar domínios existentes para o Postal + verificar SPF/DKIM/DMARC | — | MXToolbox mostra todos os registros DNS como **PASS** para cada domínio. |
| 5.3 | Ativar Guardiões + iniciar fase 1 de aquecimento (e-mails internos entre contas do sistema) | `agents/guardiao-dominios/` | Domínios em fase 1 trocando e-mails internos. Dashboard mostra `warm_phase=1`. |
| 5.4 | Configurar alerta automático: bounce > 2% pausa domínio e notifica no FBR-Click | `app/domains/service.py` | Simular bounce alto → domínio pausado + mensagem no canal `#leads-qualificados`. |

---

## Batch 6 — Frontend Dashboard
**Período:** Dias 35–45  
**Objetivo:** Dashboard completo com design system FBR, iron-session e todas as páginas funcionais

> **Design System:** Seguir `DESIGN_STANDARDS.md` rigorosamente: fontes **Inter** (corpo) + **Outfit** (títulos), dark mode `#101622`, primary `#EA580C`.  
> Pode rodar em paralelo com o Batch 5 a partir do Dia 35.

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 6.1 | Criar projeto Next.js 15 com TypeScript strict + Tailwind v4 + shadcn/ui | `package.json` · `tsconfig.json` | `npx tsc` sem erros. `npm run dev` sobe na porta 3000. |
| 6.2 | Implementar iron-session: login, logout, middleware de proteção de rotas | `app/api/auth/` · `middleware.ts` · `lib/session.ts` | Rota protegida sem cookie → redireciona para `/login`. |
| 6.3 | Implementar proxy Next.js: todas as chamadas ao FastAPI via `/api/proxy` | `app/api/proxy/[...path]/route.ts` | Fetch direto ao FastAPI → 401. Via proxy com cookie → 200. |
| 6.4 | Configurar fontes Inter + Outfit no `layout.tsx` conforme DESIGN_STANDARDS.md | `app/layout.tsx` · `globals.css` | Inspecionar: `body` usa Inter, `h1`/`h2` usam Outfit. Dark mode ativo (`#101622`). |
| 6.5 | Página: Dashboard de saúde dos domínios com atualização via WebSocket | `app/dashboard/domains/page.tsx` | Bounce de domínio muda status em tempo real sem refresh. |
| 6.6 | Página: Pipeline de leads com funil e filtros por stage/score/campanha | `app/dashboard/leads/page.tsx` | Filtro por score > 70 retorna apenas leads qualificados. |
| 6.7 | Página: Configuração de ICP no-code com formulário completo | `app/dashboard/icp/page.tsx` | Criar ICP → Garimpeiros iniciam coleta em até 30 minutos. |
| 6.8 | Página: Status dos agentes com logs em tempo real (SSE) + kill switch | `app/dashboard/agents/page.tsx` | Agente offline → badge vermelho. Kill switch funcional com confirmação. |
| 6.9 | Página: Relatórios executivos com exportação CSV | `app/dashboard/reports/page.tsx` | Relatório semanal exibido. Botão Export gera CSV válido. |

---

## Batch 7 — Integração FBR-Click
**Período:** Dias 45–52  
**Objetivo:** SQLs chegando no FBR-Click com contexto completo e feedback loop operacional

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 7.1 | Registrar Cadenciador Bot no FBR-Click com permissão no canal `#leads-qualificados` | `agents/cadenciador/` · FBR-Click admin | Bot aparece na sidebar do FBR-Click com badge 🤖. |
| 7.2 | Implementar handoff completo: SQL gerado → deal criado no FBR-Click → @menção ao vendedor | `app/campaigns/dispatcher.py` | SQL de teste aparece como deal com todos os campos do payload (Seção 8.2 PRD Backend). |
| 7.3 | Implementar recebimento de feedback deal.won/lost → retroalimentar Time 6 | `app/webhooks/fbr_click.py` · `app/intelligence/service.py` | Fechar deal no FBR-Click → `intelligence_reports` atualizado em ≤ 5 min. |
| 7.4 | Configurar canal `#leads-report` no FBR-Click para relatórios semanais do Time 6 | `agents/inteligencia/TASKS.md` | Relatório de teste postado manualmente aparece com formatação correta. |

---

## Batch 8 — Produção e Entrega
**Período:** Dias 52–60  
**Objetivo:** Sistema em produção com monitoring, backup, testes de carga e handoff para o time

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 8.1 | Configurar Grafana + Prometheus: dashboards de infra (CPU, RAM, Redis, Postgres) | `docker-compose.yml` | Grafana acessível. Métricas de todos os containers visíveis. |
| 8.2 | Configurar backup automático do PostgreSQL para storage externo (diário às 3h UTC) | `scripts/backup.sh` · cron | Simular restore a partir do backup gerado. Dados íntegros. |
| 8.3 | Teste de carga: 1000 leads ingeridos em batch — verificar performance e filas | — | 1000 leads enriquecidos e scorados em < 30min. Zero erros no audit log. |
| 8.4 | Teste de fallback LLM: desligar Mac Mini → verificar redirecionamento para Claude API | — | Dashboard mostra `"LLM Layer: 2 (fallback)"`. Operação contínua sem interrupção. |
| 8.5 | Documentação do README: features, fluxo de operação, como criar um ICP, como interpretar o dashboard | `README.md` | README revisado pelo gestor do projeto e aprovado. |
| 8.6 | Handoff para o time: demonstração de kill switches, fallbacks e procedimentos de emergência | — | Todos os owners sabem: como pausar agentes, verificar logs e acionar fallback manual. |

---

## Milestones

| Dia | Marco | Critério de Sucesso |
|-----|-------|---------------------|
| Dia 7 | Infraestrutura pronta | VPS, Docker, Tailscale e Postgres funcionais. Ollama respondendo via Tailscale. |
| Dia 12 | Database completo | Todas as tabelas criadas, RLS aplicado, indexes criados e seed executado. |
| Dia 22 | Backend operacional | Todos os endpoints FastAPI respondendo. LLM cascade testado. Audit log funcionando. |
| Dia 35 | Agentes ativos | 13 agentes registrados no FBR-Click e executando heartbeats sem erro. |
| Dia 42 | Mail server ativo | Postal configurado, domínios em fase 1 de aquecimento, SPF/DKIM/DMARC validados. |
| **Dia 45** | 🎯 **Primeiros SQLs** | **Primeiros leads qualificados chegando no FBR-Click via Cadenciador Bot.** |
| Dia 52 | Frontend completo | Dashboard com todas as páginas funcionais, WebSocket e SSE ativos. |
| **Dia 60** | 🚀 **MVP entregue** | **Sistema em produção, monitoring ativo, backup configurado, handoff realizado.** |

---

## Referências

- PRD Backend completo: `docs/prd-backend.md`
- PRD Frontend completo: `docs/prd-frontend.md`
- Arquitetura e pressupostos: `docs/fbr-arquitetura.md`
- Regras de segurança e código: `docs/securitycoderules.md`
- Padrões visuais: `docs/DESIGN_STANDARDS.md`

---

*FBR-Leads · Plano de Implementação v2.0 · Fevereiro 2026 · Facebrasil · Confidencial*
