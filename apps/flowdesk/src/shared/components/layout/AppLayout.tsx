import { Sidebar } from "./Sidebar";
import { Header } from "./Header";

export function AppLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="flex h-screen bg-slate-50 dark:bg-slate-950 overflow-hidden font-sans">
            <Sidebar />
            <div className="flex-1 flex flex-col relative overflow-hidden">
                <Header />
                <main className="flex-1 overflow-y-auto bg-white dark:bg-slate-950/20 shadow-inner rounded-tl-3xl border-t border-l border-slate-100 dark:border-slate-800/50 m-1">
                    {children}
                </main>
            </div>
        </div>
    );
}
