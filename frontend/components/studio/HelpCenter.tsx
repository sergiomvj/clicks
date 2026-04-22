"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { usePathname } from "next/navigation";

import { AGENT_PROFILE, normalizeHelpText, resolveHelpEntry } from "@/lib/help/leon-knowledge";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type QuickAction = {
  href: string;
  label: string;
  description: string;
};

function buildResponse(question: string, entry: ReturnType<typeof resolveHelpEntry>) {
  const normalized = normalizeHelpText(question);

  if (!normalized) {
    return `Estou olhando a tela ${entry.label}. Posso te explicar o objetivo, os elementos principais, o checklist de uso ou a proxima acao recomendada.`;
  }

  if (entry.keywords.some((keyword) => normalized.includes(keyword))) {
    return `${entry.label}: ${entry.summary} Uso pratico: ${entry.uses.join(". ")}.`;
  }

  if (normalized.includes("objetivo") || normalized.includes("serve") || normalized.includes("funcao")) {
    return `Objetivo da tela ${entry.label}: ${entry.purpose}`;
  }

  if (normalized.includes("elemento") || normalized.includes("tem") || normalized.includes("mostra")) {
    return `Nesta tela voce encontra: ${entry.elements.join(", ")}.`;
  }

  if (normalized.includes("usar") || normalized.includes("como") || normalized.includes("faco")) {
    return `Uso pratico de ${entry.label}: ${entry.uses.join(". ")}.`;
  }

  if (normalized.includes("checklist") || normalized.includes("passo") || normalized.includes("validar")) {
    return `Checklist rapido de ${entry.label}: ${entry.playbook.join(". ")}.`;
  }

  if (normalized.includes("approval") || normalized.includes("aprov")) {
    return "Approvals devem ser revisados antes de qualquer acao sensivel. Se houver pendencia, trate isso primeiro para nao travar a operacao.";
  }

  return `Posso te ajudar apenas com a pagina atual: ${entry.label}. Resumo: ${entry.summary}`;
}

function buildQuickActions(pathname: string, entry: ReturnType<typeof resolveHelpEntry>): QuickAction[] {
  const spaceMatch = pathname.match(/^\/spaces\/([^/]+)/);
  const channelMatch = pathname.match(/^\/spaces\/([^/]+)\/channels\/([^/]+)/);
  const spaceId = spaceMatch?.[1];
  const channelId = channelMatch?.[2];

  if (!spaceId) {
    return [{ href: "/spaces", label: "Ir para operacao", description: "Voltar para a entrada do workspace comercial." }];
  }

  if (entry.id === "commercial-channel") {
    return [
      { href: `/spaces/${spaceId}/pipeline`, label: "Abrir pipeline", description: "Ver o deal atual no funil comercial." },
      { href: `/spaces/${spaceId}/tasks`, label: "Abrir tarefas", description: "Revisar follow-ups e pendencias do canal." },
      { href: `/spaces/${spaceId}/settings/agents`, label: "Abrir agentes", description: "Validar approvals, escopos e kill switch." },
    ];
  }

  if (entry.id === "pipeline") {
    return [
      channelId
        ? { href: `/spaces/${spaceId}/channels/${channelId}`, label: "Voltar ao canal", description: "Retornar para a operacao detalhada do deal." }
        : { href: `/spaces/${spaceId}/tasks`, label: "Ir para tarefas", description: "Tratar pendencias operacionais do pipeline." },
      { href: `/spaces/${spaceId}/tasks`, label: "Ver tarefas", description: "Acompanhar follow-ups vinculados ao funil." },
      { href: `/spaces/${spaceId}/settings/agents`, label: "Ver approvals", description: "Conferir acoes sensiveis que podem bloquear avancos." },
    ];
  }

  if (entry.id === "tasks") {
    return [
      { href: `/spaces/${spaceId}/pipeline`, label: "Abrir pipeline", description: "Cruzar as tarefas com o estado atual dos deals." },
      { href: `/spaces/${spaceId}/settings/agents`, label: "Ver agentes", description: "Checar tarefas criadas automaticamente e governanca." },
    ];
  }

  if (entry.id === "agents-settings") {
    return [
      { href: `/spaces/${spaceId}/pipeline`, label: "Abrir pipeline", description: "Validar impacto operacional das acoes dos agentes." },
      { href: `/spaces/${spaceId}/tasks`, label: "Abrir tarefas", description: "Revisar itens criados por agentes e follow-ups." },
    ];
  }

  return [{ href: `/spaces/${spaceId}/pipeline`, label: "Abrir pipeline", description: "Seguir para a leitura comercial principal do workspace." }];
}

export function HelpCenter() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const entry = useMemo(() => resolveHelpEntry(pathname), [pathname]);
  const quickActions = useMemo(() => buildQuickActions(pathname, entry), [pathname, entry]);

  useEffect(() => {
    const handler = () => setIsOpen(true);
    window.addEventListener("fbr-help:open", handler);
    return () => window.removeEventListener("fbr-help:open", handler);
  }, []);

  useEffect(() => {
    setMessages([]);
    setQuestion("");
  }, [entry.id]);

  function askHelp(input?: string) {
    const userMessage = (input ?? question).trim();
    if (!userMessage) {
      return;
    }

    const answer = buildResponse(userMessage, entry);
    setMessages((current) => [
      ...current,
      { role: "user", content: userMessage },
      { role: "assistant", content: answer },
    ]);
    setQuestion("");
  }

  return (
    <>
      <button className="help-floating-button" type="button" onClick={() => setIsOpen(true)}>
        Preciso de Ajuda
      </button>
      <aside className={`help-drawer ${isOpen ? "help-drawer-open" : ""}`}>
        <div className="help-drawer-header">
          <div className="stack-tight">
            <div className="eyebrow">Preciso de Ajuda</div>
            <h2 className="section-title">{entry.label}</h2>
            <p className="muted">{entry.summary}</p>
          </div>
          <button className="button-secondary" type="button" onClick={() => setIsOpen(false)}>
            Fechar
          </button>
        </div>

        <section className="help-block stack-tight">
          <div className="eyebrow">Ajuda automatica da pagina atual</div>
          <p><strong>Objetivo:</strong> {entry.purpose}</p>
          <div>
            <strong>Elementos principais</strong>
            <ul className="help-list">
              {entry.elements.map((element) => (
                <li key={element}>{element}</li>
              ))}
            </ul>
          </div>
          <div>
            <strong>Uso pratico</strong>
            <ul className="help-list">
              {entry.uses.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        </section>

        <section className="help-block stack-tight">
          <div className="eyebrow">Checklist rapido</div>
          <ul className="help-list">
            {entry.playbook.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </section>

        <section className="help-block stack-tight">
          <div className="eyebrow">Proximas acoes</div>
          <div className="help-actions-grid">
            {quickActions.map((action) => (
              <Link key={action.href + action.label} className="help-action-card" href={action.href} onClick={() => setIsOpen(false)}>
                <strong>{action.label}</strong>
                <span>{action.description}</span>
              </Link>
            ))}
          </div>
        </section>

        <div className="help-divider">Ainda tem duvidas ? Pergunte ao Leon.</div>

        <section className="help-block stack-tight">
          <div className="eyebrow">Perguntas sugeridas</div>
          <div className="help-suggestion-grid">
            {entry.quickQuestions.map((suggestion) => (
              <button key={suggestion} className="help-suggestion-chip" type="button" onClick={() => askHelp(suggestion)}>
                {suggestion}
              </button>
            ))}
          </div>
        </section>

        <section className="help-block stack-tight">
          <div className="eyebrow">Chat com o agente</div>
          <p className="muted">{AGENT_PROFILE.name} | {AGENT_PROFILE.role}</p>
          <div className="help-chat-log">
            {!messages.length && <p className="muted">O contexto foi carregado para a pagina atual. Suas perguntas ficarao restritas a esta tela.</p>}
            {messages.map((message, index) => (
              <article key={`${message.role}-${index}`} className={`help-chat-bubble ${message.role === "user" ? "help-chat-user" : "help-chat-assistant"}`}>
                {message.content}
              </article>
            ))}
          </div>
          <textarea
            className="input help-textarea"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder={`Pergunte ao Leon sobre ${entry.label}`}
          />
          <button className="button" type="button" onClick={() => askHelp()}>
            Perguntar ao Leon
          </button>
        </section>
      </aside>
      {isOpen && <button className="help-backdrop" type="button" aria-label="Fechar ajuda" onClick={() => setIsOpen(false)} />}
    </>
  );
}
