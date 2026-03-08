"use client";

import { useCampaigns } from "@/hooks/useCampaigns";

export default function CampaignsPage() {
  const { items, loading, error } = useCampaigns();

  return (
    <section className="stack">
      <div className="stack">
        <span className="eyebrow">Campaigns</span>
        <h1 className="page-title">Campanhas, escrita e dispatch em uma trilha unica</h1>
        <p className="muted">Leitura inicial do backend por `/api/proxy/campaigns`.</p>
      </div>
      <article className="surface-card stack">
        {loading ? <p>Carregando campanhas...</p> : null}
        {error ? <p>Falha ao carregar campanhas: {error}</p> : null}
        {!loading && !error ? (
          <ul className="list">
            {items.map((campaign) => (
              <li key={campaign.id}>
                {campaign.name} - status {campaign.status} - criada em {new Date(campaign.created_at).toLocaleDateString("pt-BR")}
              </li>
            ))}
          </ul>
        ) : null}
      </article>
    </section>
  );
}
