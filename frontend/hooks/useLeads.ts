"use client";

import { useEffect, useState } from "react";

import type { LeadItem } from "@/lib/types";

interface LeadsResponse {
  items: LeadItem[];
}

export function useLeads() {
  const [items, setItems] = useState<LeadItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const response = await fetch("/api/proxy/leads", { cache: "no-store" });
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = (await response.json()) as LeadsResponse;
        if (active) {
          setItems(data.items);
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
