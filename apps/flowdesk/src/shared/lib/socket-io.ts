import { Server } from "socket.io";
import { createAdapter } from "@socket.io/redis-adapter";
import { pub, sub } from "./redis";
import { saveMessage } from "@/features/messaging/services/message-service";

export function initSocket(server: any) {
    const io = new Server(server, {
        cors: {
            origin: process.env.NEXTAUTH_URL || "http://localhost:3000",
            methods: ["GET", "POST"],
            credentials: true,
        },
    });

    io.adapter(createAdapter(pub, sub));

    io.on("connection", (socket) => {
        console.log("🟢 Client connected:", socket.id);

        socket.on("join-channel", (channelId) => {
            socket.join(`channel:${channelId}`);
            console.log(`👤 Client ${socket.id} joined channel: ${channelId}`);
        });

        socket.on("send-message", async (data) => {
            try {
                // Persist message to database
                const savedMsg = await saveMessage({
                    channelId: data.channelId,
                    userId: data.senderId || "default-user-id", // Fallback for dev
                    content: data.text,
                });

                const broadcastData = {
                    id: savedMsg.id,
                    text: savedMsg.content,
                    sender: savedMsg.user.name || "Unknown",
                    timestamp: new Date(savedMsg.createdAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    isAgent: savedMsg.user.role === "AGENT",
                    channelId: data.channelId,
                };

                // Broadcast to all clients in the channel
                io.to(`channel:${data.channelId}`).emit("new-message", broadcastData);
                console.log(`✉️ Message saved and sent to channel ${data.channelId}`);
            } catch (error) {
                console.error("❌ Error saving message:", error);
            }
        });

        socket.on("disconnect", () => {
            console.log("🔴 Client disconnected:", socket.id);
        });
    });

    return io;
}
