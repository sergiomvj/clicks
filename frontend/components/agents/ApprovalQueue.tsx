"use client";

import { useMemo, useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { apiFetch } from "@/lib/api";
import type { ApprovalRecord } from "@/lib/types";

function getPayloadText(payload: Record<string, unknown>, key: string): string | null {
  const value = payload[key];
  if (value === null || value === undefined) {
    return null;
  }
  const text = String(value).trim();
  return text ? text : null;
}

export function ApprovalQueue({ approvals }: { approvals: ApprovalRecord[] }) {
  const router = useRouter();
  const [notesById, setNotesById] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);
  const [activeApprovalId, setActiveApprovalId] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const pending = useMemo(
    () => approvals.filter((approval) => approval.status === "pending" || approval.status === "expired"),
    [approvals],
  );

  async function decideApproval(approvalId: string, status: "approved" | "rejected") {
    setError(null);
    setActiveApprovalId(approvalId);
    try {
      await apiFetch(`agents/approvals/${approvalId}`, {
        method: "PATCH",
        body: JSON.stringify({
          status,
          decision_notes:
            notesById[approvalId]?.trim() ||
            (status === "approved" ? "Approval confirmado no painel operacional." : "Approval rejeitado no painel operacional."),
        }),
      });
      startTransition(() => router.refresh());
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Falha ao decidir approval.");
    } finally {
      setActiveApprovalId(null);
    }
  }

  return (
    <section className="surface-card stack">
      <div className="section-header">
        <h2 className="section-title">Fila de approvals</h2>
        <span className="muted">{pending.length} pendentes ou expirados</span>
      </div>
      {pending.map((approval) => {
        const dealId = getPayloadText(approval.payload, "deal_id");
        const stage = getPayloadText(approval.payload, "stage");
        const body = getPayloadText(approval.payload, "body");
        const isExpired = approval.status === "expired";
        const isBusy = isPending || activeApprovalId === approval.id;

        return (
          <article key={approval.id} className="approval-card stack-tight">
            <div className="row-inline">
              <strong>{approval.action_type}</strong>
              <span className={`status-pill ${isExpired ? "status-warn" : ""}`}>{approval.status}</span>
            </div>
            <p className="muted">Solicitado em {new Date(approval.requested_at).toLocaleString("pt-BR")}</p>
            {approval.expires_at && <p className="muted">Expira em {new Date(approval.expires_at).toLocaleString("pt-BR")}</p>}
            {dealId && <p className="muted">Deal: {dealId}</p>}
            {stage && <p className="muted">Stage alvo: {stage}</p>}
            {body && <p className="muted">Mensagem: {body}</p>}
            {!isExpired && (
              <>
                <input
                  className="input"
                  value={notesById[approval.id] ?? ""}
                  onChange={(event) => setNotesById((current) => ({ ...current, [approval.id]: event.target.value }))}
                  placeholder="Observacao da decisao"
                />
                <div className="row-actions">
                  <button className="button" disabled={isBusy} onClick={() => decideApproval(approval.id, "approved")} type="button">
                    Aprovar
                  </button>
                  <button className="button button-secondary" disabled={isBusy} onClick={() => decideApproval(approval.id, "rejected")} type="button">
                    Rejeitar
                  </button>
                </div>
              </>
            )}
          </article>
        );
      })}
      {!pending.length && <p className="muted">Nenhum approval aguardando acao humana.</p>}
      {error && <p className="muted">{error}</p>}
    </section>
  );
}
