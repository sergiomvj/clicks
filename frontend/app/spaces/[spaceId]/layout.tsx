import type { ReactNode } from "react";

import { Sidebar } from "@/components/layout/Sidebar";
import { getSpaceBundle } from "@/lib/server-api";

export default async function SpaceLayout({ children }: { children: ReactNode }) {
  const { spaces, channels } = await getSpaceBundle();

  return (
    <div className="dashboard-shell">
      <Sidebar spaces={spaces} channels={channels} />
      <main className="main-content">{children}</main>
    </div>
  );
}
