# Plano de Implementação Detalhado: 1FBR-Click (FlowDesk + OpenClaw)

Este plano descreve a jornada de desenvolvimento da plataforma **FlowDesk**, integrando a colaboração humana com agentes autônomos **OpenClaw** e recursos compartilhados.

## User Review Required

> [!IMPORTANT]
> **Ordem de Execução:** O plano segue rigorosamente a ordem numérica dos documentos, priorizando a estabilidade do core (FlowDesk) antes da integração dos agentes.
> **Infraestrutura:** Recomenda-se validar as credenciais do Supabase e Cloudflare R2 antes da Fase 1.

---

## Fase 1: Fundação Core & MVP (FlowDesk)
*Foco: Documento 1 - Arquitetura Técnica & UX Base*

### 1.1 Infraestrutura e Autenticação
- [ ] Configuração do Monorepo (Next.js 14 + Tailwind v4 + TypeScript)
- [ ] Setup do Banco de Dados (PostgreSQL/Supabase) com RLS (Row Level Security)
- [ ] Implementação do Auth Service (NextAuth + JWT + RBAC)
- [ ] Configuração do Storage (Cloudflare R2) e Cache (Redis/Upstash)

### 1.2 Mensagens e Real-Time
- [ ] Implementação do `messaging-service` (Socket.io + Redis Pub/Sub)
- [ ] Criação da interface de chat: Sidebar, Área Central e Threads
- [ ] Sistema de Reações, Menções e Status Formal de Threads (Em discussão, Decidido, etc.)

### 1.3 Gestão de Tarefas (MVP)
- [ ] Implementação do `task-service` (CRUD de tarefas, subtarefas, prioridades)
- [ ] **Fluxo Crítico:** Conversão de Mensagem → Tarefa (Mini-modal inline)
- [ ] Sidebar de tarefas contextual por canal

---

## Fase 2: Integração OpenClaw & Shared Resources
*Foco: Documentos 2 e 3 - Automação & Infra de Conhecimento*

### 2.1 Ecossistema de Agentes (OpenClaw)
- [ ] Setup do `agent-service` e `agent-gateway` (WebSocket para agentes)
- [ ] Implementação do `git-watcher` para carregar Markdowns (SOUL, IDENTITY, etc.)
- [ ] Sistema de Audit Logs e Ações Sensíveis (Pendentes de aprovação humana)

### 2.2 Shared Resources (Infra Global)
- [ ] Estruturação do repositório `fbr-click-shared`
- [ ] Implementação dos primeiros **Commands** (/briefing, /resumo, /ajuda)
- [ ] Criação dos **Connectors** iniciais (Meta Ads, Google Ads, SMTP)
- [ ] Setup do Servidor **MCP Native** para os agentes acessarem a API do FlowDesk

---

## Fase 3: Capacidades Avançadas & Cross-Domain
*Foco: Documentos 3 e 4 - Inteligência e Colaboração*

### 3.1 Skills e Hooks
- [ ] Implementação de **Skills** especializadas (Redação Comercial, Análise de Pipeline)
- [ ] Setup do motor de **Hooks** (Ex: `on-deal-stage-change` disparando ações de múltiplos agentes)
- [ ] Integração de scripts Python/Node para relatórios complexos

### 3.2 Lógica Cross-Domain
- [ ] Implementação da política "Propose First" para ações fora do domínio do agente
- [ ] Fluxo de confirmação em linguagem natural para ativação de skills compartilhadas
- [ ] Registro de aprendizados na `MEMORY.md` via Git após sessões cross-domain

---

## Fase 4: Verticais de Negócio (CRM & Marketing)
*Foco: Documento 1 - Expansão de Features*

### 4.1 CRM Leve & Pipeline
- [ ] Implementação do `crm-service` (Deals, Stages, Atividades)
- [ ] View de Kanban e Dashboards de Forecast
- [ ] Automações de Pipeline (Mover stage → Criar task)

### 4.2 Fluxos de Aprovação e KPIs
- [ ] Sistema de Aprovação de Criativos (Marketing) com anotações inline
- [ ] Implementação da **KPI Bar** contextual no topo dos Spaces
- [ ] Dashboards executivos e integração final com ferramentas externas (HubSpot/Slack)

---

## Plano de Verificação

### Testes Automatizados
- Unitários para lógica de RBAC e RLS.
- Integração para o fluxo Mensagem → Tarefa.
- E2E (Playwright) para o ciclo de vida do Agente (Markdown → Ação no Chat).

### Validação Manual
- Verificação visual conforme `DESIGN_STANDARDS.md`.
- Teste de proatividade do agente (Heartbeat) em ambiente de staging.
