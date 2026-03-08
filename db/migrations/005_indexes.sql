CREATE INDEX idx_leads_workspace ON leads(workspace_id);
CREATE INDEX idx_leads_funnel ON leads(workspace_id, funnel_stage);
CREATE INDEX idx_leads_score ON leads(workspace_id, score DESC);
CREATE INDEX idx_domains_active ON domains(workspace_id, is_active);
CREATE INDEX idx_sends_lead ON email_sends(lead_id, sent_at DESC);
CREATE INDEX idx_logs_workspace ON agent_action_logs(workspace_id, executed_at DESC);
CREATE INDEX idx_logs_agent ON agent_action_logs(agent_id, executed_at DESC);
