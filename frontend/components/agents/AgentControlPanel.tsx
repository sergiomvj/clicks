"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";
import type { AgentControlRecord } from "@/lib/types";

export function AgentControlPanel({ control }: { control: AgentControlRecord }) {
  const router = useRouter();
  const [reason, setReason] = useState(control.reason ?? "");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  async function toggleKillSwitch(nextState: boolean) {
    setError(null);
    try {
      await apiFetch("agents/control/kill-switch", {
        method: "POST",
        body: JSON.stringify({
          active: nextState,
          reason: reason || (nextState ? "Kill switch ativado manualmente." : "Kill switch desativado manualmente."),
        }),
      });
      startTransition(() => router.refresh());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Falha ao atualizar kill switch.");
    }
  }

  return (
    <section className="surface-card stack">
      <h2 className="section-title">Controle de agentes</h2>
      <p className="muted">
        Kill switch atual: <strong>{control.kill_switch_active ? "Ativo" : "Inativo"}</strong>
      </p>
      <input
        className="input"
        value={reason}
        onChange={(event) => setReason(event.target.value)}
        placeholder="Motivo da alteracao"
      />
      <div className="row-actions">
        <button className="button" disabled={isPending || control.kill_switch_active} onClick={() => toggleKillSwitch(true)} type="button">
          Ativar kill switch
        </button>
        <button className="button button-secondary" disabled={isPending || !control.kill_switch_active} onClick={() => toggleKillSwitch(false)} type="button">
          Desativar kill switch
        </button>
      </div>
      {control.reason && <p className="muted">Motivo atual: {control.reason}</p>}
      {control.updated_at && <p className="muted">Ultima alteracao: {control.updated_at}</p>}
      {error && <p className="muted">{error}</p>}
    </section>
  );
}
