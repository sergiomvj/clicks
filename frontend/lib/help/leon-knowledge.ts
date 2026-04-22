export type HelpDocEntry = {
  id: string;
  label: string;
  route: string;
  routePrefix?: string;
  summary: string;
  purpose: string;
  elements: string[];
  uses: string[];
  keywords: string[];
  quickQuestions: string[];
  playbook: string[];
};

export const AGENT_PROFILE = {
  name: "Leon Guavamango",
  team: "Dev Facebrasil",
  role: "Gerente de Homologacao e Implantacao",
};

export const HELP_DOCS: HelpDocEntry[] = [
  {
    id: "spaces-overview",
    label: "Visao geral",
    route: "/spaces",
    summary: "Ponto de entrada do workspace comercial, direcionando a operacao para o canal principal disponivel.",
    purpose: "Evitar friccao de navegacao e levar o usuario rapidamente para a operacao comercial ativa.",
    elements: [
      "resolucao do primeiro space disponivel",
      "resolucao do primeiro canal associado",
      "redirecionamento automatico para a area operacional",
    ],
    uses: [
      "entrar rapidamente no workspace sem precisar escolher rota manualmente",
      "verificar se a estrutura base de spaces e canais esta ativa",
    ],
    keywords: ["visao geral", "spaces", "entrada", "workspace", "canal inicial"],
    quickQuestions: [
      "Como validar se o workspace esta pronto para operar?",
      "O que devo conferir antes de entrar no canal principal?",
      "Para que serve esta tela inicial?",
    ],
    playbook: [
      "confira se o redirecionamento para o canal principal ocorreu sem erro",
      "valide se existem spaces e canais ativos",
      "entre no canal principal para acompanhar mensagens, tarefas e pipeline",
    ],
  },
  {
    id: "commercial-channel",
    label: "Canal Comercial",
    route: "/spaces/[spaceId]/channels/[channelId]",
    routePrefix: "/spaces/",
    summary: "Tela operacional principal com mensagens, pipeline, tarefas, approvals e monitor de agentes no contexto do canal comercial.",
    purpose: "Concentrar a execucao do deal aquecido e a operacao comercial do dia a dia em uma unica experiencia.",
    elements: [
      "cabecalho com metricas de deals, tarefas e mensagens de agentes",
      "lista de mensagens do canal",
      "quadro de pipeline",
      "board de tarefas",
      "monitor de agentes",
      "fila de approvals",
    ],
    uses: [
      "acompanhar o lead recebido do 1FBR-Leads",
      "revisar mensagens e rascunhos gerados por agentes",
      "acompanhar tarefas e aprovacoes sem sair da operacao",
    ],
    keywords: ["canal", "mensagens", "deal", "approval", "agente", "pipeline", "tarefa"],
    quickQuestions: [
      "Como revisar um rascunho criado por agente?",
      "Onde vejo approvals pendentes nesta operacao?",
      "Como acompanhar um deal aquecido neste canal?",
    ],
    playbook: [
      "leia as mensagens e identifique se ha rascunhos ou orientacoes de agente",
      "verifique a fila de approvals antes de executar a proxima acao sensivel",
      "acompanhe tarefas de follow-up e relacao do deal com o pipeline",
    ],
  },
  {
    id: "pipeline",
    label: "Pipeline",
    route: "/spaces/[spaceId]/pipeline",
    routePrefix: "/spaces/",
    summary: "Visao do funil comercial por stage com destaque para deals aquecidos do 1FBR-Leads.",
    purpose: "Permitir leitura executiva e operacional do CRM, priorizando origem, stage e volume por etapa.",
    elements: [
      "metricas resumidas do pipeline",
      "colunas por stage",
      "cards de deals",
      "fila de approvals",
    ],
    uses: [
      "visualizar gargalos do funil",
      "identificar deals quentes do 1FBR-Leads",
      "acompanhar mudancas de stage em tempo real",
    ],
    keywords: ["pipeline", "crm", "stage", "funil", "deal", "proposta", "negociacao"],
    quickQuestions: [
      "Como identificar deals vindos do 1FBR-Leads?",
      "O que significa um gargalo no funil?",
      "Como validar se um deal pode mudar de stage?",
    ],
    playbook: [
      "observe em qual coluna os deals estao acumulando",
      "priorize deals aquecidos destacados no quadro",
      "use approvals e tarefas para destravar avancos do funil",
    ],
  },
  {
    id: "tasks",
    label: "Tarefas",
    route: "/spaces/[spaceId]/tasks",
    routePrefix: "/spaces/",
    summary: "Painel de tarefas do workspace com origem humana e automatizada, prioridade e status operacional.",
    purpose: "Dar controle rapido sobre follow-ups, pendencias e tarefas criadas por agentes.",
    elements: [
      "metricas de pendencia, prioridade e origem",
      "cards de tarefas",
      "status, prioridade e vencimento",
    ],
    uses: [
      "acompanhar follow-ups comerciais",
      "validar tarefas criadas por agentes",
      "detectar gargalos operacionais de execucao",
    ],
    keywords: ["tarefas", "follow-up", "prioridade", "board", "pendencia"],
    quickQuestions: [
      "Como saber quais tarefas vieram de agentes?",
      "O que devo priorizar neste board?",
      "Como usar as tarefas para follow-up comercial?",
    ],
    playbook: [
      "priorize tarefas vencidas ou de alta prioridade",
      "revise tarefas criadas automaticamente por agentes",
      "use o board para garantir continuidade dos follow-ups",
    ],
  },
  {
    id: "agents-settings",
    label: "Agentes e Governanca",
    route: "/spaces/[spaceId]/settings/agents",
    routePrefix: "/spaces/",
    summary: "Painel de governanca dos agentes com kill switch, approvals, escopo, owners e estado do git watcher.",
    purpose: "Controlar automacao com seguranca, rastreabilidade e visibilidade operacional.",
    elements: [
      "painel de kill switch",
      "monitor de agentes",
      "owners e escopos por agente",
      "fila de approvals",
      "estado do git watcher por repositorio",
    ],
    uses: [
      "ligar e desligar o kill switch",
      "aprovar ou rejeitar acoes sensiveis",
      "validar saude operacional dos agentes cadastrados",
    ],
    keywords: ["agentes", "kill switch", "approval", "watcher", "governanca", "escopo"],
    quickQuestions: [
      "Quando devo usar o kill switch?",
      "Como validar o escopo de um agente?",
      "O que fazer com approvals expirados ou pendentes?",
    ],
    playbook: [
      "confira owners, escopos e approvals obrigatorios por agente",
      "valide o estado do git watcher para cada repositorio monitorado",
      "ative o kill switch se houver comportamento inseguro ou fora do escopo",
    ],
  },
];

export function resolveHelpEntry(pathname: string): HelpDocEntry {
  const exact = HELP_DOCS.find((entry) => entry.route === pathname);
  if (exact) {
    return exact;
  }

  const dynamic = HELP_DOCS.find((entry) => {
    if (!entry.routePrefix) {
      return false;
    }

    if (entry.id === "commercial-channel") {
      return /^\/spaces\/[^/]+\/channels\/[^/]+$/.test(pathname);
    }
    if (entry.id === "pipeline") {
      return /^\/spaces\/[^/]+\/pipeline$/.test(pathname);
    }
    if (entry.id === "tasks") {
      return /^\/spaces\/[^/]+\/tasks$/.test(pathname);
    }
    if (entry.id === "agents-settings") {
      return /^\/spaces\/[^/]+\/settings\/agents$/.test(pathname);
    }
    return pathname.startsWith(entry.routePrefix);
  });

  return dynamic ?? HELP_DOCS[0];
}

export function normalizeHelpText(value: string): string {
  return value.trim().toLowerCase();
}
