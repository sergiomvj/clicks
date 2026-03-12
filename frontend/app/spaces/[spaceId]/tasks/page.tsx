import { RealtimeWorkspaceBridge } from "@/components/realtime/RealtimeWorkspaceBridge";
import { TaskBoard } from "@/components/tasks/TaskBoard";
import { getTasks } from "@/lib/server-api";

export default async function TasksPage({ params }: { params: Promise<{ spaceId: string }> }) {
  const { spaceId } = await params;
  const tasks = await getTasks();

  return (
    <>
      <RealtimeWorkspaceBridge workspaceId={spaceId} />
      <TaskBoard tasks={tasks} />
    </>
  );
}
