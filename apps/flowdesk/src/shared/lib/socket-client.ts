"use client";

import { io, Socket } from "socket.io-client";

let socket: Socket;

export const getSocket = () => {
    if (!socket) {
        socket = io(process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000", {
            reconnectionAttempts: 5,
            reconnectionDelay: 1000,
            autoConnect: false,
        });
    }
    return socket;
};
