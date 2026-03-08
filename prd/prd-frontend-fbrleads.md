# FBR-LEADS — PRD Frontend v2.0
> **Stack:** Next.js 15 + TypeScript strict + Tailwind v4 + shadcn/ui  
> **Design System:** DESIGN_STANDARDS.md (NovaFacebrasil)  
> **Versão:** 2.0 · Fevereiro 2026 · Facebrasil · Confidencial

---

## 1. Design System — Padrões Visuais

Todos os componentes seguem rigorosamente o `DESIGN_STANDARDS.md`. Dark mode é o padrão do sistema.

### 1.1 Tipografia

| Uso | Fonte | Peso | Classe Tailwind |
|-----|-------|------|-----------------|
| Logo / Marca | Outfit | ExtraBold (800) | `font-heading font-extrabold tracking-tight text-primary` |
| Títulos H1 | Outfit | Bold (700) | `font-heading text-4xl font-bold` |
| Títulos H2, H3 | Outfit | SemiBold (600) | `font-heading text-2xl font-semibold` |
| Títulos H4–H6 | Outfit | Medium (500) | `font-heading text-xl font-medium` |
| Corpo de texto | Inter | Regular (400) | `font-sans text-base` (padrão global) |
| Destaques / Links | Inter | Medium (500) | `font-sans font-medium` |

### 1.2 Paleta de Cores

| Token | Hex | Uso |
|-------|-----|-----|
| `bg-background` (dark) | `#101622` | Background principal — dark mode padrão |
| `bg-card` (dark) | `#1E293B` | Superfícies, cards, painéis |
| `text-primary` | `#EA580C` | Botões principais, links ativos, ícones de destaque |
| `text-foreground` | `#F8FAFC` | Texto principal sobre fundo escuro |
| `text-muted` | `#64748B` | Textos secundários, labels, datas |
| `border` | `#E2E8F0` | Bordas de cards e separadores |
| `bg-accent` | `#FCD34D` | Badges de status, destaques complementares |

### 1.3 Implementação no layout.tsx

```tsx
// app/layout.tsx
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

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={`${inter.variable} ${outfit.variable} dark`}>
      <body className="font-sans antialiased bg-background text-foreground">
        {children}
      </body>
    </html>
  );
}
```

### 1.4 globals.css — Tailwind v4 @theme

```css
@theme inline {
  --font-sans:    var(--font-inter), ui-sans-serif, system-ui, sans-serif;
  --font-heading: var(--font-outfit), ui-sans-serif, system-ui, sans-serif;

  --color-brand-primary: #EA580C;
  --color-brand-dark:    #101622;
  --color-brand-card:    #1E293B;
}
```

---

## 2. Mapa de Páginas — App Router

| Rota | Página | Acesso | Descrição |
|------|--------|--------|-----------|
| `/login` | Login | Público | Autenticação iron-session — redireciona para dashboard se autenticado |
| `/dashboard` | Overview | Autenticado | Métricas gerais: leads, bounce rate, SQLs gerados, domínios ativos |
| `/dashboard/domains` | Saúde dos Domínios | Autenticado | Monitor em tempo real (WebSocket): score, fase, bounce, blacklist |
| `/dashboard/leads` | Pipeline de Leads | Autenticado | Funil com filtros por stage, score e campanha. Exportação CSV |
| `/dashboard/icp` | Configuração de ICP | Autenticado | Formulário no-code para criar e editar perfis de cliente ideal |
| `/dashboard/campaigns` | Campanhas | Autenticado | Criar campanhas, ver status, abrir detalhe de cada uma |
| `/dashboard/agents` | Status dos Agentes | Autenticado | Monitor em tempo real: online/offline/erro, logs, kill switch |
| `/dashboard/reports` | Relatórios Executivos | Autenticado | Relatório semanal do Time 6 com exportação CSV |

---

## 3. Árvore de Componentes

### 3.1 Estrutura de Pastas

```
app/
├── layout.tsx                    # Root layout (fontes, dark mode, providers)
├── (auth)/
│   └── login/
│       └── page.tsx              # Página de login
└── dashboard/
    ├── layout.tsx                # Dashboard layout: sidebar + header + main
    ├── page.tsx                  # Overview / home do dashboard
    ├── domains/
    │   └── page.tsx
    ├── leads/
    │   └── page.tsx
    ├── icp/
    │   └── page.tsx
    ├── campaigns/
    │   ├── page.tsx
    │   └── [id]/page.tsx
    ├── agents/
    │   └── page.tsx
    └── reports/
        └── page.tsx

components/
├── domains/
│   ├── DomainCard.tsx
│   └── DomainHealthBadge.tsx
├── leads/
│   ├── LeadFunnelChart.tsx
│   ├── LeadCard.tsx
│   └── ScoreBadge.tsx
├── agents/
│   ├── AgentStatusBadge.tsx
│   ├── AgentLogFeed.tsx
│   └── KillSwitch.tsx
├── icp/
│   └── ICPForm.tsx
├── campaigns/
│   └── CampaignBuilder.tsx
└── ui/                           # Componentes base (shadcn/ui + customizados)
    ├── MetricCard.tsx
    ├── DataTable.tsx
    ├── StatsBar.tsx
    └── RealtimeIndicator.tsx

hooks/
├── useDomains.ts
├── useDomainHealth.ts            # WebSocket
├── useLeads.ts
├── useLead.ts
├── useCampaigns.ts
├── useAgents.ts
├── useAgentLogs.ts               # SSE
├── useReport.ts
└── useICPProfiles.ts

lib/
├── session.ts                    # iron-session config
└── api.ts                        # fetch wrapper para /api/proxy
```

### 3.2 Componentes Reutilizáveis

| Componente | Localização | Descrição |
|-----------|-------------|-----------|
| `DomainCard` | components/domains/ | Card de domínio com score, fase, bounce rate e status de blacklist |
| `DomainHealthBadge` | components/domains/ | Badge de status: saudável / alerta / crítico / bloqueado |
| `LeadFunnelChart` | components/leads/ | Funil visual com quantidade por estágio e velocidade de progressão |
| `LeadCard` | components/leads/ | Card de lead com score, empresa, stage e botão de ação |
| `ScoreBadge` | components/leads/ | Badge visual de score 0-100 com cores por faixa |
| `AgentStatusBadge` | components/agents/ | Badge online (verde) / offline (vermelho) / erro (amarelo) |
| `AgentLogFeed` | components/agents/ | Feed de logs em tempo real via SSE com paginação |
| `KillSwitch` | components/agents/ | Botão de pausa de agente com confirmação e registro em audit log |
| `ICPForm` | components/icp/ | Formulário no-code: setores, portes, cargos, regiões, keywords |
| `CampaignBuilder` | components/campaigns/ | Wizard de criação de campanha em 3 etapas |
| `MetricCard` | components/ui/ | Card de métrica com valor, variação e ícone |
| `DataTable` | components/ui/ | Tabela com ordenação, filtros e exportação CSV (shadcn/ui) |
| `StatsBar` | components/ui/ | Barra de progresso animada para métricas de performance |
| `RealtimeIndicator` | components/ui/ | Indicador pulsante de dados ao vivo (WebSocket ativo) |

---

## 4. Especificação Detalhada das Páginas

### 4.1 Overview — /dashboard

Painel principal com visão geral do sistema. Atualizado automaticamente a cada 60 segundos.

| Seção | Componentes | Dados |
|-------|-------------|-------|
| Métricas principais | 4x `MetricCard` | Leads hoje · SQLs gerados · Taxa de resposta · Domínios ativos |
| Saúde dos domínios | `StatsBar` por domínio | Bounce rate e capacidade disponível por domínio |
| Funil resumido | `LeadFunnelChart` | Quantidade de leads por estágio em tempo real |
| Últimos SQLs | `LeadCard` (5 recentes) | SQLs gerados nas últimas 24h com score e empresa |

### 4.2 Saúde dos Domínios — /dashboard/domains

> **WebSocket:** Esta página usa WebSocket persistente para atualização em tempo real sem refresh de página.

| Seção | Componentes | Funcionalidade |
|-------|-------------|----------------|
| Lista de domínios | `DomainCard` + `DomainHealthBadge` | Score, fase (1-4), sends_today/daily_limit, bounce_rate, status blacklist |
| Filtros | `Select` + `Switch` (shadcn) | Filtrar por fase, status e score mínimo |
| Alerta de domínio | `Toast` (shadcn) | Notificação automática quando bounce > 2% ou blacklist detectada |
| Rotação manual | `Dialog` de confirmação | Avançar fase de aquecimento com aprovação explícita |

### 4.3 Pipeline de Leads — /dashboard/leads

| Seção | Componentes | Funcionalidade |
|-------|-------------|----------------|
| Funil visual | `LeadFunnelChart` | Kanban-like com quantidade e velocidade por estágio |
| Tabela de leads | `DataTable` | Colunas: nome, empresa, score, stage, fonte, data. Ordenável. |
| Filtros | `Select` + `Slider` + `Input` | Por stage, score mínimo, campanha, fonte e período |
| Exportação | `Button` + Download | CSV com todos os campos do lead — filtros aplicados na exportação |
| Detalhe do lead | `Sheet` (shadcn) | Painel lateral com dados completos, histórico de interações e enrichment |

### 4.4 Configuração de ICP — /dashboard/icp

> **No-code:** Operador de marketing cria e edita ICPs sem escrever código. Após salvar, Garimpeiros iniciam coleta em até 30 minutos.

| Campo | Componente | Validação |
|-------|-----------|-----------|
| Nome do ICP | `Input` | Obrigatório · min 3 chars |
| Setores de atuação | `MultiSelect` (shadcn) | Lista pré-definida + opção "outro" |
| Porte das empresas | `CheckboxGroup` | Micro / Pequena / Média / Grande / Enterprise |
| Cargos-alvo | `TagInput` | Texto livre com chips — ex: "CEO", "Diretor de Marketing" |
| Regiões | `MultiSelect` | Estados BR + "Internacional" + "Brasil nos EUA" |
| Palavras-chave | `TagInput` | Keywords para scraping contextual |
| Score mínimo | `Slider` (0-100) | Leads abaixo do score são descartados automaticamente |

### 4.5 Status dos Agentes — /dashboard/agents

> **Tempo real:** Feed de logs atualizado via SSE (Server-Sent Events). Kill switch disponível para cada agente individualmente.

| Seção | Componentes | Funcionalidade |
|-------|-------------|----------------|
| Grid de agentes | `AgentStatusBadge` + últimas ações | 13 agentes em grid 3x5. Status: online / offline / erro / pausado |
| Log feed | `AgentLogFeed` | Feed em tempo real das últimas ações por agente com filtro por tipo |
| Kill switch | `KillSwitch` + `Dialog` | Pausa agente individual. Requer confirmação com registro em audit log |
| Métricas por agente | `MetricCard` | Ações nas últimas 24h, taxa de erro, último heartbeat |

### 4.6 Relatórios Executivos — /dashboard/reports

| Seção | Componentes | Funcionalidade |
|-------|-------------|----------------|
| Relatório da semana | Renderização Markdown | Insights do Time 6 com análise de campanhas e ICP |
| Histórico | `Select` de semanas | Navegar entre relatórios anteriores |
| Exportação | `Button` + Download | CSV com métricas brutas da semana selecionada |

---

## 5. Auth Flow — iron-session

> **Regra Absoluta:** Frontend NUNCA se comunica diretamente com o FastAPI backend. Todo request passa pelo proxy Next.js API Routes (`/api/proxy`).

### 5.1 Fluxo de Autenticação

```
Browser → POST /api/auth/login
   ↓ credentials validadas
Next.js API Route → iron-session.set(session)
   ↓ cookie httpOnly + secure + sameSite=lax
Browser recebe cookie (JS NÃO pode ler)

Browser → GET /dashboard/leads
   ↓ middleware.ts verifica cookie
Session inválida → redirect /login
Session válida → request passa
   ↓
Component → fetch("/api/proxy/leads?stage=sql")
   ↓ Next.js proxy decripta cookie
Next.js proxy → FastAPI /api/leads + header X-Workspace-Id
   ↓ FastAPI valida X-Workspace-Id
Dados retornam ao componente
```

### 5.2 Arquivos de Auth

```
app/
├── api/
│   ├── auth/
│   │   ├── login/route.ts        # POST: valida credentials, cria session
│   │   └── logout/route.ts       # POST: destroi session, redirect /login
│   └── proxy/[...path]/route.ts  # Proxy autenticado para FastAPI
├── middleware.ts                  # Verifica session em rotas /dashboard/*
└── lib/
    └── session.ts                 # iron-session config (SESSION_SECRET do .env)
```

### 5.3 Proxy Next.js → FastAPI

```typescript
// app/api/proxy/[...path]/route.ts
import { getIronSession } from "iron-session";
import { sessionOptions } from "@/lib/session";

export async function GET(
  req: Request,
  { params }: { params: { path: string[] } }
) {
  const session = await getIronSession(req, new Response(), sessionOptions);
  if (!session.workspaceId) return new Response(null, { status: 401 });

  const path = params.path.join("/");
  const url = new URL(req.url);
  const backendRes = await fetch(
    `${process.env.BACKEND_URL}/api/${path}${url.search}`,
    {
      headers: {
        "X-Workspace-Id": session.workspaceId,
        "Content-Type": "application/json",
      },
    }
  );

  return new Response(backendRes.body, { status: backendRes.status });
}

// Repetir para POST, PATCH, DELETE
```

---

## 6. Camada de API — Hooks e Tempo Real

### 6.1 React Hooks por Domínio

| Hook | Endpoint consumido | Atualização |
|------|--------------------|-------------|
| `useDomains()` | `/api/proxy/domains` | Polling a cada 30s |
| `useLeads(filters)` | `/api/proxy/leads` | On-demand com filtros |
| `useLead(id)` | `/api/proxy/leads/{id}` | On-demand |
| `useCampaigns()` | `/api/proxy/campaigns` | Polling a cada 60s |
| `useAgents()` | `/api/proxy/logs` | On-demand |
| `useReport()` | `/api/proxy/intelligence/report` | On-demand |
| `useICPProfiles()` | `/api/proxy/icp` | On-demand |

### 6.2 WebSocket — Saúde dos Domínios

```typescript
// hooks/useDomainHealth.ts
import { useState, useEffect } from "react";
import type { Domain } from "@/types";

export function useDomainHealth() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(`wss://${location.host}/api/ws/domains`);

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);

    ws.onmessage = (event) => {
      const updated = JSON.parse(event.data) as Partial<Domain> & { id: string };
      setDomains((prev) =>
        prev.map((d) => (d.id === updated.id ? { ...d, ...updated } : d))
      );
    };

    return () => ws.close();
  }, []);

  return { domains, connected };
}
```

### 6.3 SSE — Log Feed dos Agentes

```typescript
// hooks/useAgentLogs.ts
import { useState, useEffect } from "react";
import type { AgentLog } from "@/types";

export function useAgentLogs(agentId?: string) {
  const [logs, setLogs] = useState<AgentLog[]>([]);

  useEffect(() => {
    const params = agentId ? `?agent_id=${agentId}` : "";
    const es = new EventSource(`/api/proxy/logs/stream${params}`);

    es.onmessage = (event) => {
      const log = JSON.parse(event.data) as AgentLog;
      setLogs((prev) => [log, ...prev].slice(0, 100)); // Manter últimos 100
    };

    return () => es.close();
  }, [agentId]);

  return { logs };
}
```

---

## 7. Requisitos Não-Funcionais

| Categoria | Requisito | Implementação |
|-----------|-----------|---------------|
| Performance | Endpoints FastAPI < 500ms para 95% das requisições | Redis cache + asyncpg connection pool |
| Performance | Streaming de IA via SSE — nunca aguardar resposta completa | `EventSource` no frontend + SSE no FastAPI |
| Responsivo | Dashboard funcional em 1280px, 1440px e 1920px | Tailwind breakpoints `lg`, `xl`, `2xl` |
| Dark Mode | Dark mode padrão conforme DESIGN_STANDARDS.md | `bg-background: #101622` · classes `dark:` |
| Loading States | Skeleton em todas as ações assíncronas | `shadcn/ui Skeleton` em todos os componentes de dados |
| Acessibilidade | Contraste > 4.5:1 em todos os textos | Verificação WCAG 2.1 AA — Inter/Outfit sobre `#101622` |
| Segurança | Nenhum ID interno em URLs ou console do browser | Slugs e UUIDs curtos. Zero `console.log` de dados sensíveis. |
| TypeScript | strict mode habilitado. Sem `any`, sem `@ts-ignore` | `tsconfig: "strict": true` · ESLint `no-explicit-any` |

---

## 8. Stack e Dependências Frontend

```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "iron-session": "^8.0.0",
    "@tanstack/react-table": "^8.0.0",
    "recharts": "^2.0.0",
    "react-hook-form": "^7.0.0",
    "zod": "^3.0.0",
    "lucide-react": "latest",
    "sonner": "latest",
    "date-fns": "^3.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "eslint": "^8.0.0",
    "@typescript-eslint/eslint-plugin": "latest"
  }
}
```

**shadcn/ui components usados:**
`Button` · `Card` · `Dialog` · `Sheet` · `Select` · `Slider` · `Switch` · `Table` · `Tabs` · `Toast` · `Skeleton` · `Badge` · `Input` · `Label` · `Separator`

---

## 9. Security Checklist — Frontend

| Item | Status | Implementação |
|------|--------|---------------|
| iron-session com cookie `httpOnly + secure + sameSite=lax` | ✅ Obrigatório | `lib/session.ts` — `SESSION_SECRET` do `.env` |
| Frontend NUNCA fala diretamente com FastAPI | ✅ Obrigatório | Todos os fetches via `/api/proxy/[...path]` |
| Variáveis sensíveis sem prefixo `NEXT_PUBLIC_` | ✅ Obrigatório | `SESSION_SECRET` e `BACKEND_URL` apenas no servidor |
| Nenhum ID interno em URLs visíveis | ✅ Obrigatório | Slugs e UUIDs curtos em rotas dinâmicas |
| Zero `console.log` de dados sensíveis | ✅ Obrigatório | ESLint rule: `no-console` em produção |
| TypeScript strict mode — sem `any` | ✅ Obrigatório | `tsconfig strict: true` + ESLint `no-explicit-any` |
| Middleware de proteção em `/dashboard/*` | ✅ Obrigatório | `middleware.ts` — redirect `/login` sem session |
| CORS restritivo no FastAPI | ✅ Obrigatório | Apenas domínio do frontend aceito no backend |
| Dark mode com contraste > 4.5:1 | ✅ Obrigatório | Paleta DESIGN_STANDARDS validada com WCAG |
| Loading states em toda ação assíncrona | ✅ Obrigatório | `shadcn/ui Skeleton` em todos os componentes de dados |

---

*FBR-Leads · PRD Frontend v2.0 · Fevereiro 2026 · Facebrasil · Confidencial*
