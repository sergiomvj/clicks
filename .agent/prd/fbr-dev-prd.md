
FBR-DEV Plataforma de Desenvolvimento de Sistemas — GitHub × Slack × OpenClaw
Especificação Técnica Completa — Facebrasil · v1.0 · Fevereiro 2026
⚙️ O que é o FBR-DEV?
FBR-DEV é a plataforma de gestão de desenvolvimento de sistemas do Facebrasil. Une GitHub Projects (gestão de issues e sprints), Slack (comunicação do time), e agentes autônomos OpenClaw (execução, revisão, monitoramento e alertas) num único workspace onde devs humanos, contractors e agentes convivem. Princípio central: "Todo código nasce de uma conversa. Todo deploy gera uma notificação." Diferença em relação ao FBR-Click:   • FBR-Click → gestão de marketing e vendas (times comerciais)   • FBR-DEV   → gestão de desenvolvimento de sistemas (times técnicos)   • Ambos compartilham a mesma arquitetura OpenClaw, os mesmos     conceitos de Shared Resources e capacidades cross-domain.     O FBR-DEV é o "irmão técnico" do FBR-Click.

PARTE 1 — VISÃO GERAL DO SISTEMA
1.1 Stack Tecnológico
Camada	Tecnologia	Justificativa
Frontend	Next.js 14 (App Router) + TypeScript	SSR, performance, integração com Vercel/Coolify
Backend API	tRPC + Fastify	Type-safety end-to-end, sem overhead de REST convencional
Banco de dados	PostgreSQL (Supabase) + Row Level Security	Multi-tenant seguro, real-time subscriptions nativas
Cache / Filas	Redis + BullMQ	Filas de webhook, jobs de CI/CD, notificações assíncronas
Real-time	Socket.io + Redis Pub/Sub	Notificações de PR, deploy e alertas em tempo real
Agentes	OpenClaw Gateway (Node.js)	Mesmo padrão do FBR-Click — agentes autônomos
Auth	NextAuth.js + GitHub OAuth	Login com conta GitHub — natural para devs
Deploy	Coolify (self-hosted) + Docker Compose	VPS próprio do Facebrasil, sem vendor lock-in
CI/CD	GitHub Actions	Nativo ao GitHub, integração direta com Projects
Monitoramento	Sentry + Grafana + Prometheus	Errors, métricas de infra e performance
Comunicação	Slack (primário) + WhatsApp + Telegram	Slack para time técnico, WhatsApp/Telegram para alertas críticos
Gestão externa	GitHub Projects (nativo) + Linear (opcional)	Kanban de issues diretamente no GitHub
1.2 Tipos de Membros no FBR-DEV
Tipo	Quem é	Autenticação	Permissões padrão	Interface principal
Admin	Tech Lead / CTO	GitHub OAuth + 2FA	Total — configura agentes, approva deploys em prod	FBR-DEV Web + Slack
Dev Humano	Desenvolvedor interno	GitHub OAuth	Cria issues, PRs, reviews, configura CI/CD	VS Code + GitHub + Slack
Contractor	Dev externo / freelancer	GitHub OAuth (repo específico)	Scope limitado: apenas repos atribuídos	GitHub + Slack (canal dedicado)
Agente OpenClaw	Bot autônomo configurado	JWT rotacionado 24h	Definido em AGENTS.md do agente	API FBR-DEV + GitHub API + Slack API
1.3 Os 4 Fluxos Centrais
Equivalentes ao fluxo Mensagem→Tarefa do FBR-Click. Cada fluxo é um ciclo completo com entrada, processamento por agentes, e entrega verificável.
📋 Issue → PR → Merge Fluxo de feature	🚀 Commit → Deploy → Monitor Fluxo de entrega	🐛 Bug → Triage → Fix → Close Fluxo de correção	📅 Sprint → Daily → Retro Fluxo de gestão

PARTE 2 — ARQUITETURA DE MICROSSERVIÇOS
2.1 Microsserviços do FBR-DEV
Serviço	Responsabilidade	Tecnologia	Comunica com
gateway-service	API gateway, auth, rate limiting, roteamento	Fastify + JWT	Todos os serviços internos
github-service	Webhook receiver do GitHub, sincroniza issues/PRs/commits	Node.js + Octokit	issue-service, pr-service, deploy-service
issue-service	CRUD de issues, labels, milestones, assignments	tRPC + PostgreSQL	github-service, sprint-service, agent-service
pr-service	Pull requests, reviews, checks de CI, merge rules	tRPC + PostgreSQL	github-service, deploy-service, agent-service
deploy-service	Pipelines de deploy, ambientes, rollback, status	Node.js + BullMQ	github-service, monitoring-service, notify-service
sprint-service	Sprints, planning, burndown, velocity, retrospectiva	tRPC + PostgreSQL	issue-service, agent-service
monitoring-service	Integração Sentry + Grafana + Prometheus, alertas	Node.js + Redis	deploy-service, agent-service, notify-service
notify-service	Despacha notificações: Slack, WhatsApp, Telegram, email	Node.js + BullMQ	Todos os serviços, agent-service
agent-service	Gerencia agentes OpenClaw: registro, markdowns, lifecycle	Node.js + PostgreSQL	github-service, issue-service, deploy-service
shared-sync	Sincroniza Shared Resources do Git para o VPS	Node.js + simple-git	agent-service, filesystem VPS
2.2 Modelo de Dados Central
| ENTIDADES PRINCIPAIS WORKSPACE id, name, github_org, slack_workspace_id github_app_id, github_installation_id REPOSITORY id, workspace_id, github_repo_id, name default_branch, environments[], slack_channel_id ISSUE id, repo_id, github_issue_number, title type: feature|bug|chore|spike status, priority, assignee_ids[], sprint_id labels[], estimate_points, linked_pr_id PULL_REQUEST id, repo_id, github_pr_number, title status: draft|open|review|approved|merged|closed author_id, reviewer_ids[], linked_issue_id ci_status, checks_passed, deploy_blocked | ENTIDADES DE PROCESSO DEPLOY id, repo_id, pr_id, environment status: queued|building|deploying|live|failed|rolled_back commit_sha, triggered_by (user|agent|ci) started_at, finished_at, duration_sec SPRINT id, workspace_id, name, goal start_date, end_date, status velocity_planned, velocity_delivered INCIDENT id, repo_id, severity: P0|P1|P2|P3 source: sentry|grafana|manual|agent status: open|investigating|resolved linked_issue_id, timeline: Event[] AGENT (herdado do FBR-Click) id, workspace_id, name, git_repo_url scope: repos[], channels[], permissions[] model_primary, heartbeat_interval_min |
| :---- | :---- |
PARTE 3 — OS 4 FLUXOS CENTRAIS DETALHADOS
3.1 Fluxo 1: Issue → Pull Request → Review → Merge
O ciclo de vida de uma feature ou bug fix, do problema até o código em produção.
Passo	Ator	Ação	FBR-DEV registra	Agente age
1	Dev humano	Cria issue no GitHub Projects ou via /issue no Slack	ISSUE criada, vinculada ao sprint ativo	Triage Bot avalia prioridade e sugere label
2	Dev Bot (agente)	Se issue for bem definida e estimável, cria branch padrão	Branch feat/issue-{n}-{slug} criada	Dev Bot notifica no Slack: "Branch pronta para desenvolvimento"
3	Dev humano / Contractor	Desenvolve, commita, abre Pull Request	PR criado, vinculado à issue, status: draft	Review Bot analisa diff e posta comentário inicial no PR
4	Review Bot	Analisa PR: complexidade, testes, padrões de código	PR status: open, checks iniciados	Posta checklist de review no PR e notifica reviewers no Slack
5	Dev humano revisor	Faz code review, aprova ou pede mudanças	PR status: approved/changes_requested	Review Bot resume o feedback e atualiza issue vinculada
6	CI/CD (GitHub Actions)	Roda testes, lint, build	PR checks_passed: true/false	Deploy Bot alerta no Slack se CI falhar com link para logs
7	Tech Lead (admin)	Aprova merge para main/production	PR status: merged, issue: done	Deploy Bot inicia pipeline de deploy automaticamente
8	Deploy Bot	Monitora deploy, verifica health check	DEPLOY status: live	Notifica Slack: "Deploy #n concluído em X seg — tudo verde ✅"
3.2 Fluxo 2: Commit → Deploy → Monitor → Alertar
O ciclo de entrega contínua — do código commitado até o monitoramento em produção.
| ⚡ TRIGGER: Push para branch main (ou tag de release) PASSO 1 — github-service recebe webhook push:    Registra commit: sha, author, message, files_changed    Verifica: é merge de PR aprovado? É tag de release?    Se sim → emite evento deploy.triggered PASSO 2 — deploy-service inicia pipeline:    Enfileira job no BullMQ: build → test → deploy → health_check    Notifica Slack #deploys: "🚀 Deploy iniciado: [repo] → [env] por [author]" PASSO 3 — GitHub Actions executa:    Build Docker image → push registry → deploy no Coolify    Status em tempo real via GitHub API → FBR-DEV via webhook PASSO 4 — Deploy Bot monitora:    Health check a cada 30s por 5 minutos pós-deploy    Verifica: HTTP 200, response time < 2s, error rate < 1% 🟢 SUCESSO:    Slack #deploys: "✅ Deploy concluído — [repo] v[version] em prod"    "⏱ Build: 2m14s | Deploy: 45s | Health check: OK"    Issue(s) vinculadas ao PR marcadas como Done no GitHub Projects 🔴 FALHA:    Deploy Bot inicia rollback automático para versão anterior    Abre INCIDENT P1 automaticamente    Notifica Slack + WhatsApp do Tech Lead    Cria issue de bug vinculada ao commit problemático 📋 MONITORAMENTO CONTÍNUO (pós-deploy):    Monitor Bot verifica Sentry a cada 5 min    Verifica Grafana: CPU, memória, latência, error rate    Se threshold cruzado → INCIDENT aberto automaticamente |
| :---- |
3.3 Fluxo 3: Bug Report → Triage → Fix → Test → Close
O ciclo de correção de bugs — do reporte até a verificação em produção.
Passo	Ator	Ação	FBR-DEV	Agente
1 — Report	Qualquer membro / Sentry automático	Descreve bug no Slack ou abre issue no GitHub	ISSUE criada: type=bug, status=open	Triage Bot coleta: severidade, reprodução, ambiente
2 — Triage	Triage Bot + Tech Lead	Classifica: P0 crítico	P1 alto	P2 médio
3 — Investigação	Dev assignado	Investiga, identifica root cause, comenta na issue	ISSUE status: investigating	Debug Bot busca logs no Sentry + Grafana e posta contexto na issue
4 — Fix	Dev assignado	Cria branch bug/issue-{n}, desenvolve correção	PR criado: type=bugfix, urgency baseada na prioridade	Review Bot aplica checklist específica de bugfix (regressão, edge cases)
5 — Test	Dev + Review Bot	Review do fix, CI passa, testes de regressão	PR checks_passed, review aprovado	Review Bot verifica se o bug original está coberto por teste
6 — Deploy	Deploy Bot	Merge e deploy com prioridade (P0/P1 = deploy imediato)	DEPLOY urgente para produção	Deploy Bot monitora por 15 min extra após bugfix deploy
7 — Verificação	Monitor Bot + Reporter	Confirma que erro sumiu do Sentry, métricas normais	INCIDENT status: resolved, ISSUE: done	Monitor Bot posta post-mortem automático para P0/P1
3.4 Fluxo 4: Sprint Planning → Daily Standup → Retrospectiva
O ciclo de gestão ágil — automatizado por agentes mas centrado em decisões humanas.
SPRINT PLANNING (início do sprint) Agente: Sprint Bot Segunda-feira 9h: posta no Slack #dev-geral o board do sprint Lista issues do backlog ordenadas por prioridade Calcula velocity disponível baseado no histórico Sugere issues para o sprint baseado em prioridade × estimativa Tech Lead confirma o scope — Sprint Bot fecha o planning DAILY STANDUP (todo dia útil) Agente: Standup Bot 9h30: coleta status de todos os PRs abertos Identifica blockers: PRs sem review há +24h, CI falhando Posta resumo estruturado no Slack: O que foi feito / O que vem / Blockers Marca @menção nos responsáveis por blockers Devs confirmam ou corrigem o resumo em thread	RETROSPECTIVA (fim do sprint) Agente: Retro Bot Sexta último dia do sprint: compila métricas do sprint Velocity planejado vs. entregue Issues abertas vs. fechadas vs. carry-over Deploys bem-sucedidos vs. com rollback Bugs abertos no período PRs: tempo médio de review, tempo médio de merge Posta relatório completo no Slack + abre thread para discussão MÉTRICAS AUTOMÁTICAS Lead time: issue criada → merged Cycle time: PR aberto → merged Deployment frequency: deploys por semana MTTR: tempo médio de resolução de incidents Change failure rate: % de deploys que geraram rollback

PARTE 4 — AGENTES OPENCLAW DO FBR-DEV
Seis agentes especializados, cada um com seus 7 markdowns no Git. Todos herdam dos Shared Resources do FBR-DEV e seguem a mesma arquitetura do FBR-Click.
4.1 Catálogo de Agentes
Agente	Domínio	Gatilhos principais	Autonomia máxima sem aprovação
Triage Bot 🏷️	Classificação de issues e bugs	issue.created, sentry.error_new, mention	Aplicar labels, assignar issues, abrir incidente P2/P3
Review Bot 👁️	Code review e qualidade	pr.opened, pr.updated, pr.review_requested	Postar comentários de review, aprovar PRs simples (<50 linhas)
Deploy Bot 🚀	Pipeline de deploy e rollback	pr.merged, tag.created, deploy.failed	Deploy em staging, rollback automático em falha
Monitor Bot 📡	Observabilidade e alertas	sentry.error, grafana.alert, cron (5min)	Abrir incidente, notificar Slack, criar issue de bug
Standup Bot 📅	Gestão de sprint e cerimônias	cron (daily 9h30), sprint.started, sprint.ended	Gerar e postar relatórios, fechar sprint, criar próximo
Debug Bot 🐛	Investigação de bugs e incidentes	incident.opened, issue.assigned (type=bug), mention	Coletar logs, buscar contexto, postar análise na issue
4.2 SOUL.md e AGENTS.md — Exemplos por Agente
Triage Bot
# SOUL.md — Triage Bot / FBR-DEV ## Identidade Sou o guardião da qualidade das issues do FBR-DEV. Minha função é garantir que nenhuma issue fique sem classificação, prioridade ou responsável por mais de 30 minutos. ## Tom - Objetivo e direto: sem texto desnecessário - Técnico mas acessível: contractors também me lêem - Sempre incluo: severidade, contexto, próximo passo sugerido ## Restrições absolutas - Nunca fechar uma issue sem confirmação humana - Nunca abrir incidente P0/P1 sem notificar Tech Lead imediatamente - Nunca assignar contractor a issue fora do seu repo autorizado - Prioridade P0: sempre acorda o Tech Lead (WhatsApp), independente do horário

# AGENTS.md — Triage Bot (trecho) scope:   repos: all                    # acesso a todos os repos do workspace   slack_channels: [dev-geral, incidents, bugs] shared_resources:   skills: [analise-issue, classificacao-bug, estimativa-pontos]   hooks: [on-issue-created, on-sentry-error, on-incident-opened]   scripts: [python/issue_classifier.py, python/severity_scorer.py]   connectors: [sentry, github-issues]   mcp: [fbr-dev-mcp, github-mcp, sentry-mcp] autonomy:   can_apply_labels: true   can_assign_issues: true   can_open_incident: [P2, P3]   # P0/P1 requerem aprovação humana   can_close_issue: false   requires_approval: [P0, P1, close_issue, delete_branch]
Deploy Bot
# SOUL.md — Deploy Bot / FBR-DEV ## Identidade Sou o responsável pela saúde dos deploys do Facebrasil. Monitoro cada pipeline, reajo imediatamente a falhas, e mantenho o time informado em tempo real. ## Regras de deploy - Staging: deploy automático em qualquer PR merged para develop - Production: apenas PR merged para main com aprovação do Tech Lead - Hotfix: PR com label "hotfix" pode ir direto para prod com aprovação - Rollback: automático se health check falhar por 3 tentativas consecutivas ## Restrições absolutas - Nunca fazer deploy em produção sem aprovação humana explícita - Nunca ignorar falha de CI — deploy bloqueado até CI verde - Se rollback em produção: SEMPRE notificar Tech Lead via WhatsApp - Janela de silêncio para deploys: 23h-7h EST (apenas hotfixes P0)
4.3 Os 7 Markdowns no Contexto de Dev
Arquivo	No FBR-Click era...	No FBR-DEV é...	Exemplo de conteúdo específico
SOUL.md	Tom comercial, regras de pipeline CRM	Tom técnico, regras de CI/CD e qualidade de código	Padrões de nomenclatura, regras de merge, política de rollback
IDENTITY.md	Agente comercial com goals de vendas	Agente técnico com goals de qualidade e entrega	SLA de review, targets de lead time, DORA metrics goals
TASKS.md	Triggers de deal, follow-up de clientes	Triggers de PR, deploy, sentry error, cron de sprint	On PR opened: checklist; On deploy failed: rollback + notificar
AGENTS.md	Scope de canais de vendas	Scope de repos, branches, environments	repos: [fbr-click, fbr-dev], branches: [main, develop], env: [prod, staging]
MEMORY.md	Histórico de clientes e deals	Histórico de decisões técnicas, bugs recorrentes, padrões	Issue #234 era falso positivo no Sentry; PR review: prefere comentários inline
TOOLS.md	Actions do CRM, WhatsApp Business	GitHub API, Sentry API, Coolify API, Slack API	fbr_create_pr_comment, fbr_trigger_deploy, fbr_open_incident
USER.md	Contexto do time de vendas	Contexto do time de dev: stack, convenções, preferências	Commits: conventional commits; branches: feat/fix/chore/; PR: squash merge only

PARTE 5 — SHARED RESOURCES DO FBR-DEV
Mesma arquitetura do FBR-Click: repositório Git separado (fbr-dev-shared), espelhado no VPS em /opt/fbr-dev/shared/. Agentes declaram dependências no AGENTS.md.
5.1 COMMANDS — Comandos Slash para Times de Dev
Comando	Onde usar	O que faz	Agente executor
/issue [título]	Slack	Cria issue no GitHub Projects com título e tipo inferido	Triage Bot
/pr [número]	Slack	Resume o estado atual de um PR: checks, reviewers, blockers	Review Bot
/deploy [repo] [env]	Slack	Solicita deploy manual em ambiente específico (requer aprovação)	Deploy Bot
/status [repo]	Slack	Status atual: último deploy, incidents abertos, CI status	Monitor Bot
/sprint	Slack	Resume o sprint atual: progresso, blockers, burndown	Standup Bot
/bug [descrição]	Slack	Abre bug report rápido com triage automática	Triage Bot
/incident [severidade]	Slack	Abre incident manualmente: P0/P1/P2/P3	Monitor Bot
/review [pr-número]	Slack / GitHub	Solicita review do Review Bot para um PR específico	Review Bot
/rollback [repo]	Slack	Solicita rollback do último deploy (requer aprovação Tech Lead)	Deploy Bot
/retro	Slack	Gera relatório de retrospectiva do sprint atual	Standup Bot
/debug [issue-número]	Slack	Debug Bot coleta contexto completo de uma issue/bug	Debug Bot
/daily	Slack	Força geração do standup imediatamente (fora do horário)	Standup Bot
5.2 SKILLS — Capacidades Especializadas de Dev
Skill	Ensina o agente a...	Input	Output	cross_domain
analise-pr	Revisar PRs: complexidade, riscos, padrões, cobertura de testes	diff do PR + histórico do repo	Checklist de review com comentários por arquivo	Não
classificacao-bug	Classificar bugs por severidade, impacto e urgência	Descrição do bug + stack trace	Prioridade P0-P3 com justificativa	Não
estimativa-pontos	Estimar story points baseado em complexidade e histórico	Título + descrição da issue	Story points sugeridos (1/2/3/5/8/13) com raciocínio	Não
post-mortem	Escrever post-mortem técnico de incidents P0/P1	Timeline do incident + métricas	Documento post-mortem estruturado	Não
release-notes	Gerar release notes a partir de PRs merged	Lista de PRs do período	Release notes por categoria: features, fixes, breaking changes	Sim
analise-performance	Interpretar métricas de Grafana/Sentry e recomendar ações	Dashboard data + error logs	Análise com recomendações priorizadas	Sim — cross para Comercial/Content
documentacao-tecnica	Gerar documentação de API e README a partir do código	Código fonte + comentários	Markdown de documentação estruturada	Sim
5.3 HOOKS — Encadeamento de Eventos de Dev
Hook	Evento disparador	Agentes envolvidos	Sequência
on-pr-opened	pull_request.opened	Review Bot	Review Bot analisa diff → posta checklist → notifica reviewers
on-ci-failed	check_suite.completed (failed)	Review Bot + Deploy Bot	Deploy Bot bloqueia merge → Review Bot posta link para logs no PR
on-pr-merged	pull_request.merged	Deploy Bot + Standup Bot	Deploy Bot inicia pipeline → Standup Bot atualiza burndown do sprint
on-deploy-failed	deploy.failed	Deploy Bot + Monitor Bot + Triage Bot	Deploy Bot faz rollback → Monitor Bot abre incident → Triage Bot cria issue
on-sentry-error	sentry.error_new (threshold)	Monitor Bot + Triage Bot	Monitor Bot avalia severidade → Triage Bot abre issue com contexto completo
on-issue-created	issues.opened	Triage Bot	Triage Bot classifica tipo, prioridade, assignee sugerido
on-sprint-ended	sprint.end_date_reached	Standup Bot + Triage Bot	Standup Bot gera retro → Triage Bot move issues abertas para backlog
on-pr-stale	pr.no_activity_48h	Review Bot + Standup Bot	Review Bot pinga reviewers → Standup Bot marca como blocker no daily
on-incident-resolved	incident.status=resolved	Monitor Bot + Debug Bot	Debug Bot gera post-mortem → Monitor Bot fecha incident e notifica time
5.4 CONNECTORS — Integrações Externas
Connector	Serviço	Auth	Funções principais para agentes
github	GitHub API v4 (GraphQL) + v3 (REST)	GitHub App (installation token)	create_issue, create_pr_comment, get_pr_diff, trigger_workflow, get_checks
sentry	Sentry API v0	Auth Token	get_issues, get_events, resolve_issue, get_stacktrace, query_performance
slack	Slack Web API + Events API	Bot Token + Signing Secret	post_message, reply_thread, add_reaction, create_channel, get_channel_history
coolify	Coolify API v1	API Key	trigger_deploy, get_deploy_status, rollback, get_logs, get_environments
grafana	Grafana HTTP API	API Key	query_metrics, get_dashboard, create_annotation, get_alerts
whatsapp	WhatsApp Business Cloud API	Bearer Token	send_message (alertas P0/P1 para Tech Lead)
telegram	Telegram Bot API	Bot Token	send_message (canal de alertas críticos)
linear	Linear API (GraphQL)	API Key (opcional)	sync_issues, create_issue, update_status (se Linear ativo)
5.5 MCP — Servidores para Agentes de Dev
MCP	Tools expostas	Agentes que usam
fbr-dev-mcp	create_issue, update_pr_status, open_incident, post_slack, trigger_deploy, get_sprint_data	Todos os agentes
github-mcp	read_file, write_file, commit, list_prs, get_diff, create_branch, merge_pr	Review Bot, Deploy Bot, Debug Bot
sentry-mcp	query_errors, get_traces, resolve_issue, get_performance_metrics	Monitor Bot, Debug Bot, Triage Bot
filesystem-mcp	read_file, write_file (sandbox /tmp), run_script	Debug Bot, Review Bot
browser-mcp	navigate, extract_text, screenshot (para scraping de docs)	Debug Bot (pesquisa de erros externos)
sqlite-mcp	query, insert (cache local de métricas e histórico)	Standup Bot, Monitor Bot

PARTE 6 — INTEGRAÇÕES DETALHADAS
6.1 GitHub Integration — O Centro do FBR-DEV
O GitHub é a fonte da verdade do FBR-DEV. Toda issue, PR, commit, check e deploy parte do GitHub. O FBR-DEV sincroniza em tempo real via GitHub App (webhooks) e GitHub API.
WEBHOOKS RECEBIDOS DO GITHUB issues: opened, edited, labeled, assigned, closed pull_request: opened, synchronize, review_requested, closed, merged pull_request_review: submitted (approved/changes_requested) check_suite: completed (success/failure) check_run: completed push: para branches configuradas create: branch ou tag criada release: published workflow_run: completed (GitHub Actions) projects_v2_item: edited (GitHub Projects card movido)	AÇÕES QUE O FBR-DEV FAZ NO GITHUB Criar e comentar em issues via agentes Postar review comments em PRs Aplicar labels automaticamente Assignar issues baseado em expertise (MEMORY.md) Mover cards no GitHub Projects via API Criar branches com convenção de nomenclatura Triggerar GitHub Actions workflows Criar releases com release notes automáticas Gerenciar milestones e sprints via Projects API
6.2 Slack Integration — A Interface do Time
Slack é onde o time dev vive. O FBR-DEV transforma eventos técnicos em notificações contextuais no Slack, e aceita comandos slash que se transformam em ações no GitHub.
| # Canais Slack do FBR-DEV (criados automaticamente) #dev-geral         → comunicação geral do time dev #deploys           → notificações de todos os deploys (staging + prod) #incidents         → alertas de incidentes P0/P1 + post-mortems #code-review       → notificações de PRs abertos aguardando review #bugs              → issues de bug abertas e atualizações #standup           → daily automático às 9h30 + thread de confirmação #sprint-{n}        → canal dedicado ao sprint ativo #contractors       → canal isolado para contractors (sem acesso ao resto) # Formato padrão de notificação de deploy no Slack: 🚀 Deploy em produção Repo: fbr-click  |  Versão: v2.4.1 Por: @rafael (PR #234 — feat: pipeline cross-domain) Status: ✅ Concluído em 3m42s Health check: OK  |  Error rate: 0.02%  |  P95 latency: 187ms # Formato de alerta P0 (Slack + WhatsApp): 🚨 INCIDENT P0 — fbr-click PRODUÇÃO Error rate: 12.4% (threshold: 1%) Sentry: 847 erros nos últimos 5min Último deploy: v2.4.1 há 8 minutos Ação automática: rollback iniciado para v2.4.0 @tech-lead aprovação necessária para confirmar rollback |
| :---- |
6.3 CI/CD — GitHub Actions + Coolify
# .github/workflows/fbr-dev-pipeline.yml # Template padrão para todos os repos do Facebrasil name: FBR-DEV Pipeline on:   push:     branches: [main, develop]   pull_request:     branches: [main, develop] jobs:   lint-and-test:     runs-on: ubuntu-latest     steps:       - uses: actions/checkout@v4       - name: Setup Node         uses: actions/setup-node@v4         with: { node-version: 20, cache: npm }       - run: npm ci       - run: npm run lint       - run: npm run test       - name: Notify FBR-DEV         uses: facebrasil/fbr-dev-action@v1  # action customizada         with:           event: ci_completed           status: ${{ job.status }}   deploy-staging:     needs: lint-and-test     if: github.ref == refs/heads/develop     runs-on: ubuntu-latest     steps:       - name: Deploy to Coolify (staging)         run: curl -X POST $COOLIFY_WEBHOOK_STAGING         env: { COOLIFY_WEBHOOK_STAGING: ${{ secrets.COOLIFY_WEBHOOK_STAGING }} }   deploy-production:     needs: lint-and-test     if: github.ref == refs/heads/main     environment: production    # requer aprovação manual no GitHub     runs-on: ubuntu-latest     steps:       - name: Deploy to Coolify (prod)         run: curl -X POST $COOLIFY_WEBHOOK_PROD

PARTE 7 — INTERFACE E UX DO FBR-DEV
O FBR-DEV tem interface web complementar ao GitHub e Slack — não substitui, agrega. O dev passa a maior parte do tempo no VS Code, GitHub e Slack. O FBR-DEV é o painel de controle que une tudo.
7.1 Telas Principais
Tela	Propósito	Dados principais	Agentes visíveis
Dashboard	Visão geral do workspace de dev	Deploy recente, incidents abertos, PRs aguardando review, burndown do sprint	Status de todos os agentes ativos
Sprint Board	Kanban do sprint atual (espelho do GitHub Projects)	Issues por stage: Backlog → Todo → In Progress → Review → Done	Standup Bot e Triage Bot como membros do board
Pipeline View	Status de todos os deploys em tempo real	Por ambiente: staging/production — status, logs, métricas pós-deploy	Deploy Bot e Monitor Bot visíveis por deploy
PR Queue	Fila de Pull Requests aguardando ação	Ordenados por urgência: blocked, awaiting review, CI failing	Review Bot com sugestão de próximo PR a revisar
Incidents	Painel de observabilidade e incidents	Incidents ativos, histórico, MTTR, error rate por serviço	Monitor Bot e Debug Bot como primeiro resposta
Agents Panel	Admin: gerencia todos os agentes OpenClaw	Status, último heartbeat, ações recentes, markdowns carregados	Todos os agentes — igual ao FBR-Click
7.2 Componentes Específicos de Dev
PR CARD (no PR Queue) Número + título truncado Autor (avatar) + reviewers (avatars) CI status badge: ✅ / ❌ / ⏳ Tempo aberto: "há 2h", "há 3 dias" (vermelho se >48h) Labels de tipo: feature / bugfix / chore Linhas alteradas: +340 -120 (cor por tamanho) Link direto para o PR no GitHub Hover: checklist do Review Bot resumida DEPLOY CARD (no Pipeline View) Repo + ambiente + versão Status com cor: 🟢 Live / 🟡 Deploying / 🔴 Failed / ⬅️ Rolled back Duração do deploy Triggered by: avatar do dev ou ícone 🤖 se por agente P95 latency + error rate pós-deploy Botão "Rollback" (requer aprovação)	INCIDENT CARD (no Incidents) Severidade badge: P0 vermelho / P1 laranja / P2 amarelo / P3 cinza Título + repo afetado Tempo aberto + SLA restante Assignee + status: open / investigating / resolved Source: Sentry / Grafana / Manual / Agent Timeline compacta: últimas 3 ações Link para post-mortem (se resolvido) AGENT ACTIVITY (em todas as telas) Badge 🤖 em tudo que um agente criou ou comentou Tooltip: "Deploy Bot · há 3min · trigger: pr.merged #234" Fundo lilás sutil em mensagens de agentes (igual ao FBR-Click) Log de auditoria completo: clique → histórico de ações do agente

PARTE 8 — SEGURANÇA E GOVERNANÇA
8.1 Regras de Autonomia por Agente
Agentes de dev têm acesso a sistemas críticos. A tabela abaixo define o que cada agente pode fazer sem aprovação humana vs. o que requer confirmação.
Agente	Autonomia total (sem aprovação)	Requer aprovação humana
Triage Bot	Aplicar labels, assignar issues, abrir P2/P3	Abrir P0/P1, fechar issues, alterar milestone
Review Bot	Postar comentários, aprovar PRs simples (<50 linhas, sem lógica de negócio)	Aprovar PRs complexos, solicitar rebase, sugerir fechamento de PR
Deploy Bot	Deploy em staging, rollback automático em falha, health check	Deploy em produção, rollback manual, hotfix sem CI
Monitor Bot	Abrir incidents, notificar Slack, criar issues de bug	Escalar P0 para WhatsApp fora do horário, fechar incident
Standup Bot	Gerar e postar relatórios, mover cards no Projects, fechar sprint	Criar novo sprint, alterar velocity histórico, reabrir issues fechadas
Debug Bot	Coletar logs, buscar contexto, postar análise em issues	Sugerir fix, criar PR diretamente, modificar código
8.2 Contractors — Isolamento e Controle
🔒 Política de acesso para contractors
Contractors são desenvolvedores externos com acesso limitado e auditado. Regras de isolamento:   • Acesso apenas aos repositórios explicitamente autorizados pelo Tech Lead   • Canal Slack #contractors isolado — sem acesso a #incidents, #deploys, #dev-geral   • Agentes NÃO podem assignar issues a contractors sem aprovação humana   • PRs de contractors requerem review de pelo menos 1 dev interno   • Nenhum contractor tem acesso a Coolify, Sentry ou Grafana diretamente   • Toda ação de contractor no GitHub é logada no AGENT_ACTION_LOG O que um agente PODE fazer com contractors:   • Review Bot pode comentar em PRs de contractors normalmente   • Triage Bot pode assignar issues em repos autorizados   • Deploy Bot NÃO aceita deploy de commits de contractors sem revisão interna
8.3 DORA Metrics — Métricas de Saúde do Time
Métrica DORA	Definição	Meta FBR-DEV	Agente que monitora
Deployment Frequency	Com que frequência fazemos deploy em prod	≥ 1x por semana por repo ativo	Standup Bot (relatório semanal)
Lead Time for Changes	Tempo de issue criada até deploy em prod	< 5 dias úteis	Standup Bot (burndown + cycle time)
Change Failure Rate	% de deploys que causaram rollback ou incident	< 5%	Deploy Bot + Monitor Bot
Time to Restore Service	Tempo de incident aberto até resolved	< 2h para P0/P1; < 24h para P2	Monitor Bot + Debug Bot

PARTE 9 — ROADMAP DE IMPLEMENTAÇÃO
9.1 Fase 1 — MVP (Meses 1-3)
INFRAESTRUTURA Setup do repositório fbr-dev-shared no GitHub Deploy do FBR-DEV no VPS (Docker Compose + Coolify) GitHub App instalada na org Facebrasil Integração Slack configurada (Bot Token + webhooks) Banco PostgreSQL + Redis provisionados AGENTES Triage Bot: markdowns completos + deploy Deploy Bot: markdowns + integração Coolify Standup Bot: markdowns + cron configurado	FLUXOS ATIVOS Fluxo 1: Issue → PR → Merge (básico) Fluxo 2: Commit → Deploy → Notify (staging + prod) Comandos /issue, /deploy, /status, /sprint no Slack INTEGRAÇÕES GitHub webhooks: issues, PRs, push, checks Slack: notificações de deploy e incidents Coolify: trigger de deploy via API GitHub Projects: sincronização básica de cards
9.2 Fase 2 — Growth (Meses 4-6)
AGENTES Review Bot: análise de PR + checklist automática Monitor Bot: Sentry + Grafana + alertas Debug Bot: investigação de bugs com contexto FLUXOS Fluxo 3: Bug → Triage → Fix → Close completo Fluxo 4: Sprint → Daily → Retro completo DORA Metrics dashboard automático	INTEGRAÇÕES Sentry: erros em tempo real → incidents automáticos Grafana: métricas de infra → alertas inteligentes WhatsApp/Telegram: alertas P0 para Tech Lead Linear (opcional): sync bidirecional de issues CAPACIDADES CROSS-DOMAIN release-notes cross para FBR-Click (changelog de produto) analise-performance cross para times de negócio
9.3 Fase 3 — Scale (Meses 7-10)
🚀 Capacidades avançadas da Fase 3
Agentes que escrevem código: Debug Bot propõe fix direto no PR (para bugs simples) Auto-scaling de agentes: múltiplas instâncias do Review Bot para repos de alta atividade AI-powered sprint planning: Standup Bot sugere scope do sprint com base em velocity histórico Capacidades cross-domain FBR-DEV → FBR-Click: agentes de dev informam time comercial   sobre lançamentos, bugs que afetam clientes, e estimativas de feature requests Post-mortem automatizado com root cause analysis via LLM Predição de bugs: Review Bot identifica padrões de código que historicamente geram bugs
FBR-DEV — Especificação Técnica v1.0
Fevereiro 2026  ·  Facebrasil  ·  GitHub × Slack × OpenClaw