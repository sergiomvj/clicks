import { MetricCard } from "@/components/ui/MetricCard";
import { StatusPill } from "@/components/ui/StatusPill";

export default function DashboardPage() {
  return (
    <section className="page-shell">
      <header className="header-row">
        <div className="stack">
          <span className="eyebrow">Overview</span>
          <h1 className="page-title">Saude da operacao outbound em um so painel</h1>
          <p className="muted">Leads, dominios, agentes e SQLs monitorados a partir do proxy autenticado do Next.</p>
        </div>
        <div className="surface-card stack">
          <span className="section-title">Estado atual</span>
          <StatusPill label="LLM layer 1 online" tone="good" />
          <StatusPill label="Bounce em observacao" tone="warn" />
        </div>
      </header>

      <div className="metric-grid">
        <MetricCard label="Leads hoje" value="124" hint="18 acima da media semanal" />
        <MetricCard label="SQLs gerados" value="09" hint="3 enviados ao FBR-Click" />
        <MetricCard label="Bounce rate" value="1.4%" hint="Abaixo do limite critico" />
        <MetricCard label="Dominios ativos" value="04" hint="1 em warm phase 2" />
      </div>

      <div className="card-grid">
        <article className="surface-card stack">
          <h2 className="section-title">Prioridades do dia</h2>
          <ul className="list">
            <li>Confirmar handoff dos SQLs com mais score.</li>
            <li>Subir o dashboard em paralelo ao aquecimento.</li>
            <li>Validar webhooks Postal e FBR-Click.</li>
          </ul>
        </article>
        <article className="surface-card stack">
          <h2 className="section-title">Sinais recentes</h2>
          <ul className="list">
            <li>LinkedIn premium segue estavel nas ultimas 24h.</li>
            <li>OpenClaw scaffold pronto para registro dos agentes.</li>
            <li>Backend Batch 3 estruturado e protegido por headers.</li>
          </ul>
        </article>
      </div>
    </section>
  );
}
