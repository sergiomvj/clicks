import type { ReactNode } from "react";

import { KpiOverview } from "@/components/dashboard/KpiOverview";
import { Sidebar } from "@/components/layout/Sidebar";
import { HelpCenter } from "@/components/studio/HelpCenter";
import { getKpis, getSpaceBundle } from "@/lib/server-api";

export default async function SpaceLayout({ children }: { children: ReactNode }) {
  const [{ spaces, channels }, kpis] = await Promise.all([getSpaceBundle(), getKpis()]);

  return (
    <div className="dashboard-shell">
      <Sidebar spaces={spaces} channels={channels} />
      <main className="main-content">
        <div className="stack">
          <KpiOverview kpis={kpis} />
          {children}
        </div>
      </main>
      <HelpCenter />
    </div>
  );
}
