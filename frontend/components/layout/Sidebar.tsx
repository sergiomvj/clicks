"use client";

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

const CHANNEL_TYPE_LABELS: Record<string, string> = {
  general: "Geral",
  deal: "Deals",
  task: "Tarefas",
  system: "Sistema",
  "agent-log": "Agent Log",
};

function groupChannels(channels: ChannelRecord[]) {
  return channels.reduce<Record<string, ChannelRecord[]>>((acc, channel) => {
    const key = channel.channel_type || "other";
    acc[key] = [...(acc[key] || []), channel];
    return acc;
  }, {});
}

export function Sidebar({ spaces, channels }: SidebarProps) {
  const totalChannels = channels.length;
  const groupedChannels = groupChannels(channels);

  return (
    <aside className="sidebar stack">
      <div className="sidebar-hero stack-tight">
        <div className="eyebrow">FBR-CLICK</div>
        <div className="brand-mark">Hub vivo de operacao</div>
        <p className="muted">Base central do ecossistema para deals, tarefas, agentes, sistema e observacao operacional.</p>
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
        <button className="sidebar-link sidebar-help-link" type="button" onClick={() => window.dispatchEvent(new CustomEvent("fbr-help:open"))}>
          Preciso de Ajuda
        </button>
      </nav>
      <section className="sidebar-group">
        <div className="eyebrow">Spaces</div>
        {spaces.map((space) => (
          <Link key={space.id} className="sidebar-link" href={`/spaces/${space.id}/channels/${channels.find((channel) => channel.space_id === space.id)?.id ?? ""}`}>
            {space.name}
          </Link>
        ))}
      </section>
      {Object.entries(groupedChannels).map(([channelType, items]) => (
        <section className="sidebar-group" key={channelType}>
          <div className="eyebrow">{CHANNEL_TYPE_LABELS[channelType] ?? channelType}</div>
          {items.map((channel) => (
            <Link key={channel.id} className="sidebar-link" href={`/spaces/${channel.space_id}/channels/${channel.id}`}>
              #{channel.slug}
            </Link>
          ))}
        </section>
      ))}
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
