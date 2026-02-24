"use client";

import { useState, useEffect, useRef } from "react";
import { Send, Plus, Smile, Paperclip } from "lucide-react";
import { getSocket } from "@/shared/lib/socket-client";
import { cn } from "@/shared/lib/utils";

interface Message {
    id: string;
    text: string;
    sender: string;
    timestamp: string;
    isAgent?: boolean;
}

export function ChatContainer({ channelId }: { channelId: string }) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(true);
    const [inputText, setInputText] = useState("");
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const socket = getSocket();

    useEffect(() => {
        // Fetch initial messages
        const fetchMessages = async () => {
            try {
                const response = await fetch(`/api/messages?channelId=${channelId}`);
                const data = await response.json();
                if (Array.isArray(data)) {
                    setMessages(data);
                }
            } catch (error) {
                console.error("❌ Error fetching history:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchMessages();

        socket.connect();
        socket.emit("join-channel", channelId);

        socket.on("new-message", (message: Message) => {
            setMessages((prev) => [...prev, message]);
        });

        return () => {
            socket.off("new-message");
            socket.disconnect();
        };
    }, [channelId]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSendMessage = () => {
        if (!inputText.trim()) return;

        const newMessage: Message = {
            id: Date.now().toString(),
            text: inputText,
            sender: "Sergio", // TODO: Get from Auth session
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        socket.emit("send-message", { ...newMessage, channelId });
        setInputText("");
    };

    return (
        <div className="flex flex-col h-full bg-white dark:bg-slate-950/20">
            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={cn(
                            "flex items-start gap-4 transition-all hover:bg-slate-50/50 dark:hover:bg-slate-900/30 p-2 rounded-xl -ml-2",
                            msg.sender === "Sergio" ? "flex-row-reverse" : ""
                        )}
                    >
                        <div className={cn(
                            "w-10 h-10 rounded-full flex-shrink-0 flex items-center justify-center border shadow-sm",
                            msg.isAgent
                                ? "bg-orange-100 dark:bg-orange-900/30 border-orange-200 dark:border-orange-800"
                                : "bg-slate-200 dark:bg-slate-800 border-slate-100 dark:border-slate-700 overflow-hidden"
                        )}>
                            {msg.isAgent ? (
                                <span className="text-orange-600 dark:text-orange-400 font-bold text-xs">AI</span>
                            ) : (
                                <img src={`https://ui-avatars.com/api/?name=${msg.sender}&background=f97316&color=fff`} alt={msg.sender} />
                            )}
                        </div>
                        <div className={cn("max-w-[80%]", msg.sender === "Sergio" ? "text-right" : "")}>
                            <div className={cn("flex items-center gap-2 mb-1", msg.sender === "Sergio" ? "flex-row-reverse" : "")}>
                                <span className="font-bold text-sm text-slate-900 dark:text-white">{msg.sender}</span>
                                {msg.isAgent && (
                                    <span className="text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 px-1.5 py-0.5 rounded font-medium uppercase tracking-wider">Agente</span>
                                )}
                                <span className="text-[10px] text-slate-400">{msg.timestamp}</span>
                            </div>
                            <p className={cn(
                                "text-sm leading-relaxed font-sans p-3 rounded-2xl shadow-sm",
                                msg.sender === "Sergio"
                                    ? "bg-orange-500 text-white"
                                    : "bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-100 dark:border-slate-800"
                            )}>
                                {msg.text}
                            </p>
                        </div>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800/50">
                <div className="max-w-4xl mx-auto relative">
                    <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-2 border border-slate-200 dark:border-slate-700 focus-within:ring-2 focus-within:ring-orange-500/20 focus-within:border-orange-500/50 transition-all shadow-inner">
                        <button className="p-2 text-slate-400 hover:text-orange-500 hover:bg-white dark:hover:bg-slate-800 rounded-xl transition-all shadow-sm">
                            <Plus className="w-5 h-5" />
                        </button>

                        <input
                            type="text"
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                            placeholder="Mande uma mensagem ou peça uma ação para os agentes..."
                            className="flex-1 bg-transparent border-none focus:ring-0 text-sm py-2 px-2 text-slate-900 dark:text-white placeholder-slate-400 font-sans outline-none"
                        />

                        <div className="flex items-center gap-1">
                            <button className="p-2 text-slate-400 hover:text-orange-500 transition-colors">
                                <Smile className="w-5 h-5" />
                            </button>
                            <button className="p-2 text-slate-400 hover:text-orange-500 transition-colors">
                                <Paperclip className="w-5 h-5" />
                            </button>
                            <div className="w-px h-6 bg-slate-200 dark:bg-slate-700 mx-1" />
                            <button
                                onClick={handleSendMessage}
                                className="bg-orange-500 hover:bg-orange-600 text-white p-2 rounded-xl shadow-lg shadow-orange-500/20 transition-all active:scale-95 group"
                            >
                                <Send className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
