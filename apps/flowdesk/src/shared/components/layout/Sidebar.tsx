"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Hash,
    MessageSquare,
    CheckSquare,
    BarChart3,
    Settings,
    Plus,
    Search,
    ChevronDown
} from "lucide-react";
import { cn } from "@/shared/lib/utils";

const channels = [
    { id: "general", name: "Geral", icon: Hash, type: "chat" },
    { id: "tasks", name: "Tarefas", icon: CheckSquare, type: "tasks" },
    { id: "deals", name: "Vendas", icon: BarChart3, type: "deals" },
    { id: "support", name: "Suporte", icon: MessageSquare, type: "chat" },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 border-r border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col h-screen">
            {/* Space Selector / Header */}
            <div className="p-4 border-b border-slate-50 dark:border-slate-800/50">
                <button className="flex items-center justify-between w-full p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors group">
                    <div className="flex items-center gap-3 text-left">
                        <div className="w-8 h-8 rounded bg-orange-500 flex items-center justify-center text-white font-bold text-sm">
                            F
                        </div>
                        <div>
                            <p className="text-sm font-bold text-slate-900 dark:text-white truncate">Facebrasil</p>
                            <p className="text-xs text-slate-400 dark:text-slate-500 truncate">Marketing</p>
                        </div>
                    </div>
                    <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300" />
                </button>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto p-3 space-y-6">
                <div>
                    <div className="flex items-center justify-between px-2 mb-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        <span>Canais</span>
                        <button className="hover:text-slate-600 dark:hover:text-slate-300">
                            <Plus className="w-4 h-4" />
                        </button>
                    </div>
                    <ul className="space-y-1">
                        {channels.map((channel) => (
                            <li key={channel.id}>
                                <Link
                                    href={`/channels/${channel.id}`}
                                    className={cn(
                                        "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200",
                                        pathname.includes(channel.id)
                                            ? "bg-orange-50 dark:bg-orange-950/30 text-orange-600 dark:text-orange-400 shadow-sm"
                                            : "text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 hover:text-slate-900 dark:hover:text-slate-200"
                                    )}
                                >
                                    <channel.icon className="w-4 h-4" />
                                    {channel.name}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>

                <div>
                    <div className="px-2 mb-2 text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
                        <span>Privados</span>
                    </div>
                    <ul className="space-y-1 opacity-50 grayscale pointer-events-none">
                        <li className="px-3 py-2 text-xs text-slate-400 italic">Em breve...</li>
                    </ul>
                </div>
            </nav>

            {/* Bottom Actions */}
            <div className="p-4 border-t border-slate-50 dark:border-slate-800/50 space-y-2">
                <button className="flex items-center gap-3 w-full px-3 py-2 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-lg transition-colors">
                    <Settings className="w-4 h-4" />
                    Configurações
                </button>
            </div>
        </aside>
    );
}
