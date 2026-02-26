# FBR-Leads PRD v2.0 — Fonte de Verdade para Implementação
> **Stack:** OpenClaw + n8n + FastAPI + PostgreSQL + Redis + Next.js
> **Prazo:** 60 dias · 8 batches · ~50 tasks de 5–15 min cada
> **Referências obrigatórias:** `docs/fbr-arquitetura.md` · `docs/securitycoderules.md`
> **Versão:** 2.0 — migração completa de CrewAI para OpenClaw

---

## VISÃO DO PRODUTO

**Problema:** Times comerciais perdem horas por semana em prospecção manual — buscar empresas, validar e-mails, personalizar mensagens e controlar follow-ups. Trabalho repetitivo, pouco escalável, leads de baixa qualidade.

**Solução:** FBR-Leads automatiza o ciclo completo de prospecção outbound: captação → enriquecimento → validação → aquecimento → handoff. O time de vendas só recebe SQLs — leads que já responderam ou demonstraram interesse, com contexto completo no FBR-Click.

**Público-alvo:** Times de vendas B2B de empresas brasileiras (10–200 colaboradores). Caso inicial: Facebrasil — vende espaços publicitários e serviços digitais para empresas brasileiras nos EUA.

**Métricas de sucesso do MVP:**
- ≥ 500 leads novos/semana por ICP ativo
- ≥ 85% dos leads com e-mail válido
- Taxa de resposta ≥ 3% na cadência
- Taxa de bounce < 2% por domínio
- 100% dos SQLs entregues via agente no FBR-Click

---

## ARQUITETURA GERAL

### Stack por camada

```
Frontend    → Next.js 15 + TypeScript strict + Tailwind + shadcn/ui
Proxy       → Next.js API Routes (obrigatório — frontend nunca fala direto com backend)
Backend     → FastAPI + Python 3.11+ (todas as rotas async)
Agentes     → OpenClaw Gateway (Node.js · porta 3500)
Orquestração → n8n (instância dedicada fbr-leads)
Banco       → PostgreSQL 16 (RLS em todas as tabelas)
Cache/Filas → Redis 7
Mail Server → Postal (open source)
Scraping    → Firecrawl + Python/Playwright
LLM         → Ollama (Camada 1) → Claude API (Camada 2) → GPT-4o (Camada 3)
Rede        → Tailscale (VPS ↔ Mac Mini M4)
Infra       → VPS Hetzner 8 vCores / 32GB / 200GB NVMe · Ubuntu 24.04
Containers  → Docker Compose (toda a stack)
```

### Estrutura de pastas do backend

```
fbr-leads-backend/
├── app/
│   ├── main.py                  # FastAPI app factory + lifespan
│   ├── core/
│   │   ├── config.py            # pydantic-settings (.env)
│   │   ├── database.py          # asyncpg pool
│   │   ├── redis.py             # Redis client + filas
│   │   ├── llm.py               # cascade Ollama→Claude→GPT-4o
│   │   └── security.py          # JWT validation + rate limiting
│   ├── domains/                 # Time 1 — Guardiões
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── leads/                   # Times 2, 3 — Garimpeiros + Analistas
│   │   ├── routes.py
│   │   ├── service.py
│   │   ├── enrichment.py
│   │   ├── scorer.py
│   │   └── schemas.py
│   ├── campaigns/               # Times 4, 5 — Redatores + Cadenciadores
│   │   ├── routes.py
│   │   ├── service.py
│   │   ├── writer.py            # geração de e-mail via Claude API
│   │   ├── dispatcher.py        # seleção de domínio por capacidade
│   │   └── schemas.py
│   ├── intelligence/            # Time 6 — Inteligência
│   │   ├── routes.py
│   │   ├── service.py
│   │   └── schemas.py
│   ├── webhooks/
│   │   ├── postal.py            # bounce/abertura/clique
│   │   └── fbr_click.py         # feedback deal.won/lost
│   └── agents/
│       ├── openclaw_bridge.py   # proxy interno para o Gateway
│       └── action_logger.py     # wrapper de audit log para toda ação
├── agents/                      # repositórios dos 7 Markdowns
│   ├── guardiao-dominios/
│   ├── garimpeiro-linkedin/
│   ├── garimpeiro-cnpj/
│   ├── analista-enriquecedor/
│   ├── redator-principal/
│   ├── cadenciador/
│   └── inteligencia/
├── .env.example
├── docker-compose.yml
└── requirements.txt
```

---

## DATABASE

### Tabelas e relações

| Tabela | Descrição | Relações chave |
|--------|-----------|----------------|
| workspaces | Multi-tenant — cada empresa é um workspace isolado | 1:N com todas as outras |
| domains | Domínios de e-mail com métricas de aquecimento e reputação | N:1 workspace |
| icp_profiles | Perfil de cliente ideal: setor, porte, cargos, região, keywords | N:1 workspace · 1:N campaigns |
| leads | Perfil completo: dados pessoais, empresa, score, estágio no funil | N:1 workspace |
| campaigns | Configuração de campanha com ICP e domínios ativos | N:1 workspace |
| email_sequences | Template de cadência de 4 toques | N:1 campaign |
| email_sends | Registro de cada e-mail enviado | N:1 lead · N:1 domain |
| interactions | Abertura, clique, resposta, opt-out, bounce | N:1 lead · N:1 email_sends |
| agent_action_logs | Audit log imutável (append-only) de toda ação de agente | N:1 workspace |
| intelligence_reports | Relatórios semanais do Time 6 | N:1 workspace · N:1 campaign |

### Schema SQL — tabelas principais

```sql
-- WORKSPACES
CREATE TABLE workspaces (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  slug        TEXT UNIQUE NOT NULL,
  owner_id    UUID NOT NULL REFERENCES auth.users(id),
  settings    JSONB DEFAULT '{}',
  created_at  TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

-- DOMAINS
CREATE TABLE domains (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id     UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  domain           TEXT NOT NULL,
  warm_phase       SMALLINT DEFAULT 1 CHECK (warm_phase BETWEEN 1 AND 4),
  daily_limit      SMALLINT DEFAULT 10,
  sends_today      SMALLINT DEFAULT 0,
  reputation_score SMALLINT DEFAULT 100 CHECK (reputation_score BETWEEN 0 AND 100),
  bounce_rate      NUMERIC(5,2) DEFAULT 0,
  is_blacklisted   BOOLEAN DEFAULT FALSE,
  is_active        BOOLEAN DEFAULT TRUE,
  warm_started_at  TIMESTAMPTZ,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

-- ICP_PROFILES
CREATE TABLE icp_profiles (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name          TEXT NOT NULL,
  sectors       TEXT[] DEFAULT '{}',
  company_sizes TEXT[] DEFAULT '{}',
  target_roles  TEXT[] DEFAULT '{}',
  regions       TEXT[] DEFAULT '{}',
  keywords      TEXT[] DEFAULT '{}',
  min_score     SMALLINT DEFAULT 60,
  created_at    TIMESTAMPTZ DEFAULT now()
);

-- LEADS
CREATE TABLE leads (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id    UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  campaign_id     UUID REFERENCES campaigns(id),
  icp_profile_id  UUID REFERENCES icp_profiles(id),
  -- Dados pessoais
  name            TEXT,
  email           TEXT,
  email_valid     BOOLEAN,
  role            TEXT,
  linkedin_url    TEXT,
  -- Dados da empresa
  company_name    TEXT,
  company_cnpj    TEXT,
  company_sector  TEXT,
  company_size    TEXT,
  company_website TEXT,
  -- Qualificação
  score           SMALLINT DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
  funnel_stage    TEXT DEFAULT 'captured' CHECK (funnel_stage IN
                  ('captured','enriching','validated','warming','qualified','sql','discard')),
  source          TEXT,  -- linkedin|cnpj|maps|scraping|trigger
  enrichment_data JSONB DEFAULT '{}',
  discard_reason  TEXT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

-- AGENT_ACTION_LOGS (append-only)
CREATE TABLE agent_action_logs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id  UUID NOT NULL REFERENCES workspaces(id),
  agent_id      TEXT NOT NULL,
  team          TEXT NOT NULL,  -- guardiao|garimpeiro|analista|redator|cadenciador|inteligencia
  action_type   TEXT NOT NULL,
  trigger_type  TEXT NOT NULL,  -- heartbeat|event|manual
  payload       JSONB NOT NULL DEFAULT '{}',
  result        JSONB,
  error         TEXT,
  executed_at   TIMESTAMPTZ DEFAULT now()
  -- SEM updated_at — append-only
);
```

### RLS — policies obrigatórias

```sql
-- Habilitar em TODAS as tabelas
ALTER TABLE workspaces        ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains           ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads             ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns         ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sends       ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions      ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_action_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles      ENABLE ROW LEVEL SECURITY;

-- Isolamento por workspace (aplicar em cada tabela)
CREATE POLICY leads_workspace_isolation ON leads
  FOR ALL USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

-- Audit log: apenas INSERT
CREATE POLICY audit_insert_only ON agent_action_logs FOR INSERT WITH CHECK (true);
CREATE POLICY audit_select_workspace ON agent_action_logs FOR SELECT USING (
  workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
);
-- NÃO criar policies de UPDATE ou DELETE em agent_action_logs
```

### Triggers e indexes

```sql
-- updated_at automático
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = now(); RETURN NEW; END; $$ LANGUAGE plpgsql;

CREATE TRIGGER leads_updated_at     BEFORE UPDATE ON leads     FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER domains_updated_at   BEFORE UPDATE ON domains   FOR EACH ROW EXECUTE FUNCTION update_updated_at();
CREATE TRIGGER campaigns_updated_at BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Reset diário de sends_today (00:00 UTC via pg_cron)
SELECT cron.schedule('reset-sends-today', '0 0 * * *',
  'UPDATE domains SET sends_today = 0 WHERE is_active = true');

-- Indexes de performance
CREATE INDEX idx_leads_workspace  ON leads(workspace_id);
CREATE INDEX idx_leads_funnel     ON leads(workspace_id, funnel_stage);
CREATE INDEX idx_leads_score      ON leads(workspace_id, score DESC);
CREATE INDEX idx_domains_active   ON domains(workspace_id, is_active);
CREATE INDEX idx_sends_lead       ON email_sends(lead_id, sent_at DESC);
CREATE INDEX idx_logs_workspace   ON agent_action_logs(workspace_id, executed_at DESC);
CREATE INDEX idx_logs_agent       ON agent_action_logs(agent_id, executed_at DESC);
```

---

## ENDPOINTS FASTAPI

Todos os endpoints `/api/*` requerem header `X-Agent-Id` (JWT do agente OpenClaw). Sem esse header → 401.

| Método | Path | Descrição | Time |
|--------|------|-----------|------|
| GET | /health | Status do sistema, LLM ativo, conexão Tailscale | — |
| GET | /api/domains | Listar domínios com métricas de saúde | T1 |
| POST | /api/domains | Cadastrar novo domínio | T1 |
| PATCH | /api/domains/{id}/phase | Avançar fase de aquecimento | T1 |
| POST | /api/domains/{id}/check-blacklist | Verificação imediata em blacklists | T1 |
| POST | /api/leads/ingest | Ingerir batch de leads brutos | T2 |
| POST | /api/leads/{id}/enrich | Triggar enriquecimento de lead específico | T3 |
| POST | /api/leads/{id}/validate-email | Chamar ZeroBounce e salvar resultado | T3 |
| POST | /api/leads/{id}/score | Calcular score via LLM e persistir | T3 |
| GET | /api/leads | Listar leads com filtros (stage, score, campaign) | T3 |
| GET | /api/leads/{id} | Detalhe completo com histórico de interações | T3 |
| POST | /api/campaigns | Criar campanha com ICP e sequência | T4 |
| POST | /api/campaigns/{id}/write-email | Gerar e-mail personalizado via Claude API | T4 |
| POST | /api/campaigns/{id}/dispatch | Dispatcher seleciona domínio e agenda envio | T5 |
| POST | /api/webhooks/postal | Receber bounce/abertura/clique (HMAC-SHA256) | T5 |
| POST | /api/webhooks/fbr-click | Receber feedback deal.won/lost (HMAC-SHA256) | T6 |
| GET | /api/intelligence/report | Buscar relatório semanal mais recente | T6 |
| POST | /api/intelligence/generate | Triggar geração de relatório manualmente | T6 |
| GET | /api/logs | Listar audit log com filtros | — |
| GET | /api/icp | Listar perfis ICP do workspace | — |
| POST | /api/icp | Criar ou atualizar perfil ICP | — |

---

## CASCATA DE LLM — app/core/llm.py

```python
# Comportamento esperado do módulo llm.py

# 1. No startup do FastAPI, n8n já fez health check nas 3 camadas e publicou no Redis:
#    redis.set("llm:layer1:status", "ok"|"error")
#    redis.set("llm:layer2:status", "ok"|"error")
#    redis.set("llm:layer3:status", "ok"|"error")

# 2. llm.py lê o status do Redis antes de cada chamada (sem latência de health check)

# 3. Lógica de roteamento:
#    - Se layer1 ok → Ollama (timeout 15s)
#    - Se layer1 error → Claude API (timeout 30s)
#    - Se layer2 error → GPT-4o (timeout 30s)
#    - Se layer3 error → raise LLMUnavailableError + alerta crítico para owner

# 4. GET /health deve retornar qual camada está ativa:
#    {"status": "ok", "llm_layer": 1, "model": "llama3.1:8b"}
```

---

## OS 6 TIMES DE AGENTES OPENCLAW

### Time 1 — Guardiões do Mail Server

**Missão:** Proteger e maximizar a reputação de cada domínio. Fundação de toda a operação.

| Agente | LLM | Heartbeat | Ações autônomas | Requer aprovação |
|--------|-----|-----------|-----------------|------------------|
| Auditor de Domínios | Ollama | A cada 30min | Verificar blacklists, SPF/DKIM/DMARC | — |
| Gestor de Aquecimento | Ollama | A cada 30min | Controlar ramp-up, ajustar daily_limit | Pausar domínio definitivamente |
| Monitor de Reputação | Ollama | A cada 30min | Acompanhar métricas, emitir alertas | — |
| Controlador de Rotação | Ollama | Contínuo (Redis) | Distribuir volume entre domínios saudáveis | Alterar fase de aquecimento manualmente |

**Protocolo de aquecimento:**

| Fase | Período | Volume/dia | Atividade |
|------|---------|-----------|-----------|
| 1 | Dias 1–30 | Interno apenas | Troca de e-mails entre contas do sistema |
| 2 | Dias 31–60 | 10–20 e-mails | Primeiros contatos externos (leads alto score) |
| 3 | Dias 61–90 | 30–50 e-mails | Volume controlado com cadências completas |
| 4 | Dia 90+ | 50–100 e-mails | Operação plena com monitoramento contínuo |

### Time 2 — Garimpeiros

**Missão:** Captar dados brutos de múltiplas fontes e transformar em registros estruturados.

| Agente | LLM | Heartbeat | Fonte de dados |
|--------|-----|-----------|----------------|
| Scraper Web | Ollama | Sob demanda (n8n) | Firecrawl em sites institucionais |
| Scraper Especializado | Ollama | Sob demanda (n8n) | Python/Playwright para fontes específicas |
| Coletor CNPJ | Ollama | A cada 4h | CNPJ.biz + Receita Federal |
| Minerador LinkedIn | Ollama (deduplicação) | A cada 2h | Apify — rate limiting respeitado |
| Agente de Gatilhos | Ollama | A cada 6h | Google Alerts, RSS, portais de vagas |

**Fontes e deduplicação:**
- Deduplicação automática por CNPJ/domínio antes de inserir no banco
- LinkedIn tratado como fonte "premium mas instável" — sistema funciona sem ela

### Time 3 — Analistas

**Missão:** Enriquecer, validar e qualificar leads. Pipeline rígido em 3 etapas obrigatórias.

**Pipeline de validação (ordem imutável):**
```
1. Validar e-mail via ZeroBounce → se inválido: discard imediato
2. Verificar aderência ao ICP → se fora do perfil: archive
3. Calcular score 0-100 via LLM → se abaixo de min_score: discard
         ↓
   Lead entra na fila de aquecimento
```

| Agente | LLM | Heartbeat |
|--------|-----|-----------|
| Enriquecedor | Ollama | Contínuo (fila Redis) |
| Validador de E-mail | — (API ZeroBounce) | Contínuo (fila Redis) |
| Analista de ICP | Ollama | Contínuo (fila Redis) |
| Scorer | Ollama → Claude | Contínuo (fila Redis) |

### Time 4 — Redatores

**Missão:** Criar mensagens altamente personalizadas. Personalização é o que separa prospecção de spam.

| Agente | LLM | Heartbeat | Requer aprovação |
|--------|-----|-----------|------------------|
| Pesquisador de Contexto | Ollama | Junto com Redator | — |
| Redator Principal | **Claude (obrigatório)** | Sob demanda (campanha) | — |
| Revisor | Ollama | Junto com Redator | Reprovar e-mail (retorna para Redator com feedback) |
| Testador A/B | Ollama | Junto com Redator | — |

**Regras de redação para proteção de domínio:**

Obrigatório:
- Mencionar contexto específico da empresa do lead
- Texto curto (3–5 parágrafos)
- Um único CTA claro
- Tom de conversa, não de vendas

Proibido:
- Links no primeiro e-mail
- Anexos de qualquer tipo
- Palavras-gatilho: GRÁTIS, PROMOÇÃO, CLIQUE AQUI
- Mais de uma pergunta no mesmo e-mail

### Time 5 — Cadenciadores

**Missão:** Controlar timing e sequência de envio respeitando limites de cada domínio.

**Cadência padrão:**

| Toque | Timing | Objetivo |
|-------|--------|----------|
| #1 | Dia 1 | Primeiro contato — contexto específico, sem oferta |
| #2 | Dia 4 | Reforçar com valor — conteúdo relevante para o setor |
| #3 | Dia 9 | Criar urgência leve — referência a cliente similar |
| #4 | Dia 16 | Breakup — tom direto, porta aberta |

| Agente | LLM | Heartbeat | Requer aprovação |
|--------|-----|-----------|------------------|
| Dispatcher | Ollama | Contínuo (fila Redis) | Cancelar envio de toda uma campanha |
| Agendador | Ollama | Contínuo (fila Redis) | — |
| Monitor de Respostas | Ollama | A cada 15min | — |
| Registrador | — | Contínuo (fila Redis) | — |

**Regras do Dispatcher:**
- Selecionar domínio com `sends_today < daily_limit`
- Respeitar horário comercial do fuso do lead
- Sem envios em fins de semana
- Pausa automática se bounce detectado
- Resposta positiva → aciona handoff para FBR-Click imediatamente

### Time 6 — Inteligência

**Missão:** Retroalimentar os outros cinco times com aprendizados. Cérebro estratégico do sistema.

| Agente | LLM | Heartbeat |
|--------|-----|-----------|
| Analista de Campanha | Claude | Domingo 18h UTC-5 |
| Otimizador de Mensagens | Claude | Domingo 18h UTC-5 |
| Analista de ICP | Claude | Domingo 18h UTC-5 |
| Gerador de Relatórios | Claude | Domingo 18h UTC-5 |

---

## INTEGRAÇÃO FBR-CLICK

### Canal dedicado: #leads-qualificados

- Cadenciador Bot é o membro responsável pelo canal
- Aparece na sidebar do FBR-Click como qualquer outro membro do time
- Vendedor NUNCA precisa acessar o dashboard do FBR-Leads

### Payload do handoff SQL

```json
{
  "event": "sql_handoff",
  "lead": {
    "name": "Rafael Souza",
    "role": "Diretor de Marketing",
    "company": "TechCorp Brasil",
    "cnpj": "12.345.678/0001-99",
    "email": "rafael@techcorp.com.br",
    "linkedin": "linkedin.com/in/rafaelsouza",
    "score": 87,
    "source": "linkedin",
    "icp_match": "Empresas brasileiras nos EUA · Porte médio · Marketing",
    "enrichment_notes": "Empresa abriu escritório em Miami em jan/26.",
    "interaction_summary": "3 e-mails enviados. Respondeu ao Toque #2 com interesse."
  },
  "action": {
    "create_deal": true,
    "notify_user_id": "usr_julia_manager",
    "post_to_channel": "chn_leads_qualificados"
  }
}
```

### Feedback loop FBR-Click → FBR-Leads

| Evento | Ação no FBR-Leads | Impacto no modelo |
|--------|-------------------|--------------------|
| deal.won | Marcar lead como convertido | Reforça padrões do ICP e scoring |
| deal.lost (preço) | Marcar lost + registrar razão | Ajusta peso de variáveis de budget |
| deal.lost (não era decisor) | Marcar lost + registrar razão | Refina filtragem de cargos |
| deal.lost (sem resposta) | Marcar lost | Otimiza padrões de mensagem |

---

## VARIÁVEIS DE AMBIENTE (.env.example)

```bash
# ══ DATABASE ══
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fbr_leads
REDIS_URL=redis://localhost:6379/0

# ══ LLM CAMADA 1 — Ollama (Tailscale) ══
OLLAMA_BASE_URL=http://100.x.x.x:11434   # IP Tailscale do Mac Mini
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT_SECONDS=15

# ══ LLM CAMADA 2 — Claude API ══
ANTHROPIC_API_KEY=sk-ant-...              # NUNCA commitar
ANTHROPIC_MODEL=claude-sonnet-4-6
ANTHROPIC_TIMEOUT_SECONDS=30

# ══ LLM CAMADA 3 — GPT-4o (reserva) ══
OPENAI_API_KEY=sk-...                     # NUNCA commitar
OPENAI_MODEL=gpt-4o

# ══ INTEGRAÇÕES EXTERNAS ══
ZEROBOUNCE_API_KEY=zb-...                 # NUNCA commitar
APIFY_API_TOKEN=apify_...                 # NUNCA commitar
FIRECRAWL_API_KEY=fc-...                  # NUNCA commitar

# ══ POSTAL MAIL SERVER ══
POSTAL_API_URL=https://postal.fbr.internal
POSTAL_API_KEY=postal-...                 # NUNCA commitar
POSTAL_WEBHOOK_SECRET=...                 # HMAC-SHA256 — NUNCA commitar

# ══ FBR-CLICK INTEGRATION ══
FBR_CLICK_API_URL=https://fbr-click.com/api
FBR_CLICK_WEBHOOK_SECRET=...              # HMAC-SHA256 — NUNCA commitar
FBR_CLICK_CHANNEL_LEADS=chn_...           # ID do canal #leads-qualificados

# ══ OPENCLAW GATEWAY ══
OPENCLAW_GATEWAY_URL=http://localhost:3500
OPENCLAW_WORKSPACE_ID=ws_...              # ID do workspace no FBR-Click

# ══ DASHBOARD ══
SESSION_SECRET=...                        # 64 chars · openssl rand -base64 48
BACKEND_URL=http://localhost:8000         # Proxy Next.js → FastAPI (interno)
```

---

## DEPENDÊNCIAS (requirements.txt)

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
apify-client==1.8.0
firecrawl-py==1.4.0
playwright==1.49.0
slowapi==0.1.9
```

---

## IMPLEMENTATION PLAN — 8 BATCHES

### Como usar este plano no Antigravity

Para cada batch, disparar uma Mission com este prompt base:
```
Execute o [Batch X — Nome]. 
Fonte de verdade: docs/fbr-leads-prd.md (seção do batch).
Regras obrigatórias: docs/securitycoderules.md.
Arquitetura: docs/fbr-arquitetura.md.
Critério de conclusão: todas as verificações da tabela do batch passando.
Não avançar para o próximo batch sem verificação OK em todas as tasks.
```

---

### Batch 1 — Fundação (Dias 1–7)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 1.1 | Provisionar VPS Hetzner (8 vCores / 32GB / 200GB NVMe · Ubuntu 24.04) | — | SSH funciona. `df -h` mostra 200GB. |
| 1.2 | Instalar Docker + Docker Compose | — | `docker --version` retorna sem erro. |
| 1.3 | Configurar Tailscale na VPS e no Mac Mini M4 | — | `ping [tailscale-ip-mac]` responde da VPS. |
| 1.4 | Testar Ollama via Tailscale: `curl http://[tailscale-ip]:11434/api/tags` | app/core/llm.py | Retorna lista de modelos com status 200. |
| 1.5 | Criar docker-compose.yml com: postgres, redis, fastapi, n8n, nginx | docker-compose.yml | `docker compose up -d` sobe todos sem erro. |
| 1.6 | Configurar PostgreSQL 16 com extensões uuid-ossp + pg_cron | app/core/database.py | `SELECT gen_random_uuid()` retorna UUID válido. |
| 1.7 | Criar .env e .env.example com todas as variáveis | .env · .env.example | FastAPI inicia sem erros de variável faltando. |
| 1.8 | Configurar Nginx como proxy reverso com SSL (Certbot) | nginx/default.conf | `https://leads.fbr.internal` retorna 200. |

---

### Batch 2 — Database (Dias 7–12)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 2.1 | Executar SQL de criação de todas as tabelas (seção Database deste PRD) | — | `\dt` no psql lista todas as tabelas. |
| 2.2 | Aplicar RLS em todas as tabelas (seção RLS deste PRD) | — | SELECT com user diferente retorna 0 rows. |
| 2.3 | Criar triggers updated_at + pg_cron para reset de sends_today | — | UPDATE em leads atualiza updated_at. |
| 2.4 | Criar todos os indexes de performance (seção Indexes deste PRD) | — | EXPLAIN ANALYZE usa index, não seq scan. |
| 2.5 | Seed: workspace de teste + domínio de teste + ICP de teste | app/core/database.py | `SELECT count(*) FROM workspaces` retorna 1. |

---

### Batch 3 — Backend Core (Dias 12–22)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 3.1 | FastAPI app factory com lifespan (startup/shutdown de conexões) | app/main.py | GET /health retorna `{status: ok, llm_layer: 1}`. |
| 3.2 | app/core/llm.py com cascade Ollama→Claude→GPT-4o + health check Redis | app/core/llm.py | Desligar Ollama → redireciona para Claude automaticamente. |
| 3.3 | Middleware JWT para agentes (header X-Agent-Id) | app/core/security.py | Sem header → 401. Token válido → passa. |
| 3.4 | Domínios: CRUD + service de saúde + dispatcher básico | app/domains/ | POST cria domínio. GET retorna lista com métricas. |
| 3.5 | Leads: ingest em batch + enrichment pipeline + scorer | app/leads/ | POST /ingest aceita array. Score calculado via Ollama. |
| 3.6 | Campaigns: criação + writer (Claude) + dispatcher | app/campaigns/ | POST cria campanha. Writer gera e-mail personalizado. |
| 3.7 | Webhook Postal com validação HMAC-SHA256 | app/webhooks/postal.py | Secret correto → lead atualizado. Errado → 403. |
| 3.8 | Webhook FBR-Click (deal.won/lost) com validação HMAC-SHA256 | app/webhooks/fbr_click.py | Feedback → intelligence_report atualizado. |
| 3.9 | action_logger.py como wrapper para toda ação de agente | app/agents/action_logger.py | Após ação de agente, count(*) em agent_action_logs cresce. |

---

### Batch 4 — OpenClaw Agents (Dias 22–35)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 4.1 | OpenClaw Gateway no docker-compose (porta 3500) | docker-compose.yml | `curl localhost:3500/health` retorna `{status: ok}`. |
| 4.2 | 7 Markdowns do Guardião de Domínios | agents/guardiao-dominios/ | Agente registrado no FBR-Click com badge 🤖. |
| 4.3 | Garimpeiro LinkedIn + testar coleta via Apify | agents/garimpeiro-linkedin/ | Heartbeat a cada 2h insere leads na tabela. |
| 4.4 | Garimpeiro CNPJ + testar consulta à Receita Federal | agents/garimpeiro-cnpj/ | Lead com CNPJ tem campos company_* preenchidos. |
| 4.5 | Analista Enriquecedor + Validador de E-mail | agents/analista-enriquecedor/ | Lead inválido → funnel_stage='discard' automaticamente. |
| 4.6 | Scorer + testar pipeline completo de qualificação | agents/scorer/ | Lead recebe score 0-100. Log mostra qual camada LLM. |
| 4.7 | Redator Principal + Revisor + Testador A/B | agents/redator-principal/ | E-mail sem links, sem spam words. 2 variações de assunto. |
| 4.8 | Dispatcher + Monitor de Respostas | agents/cadenciador/ | Dispatcher respeita daily_limit. Resposta aciona handoff. |
| 4.9 | Agente de Inteligência (Time 6) | agents/inteligencia/ | Heartbeat domingo 18h UTC-5 posta relatório no FBR-Click. |

---

### Batch 5 — Postal + Aquecimento (Dias 35–42)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 5.1 | Instalar Postal no docker-compose com banco dedicado | docker-compose.yml | Interface web acessível. API key funcional. |
| 5.2 | Migrar domínios para Postal + verificar SPF/DKIM/DMARC | — | MXToolbox mostra todos os registros como PASS. |
| 5.3 | Ativar Guardião + iniciar fase 1 de aquecimento (interno) | agents/guardiao-dominios/ | Domínios em fase 1 trocando e-mails internos. Dashboard mostra warm_phase=1. |
| 5.4 | Alerta automático: bounce > 2% pausa domínio e notifica no FBR-Click | app/domains/service.py | Simular bounce alto → domínio pausado + mensagem no canal. |

---

### Batch 6 — Frontend Dashboard (Dias 35–45)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 6.1 | Next.js 15 + TypeScript strict + Tailwind + shadcn/ui | package.json · tsconfig.json | `npx tsc` sem erros. `npm run dev` sobe na porta 3000. |
| 6.2 | iron-session: login, logout, middleware de proteção de rotas | app/api/auth/ · middleware.ts | Rota protegida sem cookie → redireciona para /login. |
| 6.3 | Proxy Next.js: todas as chamadas ao FastAPI via /api/proxy | app/api/proxy/[...path]/route.ts | Fetch direto ao FastAPI → 401. Via proxy com cookie → 200. |
| 6.4 | Dashboard de saúde dos domínios (WebSocket) | app/dashboard/domains/page.tsx | Bounce muda status em tempo real sem refresh. |
| 6.5 | Pipeline de leads com funil e filtros | app/dashboard/leads/page.tsx | Filtro por score > 70 retorna só leads qualificados. |
| 6.6 | Configuração de ICP sem código | app/dashboard/icp/page.tsx | Criar ICP → Garimpeiros iniciam coleta em até 30 min. |
| 6.7 | Status dos agentes com logs em tempo real + kill switch | app/dashboard/agents/page.tsx | Agente offline → badge vermelho. Kill switch funcional. |
| 6.8 | Relatórios executivos com exportação CSV | app/dashboard/reports/page.tsx | Relatório semanal exibido. Export gera CSV válido. |

---

### Batch 7 — Integração FBR-Click (Dias 45–52)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 7.1 | Registrar Cadenciador Bot no FBR-Click com permissão em #leads-qualificados | agents/cadenciador/ | Bot na sidebar do FBR-Click com badge 🤖. |
| 7.2 | Handoff completo: SQL → deal no FBR-Click → @menção ao vendedor | app/campaigns/dispatcher.py | SQL aparece como deal com todos os campos do payload. |
| 7.3 | Receber feedback deal.won/lost → retroalimentar Time 6 | app/webhooks/fbr_click.py | Fechar deal → intelligence_reports atualizado em ≤ 5min. |
| 7.4 | Canal #leads-report no FBR-Click para relatórios do Time 6 | agents/inteligencia/TASKS.md | Relatório de teste aparece no canal com formatação correta. |

---

### Batch 8 — Produção e Entrega (Dias 52–60)

| Task | Descrição | Arquivos | Verificação |
|------|-----------|----------|-------------|
| 8.1 | Grafana + Prometheus: dashboards de infra | docker-compose.yml | Grafana acessível. Métricas de todos os containers visíveis. |
| 8.2 | Backup automático do PostgreSQL para storage externo (diário 3h) | scripts/backup.sh | Restore a partir do backup — dados íntegros. |
| 8.3 | Teste de carga: 1000 leads em batch | — | 1000 leads enriquecidos e scorados em < 30min. Zero erros no audit log. |
| 8.4 | Teste de fallback LLM: desligar Mac Mini | — | Dashboard mostra 'LLM Layer: 2 (fallback)'. Operação contínua. |
| 8.5 | README: features, fluxo de operação, como criar ICP, como usar o dashboard | README.md | README aprovado pelo gestor do projeto. |
| 8.6 | Handoff para o time: kill switches, logs, fallback manual demonstrados | — | Todos os owners sabem pausar, verificar logs e acionar fallback. |

---

## GESTÃO DE RISCOS

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Domínio incluído em blacklist | Alto | Guardião monitora 2x/dia. Rotação automática em < 5min. |
| Taxa de bounce > 2% | Alto | Pausa automática do domínio. Revisão da fonte de leads. |
| Mac Mini M4 offline | Médio | Fallback automático para Claude API em ≤ 30s. |
| Conta Apify suspensa (LinkedIn) | Médio | Múltiplas contas em rodízio. Garimpeiros Web e CNPJ cobrem a lacuna. |
| Rate limit Claude API | Médio | Fallback automático para GPT-4o. Alerta a 80% do limite. |
| Prompt injection via dados de lead | Alto | Sanitização + instruction boundary + SOUL.md carregado primeiro. |
