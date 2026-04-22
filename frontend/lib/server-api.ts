import { getSession } from "@/lib/session";
import type { AgentControlRecord, AgentRecord, ApprovalRecord, ChannelRecord, DealRecord, GitWatcherRecord, KpiRecord, MessageRecord, SpaceRecord, TaskRecord } from "@/lib/types";

interface SpaceBundleResponse {
  spaces: SpaceRecord[];
  channels: ChannelRecord[];
}

interface MessageResponse {
  messages: MessageRecord[];
}

interface TaskResponse {
  tasks: TaskRecord[];
}

interface DealResponse {
  deals: DealRecord[];
}

interface AgentResponse {
  agents: AgentRecord[];
}

interface ApprovalResponse {
  approvals: ApprovalRecord[];
}

interface GitWatcherResponse {
  watchers: GitWatcherRecord[];
}

interface KpiResponse {
  kpis: KpiRecord[];
}

async function fetchBackend(path: string): Promise<Response> {
  const session = await getSession();
  if (!session.isLoggedIn || !session.userId || !session.workspaceId) {
    throw new Error("Session not available.");
  }

  const backendUrl = process.env.BACKEND_URL;
  if (!backendUrl) {
    throw new Error("BACKEND_URL is missing.");
  }

  return fetch(`${backendUrl}/api/${path}`, {
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": session.userId,
      "X-Workspace-Id": session.workspaceId,
    },
    cache: "no-store",
  });
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`Backend request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getSpaceBundle(): Promise<SpaceBundleResponse> {
  return parseJson<SpaceBundleResponse>(await fetchBackend("spaces"));
}

export async function getChannelMessages(channelId: string): Promise<MessageRecord[]> {
  const payload = await parseJson<MessageResponse>(await fetchBackend(`messages/${channelId}`));
  return payload.messages;
}

export async function getKpis(): Promise<KpiRecord[]> {
  const payload = await parseJson<KpiResponse>(await fetchBackend("kpis"));
  return payload.kpis;
}

export async function getTasks(): Promise<TaskRecord[]> {
  const payload = await parseJson<TaskResponse>(await fetchBackend("tasks"));
  return payload.tasks;
}

export async function getDeals(): Promise<DealRecord[]> {
  const payload = await parseJson<DealResponse>(await fetchBackend("deals"));
  return payload.deals;
}

export async function getAgents(): Promise<AgentRecord[]> {
  const payload = await parseJson<AgentResponse>(await fetchBackend("agents"));
  return payload.agents;
}

export async function getGitWatchers(): Promise<GitWatcherRecord[]> {
  const payload = await parseJson<GitWatcherResponse>(await fetchBackend("git-watcher"));
  return payload.watchers;
}

export async function getAgentControl(): Promise<AgentControlRecord> {
  return parseJson<AgentControlRecord>(await fetchBackend("agents/control"));
}

export async function getApprovals(): Promise<ApprovalRecord[]> {
  const payload = await parseJson<ApprovalResponse>(await fetchBackend("agents/approvals"));
  return payload.approvals;
}
