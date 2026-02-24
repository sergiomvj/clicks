|  |
| --- |
| **FlowDesk**  Plataforma de Colaboração para Times de Marketing & Vendas |

*Documento Técnico — Arquitetura, UX & Regras de Negócio*

Versão 1.0 | Fevereiro 2026

|  |
| --- |
| **💡 Conceito Central** |
| "Toda tarefa nasce de uma conversa. Toda conversa deveria virar uma tarefa."  FlowDesk une a estrutura do ClickUp com a fluidez do Slack em uma plataforma verticalmente  focada em times de marketing e vendas de 10–200 pessoas. Sem complexidade desnecessária.  Sem ferramentas separadas. Uma superfície onde comunicação e execução coexistem. |

|  |
| --- |
| **PARTE 1 — ARQUITETURA TÉCNICA** |

## **1.1 Visão Geral da Stack**

O FlowDesk é construído sobre uma arquitetura de microsserviços com comunicação em tempo real via WebSocket, projetada para escalar horizontalmente e suportar colaboração simultânea de centenas de usuários por workspace.

|  |  |  |
| --- | --- | --- |
| **Camada** | **Tecnologia** | **Justificativa** |
| Frontend | Next.js 14 + TypeScript | SSR para SEO, RSC para performance |
| Estado Global | Zustand + React Query | Simples, sem boilerplate excessivo |
| Real-time | Socket.io + Redis Pub/Sub | Escalabilidade horizontal com múltiplos nodes |
| API Gateway | tRPC + Fastify | Type-safe de ponta a ponta |
| Auth | NextAuth + JWT + Refresh Tokens | SSO, OAuth, magic links |
| Banco Principal | PostgreSQL (Supabase) | ACID, RLS nativo, real-time subscriptions |
| Cache | Redis (Upstash) | Sessions, pub/sub, rate limiting |
| Search | Algolia / Meilisearch | Full-text em mensagens, tarefas, arquivos |
| Storage | S3-compatible (R2 Cloudflare) | Arquivos, imagens, assets de campanha |
| Queue | BullMQ (Redis) | Notificações, webhooks, batch jobs |
| AI Layer | OpenAI / Claude API | Resumos, geração de tarefas, insights |
| Infra | Fly.io / Railway + Vercel Edge | Deploy global, baixa latência |

## **1.2 Diagrama de Microsserviços**

Cada domínio de negócio roda como um serviço independente, comunicando-se via message broker interno:

|  |  |  |
| --- | --- | --- |
| **Serviço** | **Responsabilidade** | **Dependências** |
| auth-service | Login, sessões, permissões, RBAC | PostgreSQL, Redis |
| workspace-service | Spaces, canais, membros, configurações | PostgreSQL, auth-service |
| messaging-service | Mensagens, threads, reactions, menções | PostgreSQL, Redis, storage-service |
| task-service | Tarefas, subtarefas, sprints, automações | PostgreSQL, messaging-service |
| notification-service | Push, email, in-app, digest | Redis Queue, BullMQ |
| crm-service | Leads, deals, pipeline, atividades | PostgreSQL, task-service |
| approval-service | Fluxo de aprovação de criativos/conteúdo | messaging-service, storage-service |
| analytics-service | Métricas de uso, relatórios, dashboards | PostgreSQL read replica |
| ai-service | Resumos, geração de tarefas, insights | Claude/OpenAI API, task-service |
| search-service | Indexação e busca full-text | Algolia/Meilisearch, todos os serviços |

## **1.3 Modelo de Dados Principal**

### **Entidades Core**

|  |  |
| --- | --- |
| **WORKSPACE**  *id, name, slug, plan, logo*  *created\_at, settings (JSONB)*  **SPACE**  *id, workspace\_id, name, type*  *color, icon, is\_private*  **CHANNEL**  *id, space\_id, name, purpose*  *is\_announcement, archived\_at* | **MESSAGE**  *id, channel\_id, user\_id, body*  *parent\_id, task\_id, attachments[]*  *status: open|resolved|archived*  **TASK**  *id, channel\_id, source\_message\_id*  *title, body, status, priority*  *assignees[], due\_date, labels[]*  *sprint\_id, parent\_task\_id* |

|  |  |
| --- | --- |
| **DEAL (CRM)**  *id, workspace\_id, title, value*  *stage, owner\_id, contact\_id*  *expected\_close, channel\_id*  **APPROVAL**  *id, message\_id, asset\_url*  *approvers[], status, deadline*  *comments[], version\_history[]* | **USER / MEMBER**  *id, email, name, avatar*  *role: owner|admin|member|guest*  *notification\_prefs (JSONB)*  **KPI\_WIDGET**  *id, space\_id, type, source*  *config (JSONB), position*  *refresh\_interval, last\_value* |

## **1.4 Estratégia de Real-Time**

O sistema usa uma arquitetura de rooms baseada em canais. Cada usuário conectado se inscreve nos rooms dos canais e spaces que tem acesso:

|  |
| --- |
| **Fluxo de Mensagem em Tempo Real** |
| 1. Usuário envia mensagem → POST /api/messages  2. messaging-service persiste no PostgreSQL  3. Publica evento no Redis canal: workspace:{id}:channel:{id}  4. Socket.io server recebe via Pub/Sub e emite para todos os clientes conectados ao room  5. Cliente atualiza estado via Zustand (otimistic update já mostrado)  6. notification-service consome o mesmo evento para push/email  7. search-service indexa a mensagem assincronamente via BullMQ |

## **1.5 Segurança e Permissões (RBAC)**

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Papel** | **Spaces** | **Canais** | **Tarefas** | **CRM** | **Config** |
| Owner | CRUD total | CRUD total | CRUD total | CRUD total | Total |
| Admin | Criar/Editar | CRUD total | CRUD total | CRUD total | Parcial |
| Member | Ver/Usar | Criar mensagens | CRUD próprias | Deals atribuídos | Não |
| Guest | Apenas convidados | Só leitura + reply | Ver atribuídas | Não | Não |

Row Level Security (RLS) no PostgreSQL garante que queries só retornam dados do workspace autenticado. Tokens JWT carregam workspace\_id e role, validados no API Gateway antes de qualquer query.

|  |
| --- |
| **PARTE 2 — FLUXOS DE UX** |

## **2.1 Princípios de Design**

|  |  |  |
| --- | --- | --- |
| **🎯 Opinionado** | **⚡ Velocidade** | **🔗 Contexto** |
| * Decisões tomadas pelo produto * Workflows pré-definidos para mktg/vendas * Menos configurações = menos paralisia * Padrões inteligentes desde o onboarding | * Ações com máximo 2 cliques * Shortcuts para tudo (Cmd+K universal) * Otimistic updates em toda interação * Mobile-first, offline-ready (PWA) | * Tarefa sempre linkada à mensagem origem * Thread com status formal * Histórico de decisões preservado * Quem pediu, quando, por quê |

## **2.2 Estrutura de Navegação**

A interface é dividida em três painéis principais, inspirada no layout do Slack mas com sidebar direita contextual de tarefas:

|  |  |  |
| --- | --- | --- |
| **Zona** | **Conteúdo** | **Comportamento** |
| Sidebar Esquerda (240px) | Spaces, Canais, DMs, Buscas recentes | Colapsável, organizável por drag |
| Área Central (flex) | Feed de mensagens do canal ativo | Scroll infinito, rich text, embeds |
| Painel Direito (320px) | Tarefas do canal, threads, KPIs | Colapsável, persiste por canal |
| Header do Canal | Nome, membros, KPI bar, ações rápidas | Fixa, métricas atualizadas em tempo real |
| Modal Global (Cmd+K) | Busca unificada, ações, navegação | Abre sobre tudo, fecha com Esc |

## **2.3 Fluxo Core: Mensagem → Tarefa**

Este é o fluxo mais crítico do produto. Deve ser fluido, sem fricção, preservando contexto:

|  |
| --- |
| **Passo a Passo: Converter Mensagem em Tarefa** |
| PASSO 1 — Hover na mensagem → aparece toolbar flutuante com ações  PASSO 2 — Clicar em ícone "✓ Transformar em tarefa" (ou atalho T)  PASSO 3 — Mini-modal inline (não sai do chat) com campos:  • Título (pré-preenchido com preview da mensagem)  • Responsável (autocomplete de membros)  • Prazo (date picker simplificado)  • Prioridade (P1/P2/P3/P4 com cores)  • Label (campanha, conteúdo, ads, etc)  PASSO 4 — Confirmar → tarefa aparece na sidebar direita COM link para mensagem  PASSO 5 — Mensagem original recebe badge "📋 Tarefa criada" com preview ao hover  PASSO 6 — Responsável recebe notificação com contexto da mensagem original |

## **2.4 Fluxo: Thread com Status Formal**

Diferente do Slack onde threads morrem sem conclusão, no FlowDesk toda thread tem um ciclo de vida:

|  |  |  |  |
| --- | --- | --- | --- |
| **Status** | **Cor** | **Significado** | **Quem pode mudar** |
| 💬 Em discussão | Cinza | Thread aberta, discussão ativa | Qualquer membro |
| ⏳ Aguardando | Amarelo | Bloqueado por decisão externa | Criador ou admin |
| ✅ Decidido | Verde | Decisão tomada, registrada | Criador ou admin |
| 🔒 Arquivado | Azul acinzentado | Thread encerrada, somente leitura | Admin |

Threads com status "Decidido" geram automaticamente um resumo pinado no topo do canal, acessível como histórico de decisões — algo que nenhuma ferramenta atual faz bem.

## **2.5 Fluxo: Approval de Criativos (Marketing)**

|  |
| --- |
| **Fluxo de Aprovação de Assets** |
| INÍCIO — Usuário anexa arquivo (jpg, pdf, figma link, vídeo) ao canal  TRIGGER — Clicar em "Iniciar aprovação" no anexo  CONFIG — Definir: aprovadores (1 ou mais), prazo, requer todos ou maioria  NOTIF — Aprovadores recebem notificação com preview do asset  REVISÃO — Aprovador clica no asset → abre visualizador com ferramentas:  • Anotações inline (como comentários no Figma)  • Aprovar com comentário  • Reprovar com motivo obrigatório  • Solicitar revisão com notas específicas  STATUS — Badge no canal mostra: "2/3 aprovaram" em tempo real  CONCLUSÃO — Quando todos aprovam: notificação ao criador + versão marcada como aprovada  HISTÓRICO — Todas as versões e comentários preservados, nunca deletados |

## **2.6 Fluxo: Pipeline de Vendas (CRM Leve)**

O CRM não é uma ferramenta separada — é uma view dentro do FlowDesk. Cada deal tem seu próprio canal de contexto:

|  |  |
| --- | --- |
| **STAGES DO PIPELINE**   1. Prospecção 2. Qualificação 3. Proposta Enviada 4. Negociação 5. Fechado (Ganho/Perdido)   **AÇÕES NO CARD DO DEAL**   * Comentar (thread do deal) * Criar tarefa vinculada * Agendar follow-up com lembrete * Mover de stage (drag or click) * Registrar atividade (call, email, reunião) | **VIEWS DISPONÍVEIS**   * Kanban (padrão) — drag entre stages * Lista com filtros avançados * Forecast (valor por stage) * Atividades (timeline por representante)   **AUTOMAÇÕES NATIVAS**   * Deal sem update > X dias → alerta no canal * Mover para Proposta → cria task de elaborar doc * Fechado Ganho → notifica marketing automaticamente * Follow-up vencido → reassign ou escalate |

## **2.7 KPI Bar — Dashboard Contextual**

Cada Space tem uma barra de métricas no topo, configurável por tipo de time:

|  |  |  |
| --- | --- | --- |
| **Tipo de Space** | **Métricas Padrão** | **Fonte de Dados** |
| Marketing / Campanhas | Impressões, CTR, CPL, orçamento restante | Meta Ads, Google Ads (via webhook) |
| Vendas / Pipeline | Deals abertos, valor total, fechamentos do mês | CRM interno |
| Conteúdo / Blog | Artigos publicados, aprovações pendentes, tráfego | CMS via webhook |
| Geral / Squad | Tarefas abertas, concluídas, bloqueadas, velocidade | task-service interno |

As métricas são widgets modulares — o admin do Space escolhe quais mostrar. Integração via webhooks de entrada (qualquer fonte que mande JSON) ou integrações nativas com Meta Ads, Google Ads e Google Analytics.

|  |
| --- |
| **PARTE 3 — REGRAS DE NEGÓCIO** |

## **3.1 Modelo de Planos e Limites**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Recurso** | **Free** | **Starter ($12/user)** | **Growth ($25/user)** | **Business ($49/user)** |
| Usuários | Até 5 | Até 25 | Até 100 | Ilimitado |
| Spaces | 3 | 10 | Ilimitado | Ilimitado |
| Mensagens indexadas | 10k | 100k | Ilimitado | Ilimitado |
| Storage | 5 GB | 50 GB | 500 GB | Ilimitado |
| Aprovações | Não | Sim | Sim + versões | Sim + versões + audit |
| CRM | Não | 50 deals | Ilimitado | Ilimitado + forecast |
| Automações | Não | 5 por Space | 25 por Space | Ilimitado |
| AI (resumos, insights) | Não | 100 créditos/mês | 500 créditos/mês | Ilimitado |
| Integrações | 2 | 5 | 15 | Ilimitado + custom webhook |
| SSO/SAML | Não | Não | Sim | Sim + custom domain |
| SLA de suporte | Community | Email 48h | Email 24h | Chat 4h |
| Retenção de dados | 30 dias | 1 ano | 3 anos | Ilimitado |

## **3.2 Regras de Tarefas**

|  |
| --- |
| **Status de Tarefas (obrigatório respeitar sequência)** |
| 📋 Backlog → ▶️ Em andamento → 🔍 Em revisão → ✅ Concluída  Regras de transição:  • Backlog → Em andamento: requer ao menos um responsável  • Em andamento → Em revisão: responsável marca como "pronto para revisão"  • Em revisão → Concluída: apenas admin do Space, manager ou quem criou a tarefa pode concluir  • Qualquer status → Bloqueada: qualquer membro, mas requer motivo (campo obrigatório)  • Concluída → reaberta: apenas admin ou manager, gera log de auditoria  Prioridades: P1 (crítico, badge vermelho), P2 (alto, laranja), P3 (médio, amarelo), P4 (baixo, cinza)  Overdue: tarefa com due\_date passada muda automaticamente o badge para vermelho + notifica responsável |

## **3.3 Regras de Aprovação**

|  |  |
| --- | --- |
| **Situação** | **Comportamento do Sistema** |
| Aprovação unânime requerida | Todos devem aprovar. Um "reprovar" bloqueia toda a aprovação |
| Aprovação por maioria | Contabiliza votos, maioria simples define resultado |
| Prazo vencido sem decisão | Status muda para "Expirado", notifica criador e admin do Space |
| Asset substituído após aprovação | Nova versão invalida aprovação anterior, reinicia o fluxo |
| Aprovador sem resposta 24h antes prazo | Lembrete automático enviado via notificação e email |
| Aprovador removido do workspace | Approval é reassignado ao admin do Space automaticamente |
| Comentário em asset reprovado | Thread de revisão criada com as anotações; notifica designer |

## **3.4 Regras de Mensagens e Threads**

|  |  |
| --- | --- |
| **EDIÇÃO E DELEÇÃO**   * Editar: apenas o autor, em até 24h * Mensagens editadas mostram badge "(editado)" * Deletar: autor (24h) ou admin (qualquer hora) * Mensagem com tarefa vinculada: não pode ser deletada * Admin pode deletar qualquer mensagem, gera log | **MENÇÕES E NOTIFICAÇÕES**   * @usuario: notif individual * @canal: notif todos membros do canal * @space: notif todos membros do Space * @aqui: apenas usuários online no momento * DND (Do Not Disturb) ignora todas exceto P1 * Digest diário às 9h para mensagens perdidas |

## **3.5 Automações (No-Code Rule Engine)**

O motor de automações usa estrutura de Trigger → Condição → Ação, configurável via interface visual:

|  |  |  |
| --- | --- | --- |
| **Trigger** | **Condições disponíveis** | **Ações possíveis** |
| Tarefa criada | Canal específico, label, prioridade | Atribuir responsável, enviar notif, criar checklist |
| Tarefa vencida | Sem update > N dias, responsável X | Notificar manager, reassing, postar no canal |
| Deal muda de stage | Stage específico, valor acima de R$ | Criar tarefa, notificar canal, enviar webhook |
| Mensagem com palavra-chave | Contém "#bug", "#urgente" | Criar tarefa P1, adicionar label, notificar admin |
| Aprovação concluída | Status = aprovado/reprovado | Notificar criador, mover tarefa, postar resumo |
| Novo membro no Space | Qualquer / role específico | Enviar mensagem de boas-vindas, adicionar canais padrão |
| KPI atinge threshold | Métrica < ou > valor definido | Alertar canal, criar tarefa de investigação |

## **3.6 Regras de Cobrança e Billing**

|  |
| --- |
| **Modelo de Cobrança** |
| Base: por assento ativo (usuário que fez login nos últimos 30 dias)  Cobrança mensal ou anual (desconto de 20% no anual)  Guests não contam como assento pago  Trial: 14 dias do plano Growth sem cartão  Upgrades: imediato, cobrado pro-rata  Downgrades: aplicado no próximo ciclo, dados preservados por 30 dias  Cancelamento: dados exportáveis por 90 dias após cancelamento  Limites excedidos: aviso em 80%, bloqueio soft em 100% (só leitura), hard em 110%  Usuários inativos (>60 dias): notificação ao admin, opção de remover assento com 1 clique |

## **3.7 Integrações e Webhooks**

|  |  |  |  |
| --- | --- | --- | --- |
| **Integração** | **Tipo** | **Dados sincronizados** | **Plano mínimo** |
| Meta Ads | OAuth nativo | Gastos, impressões, CTR, ROAS por campanha | Starter |
| Google Ads | OAuth nativo | Mesmo escopo Meta Ads | Starter |
| Google Analytics 4 | API Key | Sessões, conversões, fonte de tráfego | Starter |
| Slack | Bot OAuth | Receber notificações do FlowDesk no Slack | Starter |
| Zapier / Make | Webhook | Triggers e ações em qualquer app externo | Growth |
| HubSpot | API nativo | Sync bidirecional de deals e contatos | Growth |
| Pipedrive | API nativo | Importar deals existentes | Growth |
| Figma | Plugin | Preview de frames direto no canal | Growth |
| GitHub / GitLab | Webhook | PRs linkados a tarefas, deploy status | Growth |
| Custom Webhook | Configurável | Qualquer payload JSON de entrada | Business |

|  |
| --- |
| **PARTE 4 — ROADMAP DE DESENVOLVIMENTO** |

## **4.1 Fases de Lançamento**

|  |  |  |
| --- | --- | --- |
| **FASE 1 — MVP (meses 1–4)** | **FASE 2 — Growth (meses 5–8)** | **FASE 3 — Scale (meses 9–14)** |
| * Auth + workspaces + spaces * Canais + mensagens + threads * Mensagem → Tarefa (core) * Sidebar de tarefas * Notificações básicas * Mobile PWA * Planos Free e Starter | * Approval flows * CRM / Pipeline * KPI widgets nativos * Meta Ads + GA4 integração * Motor de automações * Busca full-text * Plano Growth | * AI: resumos de canais * AI: geração de tarefas * AI: insights de pipeline * HubSpot / Pipedrive sync * SSO / SAML * Audit logs completos * Plano Business |

## **4.2 Métricas de Sucesso (OKRs)**

|  |  |  |
| --- | --- | --- |
| **Fase** | **Métrica** | **Meta** |
| MVP | Workspaces ativos no final do mês 4 | 200+ workspaces |
| MVP | Retenção D30 | >35% |
| Growth | Conversão Free → Pago | >15% |
| Growth | NPS | >50 |
| Growth | ARR | R$500k |
| Scale | Churn mensal | <3% |
| Scale | Clientes Business | 20+ |
| Scale | ARR | R$2M |

*FlowDesk — Documento Técnico v1.0*

Fevereiro 2026 | Confidencial