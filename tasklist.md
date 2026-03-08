# Task List FBR-Leads

Fonte principal: `prd/plano-implantacao.md`, `prd/prd-backend-fbrleads.md` e `prd/prd-frontend-fbrleads.md`.

## Skills locais selecionadas

| Skill local | Uso no projeto |
|-------------|----------------|
| `.agent/skills/backend-security-coder` | Autenticacao, headers obrigatorios, webhooks HMAC, secrets, hardening de API e banco |
| `.agent/skills/backend-dev-guidelines` | Organizacao de modulos backend, services, rotas e validacao |
| `.agent/skills/frontend-dev-guidelines` | Estrutura do dashboard Next.js, hooks, tipagem e carregamento de dados |
| `.agent/skills/firecrawl-scraper` | Futuras etapas de scraping institucional |
| `.agent/skills/machine-learning-ops-ml-pipeline` | Pipeline de scoring e operacao de modelos quando chegarmos no enrichment e scorer |
| `.agent/skills/ui-skills` | Apoio pontual na composicao visual do dashboard |

## Batch 1 - Fundacao

- [x] Criar bootstrap do repositorio com backend FastAPI, `docker-compose.yml`, `Dockerfile`, `.env`, `.env.example` e `nginx/default.conf`
- [ ] Provisionar VPS Hetzner Ubuntu 24.04
- [ ] Instalar Docker e Docker Compose na VPS
- [ ] Configurar Tailscale entre VPS e Mac Mini
- [ ] Validar conectividade com Ollama via Tailscale
- [ ] Ajustar SSL real com Certbot e dominio interno
- [ ] Subir stack completa e validar `GET /health`

## Batch 2 - Database

- [x] Criar pasta de migrations SQL
- [x] Implementar schema principal do PRD
- [x] Habilitar RLS em todas as tabelas
- [x] Criar triggers `updated_at` e rotina `pg_cron`
- [x] Criar indexes de performance
- [x] Adicionar seed inicial de workspace, dominio e ICP

Skills foco:
- `backend-security-coder`
- `backend-dev-guidelines`

## Batch 3 - Backend Core

- [x] Expandir app factory com routers por dominio
- [x] Implementar middleware global de autenticacao por agente
- [x] Construir CRUD inicial de domains
- [x] Construir ingest, listagem, detalhe, enrichment e scoring inicial de leads
- [x] Construir campaigns, writer e dispatcher inicial
- [x] Criar webhooks Postal e FBR-Click com HMAC
- [x] Implementar audit log append-only basico

Skills foco:
- `backend-security-coder`
- `backend-dev-guidelines`
- `machine-learning-ops-ml-pipeline`

## Batch 4 - OpenClaw Agents

- [x] Criar pastas base dos agentes com os 7 markdowns obrigatorios
- [x] Configurar gateway scaffold no compose na porta 3500
- [ ] Registrar os agentes por time no gateway e no FBR-Click
- [ ] Refinar de 8 repositorios de time para a cobertura operacional completa dos 13 agentes
- [ ] Documentar limites de aprovacao e kill switch por agente conforme operacao real

## Batch 5 - Postal + Aquecimento

- [ ] Adicionar Postal ao compose de producao
- [ ] Configurar DNS SPF, DKIM e DMARC
- [ ] Implementar regras de pausa por bounce
- [ ] Ativar fase 1 de aquecimento

## Batch 6 - Frontend Dashboard

- [x] Criar app Next.js 15 com TypeScript strict
- [x] Configurar `iron-session`, login e middleware
- [x] Implementar proxy `/api/proxy/[...path]`
- [x] Aplicar design system em `layout.tsx` e `globals.css`
- [x] Implementar paginas base `domains`, `leads`, `icp`, `campaigns`, `agents`, `reports`
- [ ] Instalar dependencias e validar build real com `npm run build`
- [ ] Conectar telas aos endpoints reais do backend

Skills foco:
- `frontend-dev-guidelines`
- `ui-skills`

## Batch 7 - Integracao FBR-Click

- [ ] Criar handoff de SQL para o FBR-Click
- [ ] Registrar Cadenciador Bot
- [ ] Processar feedback `deal.won` e `deal.lost`
- [ ] Configurar publicacao de relatorios no canal dedicado

## Batch 8 - Producao e Entrega

- [ ] Adicionar Grafana e Prometheus
- [ ] Criar rotina de backup
- [ ] Executar teste de carga de 1000 leads
- [ ] Validar fallback das 3 camadas de LLM
- [ ] Atualizar README final e handoff operacional

## Ordem recomendada de execucao imediata

1. Instalar dependencias do frontend e validar build.
2. Subir a stack local com `docker compose up --build`.
3. Conectar o dashboard aos endpoints reais via proxy.
4. Partir para Postal, FBR-Click e refinamento dos 13 agentes.
