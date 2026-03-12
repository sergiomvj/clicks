# PRD Frontend — FBR-CLICK v1.0
> **Fonte canônica:** `fbr-click-prd.md` · `DESIGN_STANDARDS.md` · `securitycoderules.md`
> **Stack:** Next.js 15 + TypeScript strict + Tailwind CSS v4 + shadcn/ui + iron-session
> **Prazo MVP:** 60 dias — 8 batches

---

## 1. VISÃO DO FRONTEND

O frontend do FBR-CLICK é uma SPA (Single Page Application) estilo Slack/Linear — interface de colaboração em tempo real onde humanos e agentes autônomos OpenClaw convivem na mesma superfície visual. Toda comunicação com o backend passa obrigatoriamente pelo proxy Next.js; o frontend NUNCA fala diretamente com a API FastAPI.

---

## 2. REQUISITOS FUNCIONAIS (UX/UI)

### 2.1 Autenticação e sessão
- Tela de login com email + senha
- Sessão via iron-session (cookie httpOnly — sem localStorage)
- Middleware Next.js protege todas as rotas `/spaces/*`
- Logout imediato com limpeza de cookie

### 2.2 Layout principal — sidebar + conteúdo
- Sidebar fixa com lista de Spaces, canais dentro de cada Space e lista de agentes ativos
- Agentes listados com emoji 🤖 e badge "AGENTE" em roxo
- Barra de KPIs no topo de cada Space (métricas configuradas pelo admin)
- Navegação fluida entre canais sem reload de página

### 2.3 Mensagens em tempo real
- Lista de mensagens com scroll infinito (paginação cursor)
- WebSocket ativo: novas mensagens chegam sem refresh
- Distinção visual clara entre humano e agente:
  - **Mensagem humana:** fundo branco padrão
  - **Mensagem de agente:** fundo lilás sutil (`#faf5ff`) + badge "AGENTE" em roxo
- Input de mensagem com suporte a @menções
- Thread view ao clicar em mensagem

### 2.4 Board de tarefas
- Visualização em board (Kanban) com colunas: A Fazer, Em Andamento, Concluído, Cancelado
- Filtros por: assignee, status, prioridade, source (human/agent), prazo
- Indicador visual de source: tarefas de agente exibem ícone 🤖
- Criação rápida de tarefa com title + assignee + prazo

### 2.5 Pipeline CRM — Kanban de deals
- Kanban com colunas por stage: Prospecção → Qualificação → Proposta → Negociação → Fechado Ganha/Perdido
- Drag-and-drop entre stages (cria `deal_history` via API)
- Card de deal: nome empresa, valor, assignee, score, badge de origem (fbr-leads | manual)
- Modal de detalhe do deal: histórico de stages + tarefas vinculadas + canal dedicado

### 2.6 Painel de monitoramento de agentes (admin)
- Painel `/settings/agents` exclusivo para admins
- Cards de agente com: status em tempo real (online/offline/pausado/erro), último heartbeat, actions nas últimas 24h, aprovações pendentes
- Kill switch e botão pausar por agente
- Modal de logs completos com filtro por action_type e data
- Aprovações pendentes: aprovar / rejeitar diretamente do painel

### 2.7 Registro de novo agente (admin)
- Formulário: URL do repositório Git, branch, spaces e canais permitidos, heartbeat interval
- Validação do repositório: confirma presença dos 7 markdowns antes de salvar
- Feedback visual do status de conexão OpenClaw após registro

---

## 3. DESIGN SYSTEM

Conforme `DESIGN_STANDARDS.md` — padrões obrigatórios para todo o FBR-CLICK.

### 3.1 Tipografia

| Uso | Fonte | Peso | Classe Tailwind |
|---|---|---|---|
| Logo / Identidade | **Outfit** | ExtraBold (800) | `font-heading font-extrabold tracking-tight` |
| Títulos (H1) | **Outfit** | Bold (700) | `font-heading text-4xl font-bold` |
| Subtítulos (H2, H3) | **Outfit** | SemiBold (600) | `font-heading font-semibold` |
| Corpo de texto | **Inter** | Regular (400) | `font-sans` (padrão) |
| Destaques, links | **Inter** | Medium/SemiBold (500/600) | `font-sans font-medium` |

### 3.2 Cores

| Token | Valor | Uso |
|---|---|---|
| `bg-background` (light) | `#F8FAFC` (Slate 50) | Background principal |
| `bg-card` (light) | `#FFFFFF` | Cards e superfícies |
| `bg-background` (dark) | `#101622` | Background principal dark |
| `bg-card` (dark) | `#1E293B` | Cards dark |
| `text-primary` / `bg-primary` | `#F97316` (Orange 500) | Botões principais, links ativos |
| Badge agente | `#7C3AED` (Violet 700) | Badge "AGENTE" em roxo |
| Fundo msg agente | `#FAF5FF` | Background sutil de mensagem de agente |
| Status online | `#22C55E` (Green 500) | Indicador de agente online |
| Status offline | `#EF4444` (Red 500) | Indicador de agente offline |
| Status pausado | `#F59E0B` (Amber 500) | Indicador de agente pausado |

### 3.3 Configuração de fontes — `layout.tsx`

```tsx
import { Inter, Outfit } from "next/font/google";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${outfit.variable}`}>
      <body className="font-sans antialiased bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
```

### 3.4 globals.css — variáveis de tema (Tailwind v4)

```css
@theme inline {
  /* Fontes */
  --font-sans: var(--font-inter), ui-sans-serif, system-ui, sans-serif;
  --font-heading: var(--font-outfit), ui-sans-serif, system-ui, sans-serif;

  /* Cores da marca */
  --color-brand-primary: #F97316;
  --color-brand-dark: #101622;
  --color-agent-badge: #7C3AED;
  --color-agent-bg: #FAF5FF;
}
```

### 3.5 Identificação visual de agentes

| Elemento | Humano | Agente OpenClaw |
|---|---|---|
| Avatar | Foto ou iniciais coloridas | Emoji + iniciais (ex: 🤖CB) |
| Badge no nome | Nenhum | "AGENTE" em roxo pequeno (`text-xs bg-violet-100 text-violet-700`) |
| Cor de fundo msg | Branco padrão | Lilás sutil (`bg-[#faf5ff]`) |
| Ícone na sidebar | Avatar redondo | Avatar redondo + 🤖 |
| Tooltip hover | Online/Offline | "Agente autônomo · OpenClaw · Último heartbeat: Xmin" |

---

## 4. MAPA DE PÁGINAS (App Router)

```
app/
├── layout.tsx                          # Fontes + providers
├── page.tsx                            # Redirect → /spaces
├── login/
│   └── page.tsx                        # Tela de login
├── api/
│   ├── auth/
│   │   ├── login/route.ts              # iron-session login
│   │   └── logout/route.ts             # iron-session logout
│   └── proxy/
│       └── [...path]/route.ts          # Proxy obrigatório → FastAPI
└── spaces/
    ├── page.tsx                         # Listagem de spaces
    └── [spaceId]/
        ├── layout.tsx                   # Sidebar + KPI Bar
        ├── page.tsx                     # Redirect → primeiro canal
        ├── channels/
        │   └── [channelId]/page.tsx    # Canal com mensagens em tempo real
        ├── tasks/
        │   └── page.tsx                # Board de tarefas
        ├── pipeline/
        │   └── page.tsx                # Kanban de deals
        └── settings/
            ├── agents/page.tsx         # Gestão de agentes (admin)
            └── members/page.tsx        # Gestão de membros (admin)
```

---

## 5. ÁRVORE DE COMPONENTES

```
components/
├── layout/
│   ├── Sidebar.tsx                # Spaces, canais, agentes com badges
│   ├── AgentBadge.tsx             # Badge 🤖 + label "AGENTE" em roxo
│   └── KPIBar.tsx                 # Barra de KPIs no topo do space
│
├── messaging/
│   ├── MessageList.tsx            # Lista de mensagens com scroll infinito
│   ├── MessageInput.tsx           # Input com @menções
│   ├── AgentMessage.tsx           # Mensagem com fundo #faf5ff + badge
│   ├── HumanMessage.tsx           # Mensagem padrão de humano
│   └── ThreadView.tsx             # Thread de replies
│
├── tasks/
│   ├── TaskBoard.tsx              # Kanban de tarefas por status
│   ├── TaskCard.tsx               # Card com prioridade, assignee, source
│   └── TaskForm.tsx               # Formulário de nova tarefa
│
├── crm/
│   ├── PipelineKanban.tsx         # Kanban de deals com drag-and-drop
│   ├── DealCard.tsx               # Card: empresa, valor, score, origem
│   └── DealDetail.tsx             # Modal com histórico + tarefas + canal
│
├── agents/
│   ├── AgentMonitor.tsx           # Painel admin: status, logs, aprovações
│   ├── AgentCard.tsx              # Card de perfil do agente
│   ├── AgentStatusBadge.tsx       # Indicador online/offline/paused/error
│   ├── ApprovalRequest.tsx        # Solicitação de aprovação com aprovar/rejeitar
│   └── AgentRegisterForm.tsx      # Formulário de registro de agente
│
└── ui/                            # Componentes shadcn/ui reutilizáveis
    ├── (shadcn components)
    └── ...
```

---

## 6. HOOKS CUSTOMIZADOS

```typescript
hooks/
├── useWebSocket.ts      // Conexão WebSocket por canal — reconexão automática
├── useMessages.ts       // Mensagens com cursor pagination + otimistic update
├── useTasks.ts          // Tasks com filtros reativos
├── useDeals.ts          // Deals + drag-and-drop de stage
├── useAgents.ts         // Agentes + status em tempo real
└── useApprovals.ts      // Aprovações pendentes com polling curto (5s)
```

### 6.1 useWebSocket — padrão de reconexão

```typescript
// useWebSocket.ts
export function useWebSocket(channelId: string) {
  // Conecta em: NEXT_PUBLIC_WS_URL/ws/channels/{channelId}
  // Reconexão automática com backoff exponencial
  // Emite eventos: 'message', 'task_assigned', 'deal_stage_changed'
  // Nunca expõe token no cliente — autenticação via cookie httpOnly
}
```

---

## 7. CAMADA DE API — PROXY OBRIGATÓRIO

```typescript
// lib/api.ts — fetch wrapper que SEMPRE passa pelo proxy Next.js
export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`/api/proxy/${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
    credentials: "include", // garante envio do cookie iron-session
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Erro desconhecido" }));
    throw new Error(error.detail);
    // NUNCA expor stack traces — error.detail vem sanitizado do backend
  }
  return res.json();
}
```

```typescript
// app/api/proxy/[...path]/route.ts — proxy server-side
// 1. Descriptografa cookie iron-session
// 2. Extrai user_id
// 3. Repassa chamada ao FastAPI com header X-User-Id
// 4. NUNCA expõe BACKEND_URL ao cliente (variável sem NEXT_PUBLIC_)
```

---

## 8. AUTH FLOW (iron-session)

```typescript
// lib/session.ts
import { SessionOptions } from "iron-session";

export const sessionOptions: SessionOptions = {
  password: process.env.SESSION_SECRET!, // 64+ chars — NUNCA NEXT_PUBLIC_
  cookieName: "fbr-click-session",
  cookieOptions: {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
  },
};

// middleware.ts
// Protege todas as rotas /spaces/** e /api/proxy/**
// Redireciona para /login se sem sessão válida
```

---

## 9. SEGURANÇA — FRONTEND

Checklist obrigatório baseado em `securitycoderules.md`:

- **NUNCA** usar `localStorage` ou `sessionStorage` para tokens ou IDs internos
- **NUNCA** logar dados sensíveis em `console.log` (tokens, emails, IDs internos)
- **NUNCA** incluir `user_id`, `agent_id` ou `workspace_id` em URLs visíveis — usar slugs
- **NUNCA** usar `NEXT_PUBLIC_` em variáveis sensíveis (`SESSION_SECRET`, `BACKEND_URL`, etc.)
- **NUNCA** fazer fetch direto ao backend FastAPI — tudo passa pelo proxy `/api/proxy/`
- Error messages retornadas ao frontend **NUNCA** expõem stack traces ou queries SQL
- TypeScript strict mode habilitado — sem `any`, sem `@ts-ignore`, sem `as unknown as`
- Imports organizados: react → libs → components → hooks → utils

---

## 10. REQUISITOS NÃO-FUNCIONAIS

- **Dark mode:** suporte via classe `dark:` — `darkMode: 'class'` ativo no Tailwind
- **Responsivo:** mobile-first, funcional em telas ≥ 375px
- **Loading states:** skeleton loaders em mensagens, tarefas e deals
- **Otimistic updates:** tarefas e mensagens aparecem imediatamente antes da confirmação do backend
- **Reconexão WebSocket:** backoff exponencial automático — sem intervenção do usuário
- **Contraste:** taxa > 4.5:1 para todos os textos (WCAG AA)
- **Performance:** First Contentful Paint ≤ 1.5s na sidebar + canal inicial

---

## 11. DEPENDÊNCIAS (package.json — principais)

```json
{
  "dependencies": {
    "next": "15.x",
    "react": "18.x",
    "typescript": "5.x",
    "tailwindcss": "4.x",
    "iron-session": "^8.0.0",
    "@dnd-kit/core": "^6.0.0",
    "@dnd-kit/sortable": "^7.0.0",
    "lucide-react": "^0.400.0",
    "clsx": "^2.0.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "@types/node": "22.x",
    "@types/react": "18.x",
    "eslint": "9.x"
  }
}
```

> shadcn/ui: instalado via CLI (`npx shadcn@latest add ...`) — não listado como dependência direta.

---

## 12. CHECKLIST DE PADRONIZAÇÃO (DESIGN_STANDARDS.md)

- [ ] **Fontes instaladas:** `Inter` e `Outfit` configuradas no `layout.tsx` com `next/font/google`
- [ ] **Variáveis definidas:** `globals.css` com `--font-sans` e `--font-heading`
- [ ] **Dark mode ativo:** `darkMode: 'class'` e todos os componentes com classes `dark:`
- [ ] **Contraste testado:** textos primários com taxa > 4.5:1 em fundo claro e escuro
- [ ] **Badge de agente:** roxo (`text-violet-700 bg-violet-100`) em todos os contextos
- [ ] **Fundo de mensagem de agente:** `#faf5ff` aplicado consistentemente
- [ ] **TypeScript strict:** sem `any`, sem `@ts-ignore` em todo o codebase
