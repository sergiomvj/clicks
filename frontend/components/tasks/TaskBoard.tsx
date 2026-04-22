import type { TaskRecord } from "@/lib/types";

function getTaskTone(task: TaskRecord) {
  if (task.source === "agent") {
    return "task-card task-card-agent";
  }
  return "task-card";
}

function getPriorityLabel(priority: string) {
  const labels: Record<string, string> = {
    p0: "P0",
    p1: "P1",
    p2: "P2",
    p3: "P3",
  };
  return labels[priority] ?? priority.toUpperCase();
}

export function TaskBoard({ tasks }: { tasks: TaskRecord[] }) {
  const agentTasks = tasks.filter((task) => task.source === "agent").length;
  const pendingTasks = tasks.filter((task) => task.status !== "done").length;
  const highPriority = tasks.filter((task) => ["p0", "p1", "high", "urgent", "critical"].includes(task.priority)).length;

  return (
    <section className="surface-card stack">
      <div className="section-header">
        <div className="stack-tight">
          <h2 className="section-title">Tarefas</h2>
          <span className="muted">{agentTasks} criadas por agentes e {pendingTasks} ainda em aberto.</span>
        </div>
        <span className="agent-badge">{tasks.length} tarefas</span>
      </div>
      <div className="mini-metrics-grid">
        <article className="mini-metric-card">
          <strong>{pendingTasks}</strong>
          <span>Pendentes</span>
        </article>
        <article className="mini-metric-card">
          <strong>{highPriority}</strong>
          <span>Prioridade alta</span>
        </article>
        <article className="mini-metric-card">
          <strong>{agentTasks}</strong>
          <span>Originadas por agentes</span>
        </article>
      </div>
      <div className="task-grid">
        {tasks.map((task) => (
          <article key={task.id} className={getTaskTone(task)}>
            <div className="row-inline">
              <strong>{task.title}</strong>
              {task.source === "agent" ? <span className="agent-badge">agent-api</span> : <span className="origin-badge">{task.source}</span>}
            </div>
            <div className="row-inline">
              <span className="status-pill">{task.status}</span>
              <span className="status-pill">Prioridade {getPriorityLabel(task.priority)}</span>
            </div>
            {task.due_at && <p className="muted">Vencimento: {new Date(task.due_at).toLocaleString("pt-BR")}</p>}
          </article>
        ))}
      </div>
      {!tasks.length && <p className="muted">Nenhuma tarefa registrada.</p>}
    </section>
  );
}
