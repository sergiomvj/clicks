"use client";

import { useReports } from "@/hooks/useReports";

export default function ReportsPage() {
  const { items, loading, error } = useReports();

  return (
    <section className="stack">
      <div className="stack">
        <span className="eyebrow">Reports</span>
        <h1 className="page-title">Relatorios executivos e feedback loop</h1>
        <p className="muted">Leitura inicial do endpoint `/api/proxy/intelligence/report`.</p>
      </div>
      <article className="surface-card stack">
        {loading ? <p>Carregando relatorios...</p> : null}
        {error ? <p>Falha ao carregar relatorios: {error}</p> : null}
        {!loading && !error && items.length === 0 ? <p>Nenhum relatorio disponivel ainda.</p> : null}
        {!loading && !error && items.length > 0
          ? items.map((report) => (
              <div key={report.id} className="stack">
                <h2 className="section-title">{new Date(report.generated_at).toLocaleDateString("pt-BR")}</h2>
                <p className="muted">{report.insights || "Sem insights resumidos."}</p>
              </div>
            ))
          : null}
      </article>
    </section>
  );
}
