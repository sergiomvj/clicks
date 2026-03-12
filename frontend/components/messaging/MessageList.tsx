import type { MessageRecord } from "@/lib/types";

interface MessageListProps {
  messages: MessageRecord[];
}

function getLabel(message: MessageRecord) {
  if (message.source_system === "agent-draft") {
    return "Rascunho do agente";
  }
  if (message.author_type === "agent") {
    return "Agente";
  }
  return "Humano";
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="surface-card stack">
      <div className="section-header">
        <h2 className="section-title">Mensagens</h2>
        <span className="muted">{messages.length} itens no canal</span>
      </div>
      {messages.map((message) => (
        <article key={message.id} className={`surface-card message-card ${message.author_type === "agent" ? "message-agent" : ""} ${message.source_system === "agent-draft" ? "message-draft" : ""}`}>
          <div className="stack-tight">
            <div className="row-inline">
              <strong>{getLabel(message)}</strong>
              {message.source_system && <span className="agent-badge">{message.source_system}</span>}
            </div>
            <span className="muted">{new Date(message.created_at).toLocaleString("pt-BR")}</span>
            <p>{message.body}</p>
          </div>
        </article>
      ))}
      {!messages.length && <p className="muted">Nenhuma mensagem neste canal.</p>}
    </div>
  );
}
