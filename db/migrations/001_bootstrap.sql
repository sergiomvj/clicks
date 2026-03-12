CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, email)
);

CREATE TABLE IF NOT EXISTS spaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, slug)
);

CREATE TABLE IF NOT EXISTS channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    space_id UUID NOT NULL REFERENCES spaces(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    channel_type TEXT NOT NULL DEFAULT 'sales',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, slug)
);

CREATE TABLE IF NOT EXISTS lead_intakes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    source_type TEXT NOT NULL CHECK (source_type IN ('fbr_leads', 'social_media', 'product_site', 'manual', 'support', 'other')),
    source_system TEXT NOT NULL,
    external_reference TEXT,
    lead_name TEXT NOT NULL,
    company_name TEXT,
    email TEXT,
    phone TEXT,
    score NUMERIC(10,2),
    temperature TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    handoff_payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    lead_intake_id UUID REFERENCES lead_intakes(id) ON DELETE SET NULL,
    channel_id UUID REFERENCES channels(id) ON DELETE SET NULL,
    assignee_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    company_name TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT,
    value_cents INTEGER NOT NULL DEFAULT 0,
    stage TEXT NOT NULL DEFAULT 'prospecting',
    origin_badge TEXT NOT NULL DEFAULT 'manual',
    score NUMERIC(10,2),
    status TEXT NOT NULL DEFAULT 'open',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS deal_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    deal_id UUID NOT NULL REFERENCES deals(id) ON DELETE CASCADE,
    from_stage TEXT,
    to_stage TEXT NOT NULL,
    changed_by_type TEXT NOT NULL DEFAULT 'system',
    changed_by_id TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    deal_id UUID REFERENCES deals(id) ON DELETE SET NULL,
    channel_id UUID REFERENCES channels(id) ON DELETE SET NULL,
    assignee_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'todo',
    priority TEXT NOT NULL DEFAULT 'medium',
    source TEXT NOT NULL DEFAULT 'human',
    due_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    channel_id UUID NOT NULL REFERENCES channels(id) ON DELETE CASCADE,
    author_type TEXT NOT NULL DEFAULT 'human',
    author_id TEXT NOT NULL,
    body TEXT NOT NULL,
    source_system TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    display_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'offline',
    repository_url TEXT,
    last_heartbeat_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, slug)
);

CREATE TABLE IF NOT EXISTS approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    requested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS agent_action_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    action_type TEXT NOT NULL,
    trigger_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::JSONB,
    result JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'workspaces_updated_at_trigger') THEN
        CREATE TRIGGER workspaces_updated_at_trigger BEFORE UPDATE ON workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'users_updated_at_trigger') THEN
        CREATE TRIGGER users_updated_at_trigger BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'spaces_updated_at_trigger') THEN
        CREATE TRIGGER spaces_updated_at_trigger BEFORE UPDATE ON spaces FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'channels_updated_at_trigger') THEN
        CREATE TRIGGER channels_updated_at_trigger BEFORE UPDATE ON channels FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'lead_intakes_updated_at_trigger') THEN
        CREATE TRIGGER lead_intakes_updated_at_trigger BEFORE UPDATE ON lead_intakes FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'deals_updated_at_trigger') THEN
        CREATE TRIGGER deals_updated_at_trigger BEFORE UPDATE ON deals FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'tasks_updated_at_trigger') THEN
        CREATE TRIGGER tasks_updated_at_trigger BEFORE UPDATE ON tasks FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'messages_updated_at_trigger') THEN
        CREATE TRIGGER messages_updated_at_trigger BEFORE UPDATE ON messages FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'agents_updated_at_trigger') THEN
        CREATE TRIGGER agents_updated_at_trigger BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
END;
$$;

CREATE INDEX IF NOT EXISTS idx_spaces_workspace_id ON spaces(workspace_id);
CREATE INDEX IF NOT EXISTS idx_channels_workspace_id ON channels(workspace_id);
CREATE INDEX IF NOT EXISTS idx_channels_space_id ON channels(space_id);
CREATE INDEX IF NOT EXISTS idx_lead_intakes_workspace_id ON lead_intakes(workspace_id);
CREATE INDEX IF NOT EXISTS idx_lead_intakes_source_type ON lead_intakes(source_type);
CREATE INDEX IF NOT EXISTS idx_deals_workspace_stage ON deals(workspace_id, stage);
CREATE INDEX IF NOT EXISTS idx_tasks_workspace_status ON tasks(workspace_id, status);
CREATE INDEX IF NOT EXISTS idx_messages_channel_created_at ON messages(channel_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_action_logs_workspace_id ON agent_action_logs(workspace_id, created_at DESC);

INSERT INTO workspaces (id, slug, name)
VALUES ('00000000-0000-0000-0000-000000000001', 'fbr-click', 'FBR-CLICK')
ON CONFLICT (id) DO NOTHING;

INSERT INTO users (id, workspace_id, email, full_name, role)
VALUES ('11111111-1111-1111-1111-111111111111', '00000000-0000-0000-0000-000000000001', 'admin@fbr.local', 'Admin FBR', 'admin')
ON CONFLICT (id) DO NOTHING;

INSERT INTO spaces (id, workspace_id, slug, name)
VALUES
    ('20000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'comercial', 'Comercial'),
    ('20000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'operacoes', 'Operacoes')
ON CONFLICT (id) DO NOTHING;

INSERT INTO channels (id, workspace_id, space_id, slug, name, channel_type)
VALUES
    ('30000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'leads-qualificados', 'Leads Qualificados', 'sales'),
    ('30000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002', 'geral', 'Geral', 'general')
ON CONFLICT (id) DO NOTHING;

INSERT INTO agents (id, workspace_id, slug, display_name, status)
VALUES
    ('40000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'comercial-bot', 'Comercial Bot', 'online'),
    ('40000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'report-bot', 'Report Bot', 'online')
ON CONFLICT (id) DO NOTHING;

INSERT INTO lead_intakes (id, workspace_id, source_type, source_system, external_reference, lead_name, company_name, email, score, temperature, metadata)
VALUES
    ('50000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', 'fbr_leads', '1FBR-Leads', 'lead-001', 'Mariana Sales', 'Acme Ltda', 'mariana@acme.com', 82, 'warm', '{"campaign":"similarity-outreach"}'::jsonb),
    ('50000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', 'social_media', 'Instagram Ads', 'social-001', 'Carlos Rocha', 'Rocha Store', 'carlos@rocha.com', 61, 'warm', '{"campaign":"meta-ads"}'::jsonb)
ON CONFLICT (id) DO NOTHING;

INSERT INTO deals (id, workspace_id, lead_intake_id, channel_id, assignee_user_id, company_name, contact_name, contact_email, value_cents, stage, origin_badge, score)
VALUES
    ('60000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Acme Ltda', 'Mariana Sales', 'mariana@acme.com', 150000, 'qualification', 'fbr-leads', 82),
    ('60000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '50000000-0000-0000-0000-000000000002', '30000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Rocha Store', 'Carlos Rocha', 'carlos@rocha.com', 99000, 'prospecting', 'social-media', 61)
ON CONFLICT (id) DO NOTHING;

INSERT INTO tasks (id, workspace_id, deal_id, channel_id, assignee_user_id, title, description, status, priority, source)
VALUES
    ('70000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '60000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'Agendar discovery call', 'Lead aquecido vindo do FBR-Leads.', 'todo', 'high', 'agent')
ON CONFLICT (id) DO NOTHING;

INSERT INTO messages (id, workspace_id, channel_id, author_type, author_id, body, source_system)
VALUES
    ('80000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '30000000-0000-0000-0000-000000000001', 'agent', '40000000-0000-0000-0000-000000000001', 'Novo lead aquecido recebido do FBR-Leads e convertido em deal.', '1FBR-Leads')
ON CONFLICT (id) DO NOTHING;
