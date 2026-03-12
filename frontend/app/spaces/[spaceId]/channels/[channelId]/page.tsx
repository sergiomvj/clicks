import { AgentMonitor } from "@/components/agents/AgentMonitor";
import { ApprovalQueue } from "@/components/agents/ApprovalQueue";
import { PipelineKanban } from "@/components/crm/PipelineKanban";
import { MessageList } from "@/components/messaging/MessageList";
import { RealtimeChannelBridge } from "@/components/realtime/RealtimeChannelBridge";
import { TaskBoard } from "@/components/tasks/TaskBoard";
import { getAgents, getApprovals, getChannelMessages, getDeals, getTasks } from "@/lib/server-api";

export default async function ChannelPage({ params }: { params: Promise<{ channelId: string }> }) {
  const { channelId } = await params;
  const [messages, deals, tasks, agents, approvals] = await Promise.all([
    getChannelMessages(channelId),
    getDeals(),
    getTasks(),
    getAgents(),
    getApprovals(),
  ]);

  const fbrLeadsDeals = deals.filter((deal) => deal.origin_badge === "fbr-leads").length;
  const agentTasks = tasks.filter((task) => task.source === "agent").length;
  const agentMessages = messages.filter((message) => message.author_type === "agent").length;

  return (
    <div className="page-shell stack">
      <RealtimeChannelBridge channelId={channelId} />
      <section className="header-row">
        <div className="surface-card stack">
          <div className="eyebrow">Workspace Comercial</div>
          <h1 className="page-title">Leads entram por varios canais, mas o 1FBR-Leads abastece o pipeline aquecido.</h1>
          <p className="muted">A operacao centraliza leads de redes sociais, site do produto e outras entradas, com destaque para os handoffs aquecidos vindos do 1FBR-Leads.</p>
        </div>
        <div className="surface-card stack">
          <div className="metric-value">{deals.length}</div>
          <div className="metric-label">deals ativos na base</div>
          <div className="metric-value">{fbrLeadsDeals}</div>
          <div className="metric-label">deals originados do 1FBR-Leads</div>
          <div className="metric-value">{agentTasks}</div>
          <div className="metric-label">tarefas criadas por agentes</div>
          <div className="metric-value">{agentMessages}</div>
          <div className="metric-label">mensagens do canal geradas por agentes</div>
        </div>
      </section>
      <div className="card-grid">
        <MessageList messages={messages} />
        <PipelineKanban deals={deals} />
      </div>
      <div className="card-grid">
        <TaskBoard tasks={tasks} />
        <AgentMonitor agents={agents} />
      </div>
      <div className="card-grid">
        <ApprovalQueue approvals={approvals} />
      </div>
    </div>
  );
}
