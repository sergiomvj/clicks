import Link from "next/link";

import type { ChannelRecord, SpaceRecord } from "@/lib/types";

interface SidebarProps {
  spaces: SpaceRecord[];
  channels: ChannelRecord[];
}

const AGENT_LABELS = [
  "Comercial Bot",
  "Report Bot",
  "Onboarding Bot",
  "Approval Bot",
  "Content Bot",
  "Ads Bot",
];

export function Sidebar({ spaces, channels }: SidebarProps) {
  const totalChannels = channels.length;

  return (
    <aside className="sidebar stack">
      <div className="sidebar-hero stack-tight">
        <div className="eyebrow">FBR-CLICK</div>
        <div className="brand-mark">Pipeline vivo</div>
        <p className="muted">Base comercial que concentra leads do 1FBR-Leads, site, redes sociais e outras entradas operacionais.</p>
        <div className="sidebar-stats">
          <div>
            <strong>{spaces.length}</strong>
            <span>spaces</span>
          </div>
          <div>
            <strong>{totalChannels}</strong>
            <span>canais</span>
          </div>
        </div>
      </div>
      <nav>
        <Link className="sidebar-link active" href="/spaces">Visao geral</Link>
      </nav>
      <section className="sidebar-group">
        <div className="eyebrow">Spaces</div>
        {spaces.map((space) => (
          <Link key={space.id} className="sidebar-link" href={`/spaces/${space.id}/channels/${channels.find((channel) => channel.space_id === space.id)?.id ?? ""}`}>
            {space.name}
          </Link>
        ))}
      </section>
      <section className="sidebar-group">
        <div className="eyebrow">Canais</div>
        {channels.map((channel) => (
          <Link key={channel.id} className="sidebar-link" href={`/spaces/${channel.space_id}/channels/${channel.id}`}>
            #{channel.slug}
          </Link>
        ))}
      </section>
      <section className="sidebar-group">
        <div className="eyebrow">Agentes ativos</div>
        <div className="agent-stack">
          {AGENT_LABELS.map((label) => (
            <div key={label} className="agent-badge">AGENTE {label}</div>
          ))}
        </div>
      </section>
      <form action="/api/auth/logout" method="post">
        <button className="button-secondary" type="submit">Sair</button>
      </form>
    </aside>
  );
}
