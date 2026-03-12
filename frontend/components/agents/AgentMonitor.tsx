import type { AgentRecord, GitWatcherRecord } from "@/lib/types";

function getWatcherForAgent(agent: AgentRecord, watchers: GitWatcherRecord[]) {
  return watchers.find((watcher) => watcher.agent_id === agent.id || watcher.repository_path === agent.repository_url);
}

export function AgentMonitor({ agents, watchers = [] }: { agents: AgentRecord[]; watchers?: GitWatcherRecord[] }) {
  return (
    <section className="surface-card stack">
      <div className="section-header">
        <div className="stack-tight">
          <h2 className="section-title">Monitor de agentes</h2>
          <p className="muted">Visao unificada de status operacional, escopo e repositores observados pelo git watcher.</p>
        </div>
        <span className="agent-badge">{watchers.length} watchers ativos</span>
      </div>
      {agents.map((agent) => {
        const watcher = getWatcherForAgent(agent, watchers);
        return (
          <article key={agent.id} className="stack agent-monitor-card">
            <div className="row-inline">
              <div className="status-pill">
                {agent.display_name} {agent.status} {agent.kill_switch_active ? "paused" : "live"}
              </div>
              {watcher ? <span className="origin-badge">git {watcher.status}</span> : <span className="origin-badge">sem watcher</span>}
            </div>
            <p className="muted">Slug: {agent.slug}</p>
            <p className="muted">Owners: {agent.owners.join(", ") || "Nao definido"}</p>
            <p className="muted">Scope: {agent.scope_actions.join(", ") || "Sem escopo mapeado"}</p>
            <p className="muted">Approval obrigatorio: {agent.approval_required_actions.join(", ") || "Nenhum"}</p>
            {watcher && (
              <div className="stack-tight">
                <p className="muted">Repo: {watcher.repository_path}</p>
                <p className="muted">Branch: {watcher.branch}</p>
                {watcher.last_seen_commit && <p className="muted">Ultimo commit: {watcher.last_seen_commit}</p>}
                {watcher.last_synced_at && <p className="muted">Ultima sincronizacao: {new Date(watcher.last_synced_at).toLocaleString("pt-BR")}</p>}
                {watcher.last_error && <p className="muted">Ultimo erro: {watcher.last_error}</p>}
              </div>
            )}
          </article>
        );
      })}
      {!agents.length && <p className="muted">Nenhum agente registrado ainda.</p>}
    </section>
  );
}
