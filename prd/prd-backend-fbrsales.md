# PRD Backend â€” FBR-CLICK v1.0
> **Fonte canÃ´nica:** `FBR-CLICK-prd.md` Â· `fbr-arquitetura.md` Â· `securitycoderules.md`
> **Stack:** FastAPI + Python 3.11+ + PostgreSQL 16 + Redis 7 + OpenClaw Gateway (Node.js)
> **Prazo MVP:** 60 dias â€” 8 batches

---

## 1. VISÃƒO DO PRODUTO

FBR-CLICK Ã© o hub central de colaboraÃ§Ã£o do Facebrasil â€” onde humanos e agentes autÃ´nomos OpenClaw convivem na mesma interface, nos mesmos canais, com a mesma experiÃªncia visual. Ã‰ o ponto de chegada obrigatÃ³rio de todos os outros sistemas FBR (Leads, Dev, Suporte).

**Problema resolvido:** Times usando mÃºltiplas ferramentas perdem contexto em cada transiÃ§Ã£o. Agentes autÃ´nomos precisam de uma superfÃ­cie nativa para operar â€” nÃ£o apenas webhooks anÃ´nimos disparando notificaÃ§Ãµes.

**MÃ©tricas de sucesso do MVP:**
- 100% das notificaÃ§Ãµes de SQLs do FBR-Leads chegando via agente no FBR-CLICK
- Todos os agentes de todos os sistemas FBR registrados e operacionais
- Audit log completo de toda aÃ§Ã£o de agente
- Tempo de resposta de agente a triggers â‰¤ 2 minutos
- Dashboard de monitoramento de agentes em tempo real

---

## 2. MODELO DE USUÃRIOS

O FBR-CLICK opera com dois tipos de membros â€” humanos e agentes â€” convivendo na mesma interface.

| Atributo | UsuÃ¡rio Humano | Agente OpenClaw |
|---|---|---|
| AutenticaÃ§Ã£o | Email + senha + iron-session cookie | JWT rotacionado a cada 24h |
| Interface | Web / PWA | OpenClaw Gateway via REST + WebSocket |
| Identidade | Avatar humano + nome | Emoji ðŸ¤– + nome + badge "AGENTE" |
| Comportamento | Reativo | Proativo + reativo (heartbeat + triggers) |
| PermissÃµes | RBAC por Space | Scope definido em AGENTS.md |
| ConfiguraÃ§Ã£o | UI do FBR-CLICK | 7 Markdowns no repositÃ³rio Git |
| Auditabilidade | HistÃ³rico na plataforma | Audit log append-only completo |

---

## 3. ARQUITETURA

### 3.1 Stack tecnolÃ³gica

| Componente | Tecnologia |
|---|---|
| Backend | FastAPI + Python 3.11+ (todas as rotas async) |
| Agentes | OpenClaw Gateway â€” Node.js, porta 3500 |
| WebSocket | ConexÃ£o persistente agente â†” FBR-CLICK |
| Banco | PostgreSQL 16 (RLS em todas as tabelas) |
| Cache/Filas | Redis 7 |
| Auth humano | iron-session â€” cookie httpOnly |
| Auth agente | JWT rotacionado a cada 24h |
| Git-Watcher | Monitora repos dos agentes, recarrega markdowns |
| Infra | VPS Hetzner 8 vCores / 32GB / 200GB NVMe Â· Ubuntu 24.04 |
| Containers | Docker + Docker Compose |
| Proxy reverso | Nginx + Certbot |
| Monitoramento | Grafana + Prometheus |

### 3.2 MicrosserviÃ§os internos

| ServiÃ§o | Responsabilidade |
|---|---|
| `messaging-service` | Mensagens, threads, canais, WebSocket de usuÃ¡rios |
| `task-service` | Tarefas, subtarefas, atribuiÃ§Ãµes, prazos |
| `crm-service` | Pipeline de deals, stages, KPIs |
| `agent-service` | Registro, validaÃ§Ã£o, ciclo de vida de agentes |
| `agent-gateway` | WebSocket dedicado para conexÃµes OpenClaw |
| `agent-api` | REST API com todas as actions disponÃ­veis para agentes |
| `git-watcher` | Monitora repos Git e recarrega markdowns ao detectar push |
| `audit-log` | Registra toda aÃ§Ã£o de agente com payload, resultado, trigger |
| `notification-service` | Push notifications, @menÃ§Ãµes, alertas em tempo real |

### 3.3 Estrutura de pastas

```
FBR-CLICK-backend/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ main.py                    # FastAPI app factory + lifespan
â”‚   â”œâ”€â”€ core/
â”‚   â”‚   â”œâ”€â”€ config.py              # pydantic-settings (.env)
â”‚   â”‚   â”œâ”€â”€ database.py            # asyncpg pool
â”‚   â”‚   â”œâ”€â”€ redis.py               # Redis client + pub/sub
â”‚   â”‚   â””â”€â”€ security.py            # JWT validation (humanos + agentes)
â”‚   â”œâ”€â”€ messaging/
â”‚   â”‚   â”œâ”€â”€ routes.py
â”‚   â”‚   â”œâ”€â”€ service.py
â”‚   â”‚   â”œâ”€â”€ websocket.py           # WebSocket handler para usuÃ¡rios
â”‚   â”‚   â””â”€â”€ schemas.py
â”‚   â”œâ”€â”€ tasks/
â”‚   â”‚   â”œâ”€â”€ routes.py
â”‚   â”‚   â”œâ”€â”€ service.py
â”‚   â”‚   â””â”€â”€ schemas.py
â”‚   â”œâ”€â”€ crm/
â”‚   â”‚   â”œâ”€â”€ routes.py
â”‚   â”‚   â”œâ”€â”€ service.py
â”‚   â”‚   â””â”€â”€ schemas.py
â”‚   â”œâ”€â”€ spaces/
â”‚   â”‚   â”œâ”€â”€ routes.py
â”‚   â”‚   â”œâ”€â”€ service.py
â”‚   â”‚   â””â”€â”€ schemas.py
â”‚   â”œâ”€â”€ agents/
â”‚   â”‚   â”œâ”€â”€ routes.py              # registro, config, monitoramento
â”‚   â”‚   â”œâ”€â”€ service.py             # lÃ³gica de ciclo de vida
â”‚   â”‚   â”œâ”€â”€ gateway.py             # WebSocket para OpenClaw
â”‚   â”‚   â”œâ”€â”€ git_watcher.py         # monitora repos e recarrega markdowns
â”‚   â”‚   â”œâ”€â”€ action_logger.py       # audit log append-only
â”‚   â”‚   â”œâ”€â”€ approval.py            # fluxo de aprovaÃ§Ã£o humana
â”‚   â”‚   â””â”€â”€ schemas.py
â”‚   â”œâ”€â”€ auth/
â”‚   â”‚   â”œâ”€â”€ routes.py
â”‚   â”‚   â”œâ”€â”€ service.py
â”‚   â”‚   â””â”€â”€ schemas.py
â”‚   â””â”€â”€ webhooks/
â”‚       â”œâ”€â”€ git.py                 # recebe push events do GitHub/GitLab
â”‚       â”œâ”€â”€ fbr_leads.py
â”‚       â”œâ”€â”€ fbr_suporte.py
â”‚       â””â”€â”€ fbr_dev.py
â”œâ”€â”€ .env.example
â”œâ”€â”€ docker-compose.yml
â””â”€â”€ requirements.txt
```

---

## 4. DATABASE SCHEMA

### 4.1 VisÃ£o geral das tabelas

| Tabela | DescriÃ§Ã£o | RelaÃ§Ãµes chave |
|---|---|---|
| `workspaces` | Tenant isolado por empresa | 1:N com todas as outras |
| `users` | Membros humanos do workspace | N:1 workspace |
| `spaces` | Ãrea de trabalho por equipe | N:1 workspace Â· 1:N channels |
| `channels` | Canais de comunicaÃ§Ã£o dentro de um space | N:1 space Â· 1:N messages |
| `messages` | Mensagens de humanos e agentes | N:1 channel Â· N:1 author |
| `tasks` | Tarefas com assignee, prazo, prioridade | N:1 channel Â· N:1 assignee |
| `deals` | Deals no pipeline de CRM | N:1 space Â· 1:N deal_history |
| `deal_history` | HistÃ³rico de mudanÃ§as de stage | N:1 deal |
| `agents` | Agentes OpenClaw registrados | N:1 workspace |
| `agent_markdown_cache` | Cache dos 7 markdowns carregados | N:1 agent |
| `agent_action_logs` | Audit log imutÃ¡vel append-only | N:1 agent |
| `agent_approval_requests` | SolicitaÃ§Ãµes de aprovaÃ§Ã£o humana pendentes | N:1 agent |
| `kpis` | MÃ©tricas configuradas por space | N:1 space |

### 4.2 Schema SQL completo

```sql
-- ExtensÃµes
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- WORKSPACES
CREATE TABLE workspaces (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  slug       TEXT UNIQUE NOT NULL,
  owner_id   UUID NOT NULL,
  settings   JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- USERS
CREATE TABLE users (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  email           TEXT NOT NULL,
  password_hash   TEXT NOT NULL,
  full_name       TEXT NOT NULL,
  avatar_url      TEXT,
  role            TEXT DEFAULT 'member' CHECK (role IN ('admin','member','viewer')),
  is_active       BOOLEAN DEFAULT TRUE,
  last_active_at  TIMESTAMPTZ,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now(),
  UNIQUE(workspace_id, email)
);

-- SPACES
CREATE TABLE spaces (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name         TEXT NOT NULL,
  slug         TEXT NOT NULL,
  icon_emoji   TEXT DEFAULT 'ðŸ ',
  is_private   BOOLEAN DEFAULT FALSE,
  created_by   UUID NOT NULL REFERENCES users(id),
  created_at   TIMESTAMPTZ DEFAULT now(),
  UNIQUE(workspace_id, slug)
);

-- CHANNELS
CREATE TABLE channels (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id     UUID NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  name         TEXT NOT NULL,
  slug         TEXT NOT NULL,
  type         TEXT DEFAULT 'general' CHECK (type IN ('general','deal','task','system','agent-log')),
  is_private   BOOLEAN DEFAULT FALSE,
  created_by   UUID NOT NULL REFERENCES users(id),
  created_at   TIMESTAMPTZ DEFAULT now(),
  UNIQUE(space_id, slug)
);

-- MESSAGES
CREATE TABLE messages (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id   UUID NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  author_id    UUID NOT NULL,
  author_type  TEXT NOT NULL CHECK (author_type IN ('human','agent')),
  text         TEXT NOT NULL,
  attachments  JSONB DEFAULT '[]',
  metadata     JSONB DEFAULT '{}',
  thread_id    UUID REFERENCES messages(id),
  is_edited    BOOLEAN DEFAULT FALSE,
  created_at   TIMESTAMPTZ DEFAULT now(),
  updated_at   TIMESTAMPTZ DEFAULT now()
);

-- TASKS
CREATE TABLE tasks (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  channel_id   UUID REFERENCES channels(id),
  deal_id      UUID REFERENCES deals(id),
  title        TEXT NOT NULL,
  description  TEXT,
  assignee_id  UUID REFERENCES users(id),
  created_by   UUID NOT NULL,
  source       TEXT DEFAULT 'human' CHECK (source IN ('human','agent')),
  priority     TEXT DEFAULT 'P3' CHECK (priority IN ('P0','P1','P2','P3')),
  status       TEXT DEFAULT 'todo' CHECK (status IN ('todo','in_progress','done','cancelled')),
  due_at       TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT now(),
  updated_at   TIMESTAMPTZ DEFAULT now()
);

-- DEALS
CREATE TABLE deals (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id     UUID NOT NULL REFERENCES workspaces(id),
  space_id         UUID NOT NULL REFERENCES spaces(id),
  channel_id       UUID REFERENCES channels(id),
  title            TEXT NOT NULL,
  company_name     TEXT,
  company_cnpj     TEXT,
  contact_name     TEXT,
  contact_email    TEXT,
  contact_linkedin TEXT,
  value            NUMERIC(12,2),
  stage            TEXT DEFAULT 'prospecting' CHECK (stage IN
                   ('prospecting','qualification','proposal','negotiation','closed_won','closed_lost')),
  assignee_id      UUID REFERENCES users(id),
  score            SMALLINT,
  source           TEXT,
  lead_data        JSONB DEFAULT '{}',
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

-- DEAL_HISTORY
CREATE TABLE deal_history (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  deal_id    UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
  from_stage TEXT NOT NULL,
  to_stage   TEXT NOT NULL,
  changed_by UUID NOT NULL,
  changed_at TIMESTAMPTZ DEFAULT now()
);

-- AGENTS
CREATE TABLE agents (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id            UUID NOT NULL REFERENCES workspaces(id),
  name                    TEXT NOT NULL,
  display_name            TEXT NOT NULL,
  avatar_emoji            TEXT DEFAULT 'ðŸ¤–',
  badge_label             TEXT DEFAULT 'AGENTE',
  status                  TEXT DEFAULT 'offline' CHECK (status IN ('online','offline','paused','error')),
  model_primary           TEXT NOT NULL,
  model_fallback          TEXT,
  git_repo_url            TEXT NOT NULL,
  git_branch              TEXT DEFAULT 'main',
  git_last_sha            TEXT,
  space_ids               UUID[] DEFAULT '{}',
  channel_ids             UUID[] DEFAULT '{}',
  require_mention         BOOLEAN DEFAULT FALSE,
  heartbeat_interval_min  INT DEFAULT 30,
  last_active_at          TIMESTAMPTZ,
  is_active               BOOLEAN DEFAULT TRUE,
  created_by              UUID NOT NULL REFERENCES users(id),
  created_at              TIMESTAMPTZ DEFAULT now(),
  updated_at              TIMESTAMPTZ DEFAULT now()
);

-- AGENT_MARKDOWN_CACHE
CREATE TABLE agent_markdown_cache (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id   UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  file_type  TEXT NOT NULL CHECK (file_type IN ('SOUL','IDENTITY','TASKS','AGENTS','MEMORY','TOOLS','USER')),
  content    TEXT NOT NULL,
  git_sha    TEXT NOT NULL,
  loaded_at  TIMESTAMPTZ DEFAULT now(),
  UNIQUE(agent_id, file_type)
);

-- AGENT_ACTION_LOGS (append-only â€” sem UPDATE, sem DELETE)
CREATE TABLE agent_action_logs (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id     UUID NOT NULL REFERENCES agents(id),
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  action_type  TEXT NOT NULL CHECK (action_type IN
               ('post_message','create_task','move_deal','mention','update_task',
                'request_approval','reload_config','other')),
  trigger_type TEXT NOT NULL CHECK (trigger_type IN ('heartbeat','event','mention','manual')),
  trigger_ref  TEXT,
  payload      JSONB NOT NULL DEFAULT '{}',
  result       JSONB,
  error        TEXT,
  approved_by  UUID REFERENCES users(id),
  executed_at  TIMESTAMPTZ DEFAULT now()
  -- SEM updated_at â€” append-only por design
);

-- AGENT_APPROVAL_REQUESTS
CREATE TABLE agent_approval_requests (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id     UUID NOT NULL REFERENCES agents(id),
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  channel_id   UUID NOT NULL REFERENCES channels(id),
  action_type  TEXT NOT NULL,
  payload      JSONB NOT NULL DEFAULT '{}',
  reason       TEXT NOT NULL,
  status       TEXT DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected')),
  requested_at TIMESTAMPTZ DEFAULT now(),
  decided_by   UUID REFERENCES users(id),
  decided_at   TIMESTAMPTZ
);

-- KPIS
CREATE TABLE kpis (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  space_id     UUID NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
  workspace_id UUID NOT NULL REFERENCES workspaces(id),
  label        TEXT NOT NULL,
  value        NUMERIC(12,2) DEFAULT 0,
  target       NUMERIC(12,2),
  unit         TEXT DEFAULT 'number',
  updated_at   TIMESTAMPTZ DEFAULT now()
);
```

### 4.3 Row Level Security (RLS)

```sql
-- Habilitar em TODAS as tabelas
ALTER TABLE workspaces              ENABLE ROW LEVEL SECURITY;
ALTER TABLE users                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE spaces                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE channels                ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages                ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE deals                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE deal_history            ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_markdown_cache    ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_action_logs       ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_approval_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpis                    ENABLE ROW LEVEL SECURITY;

-- Isolamento por workspace (padrÃ£o para todas as tabelas com workspace_id)
-- Exemplo para messages â€” replicar em: spaces, channels, tasks, deals, agents, kpis
CREATE POLICY workspace_isolation ON messages
  FOR ALL USING (
    workspace_id IN (
      SELECT id FROM workspaces WHERE owner_id = current_setting('app.current_user_id')::UUID
    )
  );

-- Audit log: apenas INSERT â€” nenhum agente pode deletar ou atualizar
CREATE POLICY audit_insert_only ON agent_action_logs
  FOR INSERT WITH CHECK (true);
CREATE POLICY audit_select_workspace ON agent_action_logs
  FOR SELECT USING (
    workspace_id IN (
      SELECT id FROM workspaces WHERE owner_id = current_setting('app.current_user_id')::UUID
    )
  );
-- NÃƒO criar policies de UPDATE ou DELETE em agent_action_logs
```

### 4.4 Triggers e Indexes

```sql
-- FunÃ§Ã£o genÃ©rica de updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

-- Triggers por tabela
CREATE TRIGGER messages_updated_at BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER tasks_updated_at    BEFORE UPDATE ON tasks    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER deals_updated_at    BEFORE UPDATE ON deals    FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER agents_updated_at   BEFORE UPDATE ON agents   FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER users_updated_at    BEFORE UPDATE ON users    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Indexes de performance
CREATE INDEX idx_messages_channel   ON messages(channel_id, created_at DESC);
CREATE INDEX idx_messages_author    ON messages(author_id, author_type);
CREATE INDEX idx_tasks_workspace    ON tasks(workspace_id, status);
CREATE INDEX idx_tasks_assignee     ON tasks(assignee_id, status, due_at);
CREATE INDEX idx_deals_space        ON deals(space_id, stage);
CREATE INDEX idx_deals_workspace    ON deals(workspace_id, stage);
CREATE INDEX idx_agents_workspace   ON agents(workspace_id, is_active);
CREATE INDEX idx_logs_agent         ON agent_action_logs(agent_id, executed_at DESC);
CREATE INDEX idx_logs_workspace     ON agent_action_logs(workspace_id, executed_at DESC);
CREATE INDEX idx_approvals_pending  ON agent_approval_requests(workspace_id, status)
  WHERE status = 'pending';
```

---

## 5. ENDPOINTS FASTAPI

Todas as rotas `/api/*` requerem autenticaÃ§Ã£o. Rotas de humanos: `iron-session â†’ X-User-Id header`. Rotas de agentes: `JWT â†’ X-Agent-Id header`.

### 5.1 AutenticaÃ§Ã£o de humanos

| MÃ©todo | Path | DescriÃ§Ã£o |
|---|---|---|
| POST | `/api/auth/login` | Login com email + senha |
| POST | `/api/auth/logout` | Invalidar sessÃ£o |
| GET | `/api/auth/me` | Dados do usuÃ¡rio logado |

### 5.2 Spaces e Canais

| MÃ©todo | Path | DescriÃ§Ã£o |
|---|---|---|
| GET | `/api/spaces` | Listar spaces do workspace |
| POST | `/api/spaces` | Criar novo space |
| GET | `/api/spaces/{id}/channels` | Listar canais de um space |
| POST | `/api/spaces/{id}/channels` | Criar canal |
| PATCH | `/api/spaces/{id}` | Atualizar space |

### 5.3 Messaging

| MÃ©todo | Path | DescriÃ§Ã£o |
|---|---|---|
| GET | `/api/channels/{id}/messages` | Listar mensagens com paginaÃ§Ã£o cursor |
| POST | `/api/channels/{id}/messages` | Enviar mensagem |
| PATCH | `/api/messages/{id}` | Editar mensagem prÃ³pria |
| WS | `/ws/channels/{id}` | WebSocket em tempo real por canal |

### 5.4 Tasks

| MÃ©todo | Path | DescriÃ§Ã£o |
|---|---|---|
| GET | `/api/tasks` | Listar tarefas com filtros (status, assignee, priority, source) |
| POST | `/api/tasks` | Criar tarefa |
| PATCH | `/api/tasks/{id}` | Atualizar tarefa (status, assignee, prazo) |
| DELETE | `/api/tasks/{id}` | Cancelar tarefa (soft delete: status = 'cancelled') |

### 5.5 CRM â€” Pipeline

| MÃ©todo | Path | DescriÃ§Ã£o |
|---|---|---|
| GET | `/api/deals` | Listar deals do pipeline |
| POST | `/api/deals` | Criar deal |
| GET | `/api/deals/{id}` | Detalhe do deal |
| PATCH | `/api/deals/{id}/stage` | Mover deal de stage (cria deal_history) |
| PATCH | `/api/deals/{id}` | Atualizar dados do deal |

### 5.6 GestÃ£o de Agentes (admin)

| MÃ©todo | Path | DescriÃ§Ã£o |
|---|---|---|
| GET | `/api/agents` | Listar agentes do workspace |
| POST | `/api/agents` | Registrar novo agente |
| PATCH | `/api/agents/{id}/pause` | Pausar agente (read-only mode) |
| PATCH | `/api/agents/{id}/resume` | Reativar agente pausado |
| DELETE | `/api/agents/{id}` | Desregistrar agente (kill switch) |
| GET | `/api/agents/{id}/logs` | Logs de aÃ§Ã£o paginados |
| GET | `/api/agents/approvals` | AprovaÃ§Ãµes pendentes |
| POST | `/api/agents/approvals/{id}/decide` | Aprovar ou rejeitar aÃ§Ã£o |
| POST | `/api/agents/{id}/reload-config` | ForÃ§ar reload de markdowns do Git |

### 5.7 Rotas de agentes (JWT â€” X-Agent-Id)

| MÃ©todo | Path | DescriÃ§Ã£o | Requer aprovaÃ§Ã£o |
|---|---|---|---|
| POST | `/agent/messages` | Postar mensagem em canal | NÃ£o |
| POST | `/agent/tasks` | Criar tarefa com atribuiÃ§Ã£o | NÃ£o |
| PATCH | `/agent/tasks/{id}` | Atualizar status de tarefa | NÃ£o |
| GET | `/agent/deals` | Listar deals do pipeline | NÃ£o |
| PATCH | `/agent/deals/{id}/stage` | Mover deal de stage | Sim (para closed_won/lost) |
| POST | `/agent/mentions` | Mencionar usuÃ¡rio em canal | NÃ£o |
| GET | `/agent/kpis/{spaceId}` | Buscar mÃ©tricas do KPI bar | NÃ£o |
| POST | `/agent/approvals/request` | Solicitar aprovaÃ§Ã£o humana | â€” |
| WS | `/agents/ws` | Canal bidirecional em tempo real | â€” |

### 5.8 Webhooks externos

| MÃ©todo | Path | DescriÃ§Ã£o | Auth |
|---|---|---|---|
| POST | `/webhooks/git` | Push events do GitHub/GitLab | HMAC-SHA256 |
| POST | `/webhooks/fbr-leads` | Receber SQL handoff do FBR-Leads | HMAC-SHA256 |
| POST | `/webhooks/fbr-suporte` | Eventos do FBR-Suporte | HMAC-SHA256 |
| POST | `/webhooks/fbr-dev` | Eventos do FBR-Dev | HMAC-SHA256 |
| GET | `/health` | Health check pÃºblico | PÃºblico |

---

## 6. INTEGRAÃ‡ÃƒO OPENCLAW

### 6.1 Fluxo de comunicaÃ§Ã£o

| Evento | Origem | Destino | AÃ§Ã£o |
|---|---|---|---|
| Mensagem @agente | Humano no FBR-CLICK | OpenClaw Gateway | Agente processa e responde |
| Tarefa atribuÃ­da | task-service | OpenClaw Gateway | Agente executa TASKS.md |
| Deal muda de stage | crm-service | OpenClaw Gateway | Agente verifica triggers |
| Heartbeat tick | OpenClaw Daemon | Agent Loop | Agente age proativamente |
| Push no Git | GitHub Webhook | git-watcher | Markdowns recarregados |
| Agente posta mensagem | OpenClaw Agent Loop | messaging-service | Mensagem com badge ðŸ¤– |

### 6.2 Channel Adapter â€” interface de contrato

```typescript
export interface FBRClickConfig {
  workspaceId: string
  agentToken: string          // JWT rotacionado a cada 24h
  gatewayUrl: string          // wss://FBR-CLICK.com/agents/ws
  spaceIds: string[]
  channelIds: string[]
  requireMention: boolean
  heartbeatInterval: number   // minutos
}

interface NormalizedMessage {
  id: string
  channelId: string
  spaceId: string
  authorId: string
  authorType: 'human' | 'agent'
  text: string
  attachments: Attachment[]
  context: { taskId?: string; dealId?: string; threadId?: string }
  timestamp: string
}

type FBRClickEvent =
  | { type: 'message';            data: NormalizedMessage }
  | { type: 'task_assigned';      data: TaskAssignment }
  | { type: 'deal_stage_changed'; data: DealStageEvent }
  | { type: 'approval_requested'; data: ApprovalRequest }
  | { type: 'mention';            data: MentionEvent }
  | { type: 'channel_joined';     data: ChannelJoinEvent }
```

### 6.3 Git-Watcher â€” fluxo de atualizaÃ§Ã£o

```bash
# Ao receber push do GitHub:
# 1. Valida assinatura HMAC-SHA256
# 2. Identifica qual agente pertence ao repositÃ³rio
# 3. git clone --depth 1 (ou git pull) do branch configurado
# 4. Valida schema dos 7 markdowns (todos obrigatÃ³rios)
# 5. Se vÃ¡lido: notifica OpenClaw Gateway via WebSocket
#    {"type": "config_reload", "agentId": "...", "files": [...]}
# 6. Gateway reinicia agent loop com novos markdowns
# 7. Posta no canal de log: "âš™ï¸ ConfiguraÃ§Ã£o atualizada"
# 8. Registra no audit-log com diff das mudanÃ§as
```

---

## 7. LLM EM CASCATA (conforme fbr-arquitetura.md)

```
Camada 1 â€” Ollama (Mac Mini M4 32GB via Tailscale)
  â†’ Uso: tarefas de alto volume, classificaÃ§Ã£o, scoring
  â†’ Timeout: 15s Â· Fallback: se offline > 30s â†’ Camada 2

Camada 2 â€” Claude API (claude-sonnet-4-6)
  â†’ Uso: geraÃ§Ã£o de conteÃºdo, raciocÃ­nio complexo, personalizaÃ§Ã£o
  â†’ Timeout: 30s Â· Fallback: se rate limit ou erro â†’ Camada 3

Camada 3 â€” GPT-4o API (reserva)
  â†’ Uso: contingÃªncia total â€” nunca primÃ¡ria
  â†’ Timeout: 30s Â· Fallback: alerta crÃ­tico para owner
```

n8n faz health check nas trÃªs camadas a cada 60s e publica status no Redis. O mÃ³dulo `llm.py` lÃª o status do Redis antes de cada chamada (sem latÃªncia de health check no caminho crÃ­tico).

---

## 8. OS 6 AGENTES NATIVOS

| Agente | Space | FunÃ§Ã£o | Triggers | Heartbeat |
|---|---|---|---|---|
| Comercial Bot ðŸ’¼ | Vendas | Pipeline, follow-ups, rascunhos de proposta | Deal muda de stage | Segunda 8h, diÃ¡rio 17h |
| Content Bot âœï¸ | ConteÃºdo | Pautas, briefings, SEO | Nova tarefa de artigo | Sob demanda |
| Ads Bot ðŸ“¢ | Marketing | Monitor de campanhas Meta/Google | KPI abaixo de threshold | A cada 4h |
| Approval Bot ðŸŽ¨ | Design | Fluxo de aprovaÃ§Ã£o de criativos | Asset novo, prazo vencendo | Sob demanda |
| Report Bot ðŸ“Š | Geral | RelatÃ³rios semanais e mensais | Sexta 17h, fim de mÃªs | Sexta 17h |
| Onboarding Bot ðŸŽ“ | Geral | Boas-vindas, tour do FBR-CLICK | Novo membro adicionado | Sob demanda |

---

## 9. SEGURANÃ‡A â€” BACKEND

### 9.1 Camadas de seguranÃ§a

| Camada | Mecanismo | O que protege |
|---|---|---|
| Auth humano | iron-session cookie httpOnly secure sameSite=lax | SessÃ£o de usuÃ¡rio |
| Auth agente | JWT rotacionado a cada 24h + HMAC-SHA256 no webhook | Identidade do agente |
| AutorizaÃ§Ã£o | Scope de canais validado contra AGENTS.md no backend | Onde o agente pode agir |
| Prompt injection | SanitizaÃ§Ã£o de input antes de enviar ao OpenClaw Gateway | Hijack de comportamento |
| AÃ§Ãµes sensÃ­veis | Approval request obrigatÃ³rio para aÃ§Ãµes de alto impacto | Danos irreversÃ­veis |
| Rate limiting | MÃ¡x 60 actions/min por agente; 5 mensagens/min por canal | Spam e loops infinitos |
| Audit log | Toda action logada com payload + resultado + trigger | Rastreabilidade completa |
| Sandboxing | Agentes nÃ£o compartilham contexto entre workspaces | Vazamento cross-tenant |
| SOUL.md validation | FBR-CLICK valida presenÃ§a de regras de seguranÃ§a no SOUL.md | Agentes sem restriÃ§Ãµes |
| Kill switch | Admin desconecta agente imediatamente via UI | Comportamento anÃ´malo |

### 9.2 Regras de cÃ³digo obrigatÃ³rias (de securitycoderules.md)

- Todas as rotas FastAPI DEVEM ser `async`
- Input validation obrigatÃ³ria via Pydantic models em TODAS as rotas
- CORS restritivo: aceitar apenas domÃ­nios do frontend
- Webhooks DEVEM validar assinatura HMAC-SHA256 antes de processar
- Rate limiting por `user_id` / `agent_id` em rotas sensÃ­veis
- NUNCA retornar `None`/`null` para indicar erro â€” levantar exception especÃ­fica
- Exceptions customizadas: `AgentScopeViolationError`, `ApprovalRequiredError`, `AgentOfflineError`
- Type hints obrigatÃ³rios em todas as funÃ§Ãµes Python. Sem `Any` genÃ©rico

### 9.3 Middleware de autenticaÃ§Ã£o

```python
# Fluxo obrigatÃ³rio:
# Frontend (Next.js cookie iron-session) 
#   â†’ Next.js API Route proxy (descriptografa cookie, extrai user_id)
#   â†’ Repassa header X-User-Id para FastAPI
#   â†’ FastAPI valida X-User-Id em TODAS as rotas protegidas

# Agentes:
# OpenClaw Gateway (JWT)
#   â†’ FastAPI valida JWT, extrai agent_id
#   â†’ FastAPI verifica scope do agente contra AGENTS.md
#   â†’ Repassa X-Agent-Id internamente
```

---

## 10. VARIÃVEIS DE AMBIENTE (.env.example)

```bash
# â•â• DATABASE â•â•
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fbr_click
REDIS_URL=redis://localhost:6379/0

# â•â• AUTH HUMANOS â•â•
SESSION_SECRET=...              # 64 chars Â· openssl rand -base64 48
JWT_SECRET=...                  # para tokens de agente â€” NUNCA commitar

# â•â• OPENCLAW GATEWAY â•â•
OPENCLAW_GATEWAY_URL=http://localhost:3500
OPENCLAW_AGENT_JWT_SECRET=...   # NUNCA commitar

# â•â• GIT-WATCHER â•â•
GIT_WEBHOOK_SECRET=...          # HMAC-SHA256 â€” NUNCA commitar
GIT_CLONE_DIR=/tmp/agent-repos

# â•â• LLM â•â•
ANTHROPIC_API_KEY=sk-ant-...    # NUNCA commitar
ANTHROPIC_MODEL=claude-sonnet-4-6
OPENAI_API_KEY=sk-...           # fallback â€” NUNCA commitar
OPENAI_MODEL=gpt-4o

# â•â• WEBHOOKS DE SISTEMAS FBR â•â•
FBR_LEADS_WEBHOOK_SECRET=...    # HMAC-SHA256 â€” NUNCA commitar
FBR_SUPORTE_WEBHOOK_SECRET=...  # HMAC-SHA256 â€” NUNCA commitar
FBR_DEV_WEBHOOK_SECRET=...      # HMAC-SHA256 â€” NUNCA commitar

# â•â• FRONTEND â•â•
BACKEND_URL=http://localhost:8000
# NEXT_PUBLIC_ sÃ³ para WS URL (necessÃ¡rio no browser)
NEXT_PUBLIC_WS_URL=wss://FBR-CLICK.com/ws
```

---

## 11. DEPENDÃŠNCIAS (requirements.txt)

```
fastapi==0.115.0
uvicorn[standard]==0.31.0
asyncpg==0.30.0
redis[asyncio]==5.1.0
pydantic==2.9.0
pydantic-settings==2.5.0
anthropic==0.40.0
openai==1.55.0
httpx==0.28.0
python-jose==3.3.0
python-multipart==0.0.12
websockets==13.0
gitpython==3.1.43
slowapi==0.1.9
bcrypt==4.2.0
```

---

## 12. REQUISITOS NÃƒO-FUNCIONAIS

- Tempo de resposta de agente a triggers: â‰¤ 2 minutos
- WebSocket de usuÃ¡rios: latÃªncia â‰¤ 100ms
- API REST: p99 â‰¤ 500ms
- Kill switch de agente: desconecta em < 5 segundos
- Audit log: nunca perder eventos â€” append-only com garantia de durabilidade
- Backup automÃ¡tico do PostgreSQL: diÃ¡rio Ã s 3h para storage externo
- Disponibilidade: degradaÃ§Ã£o controlada em falha de qualquer camada LLM

---

## 13. GESTÃƒO DE RISCOS

| Risco | Impacto | MitigaÃ§Ã£o |
|---|---|---|
| Agente com comportamento anÃ´malo | Alto | Kill switch imediato na UI + read-only mode como etapa intermediÃ¡ria |
| Prompt injection via mensagem | Alto | SanitizaÃ§Ã£o obrigatÃ³ria + SOUL.md carregado primeiro |
| Agente postando fora do scope | MÃ©dio | ValidaÃ§Ã£o de scope contra AGENTS.md no backend antes de executar |
| Perda de conexÃ£o WebSocket | MÃ©dio | Reconnect automÃ¡tico com backoff exponencial |
| Markdowns invÃ¡lidos no Git | MÃ©dio | ValidaÃ§Ã£o de schema antes de recarregar; rollback se invÃ¡lido |
| AprovaÃ§Ãµes pendentes sem resposta | Baixo | Timeout de 24h: aÃ§Ã£o cancelada + alerta ao owner |
| Rate limit de LLM (Claude API) | MÃ©dio | Fallback automÃ¡tico para GPT-4o + alerta a 80% do limite |
