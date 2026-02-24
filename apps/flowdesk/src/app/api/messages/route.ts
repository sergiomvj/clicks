import { NextRequest, NextResponse } from "next/server";
import { getChannelMessages } from "@/features/messaging/services/message-service";

export async function GET(
    request: NextRequest,
    { params }: { params: { channelId: string } }
) {
    const searchParams = request.nextUrl.searchParams;
    const channelId = searchParams.get("channelId");

    if (!channelId) {
        return NextResponse.json({ error: "Channel ID is required" }, { status: 400 });
    }

    try {
        const messages = await getChannelMessages(channelId);

        const formattedMessages = messages.map((msg) => ({
            id: msg.id,
            text: msg.content,
            sender: msg.user.name || "Unknown",
            timestamp: new Date(msg.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            isAgent: msg.user.role === "AGENT",
        }));

        return NextResponse.json(formattedMessages);
    } catch (error) {
        console.error("❌ Error fetching messages:", error);
        return NextResponse.json({ error: "Failed to fetch messages" }, { status: 500 });
    }
}
