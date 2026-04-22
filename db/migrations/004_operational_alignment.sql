UPDATE tasks SET priority = 'p0' WHERE lower(priority) IN ('urgent', 'critical');
UPDATE tasks SET priority = 'p1' WHERE lower(priority) = 'high';
UPDATE tasks SET priority = 'p2' WHERE lower(priority) = 'medium';
UPDATE tasks SET priority = 'p3' WHERE lower(priority) IN ('low', 'backlog');

ALTER TABLE tasks
    ALTER COLUMN priority SET DEFAULT 'p2';

ALTER TABLE tasks
    DROP CONSTRAINT IF EXISTS tasks_priority_check;

ALTER TABLE tasks
    ADD CONSTRAINT tasks_priority_check CHECK (priority IN ('p0', 'p1', 'p2', 'p3'));

UPDATE channels SET channel_type = 'deal' WHERE channel_type = 'sales';

INSERT INTO channels (workspace_id, space_id, slug, name, channel_type)
SELECT s.workspace_id, s.id, s.slug || '-tarefas', 'Tarefas ' || s.name, 'task'
FROM spaces s
WHERE NOT EXISTS (
    SELECT 1 FROM channels c WHERE c.workspace_id = s.workspace_id AND c.space_id = s.id AND c.channel_type = 'task'
);

INSERT INTO channels (workspace_id, space_id, slug, name, channel_type)
SELECT s.workspace_id, s.id, s.slug || '-sistema', 'Sistema ' || s.name, 'system'
FROM spaces s
WHERE NOT EXISTS (
    SELECT 1 FROM channels c WHERE c.workspace_id = s.workspace_id AND c.space_id = s.id AND c.channel_type = 'system'
);

INSERT INTO channels (workspace_id, space_id, slug, name, channel_type)
SELECT s.workspace_id, s.id, s.slug || '-agent-log', 'Agent Log ' || s.name, 'agent-log'
FROM spaces s
WHERE NOT EXISTS (
    SELECT 1 FROM channels c WHERE c.workspace_id = s.workspace_id AND c.space_id = s.id AND c.channel_type = 'agent-log'
);
