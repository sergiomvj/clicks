import type { DealRecord } from "@/lib/types";

const STAGE_LABELS: Record<string, string> = {
  first_contact: "Primeiro contato",
  qualification: "Qualificacao",
  proposal: "Proposta",
  negotiation: "Negociacao",
  follow_up: "Follow-up",
  reengagement: "Reengajamento",
  closed_won: "Ganho",
  closed_lost: "Perdido",
  cancelled: "Cancelado",
};

const STAGE_ORDER = [
  "first_contact",
  "qualification",
  "proposal",
  "negotiation",
  "follow_up",
  "reengagement",
  "closed_won",
  "closed_lost",
  "cancelled",
] as const;

function getStageLabel(stage: string) {
  return STAGE_LABELS[stage] ?? stage;
}

function getOriginLabel(origin: string) {
  if (origin === "fbr-leads") {
    return "1FBR-Leads";
  }
  if (origin === "social-media") {
    return "Redes sociais";
  }
  return origin;
}

export function PipelineKanban({ deals }: { deals: DealRecord[] }) {
  const grouped = STAGE_ORDER.map((stage) => ({
    stage,
    deals: deals.filter((deal) => deal.stage === stage),
  })).filter((group) => group.deals.length > 0);

  const fbrLeadsDeals = deals.filter((deal) => deal.origin_badge === "fbr-leads").length;
  const activeDeals = deals.filter((deal) => !["closed_won", "closed_lost", "cancelled"].includes(deal.stage)).length;
  const hotterDeals = deals.filter((deal) => deal.origin_badge === "fbr-leads" && !["closed_won", "closed_lost", "cancelled"].includes(deal.stage)).length;

  return (
    <section className="surface-card stack">
      <div className="section-header">
        <div className="stack-tight">
          <h2 className="section-title">Pipeline</h2>
          <p className="muted">{fbrLeadsDeals} deals do 1FBR-Leads destacados com prioridade visual.</p>
        </div>
        <span className="agent-badge">{deals.length} deals mapeados</span>
      </div>
      <div className="mini-metrics-grid">
        <article className="mini-metric-card">
          <strong>{activeDeals}</strong>
          <span>Em andamento</span>
        </article>
        <article className="mini-metric-card">
          <strong>{hotterDeals}</strong>
          <span>Quentes do 1FBR-Leads</span>
        </article>
        <article className="mini-metric-card">
          <strong>{grouped.length}</strong>
          <span>Stages com movimento</span>
        </article>
      </div>
      <div className="pipeline-grid">
        {grouped.map((group) => (
          <section key={group.stage} className="pipeline-column">
            <div className="pipeline-column-header">
              <div className="stack-tight">
                <strong>{getStageLabel(group.stage)}</strong>
                <span className="muted">{group.deals.reduce((sum, deal) => sum + (deal.score ?? 0), 0)} pontos acumulados</span>
              </div>
              <span className="status-pill">{group.deals.length}</span>
            </div>
            <div className="pipeline-column-body">
              {group.deals.map((deal) => {
                const fromFbrLeads = deal.origin_badge === "fbr-leads";
                return (
                  <article key={deal.id} className={`pipeline-deal ${fromFbrLeads ? "pipeline-deal-hot" : ""}`}>
                    <div className="row-inline">
                      <strong>{deal.company_name}</strong>
                      <span className={`origin-badge ${fromFbrLeads ? "origin-badge-hot" : ""}`}>{getOriginLabel(deal.origin_badge)}</span>
                    </div>
                    <p className="muted">Contato: {deal.contact_name || "Nao informado"}</p>
                    <div className="pipeline-deal-footer">
                      <span className="status-pill">Score {deal.score ?? "-"}</span>
                      {deal.contact_email && <span className="muted">{deal.contact_email}</span>}
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </section>
  );
}
