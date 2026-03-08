INSERT INTO auth.users (id, email)
VALUES ('00000000-0000-0000-0000-000000000001', 'owner@facebrasil.test')
ON CONFLICT (id) DO NOTHING;

INSERT INTO workspaces (id, name, slug, owner_id, settings)
VALUES (
  '10000000-0000-0000-0000-000000000001',
  'Facebrasil Demo',
  'facebrasil-demo',
  '00000000-0000-0000-0000-000000000001',
  '{"timezone": "America/Sao_Paulo", "channel": "#leads-qualificados"}'::jsonb
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO domains (
  id,
  workspace_id,
  domain,
  warm_phase,
  daily_limit,
  sends_today,
  reputation_score,
  bounce_rate,
  is_blacklisted,
  is_active,
  warm_started_at
)
VALUES (
  '20000000-0000-0000-0000-000000000001',
  '10000000-0000-0000-0000-000000000001',
  'mail.facebrasil-demo.test',
  1,
  10,
  0,
  100,
  0,
  false,
  true,
  now()
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO icp_profiles (
  id,
  workspace_id,
  name,
  sectors,
  company_sizes,
  target_roles,
  regions,
  keywords,
  min_score
)
VALUES (
  '30000000-0000-0000-0000-000000000001',
  '10000000-0000-0000-0000-000000000001',
  'Empresas Brasileiras nos EUA',
  ARRAY['midia', 'marketing', 'servicos digitais'],
  ARRAY['media', 'grande'],
  ARRAY['CEO', 'Diretor de Marketing', 'Head de Growth'],
  ARRAY['Florida', 'Texas', 'New York'],
  ARRAY['comunidade brasileira', 'publicidade', 'expansao internacional'],
  70
)
ON CONFLICT (id) DO NOTHING;
