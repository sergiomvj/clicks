import { Metadata } from "next";
import LoginForm from "@/features/auth/components/LoginForm";

export const metadata: Metadata = {
    title: "Login | FlowDesk",
    description: "Entre na sua conta para colaborar com seu time e agentes.",
};

export default function LoginPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 p-4 relative overflow-hidden">
            {/* Background Decorative Elements */}
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-orange-100/20 via-transparent to-transparent dark:from-orange-950/20 pointer-events-none" />
            <div className="absolute top-0 right-0 p-10 opacity-10 dark:opacity-20 hidden lg:block">
                <div className="w-64 h-64 border-2 border-orange-500 rounded-full blur-3xl animate-pulse" />
            </div>

            <LoginForm />
        </div>
    );
}
