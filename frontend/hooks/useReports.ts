"use client";

import { useEffect, useState } from "react";

import type { ReportItem } from "@/lib/types";

export function useReports() {
  const [items, setItems] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const response = await fetch("/api/proxy/intelligence/report", { cache: "no-store" });
        if (response.status === 404) {
          if (active) {
            setItems([]);
            setError(null);
          }
          return;
        }
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = (await response.json()) as ReportItem | { items?: ReportItem[] };
        if (active) {
          if ("items" in data && Array.isArray(data.items)) {
            setItems(data.items);
          } else {
            setItems(data.id ? [data as ReportItem] : []);
          }
          setError(null);
        }
      } catch (loadError) {
        if (active) {
          const message = loadError instanceof Error ? loadError.message : "Unknown error";
          setError(message);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  return { items, loading, error };
}
