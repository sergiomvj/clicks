"use client";

import { useLeads } from "@/hooks/useLeads";

export default function LeadsPage() {
  const { items, loading, error } = useLeads();

  return (
    <section className="stack">
      <div className="stack">
        <span className="eyebrow">Leads</span>
        <h1 className="page-title">Pipeline com filtros por stage, score e campanha</h1>
        <p className="muted">Consumo inicial do endpoint real `/api/proxy/leads`.</p>
      </div>

      <article className="surface-card stack">
        {loading ? <p>Carregando leads...</p> : null}
        {error ? <p>Falha ao carregar leads: {error}</p> : null}
        {!loading && !error ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Lead</th>
                <th>Empresa</th>
                <th>Score</th>
                <th>Stage</th>
                <th>Fonte</th>
              </tr>
            </thead>
            <tbody>
              {items.map((lead) => (
                <tr key={lead.id}>
                  <td>{lead.name || "Sem nome"}</td>
                  <td>{lead.company_name || "Sem empresa"}</td>
                  <td>{lead.score}</td>
                  <td>{lead.funnel_stage}</td>
                  <td>{lead.source || "n/a"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}
      </article>
    </section>
  );
}
