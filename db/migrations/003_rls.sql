ALTER TABLE workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sequences ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_sends ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE intelligence_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_action_logs ENABLE ROW LEVEL SECURITY;

ALTER TABLE workspaces FORCE ROW LEVEL SECURITY;
ALTER TABLE domains FORCE ROW LEVEL SECURITY;
ALTER TABLE icp_profiles FORCE ROW LEVEL SECURITY;
ALTER TABLE campaigns FORCE ROW LEVEL SECURITY;
ALTER TABLE leads FORCE ROW LEVEL SECURITY;
ALTER TABLE email_sequences FORCE ROW LEVEL SECURITY;
ALTER TABLE email_sends FORCE ROW LEVEL SECURITY;
ALTER TABLE interactions FORCE ROW LEVEL SECURITY;
ALTER TABLE intelligence_reports FORCE ROW LEVEL SECURITY;
ALTER TABLE agent_action_logs FORCE ROW LEVEL SECURITY;

CREATE POLICY workspaces_select_own ON workspaces
  FOR SELECT USING (owner_id = auth.uid());

CREATE POLICY workspaces_insert_own ON workspaces
  FOR INSERT WITH CHECK (owner_id = auth.uid());

CREATE POLICY workspaces_update_own ON workspaces
  FOR UPDATE USING (owner_id = auth.uid())
  WITH CHECK (owner_id = auth.uid());

CREATE POLICY workspaces_delete_own ON workspaces
  FOR DELETE USING (owner_id = auth.uid());

CREATE POLICY domains_select_workspace ON domains
  FOR SELECT USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY domains_insert_workspace ON domains
  FOR INSERT WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY domains_update_workspace ON domains
  FOR UPDATE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  ) WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY domains_delete_workspace ON domains
  FOR DELETE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY icp_profiles_select_workspace ON icp_profiles
  FOR SELECT USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY icp_profiles_insert_workspace ON icp_profiles
  FOR INSERT WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY icp_profiles_update_workspace ON icp_profiles
  FOR UPDATE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  ) WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY icp_profiles_delete_workspace ON icp_profiles
  FOR DELETE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY campaigns_select_workspace ON campaigns
  FOR SELECT USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY campaigns_insert_workspace ON campaigns
  FOR INSERT WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY campaigns_update_workspace ON campaigns
  FOR UPDATE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  ) WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY campaigns_delete_workspace ON campaigns
  FOR DELETE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY leads_select_workspace ON leads
  FOR SELECT USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY leads_insert_workspace ON leads
  FOR INSERT WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY leads_update_workspace ON leads
  FOR UPDATE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  ) WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY leads_delete_workspace ON leads
  FOR DELETE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY email_sequences_select_workspace ON email_sequences
  FOR SELECT USING (
    EXISTS (
      SELECT 1
      FROM campaigns
      WHERE campaigns.id = email_sequences.campaign_id
        AND campaigns.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY email_sequences_insert_workspace ON email_sequences
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1
      FROM campaigns
      WHERE campaigns.id = email_sequences.campaign_id
        AND campaigns.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY email_sequences_update_workspace ON email_sequences
  FOR UPDATE USING (
    EXISTS (
      SELECT 1
      FROM campaigns
      WHERE campaigns.id = email_sequences.campaign_id
        AND campaigns.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  ) WITH CHECK (
    EXISTS (
      SELECT 1
      FROM campaigns
      WHERE campaigns.id = email_sequences.campaign_id
        AND campaigns.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY email_sequences_delete_workspace ON email_sequences
  FOR DELETE USING (
    EXISTS (
      SELECT 1
      FROM campaigns
      WHERE campaigns.id = email_sequences.campaign_id
        AND campaigns.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY email_sends_select_workspace ON email_sends
  FOR SELECT USING (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = email_sends.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY email_sends_insert_workspace ON email_sends
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = email_sends.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY email_sends_update_workspace ON email_sends
  FOR UPDATE USING (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = email_sends.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  ) WITH CHECK (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = email_sends.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY email_sends_delete_workspace ON email_sends
  FOR DELETE USING (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = email_sends.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY interactions_select_workspace ON interactions
  FOR SELECT USING (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = interactions.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY interactions_insert_workspace ON interactions
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = interactions.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY interactions_update_workspace ON interactions
  FOR UPDATE USING (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = interactions.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  ) WITH CHECK (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = interactions.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY interactions_delete_workspace ON interactions
  FOR DELETE USING (
    EXISTS (
      SELECT 1
      FROM leads
      WHERE leads.id = interactions.lead_id
        AND leads.workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
    )
  );

CREATE POLICY intelligence_reports_select_workspace ON intelligence_reports
  FOR SELECT USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY intelligence_reports_insert_workspace ON intelligence_reports
  FOR INSERT WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY intelligence_reports_update_workspace ON intelligence_reports
  FOR UPDATE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  ) WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY intelligence_reports_delete_workspace ON intelligence_reports
  FOR DELETE USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY agent_action_logs_select_workspace ON agent_action_logs
  FOR SELECT USING (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );

CREATE POLICY agent_action_logs_insert_workspace ON agent_action_logs
  FOR INSERT WITH CHECK (
    workspace_id IN (SELECT id FROM workspaces WHERE owner_id = auth.uid())
  );
