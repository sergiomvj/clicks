|  |
| --- |
| **FBR-Click**  *Shared Resources — Infraestrutura de Conhecimento Compartilhado* |

**COMMANDS · SKILLS · HOOKS · SCRIPTS · CONNECTORS · MCP**

*Facebrasil · v1.0 · Fevereiro 2026*

|  |
| --- |
| **🏗️ O que são os Shared Resources?** |
| Shared Resources é a camada de conhecimento e infraestrutura global do FBR-Click.  São 6 pastas versionadas em Git que TODOS os agentes do workspace podem herdar,  eliminando duplicação de código, padronizando comportamentos e centralizando  integrações externas que seriam reescritas em cada agente separadamente.  Hierarquia de resolução (do mais específico ao mais genérico):  1. Arquivo pessoal do agente (AGENTS.md, SOUL.md, etc.) — maior prioridade  2. Shared Resources declarados no AGENTS.md do agente  3. Defaults globais do workspace FBR-Click  Localização física: Repositório Git separado (fbr-click/shared-resources)  espelhado no VPS em /opt/fbr-click/shared/ via sync automático a cada push. |

|  |
| --- |
| **PARTE 1 — ESTRUTURA DO REPOSITÓRIO SHARED-RESOURCES** |

## **1.1 Árvore de Diretórios**

|  |
| --- |
| # Repositório: github.com/facebrasil/fbr-click-shared  # Branch padrão: main  # Sync automático para: /opt/fbr-click/shared/ no VPS  fbr-click-shared/  ├── COMMANDS/  │ ├── README.md # índice de todos os comandos  │ ├── vendas/ # comandos do time de vendas  │ │ ├── pipeline.md  │ │ └── proposta.md  │ ├── marketing/ # comandos do time de marketing  │ │ ├── campanha.md  │ │ └── relatorio.md  │ └── global/ # comandos disponíveis para todos  │ ├── briefing.md  │ └── resumo.md  ├── SKILLS/  │ ├── README.md  │ ├── redacao-comercial/ # skill de escrita de propostas  │ │ └── SKILL.md  │ ├── analise-pipeline/ # skill de análise de funil  │ │ └── SKILL.md  │ ├── seo-content/ # skill de otimização de conteúdo  │ │ └── SKILL.md  │ └── relatorio-executivo/ # skill de relatórios  │ └── SKILL.md  ├── HOOKS/  │ ├── README.md  │ ├── on-deal-stage-change.md # hook: deal muda de stage  │ ├── on-task-overdue.md # hook: tarefa vencida  │ ├── on-approval-complete.md # hook: approval finalizado  │ ├── on-new-member.md # hook: novo membro no workspace  │ └── on-kpi-threshold.md # hook: KPI cruza limite  ├── SCRIPTS/  │ ├── README.md  │ ├── python/ # scripts Python  │ │ ├── pipeline\_report.py  │ │ ├── kpi\_calculator.py  │ │ └── lead\_scorer.py  │ ├── node/ # scripts Node.js  │ │ ├── format\_proposal.js  │ │ └── sync\_contacts.js  │ └── bash/ # scripts shell  │ ├── git\_sync.sh  │ └── health\_check.sh  ├── CONNECTORS/  │ ├── README.md  │ ├── meta-ads/ # Meta Ads API  │ │ ├── CONNECTOR.md  │ │ └── client.js  │ ├── google-ads/ # Google Ads API  │ │ ├── CONNECTOR.md  │ │ └── client.js  │ ├── google-analytics/ # GA4 API  │ │ ├── CONNECTOR.md  │ │ └── client.js  │ ├── whatsapp-business/ # WhatsApp Business API  │ │ ├── CONNECTOR.md  │ │ └── client.js  │ └── email-smtp/ # SMTP genérico  │ ├── CONNECTOR.md  │ └── client.js  └── MCP/  ├── README.md  ├── fbr-click-mcp/ # MCP do próprio FBR-Click  │ ├── MCP.md  │ └── server.js  ├── github-mcp/ # MCP para operações no Git  │ ├── MCP.md  │ └── server.js  ├── notion-mcp/ # MCP para Notion (documentação)  │ ├── MCP.md  │ └── server.js  └── browser-mcp/ # MCP para automação de browser  ├── MCP.md  └── server.js |

## **1.2 Como um Agente Declara Dependências no AGENTS.md**

O agente lista explicitamente os recursos compartilhados que precisa. O FBR-Click resolve as dependências antes de iniciar o Gateway e monta o filesystem do agente.

|  |
| --- |
| # AGENTS.md — Comercial Bot (trecho de shared\_resources)  shared\_resources:  commands:  - global/briefing # comando /briefing disponível globalmente  - global/resumo # comando /resumo disponível globalmente  - vendas/pipeline # comandos específicos de vendas  - vendas/proposta # comandos de geração de proposta  skills:  - redacao-comercial # aprende a escrever propostas no tom certo  - analise-pipeline # aprende a analisar e interpretar funil  - relatorio-executivo # aprende formato de relatório executivo  hooks:  - on-deal-stage-change # age quando deal muda de stage  - on-task-overdue # age quando tarefa de vendas vence  - on-kpi-threshold # alerta quando pipeline abaixo da meta  scripts:  - python/pipeline\_report # gera relatório de pipeline em PDF  - python/lead\_scorer # calcula score de leads  - node/format\_proposal # formata proposta em template padrão  connectors:  - meta-ads # acessa métricas de campanhas  - whatsapp-business # envia follow-ups via WhatsApp  mcp:  - fbr-click-mcp # acesso completo à API do FBR-Click  - github-mcp # lê e commita MEMORY.md no Git |

## **1.3 Resolução e Montagem — Fluxo Técnico**

|  |  |  |  |
| --- | --- | --- | --- |
| **Passo** | **Responsável** | **O que acontece** | **Onde** |
| 1 | Admin (Git) | Faz push de novos recursos no fbr-click-shared | GitHub |
| 2 | GitHub Webhook | Notifica FBR-Click sobre mudança no shared-resources | HTTPS POST |
| 3 | shared-sync service | git pull no VPS: /opt/fbr-click/shared/ | VPS |
| 4 | resource-validator | Valida schemas de todos os arquivos alterados | FBR-Click backend |
| 5 | dependency-resolver | Para cada agente afetado, recalcula dependências | FBR-Click backend |
| 6 | agent-service | Notifica OpenClaw Gateway via WebSocket: config\_reload | WebSocket |
| 7 | OpenClaw Gateway | Remonta filesystem virtual do agente com novos recursos | VPS / Gateway |
| 8 | Agent Loop | Próximo ciclo já usa versão atualizada dos recursos | OpenClaw |
| 9 | audit-log | Registra quais agentes foram afetados e qual SHA do Git | PostgreSQL |

|  |
| --- |
| **PARTE 2 — COMMANDS** |

|  |  |
| --- | --- |
| ⌨️ | **COMMANDS/**  *Define comandos slash (/comando) e palavras-chave que ativam comportamentos específicos nos agentes* |

COMMANDS são instruções nomeadas que humanos e outros agentes podem invocar explicitamente. Funcionam como funções: têm nome, parâmetros, comportamento esperado e resposta padronizada. Cada arquivo .md dentro de COMMANDS/ define um ou mais comandos relacionados.

### **Anatomia de um arquivo COMMAND**

|  |
| --- |
| # COMMANDS/vendas/proposta.md  ---  name: proposta  aliases: [proposal, gerar-proposta]  description: Gera rascunho de proposta comercial para um deal  available\_to: [comercial-bot, report-bot]  require\_context: [deal\_id]  ---  ## Comando: /proposta  ### Quando ativado  Ativado quando um humano ou agente escreve:  /proposta [nome-do-deal]  /proposal [deal-id]  "gera uma proposta para [cliente]"  ### Parâmetros  - deal\_name ou deal\_id (obrigatório)  - tom: formal | amigável (opcional, default: formal)  - formato: completo | resumido (opcional, default: completo)  ### Comportamento esperado  1. Buscar deal no FBR-Click via fbr\_get\_deal()  2. Carregar dados do cliente de MEMORY.md  3. Carregar template via SCRIPTS/node/format\_proposal  4. Usar SKILLS/redacao-comercial para adaptar o tom  5. Postar rascunho no canal do deal como mensagem + tarefa  6. Responder: "Rascunho da proposta [deal] gerado. Tarefa criada para revisão."  ### Resposta padrão (formato)  📄 Proposta: [NOME DO CLIENTE]  Plano sugerido: [PLANO] | Valor: R$[VALOR]/m  Próximo passo: [AÇÃO SUGERIDA]  → Tarefa de revisão atribuída a @[responsável] |

### **Comandos globais obrigatórios (todo agente herda)**

|  |  |  |  |
| --- | --- | --- | --- |
| **Comando** | **Aliases** | **O que faz** | **Resposta** |
| /briefing | /status, /resumo-hoje | Gera briefing do dia para o agente | Lista de prioridades + pendências do dia |
| /resumo [canal] | /summary | Resume as últimas N mensagens do canal | Resumo em bullets com decisões destacadas |
| /tarefas | /tasks, /pendentes | Lista tarefas abertas atribuídas ao agente | Lista ordenada por prioridade + prazo |
| /ajuda | /help, /comandos | Lista todos os comandos disponíveis para este agente | Lista formatada com descrição de cada comando |
| /pausa | /pause, /silencio | Coloca agente em modo silencioso por N horas | Confirmação + hora de retorno |
| /memoria [fato] | /lembra, /save | Salva fato na MEMORY.md do agente | Confirmação do que foi salvo |
| /identidade | /quem-sou, /whoami | Agente descreve sua função e capacidades | Descrição baseada em IDENTITY.md |

|  |
| --- |
| **PARTE 3 — SKILLS** |

|  |  |
| --- | --- |
| 🧠 | **SKILLS/**  *Aprendizado especializado que amplia as capacidades cognitivas dos agentes em domínios específicos* |

SKILLS são pacotes de conhecimento especializado que "ensinam" o agente a executar tarefas de alta qualidade em um domínio. Seguem o formato SKILL.md do OpenClaw/ClawHub, mas são gerenciadas centralmente no repositório shared-resources do Facebrasil — sem dependência do ClawHub público.

### **Anatomia de um arquivo SKILL**

|  |
| --- |
| # SKILLS/redacao-comercial/SKILL.md  ---  name: redacao-comercial  description: Escrever propostas e textos comerciais no tom e formato do Facebrasil  version: 1.2.0  domain: vendas  metadata:  openclaw:  requires:  env: []  bins: []  ---  ## Skill: Redação Comercial Facebrasil  ### Contexto de domínio  O Facebrasil é uma revista eletrônica para brasileiros nos EUA desde 2010.  Clientes são empresas brasileiras com operação nos EUA.  Propostas devem equilibrar familiaridade (somos brasileiros) com  profissionalismo (estamos no mercado americano).  ### Tom obrigatório  - Direto e confiante: evitar hedging ("talvez", "pode ser", "tente")  - Personalizado: sempre mencionar o nome do cliente e contexto específico  - Orientado a resultado: focar no que o cliente GANHA, não no que vendemos  - Português brasileiro formal mas não rebuscado  ### Estrutura padrão de proposta  1. Saudação personalizada (1 parágrafo — menciona contexto da conversa)  2. Entendimento do problema (2-3 bullets)  3. Solução proposta (plano + features relevantes para ESTE cliente)  4. Investimento (valor + condições + comparativo de ROI)  5. Próximos passos (data limite + CTA específico)  ### Padrões proibidos  - Nunca usar "soluções inovadoras" ou clichês de marketing  - Nunca omitir o valor — sempre apresentar o preço com contexto  - Nunca proposta genérica — sempre customizar seção 1 e 3 |

### **Skills disponíveis no workspace Facebrasil**

|  |  |  |  |
| --- | --- | --- | --- |
| **Skill** | **Domínio** | **Ensina o agente a...** | **Agentes que usam** |
| redacao-comercial | Vendas | Escrever propostas no tom e formato do Facebrasil | Comercial Bot |
| analise-pipeline | Vendas | Interpretar dados de funil, identificar gargalos, recomendar ações | Comercial Bot, Report Bot |
| seo-content | Conteúdo | Otimizar textos para SEO, usar keywords sem perder naturalidade | Content Bot |
| redacao-editorial | Conteúdo | Escrever no estilo editorial do Facebrasil, com voz consistente | Content Bot |
| analise-ads | Marketing | Interpretar métricas de Meta/Google Ads, identificar anomalias | Ads Bot |
| relatorio-executivo | Geral | Formatar relatórios concisos para liderança (máx 1 página) | Report Bot, todos |
| comunicacao-interna | Geral | Tom certo para mensagens no canal, sem ser invasivo | Todos os agentes |

|  |
| --- |
| **PARTE 4 — HOOKS** |

|  |  |
| --- | --- |
| 🔗 | **HOOKS/**  *Diretivas de encadeamento de ações — define o que acontece após cada evento do sistema* |

HOOKS são regras de encadeamento que transformam eventos do FBR-Click em sequências de ações coordenadas entre agentes. Um HOOK define: qual evento o dispara, quais agentes devem reagir, em que ordem, e o que cada um deve fazer. São a cola entre os agentes.

### **Anatomia de um arquivo HOOK**

|  |
| --- |
| # HOOKS/on-deal-stage-change.md  ---  name: on-deal-stage-change  event: deal.stage\_changed  description: Orquestra ações quando um deal muda de stage no pipeline  version: 1.0.0  ---  ## Hook: Deal Stage Changed  ### Evento de disparo  Emitido pelo FBR-Click crm-service quando qualquer deal muda de stage.  Payload disponível: { deal\_id, deal\_name, from\_stage, to\_stage,  assignee\_id, value, client\_name, channel\_id }  ### Regras de encadeamento por transição  #### Qualquer stage → "Proposta Enviada"  AGENTE: comercial-bot  1. Executar /proposta [deal\_id] (via COMMANDS/vendas/proposta)  2. Criar tarefa: "Acompanhar resposta [client\_name]" em +5 dias  3. Postar no canal: resumo da proposta + próximo passo  #### Qualquer stage → "Negociação"  AGENTE: comercial-bot  1. Buscar histórico do deal em MEMORY.md  2. Criar tarefa: "Preparar argumentos de negociação [client\_name]"  3. Notificar manager via @menção com valor do deal  AGENTE: report-bot (paralelo, não bloqueia comercial-bot)  1. Atualizar KPI "Deals em negociação" no Space vendas  #### Qualquer stage → "Fechado — Ganho"  AGENTE: comercial-bot  1. Postar celebração no canal #geral-vendas  2. Criar tarefa de onboarding do novo cliente  AGENTE: content-bot (após comercial-bot)  1. Criar pauta de case study sobre o cliente (se autorizado)  AGENTE: ads-bot (paralelo)  1. Atualizar MEMORY.md com novo cliente como caso de sucesso  #### Qualquer stage → "Fechado — Perdido"  AGENTE: comercial-bot  1. Criar tarefa de análise de loss: "Por que perdemos [client\_name]?"  2. Registrar motivo em MEMORY.md para aprendizado futuro  3. Notificar manager com resumo do deal e motivo informado |

### **Catálogo de Hooks do Workspace Facebrasil**

|  |  |  |  |
| --- | --- | --- | --- |
| **Hook** | **Evento disparador** | **Agentes envolvidos** | **Sequência ou paralelo** |
| on-deal-stage-change | deal.stage\_changed | comercial-bot + report-bot | Comercial primeiro, report paralelo |
| on-task-overdue | task.due\_date\_passed | Agente dono da tarefa + manager | Sequencial: notifica → escalona |
| on-approval-complete | approval.decided | approval-bot → agente solicitante | Sequencial: notifica → próxima ação |
| on-new-member | member.joined\_workspace | onboarding-bot | Single agent, automático |
| on-kpi-threshold | kpi.threshold\_crossed | ads-bot ou report-bot | Depende do KPI cruzado |
| on-mention-agent | message.agent\_mentioned | Agente mencionado | Single, reativo imediato |
| on-approval-expiring | approval.deadline\_minus\_24h | approval-bot | Lembrete automático |
| on-channel-created | channel.created | Agentes do Space | Agentes se auto-registram no canal |

### **Encadeamento multi-agente — exemplo visual**

|  |
| --- |
| **📋 Cenário: Deal Construmax fechado como GANHO** |
| EVENTO: deal.stage\_changed → "Fechado — Ganho"  PASSO 1 — comercial-bot (trigger imediato):  → Posta celebração em #geral-vendas: "🎉 Deal Construmax fechado! R$6.500/m"  → Cria tarefa: "Onboarding Construmax" atribuída a Julia (manager)  → Atualiza MEMORY.md: "Construmax: cliente ativo desde 24/02/2026"  PASSO 2 — report-bot (paralelo ao passo 1):  → Atualiza KPI "Fechamentos do mês": 8 → 9  → Atualiza KPI "ARR adicionado": +R$78k  PASSO 3 — content-bot (após passo 1 concluir):  → Cria pauta em rascunho: "Case study: como a Construmax acelerou X com FBR-Click"  → Atribui a editor humano para aprovação antes de publicar  PASSO 4 — ads-bot (paralelo ao passo 3):  → Salva Construmax como referência de cliente no segmento Construção  → Verifica se há outras empresas similares no pipeline para priorizar |

|  |
| --- |
| **PARTE 5 — SCRIPTS** |

|  |  |
| --- | --- |
| 📜 | **SCRIPTS/**  *Repositório central de todos os scripts executáveis referenciados por agentes, commands, hooks e skills* |

SCRIPTS centraliza todo código executável do ecossistema FBR-Click. Agentes não escrevem scripts ad-hoc — eles referenciam scripts versionados e testados deste repositório. Isso garante consistência, segurança e facilidade de manutenção.

### **Anatomia de um script referenciável**

|  |
| --- |
| # SCRIPTS/python/pipeline\_report.py  # Referenciado como: scripts/python/pipeline\_report  # Chamada pelos agentes: run\_script("python/pipeline\_report", args)  #!/usr/bin/env python3  """  Gera relatório de pipeline em formato markdown estruturado.  Input: JSON com lista de deals do FBR-Click  Output: Markdown formatado para postar no canal  """  import sys, json  def generate\_report(deals: list) -> str:  total\_value = sum(d["value"] for d in deals)  by\_stage = {}  for deal in deals:  stage = deal["stage"]  by\_stage.setdefault(stage, []).append(deal)  lines = ["## 📊 Relatório de Pipeline", ""]  for stage, items in by\_stage.items():  stage\_value = sum(d["value"] for d in items)  lines.append(f"\*\*{stage}\*\* ({len(items)} deals · R${stage\_value:,.0f}/m)")  for d in items:  lines.append(f" • {d['name']} — R${d['value']:,.0f}/m — @{d['assignee']}")  lines.append("")  lines.append(f"\*\*Total pipeline: R${total\_value:,.0f}/m\*\*")  return "\n".join(lines)  if \_\_name\_\_ == "\_\_main\_\_":  data = json.loads(sys.stdin.read())  print(generate\_report(data["deals"])) |

### **Catálogo de Scripts**

|  |  |  |  |
| --- | --- | --- | --- |
| **Script** | **Linguagem** | **Função** | **Usado por** |
| pipeline\_report.py | Python | Gera relatório markdown do pipeline por stage e valor | Comercial Bot, Report Bot |
| kpi\_calculator.py | Python | Calcula KPIs derivados: CAC, LTV, taxa de conversão por stage | Report Bot, Ads Bot |
| lead\_scorer.py | Python | Pontua leads com base em critérios do Facebrasil (0-100) | Comercial Bot |
| format\_proposal.js | Node.js | Aplica template v3 de proposta com dados do deal | Comercial Bot |
| sync\_contacts.js | Node.js | Sincroniza contatos entre FBR-Click CRM e WhatsApp Business | Comercial Bot |
| git\_sync.sh | Bash | git pull no shared-resources com validação e rollback | shared-sync service |
| health\_check.sh | Bash | Verifica saúde de todos os agentes e serviços do FBR-Click | Monitoramento / cron |

### **Regras de segurança para SCRIPTS**

|  |  |
| --- | --- |
| **✓ OBRIGATÓRIO**   * Todo script tem header com propósito, input e output documentados * Scripts Python: tipagem com type hints * Scripts Node.js: validação de input com schema JSON * Sem hardcode de credenciais — sempre via env vars * Erros tratados explicitamente, saída de erro para stderr * Cada script tem um test mínimo em /tests/ * Versionado: mudanças incompatíveis incrementam versão no header | **✗ PROIBIDO**   * Scripts com acesso a filesystem fora de /tmp e workspace do agente * Requisições HTTP sem passar pelo CONNECTORS * Scripts que modificam outros scripts (execução auto-modificável) * Loops sem timeout definido * Acesso a variáveis de ambiente de outros agentes * Scripts maiores que 500 linhas — dividir em módulos * Dependências externas não declaradas no header |

|  |
| --- |
| **PARTE 6 — CONNECTORS** |

|  |  |
| --- | --- |
| 🔌 | **CONNECTORS/**  *Todas as conexões a APIs externas — autenticação, rate limits, e interface padronizada para os agentes* |

CONNECTORS encapsula toda a complexidade de integração com APIs externas. Agentes nunca chamam APIs diretamente — eles usam o connector correspondente. Isso centraliza autenticação, tratamento de erros, rate limiting e rotação de credenciais.

### **Anatomia de um CONNECTOR**

|  |
| --- |
| # CONNECTORS/meta-ads/CONNECTOR.md  ---  name: meta-ads  service: Meta Ads (Facebook Ads)  version: 2.0.0  auth: oauth2  env\_vars: [META\_APP\_ID, META\_APP\_SECRET, META\_ACCESS\_TOKEN]  rate\_limit: 200 req/hora por conta de anúncio  docs: https://developers.facebook.com/docs/marketing-api  ---  ## Connector: Meta Ads  ### Autenticação  OAuth 2.0 com refresh token automático.  Credenciais armazenadas em FBR-Click Vault (não no Git).  Acesso via: connector.auth("meta-ads") — retorna token válido.  ### Funções disponíveis para agentes  #### get\_campaign\_insights(account\_id, date\_range, metrics[])  Retorna: { impressions, clicks, ctr, spend, cpm, cpp, roas }  Uso: verificar performance de campanha ativa  #### get\_ad\_sets(campaign\_id)  Retorna: lista de ad sets com status e budget  #### get\_spend\_today(account\_id)  Retorna: valor gasto hoje vs. orçamento diário  Uso: alerta se gasto > 90% do orçamento antes das 18h  ### Tratamento de erros padrão  - 429 Rate Limit: retry automático com backoff exponencial (3x)  - 190 Token Expirado: refresh automático antes de retentar  - 100 Invalid Parameter: logar erro e notificar admin, não retry  ### Rate limit  Máx 200 req/hora. Connector distribui automaticamente.  Se múltiplos agentes usam o mesmo connector, fila compartilhada. |

### **Catálogo de Connectors**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Connector** | **Serviço** | **Auth** | **Funções principais** | **Agentes** |
| meta-ads | Meta Ads API v20 | OAuth2 | campaign\_insights, spend\_today, ad\_sets | Ads Bot |
| google-ads | Google Ads API v17 | OAuth2 (service account) | campaign\_metrics, keyword\_performance, budget | Ads Bot |
| google-analytics | GA4 Data API | Service Account | session\_data, conversions, traffic\_source | Ads Bot, Report Bot |
| whatsapp-business | WhatsApp Business Cloud API | Bearer Token | send\_message, send\_template, get\_status | Comercial Bot |
| email-smtp | SMTP genérico (Resend/SES) | API Key | send\_email, send\_template, get\_delivery\_status | Todos |
| openai | OpenAI API | API Key | chat\_completion, embeddings (via OpenClaw) | Fallback de LLM |
| anthropic | Anthropic API | API Key | claude\_completion (modelo primário) | Todos os agentes |

### **FBR-Click Vault — Gestão Segura de Credenciais**

|  |
| --- |
| **🔐 Como as credenciais dos Connectors são gerenciadas** |
| Credenciais NUNCA ficam no repositório Git.  São armazenadas no FBR-Click Vault — serviço dedicado de secrets.  Fluxo de acesso:  1. Admin cadastra credencial no painel: Configurações → Vault → Novo Secret  2. Secret recebe um nome de referência: ex. META\_ACCESS\_TOKEN  3. CONNECTOR.md declara quais env vars precisa: env\_vars: [META\_ACCESS\_TOKEN]  4. Ao iniciar o agente, agent-service injeta as env vars no processo OpenClaw  5. Connector acessa via process.env.META\_ACCESS\_TOKEN — nunca hardcoded  Rotação automática:  • Tokens OAuth2: refresh automático pelo connector antes de expirar  • API Keys: alerta ao admin quando próximo do vencimento  • Audit: todo acesso ao Vault é logado com agent\_id + timestamp |

|  |
| --- |
| **PARTE 7 — MCP (Model Context Protocol)** |

|  |  |
| --- | --- |
| 🤖 | **MCP/**  *Repositório central de servidores MCP — expande drasticamente as capacidades dos agentes com acesso estruturado a sistemas externos* |

MCP (Model Context Protocol, Anthropic) é o protocolo que permite agentes acessarem ferramentas, dados e sistemas externos de forma estruturada. O FBR-Click mantém um repositório central de servidores MCP que os agentes podem usar, além do MCP nativo do próprio FBR-Click.

### **Anatomia de um arquivo MCP**

|  |
| --- |
| # MCP/fbr-click-mcp/MCP.md  ---  name: fbr-click-mcp  description: MCP server que expõe todas as ações do FBR-Click como tools MCP  version: 1.0.0  transport: stdio  server\_command: node /opt/fbr-click/shared/MCP/fbr-click-mcp/server.js  env\_vars: [FBR\_AGENT\_TOKEN, FBR\_WORKSPACE\_ID, FBR\_API\_URL]  ---  ## MCP: FBR-Click Native  ### Propósito  Expõe todas as ações da Agent API do FBR-Click como tools MCP nativas,  permitindo que agentes OpenClaw usem o protocolo MCP padrão para  interagir com a plataforma.  ### Tools disponíveis  #### fbr\_post\_message  Posta mensagem em um canal do FBR-Click.  Input: { channel\_id: string, text: string, thread\_id?: string }  Output: { message\_id: string, posted\_at: string }  #### fbr\_create\_task  Cria tarefa no FBR-Click com todos os atributos.  Input: { title, channel\_id, assignee\_id, due\_date, priority, labels[] }  Output: { task\_id, url }  #### fbr\_query\_pipeline  Consulta o pipeline de vendas com filtros.  Input: { stage?, assignee\_id?, min\_value?, max\_age\_days? }  Output: { deals: Deal[], total\_value: number }  #### fbr\_get\_kpi\_snapshot  Retorna snapshot atual dos KPIs de um Space.  Input: { space\_id: string, metrics: string[] }  Output: { [metric]: { value, trend, last\_updated } }  #### fbr\_request\_human\_approval  Solicita aprovação humana para ação sensível.  Input: { action\_type, description, payload, channel\_id }  Output: { approval\_id, status: "pending" } |

### **Catálogo de MCPs**

|  |  |  |  |
| --- | --- | --- | --- |
| **MCP** | **Propósito** | **Tools principais** | **Agentes típicos** |
| fbr-click-mcp | Acesso nativo a toda API do FBR-Click | post\_message, create\_task, query\_pipeline, get\_kpi | Todos os agentes |
| github-mcp | Operações no repositório Git dos agentes | read\_file, write\_file, commit, list\_directory | Todos (para MEMORY.md) |
| notion-mcp | Leitura e escrita de documentação no Notion | read\_page, create\_page, search, update\_block | Content Bot, Report Bot |
| browser-mcp | Automação de browser para pesquisa e scraping | navigate, screenshot, extract\_text, fill\_form | Ads Bot, Content Bot |
| filesystem-mcp | Acesso controlado ao filesystem do VPS | read\_file, write\_file, list\_dir (sandbox /tmp) | Todos |
| sqlite-mcp | Banco de dados local para cache de agentes | query, insert, update, create\_table | Report Bot |

### **Como o OpenClaw carrega os MCPs declarados**

|  |
| --- |
| # Trecho do openclaw.json do agente (gerado automaticamente pelo FBR-Click)  # a partir das declarações em AGENTS.md  {  "mcpServers": {  "fbr-click-mcp": {  "command": "node",  "args": ["/opt/fbr-click/shared/MCP/fbr-click-mcp/server.js"],  "env": {  "FBR\_AGENT\_TOKEN": "${FBR\_AGENT\_TOKEN}",  "FBR\_WORKSPACE\_ID": "${FBR\_WORKSPACE\_ID}",  "FBR\_API\_URL": "https://fbr-click.com/api"  }  },  "github-mcp": {  "command": "node",  "args": ["/opt/fbr-click/shared/MCP/github-mcp/server.js"],  "env": {  "GITHUB\_TOKEN": "${GITHUB\_TOKEN}",  "AGENT\_REPO": "facebrasil/fbr-click-agents/comercial-bot"  }  }  }  }  # Este arquivo é gerado em /opt/fbr-click/agents/{agent\_id}/openclaw.json  # e injetado no Gateway ao iniciar o agente. |

|  |
| --- |
| **PARTE 8 — VISÃO UNIFICADA: AGENTE + SHARED RESOURCES** |

## **8.1 Filesystem Virtual do Agente no VPS**

Quando o FBR-Click inicia um agente, monta um filesystem virtual que combina os arquivos pessoais do agente com os recursos compartilhados declarados. O agente enxerga tudo como se fosse local.

|  |
| --- |
| # Filesystem virtual montado para o Comercial Bot  # Localização no VPS: /opt/fbr-click/agents/comercial-bot/  /opt/fbr-click/agents/comercial-bot/  ├── SOUL.md ← pessoal: do repo facebrasil/agents/comercial-bot  ├── IDENTITY.md ← pessoal  ├── TASKS.md ← pessoal  ├── AGENTS.md ← pessoal (declara shared\_resources)  ├── MEMORY.md ← pessoal (atualizado pelo agente)  ├── TOOLS.md ← pessoal  ├── USER.md ← pessoal  ├── memory/ ← pessoal (diários)  │ └── 2026-02-24.md  ├── openclaw.json ← gerado automaticamente pelo FBR-Click  │  ├── commands/ ← SYMLINKS para /opt/fbr-click/shared/COMMANDS/  │ ├── global/briefing.md  │ ├── global/resumo.md  │ ├── vendas/pipeline.md  │ └── vendas/proposta.md  │  ├── skills/ ← SYMLINKS para /opt/fbr-click/shared/SKILLS/  │ ├── redacao-comercial/SKILL.md  │ ├── analise-pipeline/SKILL.md  │ └── relatorio-executivo/SKILL.md  │  ├── hooks/ ← SYMLINKS para /opt/fbr-click/shared/HOOKS/  │ ├── on-deal-stage-change.md  │ ├── on-task-overdue.md  │ └── on-kpi-threshold.md  │  ├── scripts/ ← SYMLINKS para /opt/fbr-click/shared/SCRIPTS/  │ ├── python/pipeline\_report.py  │ ├── python/lead\_scorer.py  │ └── node/format\_proposal.js  │  ├── connectors/ ← SYMLINKS para /opt/fbr-click/shared/CONNECTORS/  │ ├── meta-ads/  │ └── whatsapp-business/  │  └── mcp/ ← SYMLINKS para /opt/fbr-click/shared/MCP/  ├── fbr-click-mcp/  └── github-mcp/ |

## **8.2 Precedência de Resolução**

Quando existe conflito entre um recurso pessoal e um compartilhado, a regra é sempre: o mais específico vence. O agente pode sobrescrever qualquer comportamento compartilhado criando um arquivo local com o mesmo nome.

|  |  |  |  |
| --- | --- | --- | --- |
| **Nível** | **Localização** | **Prioridade** | **Exemplo de uso** |
| 1 — Pessoal do agente | repo: facebrasil/agents/{agente}/ | MAIS ALTA | SOUL.md, override de SKILL local |
| 2 — Shared declarado | repo: fbr-click-shared/ (declarado no AGENTS.md) | MÉDIA | COMMANDS/, SKILLS/ padrão |
| 3 — Default FBR-Click | Embutido no agent-service | MAIS BAIXA | Comandos /ajuda, /identidade |

## **8.3 Tabela Resumo: Todos os Shared Resources**

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Pasta** | **Propósito** | **Formato** | **Editado por** | **Afeta agente quando** |
| COMMANDS/ | Define comandos /slash e palavras-chave | Markdown com frontmatter YAML | Admin / Tech Lead | Declarado em shared\_resources.commands |
| SKILLS/ | Aprendizado especializado por domínio | SKILL.md (formato OpenClaw/ClawHub) | Especialistas de domínio | Declarado em shared\_resources.skills |
| HOOKS/ | Encadeamento de ações entre agentes | Markdown com regras por evento | Admin / Arquiteto | Declarado em shared\_resources.hooks |
| SCRIPTS/ | Scripts executáveis centralizados | Python / Node.js / Bash | Desenvolvedor | Declarado em shared\_resources.scripts |
| CONNECTORS/ | Integrações com APIs externas | CONNECTOR.md + client.js | Desenvolvedor | Declarado em shared\_resources.connectors |
| MCP/ | Servidores MCP para ferramentas avançadas | MCP.md + server.js | Desenvolvedor | Declarado em shared\_resources.mcp |

*FBR-Click — Shared Resources Architecture v1.0*

Fevereiro 2026 · Facebrasil · COMMANDS · SKILLS · HOOKS · SCRIPTS · CONNECTORS · MCP