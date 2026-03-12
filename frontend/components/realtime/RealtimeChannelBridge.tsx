"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

function buildSocketUrl(channelId: string) {
  if (typeof window === "undefined") {
    return "";
  }

  const configuredBase = process.env.NEXT_PUBLIC_BACKEND_WS_URL;
  if (configuredBase) {
    return `${configuredBase.replace(/\/$/, "")}/api/messages/ws/channels/${channelId}`;
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const host = window.location.port === "3000" ? `${window.location.hostname}:8000` : window.location.host;
  return `${protocol}://${host}/api/messages/ws/channels/${channelId}`;
}

export function RealtimeChannelBridge({ channelId }: { channelId: string }) {
  const router = useRouter();
  const refreshTimeoutRef = useRef<number | null>(null);

  useEffect(() => {
    const socketUrl = buildSocketUrl(channelId);
    if (!socketUrl) {
      return;
    }

    const socket = new WebSocket(socketUrl);
    socket.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data) as { event?: string };
        if (!payload.event || payload.event === "connected") {
          return;
        }
      } catch {
        return;
      }

      if (refreshTimeoutRef.current !== null) {
        window.clearTimeout(refreshTimeoutRef.current);
      }
      refreshTimeoutRef.current = window.setTimeout(() => {
        router.refresh();
      }, 250);
    };

    return () => {
      if (refreshTimeoutRef.current !== null) {
        window.clearTimeout(refreshTimeoutRef.current);
      }
      socket.close();
    };
  }, [channelId, router]);

  return null;
}
