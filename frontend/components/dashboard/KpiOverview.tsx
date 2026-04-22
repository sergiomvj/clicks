import type { KpiRecord } from "@/lib/types";

function formatValue(kpi: KpiRecord) {
  if (kpi.unit === "%") {
    return `${kpi.current_value.toFixed(0)}%`;
  }
  if (kpi.unit === "count") {
    return `${kpi.current_value.toFixed(0)}`;
  }
  return `${kpi.current_value}`;
}

function formatTarget(kpi: KpiRecord) {
  if (kpi.unit === "%") {
    return `${kpi.target_value.toFixed(0)}%`;
  }
  if (kpi.unit === "count") {
    return `${kpi.target_value.toFixed(0)}`;
  }
  return `${kpi.target_value}`;
}

export function KpiOverview({ kpis }: { kpis: KpiRecord[] }) {
  if (!kpis.length) {
    return null;
  }

  return (
    <section className="kpi-overview surface-card">
      <div className="section-header">
        <div className="stack-tight">
          <h2 className="section-title">KPIs operacionais</h2>
          <p className="muted">Leitura rapida do estado atual da operacao frente aos alvos do conceito.</p>
        </div>
        <span className="agent-badge">{kpis.length} indicadores ativos</span>
      </div>
      <div className="kpi-overview-grid">
        {kpis.map((kpi) => (
          <article key={kpi.id} className={`kpi-overview-card kpi-status-${kpi.status}`}>
            <div className="row-inline">
              <strong>{kpi.name}</strong>
              <span className="origin-badge">{kpi.status}</span>
            </div>
            <div className="metric-value">{formatValue(kpi)}</div>
            <p className="muted">Meta: {formatTarget(kpi)}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
