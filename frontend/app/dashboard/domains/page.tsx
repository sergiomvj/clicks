"use client";

import { StatusPill } from "@/components/ui/StatusPill";
import { useDomains } from "@/hooks/useDomains";

export default function DomainsPage() {
  const { items, loading, error } = useDomains();

  return (
    <section className="stack">
      <div className="stack">
        <span className="eyebrow">Domains</span>
        <h1 className="page-title">Saude dos dominios em tempo real</h1>
        <p className="muted">Dados carregados do backend via `/api/proxy/domains`.</p>
      </div>

      {loading ? <article className="surface-card">Carregando dominios...</article> : null}
      {error ? <article className="surface-card">Falha ao carregar dominios: {error}</article> : null}

      {!loading && !error ? (
        <div className="card-grid">
          {items.map((domain) => (
            <article key={domain.id} className="surface-card stack">
              <h2 className="section-title">{domain.domain}</h2>
              <StatusPill
                label={domain.health_status}
                tone={
                  domain.health_status === "healthy"
                    ? "good"
                    : domain.health_status === "alert"
                      ? "warn"
                      : "bad"
                }
              />
              <p className="muted">
                Warm phase {domain.warm_phase} | {domain.sends_today} de {domain.daily_limit} envios | bounce {domain.bounce_rate}%
              </p>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  );
}
