import { ApprovalQueue } from "@/components/agents/ApprovalQueue";
import { AgentControlPanel } from "@/components/agents/AgentControlPanel";
import { AgentMonitor } from "@/components/agents/AgentMonitor";
import { RealtimeWorkspaceBridge } from "@/components/realtime/RealtimeWorkspaceBridge";
import { getAgentControl, getAgents, getApprovals, getGitWatchers } from "@/lib/server-api";

export default async function AgentsSettingsPage({ params }: { params: Promise<{ spaceId: string }> }) {
  const { spaceId } = await params;
  const [agents, watchers, control, approvals] = await Promise.all([getAgents(), getGitWatchers(), getAgentControl(), getApprovals()]);

  return (
    <div className="stack">
      <RealtimeWorkspaceBridge workspaceId={spaceId} />
      <AgentControlPanel control={control} />
      <div className="card-grid">
        <AgentMonitor agents={agents} watchers={watchers} />
        <ApprovalQueue approvals={approvals} />
      </div>
    </div>
  );
}
