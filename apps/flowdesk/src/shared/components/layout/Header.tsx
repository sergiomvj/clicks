"use client";

import {
    Search,
    Bell,
    Users,
    Info,
    Menu
} from "lucide-react";

export function Header() {
    return (
        <header className="h-14 border-b border-slate-100 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between px-4 sticky top-0 z-20">
            <div className="flex items-center gap-4">
                <button className="lg:hidden p-2 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg">
                    <Menu className="w-5 h-5 text-slate-600 dark:text-slate-400" />
                </button>
                <div className="flex items-center gap-2">
                    <span className="text-slate-400 dark:text-slate-600 text-lg font-light">#</span>
                    <h2 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">Geral</h2>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <div className="relative hidden md:block">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <input
                        type="text"
                        placeholder="Buscar mensagens ou arquivos..."
                        className="w-64 pl-9 pr-4 py-1.5 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50 text-xs focus:outline-none focus:ring-1 focus:ring-orange-500/50 transition-all shadow-inner"
                    />
                </div>

                <div className="flex items-center gap-1 border-l border-slate-100 dark:border-slate-800 pl-3 ml-2">
                    <button className="p-2 text-slate-500 dark:text-slate-400 hover:text-orange-500 dark:hover:text-orange-400 hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-lg transition-all relative">
                        <Bell className="w-5 h-5" />
                        <span className="absolute top-2 right-2 w-2 h-2 bg-orange-500 rounded-full border-2 border-white dark:border-slate-900" />
                    </button>

                    <button className="flex items-center gap-2 p-1.5 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors ml-1">
                        <div className="w-7 h-7 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden border border-slate-100 dark:border-slate-600 shadow-sm">
                            <img src="https://ui-avatars.com/api/?name=User&background=f97316&color=fff" alt="User Avatar" />
                        </div>
                    </button>
                </div>
            </div>
        </header>
    );
}
