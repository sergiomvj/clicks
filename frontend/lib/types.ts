export interface SpaceRecord { id: string; workspace_id: string; slug: string; name: string; }
export interface ChannelRecord { id: string; workspace_id: string; space_id: string; slug: string; name: string; channel_type: string; }
export interface DealRecord { id: string; company_name: string; contact_name?: string | null; contact_email?: string | null; stage: string; origin_badge: string; score?: number | null; }
export interface TaskRecord { id: string; title: string; status: string; priority: string; source: string; due_at?: string | null; }
export interface MessageRecord {
  id: string;
  channel_id: string;
  author_type: string;
  author_id: string;
  body: string;
  source_system?: string | null;
  created_at: string;
}
export interface AgentRecord {
  id: string;
  slug: string;
  display_name: string;
  status: string;
  repository_url?: string | null;
  scope_actions: string[];
  approval_required_actions: string[];
  owners: string[];
  kill_switch_active: boolean;
}
export interface GitWatcherRecord {
  id: string;
  workspace_id: string;
  agent_id?: string | null;
  repository_path: string;
  branch: string;
  status: string;
  last_seen_commit?: string | null;
  last_synced_at?: string | null;
  last_error?: string | null;
  created_at: string;
  updated_at: string;
}
export interface AgentControlRecord {
  workspace_id: string;
  kill_switch_active: boolean;
  reason?: string | null;
  updated_by_user_id?: string | null;
  updated_at?: string | null;
}
export interface ApprovalRecord {
  id: string;
  workspace_id: string;
  agent_id?: string | null;
  action_type: string;
  status: string;
  requested_by_user_id?: string | null;
  resolved_by_user_id?: string | null;
  decision_notes?: string | null;
  expires_at?: string | null;
  expired: boolean;
  payload: Record<string, unknown>;
  requested_at: string;
  resolved_at?: string | null;
}
