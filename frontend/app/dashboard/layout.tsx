import Link from "next/link";
import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { getSession } from "@/lib/session";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/domains", label: "Domains" },
  { href: "/dashboard/leads", label: "Leads" },
  { href: "/dashboard/icp", label: "ICP" },
  { href: "/dashboard/campaigns", label: "Campaigns" },
  { href: "/dashboard/agents", label: "Agents" },
  { href: "/dashboard/reports", label: "Reports" },
] as const;

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const session = await getSession();
  if (!session.isLoggedIn) {
    redirect("/login");
  }

  return (
    <div className="dashboard-shell">
      <aside className="sidebar stack">
        <div className="stack">
          <span className="eyebrow">NovaFacebrasil</span>
          <div className="brand-mark">FBR-Leads</div>
          <p className="muted">Workspace {session.workspaceId}</p>
        </div>

        <nav className="sidebar-links">
          {links.map((link) => (
            <Link key={link.href} className="sidebar-link" href={link.href}>
              {link.label}
            </Link>
          ))}
        </nav>

        <form action="/api/auth/logout" method="post">
          <button className="button-secondary" type="submit">Sair</button>
        </form>
      </aside>
      <main className="main-content">{children}</main>
    </div>
  );
}
