import { AppLayout } from "@/shared/components/layout/AppLayout";
import { ChatContainer } from "@/features/messaging/components/ChatContainer";

export default function Home() {
  return (
    <AppLayout>
      <ChatContainer channelId="general" />
    </AppLayout>
  );
}
