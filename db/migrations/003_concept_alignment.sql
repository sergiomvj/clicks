CREATE TABLE IF NOT EXISTS kpis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    space_id UUID REFERENCES spaces(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    unit TEXT NOT NULL DEFAULT 'count',
    target_value NUMERIC(12,2) NOT NULL DEFAULT 0,
    current_value NUMERIC(12,2) NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'neutral',
    source TEXT NOT NULL DEFAULT 'manual',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, slug)
);

CREATE TABLE IF NOT EXISTS agent_markdown_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    git_sha TEXT NOT NULL DEFAULT 'unversioned',
    content TEXT NOT NULL,
    repository_path TEXT NOT NULL,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (agent_id, file_name)
);

CREATE INDEX IF NOT EXISTS idx_kpis_workspace_id ON kpis(workspace_id, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_markdown_cache_agent_id ON agent_markdown_cache(agent_id, refreshed_at DESC);

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'kpis_updated_at_trigger') THEN
        CREATE TRIGGER kpis_updated_at_trigger BEFORE UPDATE ON kpis FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'agent_markdown_cache_updated_at_trigger') THEN
        CREATE TRIGGER agent_markdown_cache_updated_at_trigger BEFORE UPDATE ON agent_markdown_cache FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
END;
$$;

INSERT INTO kpis (id, workspace_id, space_id, slug, name, unit, target_value, current_value, status, source)
VALUES
    ('92000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'pipeline-cobertura', 'Cobertura do pipeline', '%', 100, 82, 'attention', 'seed'),
    ('92000000-0000-0000-0000-000000000002', '00000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000001', 'slas-follow-up', 'SLA de follow-up', '%', 95, 91, 'healthy', 'seed'),
    ('92000000-0000-0000-0000-000000000003', '00000000-0000-0000-0000-000000000001', '20000000-0000-0000-0000-000000000002', 'agentes-vivos', 'Agentes com heartbeat', 'count', 6, 4, 'attention', 'seed')
ON CONFLICT (id) DO NOTHING;
