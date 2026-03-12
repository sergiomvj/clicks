CREATE TABLE IF NOT EXISTS git_watchers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    repository_path TEXT NOT NULL,
    branch TEXT NOT NULL DEFAULT 'main',
    status TEXT NOT NULL DEFAULT 'idle',
    last_seen_commit TEXT,
    last_synced_at TIMESTAMPTZ,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (workspace_id, repository_path)
);

CREATE INDEX IF NOT EXISTS idx_git_watchers_workspace_id ON git_watchers(workspace_id, updated_at DESC);

CREATE OR REPLACE FUNCTION prevent_agent_action_logs_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'agent_action_logs is append-only';
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'git_watchers_updated_at_trigger') THEN
        CREATE TRIGGER git_watchers_updated_at_trigger BEFORE UPDATE ON git_watchers FOR EACH ROW EXECUTE FUNCTION update_updated_at();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'agent_action_logs_no_update_trigger') THEN
        CREATE TRIGGER agent_action_logs_no_update_trigger BEFORE UPDATE ON agent_action_logs FOR EACH ROW EXECUTE FUNCTION prevent_agent_action_logs_mutation();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'agent_action_logs_no_delete_trigger') THEN
        CREATE TRIGGER agent_action_logs_no_delete_trigger BEFORE DELETE ON agent_action_logs FOR EACH ROW EXECUTE FUNCTION prevent_agent_action_logs_mutation();
    END IF;
END;
$$;
