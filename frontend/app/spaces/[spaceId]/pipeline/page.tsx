import { ApprovalQueue } from "@/components/agents/ApprovalQueue";
import { PipelineKanban } from "@/components/crm/PipelineKanban";
import { RealtimeWorkspaceBridge } from "@/components/realtime/RealtimeWorkspaceBridge";
import { getApprovals, getDeals } from "@/lib/server-api";

export default async function PipelinePage({ params }: { params: Promise<{ spaceId: string }> }) {
  const { spaceId } = await params;
  const [deals, approvals] = await Promise.all([getDeals(), getApprovals()]);
  const fbrLeadsDeals = deals.filter((deal) => deal.origin_badge === "fbr-leads").length;

  return (
    <div className="stack">
      <RealtimeWorkspaceBridge workspaceId={spaceId} />
      <section className="header-row">
        <div className="surface-card stack">
          <div className="eyebrow">Pipeline Comercial</div>
          <h1 className="page-title">O funil agora destaca o que veio aquecido do 1FBR-Leads.</h1>
          <p className="muted">Deals vindos do motor de aquecimento entram com mais contraste visual para acelerar leitura e decisao operacional.</p>
        </div>
        <div className="surface-card stack">
          <div className="metric-value">{deals.length}</div>
          <div className="metric-label">deals no pipeline</div>
          <div className="metric-value">{fbrLeadsDeals}</div>
          <div className="metric-label">deals com origem 1FBR-Leads</div>
        </div>
      </section>
      <PipelineKanban deals={deals} />
      <ApprovalQueue approvals={approvals} />
    </div>
  );
}
