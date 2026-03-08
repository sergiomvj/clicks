"use client";

import { useEffect, useState } from "react";

import type { CampaignItem } from "@/lib/types";

interface CampaignsResponse {
  items: CampaignItem[];
}

export function useCampaigns() {
  const [items, setItems] = useState<CampaignItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const response = await fetch("/api/proxy/campaigns", { cache: "no-store" });
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }
        const data = (await response.json()) as CampaignsResponse;
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
