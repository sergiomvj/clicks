import { StatusPill } from "@/components/ui/StatusPill";

export default function AgentsPage() {
  return (
    <section className="stack">
      <div className="stack">
        <span className="eyebrow">Agents</span>
        <h1 className="page-title">Estado dos agentes e kill switch operacional</h1>
        <p className="muted">Estrutura pronta para SSE e visualizacao do audit log em tempo real.</p>
      </div>
      <div className="card-grid">
        <article className="surface-card stack">
          <h2 className="section-title">Guardiao de Dominios</h2>
          <StatusPill label="online" tone="good" />
        </article>
        <article className="surface-card stack">
          <h2 className="section-title">Cadenciador</h2>
          <StatusPill label="paused for review" tone="warn" />
        </article>
      </div>
    </section>
  );
}
