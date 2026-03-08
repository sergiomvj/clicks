export interface DomainItem {
  id: string;
  workspace_id: string;
  domain: string;
  warm_phase: number;
  daily_limit: number;
  sends_today: number;
  reputation_score: number;
  bounce_rate: number;
  is_blacklisted: boolean;
  is_active: boolean;
  health_status: string;
}

export interface LeadItem {
  id: string;
  name: string | null;
  email: string | null;
  company_name: string | null;
  score: number;
  funnel_stage: string;
  source: string | null;
  created_at: string;
}

export interface CampaignItem {
  id: string;
  name: string;
  status: string;
  created_at: string;
}

export interface ReportItem {
  id: string;
  insights: string | null;
  generated_at: string;
}
