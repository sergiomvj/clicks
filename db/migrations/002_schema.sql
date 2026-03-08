CREATE TABLE workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  owner_id UUID NOT NULL REFERENCES auth.users(id),
  settings JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE domains (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  domain TEXT NOT NULL,
  warm_phase SMALLINT NOT NULL DEFAULT 1 CHECK (warm_phase BETWEEN 1 AND 4),
  daily_limit SMALLINT NOT NULL DEFAULT 10,
  sends_today SMALLINT NOT NULL DEFAULT 0,
  reputation_score SMALLINT NOT NULL DEFAULT 100 CHECK (reputation_score BETWEEN 0 AND 100),
  bounce_rate NUMERIC(5,2) NOT NULL DEFAULT 0,
  is_blacklisted BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  warm_started_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (workspace_id, domain)
);

CREATE TABLE icp_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  sectors TEXT[] NOT NULL DEFAULT '{}'::text[],
  company_sizes TEXT[] NOT NULL DEFAULT '{}'::text[],
  target_roles TEXT[] NOT NULL DEFAULT '{}'::text[],
  regions TEXT[] NOT NULL DEFAULT '{}'::text[],
  keywords TEXT[] NOT NULL DEFAULT '{}'::text[],
  min_score SMALLINT NOT NULL DEFAULT 60 CHECK (min_score BETWEEN 0 AND 100),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE campaigns (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
  icp_profile_id UUID REFERENCES icp_profiles(id) ON DELETE SET NULL,
  name TEXT,
  email TEXT,
  email_valid BOOLEAN,
  role TEXT,
  linkedin_url TEXT,
  company_name TEXT,
  company_cnpj TEXT,
  company_sector TEXT,
  company_size TEXT,
  company_website TEXT,
  score SMALLINT NOT NULL DEFAULT 0 CHECK (score BETWEEN 0 AND 100),
  funnel_stage TEXT NOT NULL DEFAULT 'captured' CHECK (
    funnel_stage IN ('captured', 'enriching', 'validated', 'warming', 'qualified', 'sql', 'discard')
  ),
  source TEXT,
  enrichment_data JSONB NOT NULL DEFAULT '{}'::jsonb,
  discard_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE email_sequences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  touch_number SMALLINT NOT NULL CHECK (touch_number BETWEEN 1 AND 4),
  day_offset SMALLINT NOT NULL,
  subject TEXT,
  body TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (campaign_id, touch_number)
);

CREATE TABLE email_sends (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
  sequence_id UUID REFERENCES email_sequences(id) ON DELETE SET NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (
    status IN ('pending', 'sent', 'bounced', 'opened', 'clicked', 'replied')
  ),
  sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
  email_send_id UUID REFERENCES email_sends(id) ON DELETE SET NULL,
  type TEXT NOT NULL CHECK (type IN ('open', 'click', 'reply', 'opt_out', 'bounce')),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE intelligence_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  campaign_id UUID REFERENCES campaigns(id) ON DELETE SET NULL,
  content JSONB NOT NULL DEFAULT '{}'::jsonb,
  insights TEXT,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE agent_action_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  agent_id TEXT NOT NULL,
  team TEXT NOT NULL,
  action_type TEXT NOT NULL,
  trigger_type TEXT NOT NULL,
  payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  result JSONB,
  error TEXT,
  executed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
