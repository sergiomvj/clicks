|  |
| --- |
| **FBR-Click — Adendo**  *Shared Resources como Capacidades Cross-Domain: o agente além do seu papel* |

*"O que eu sei fazer todos os dias é meu domínio. O que eu posso fazer quando a situação exige é minha capacidade."*

*Facebrasil · FBR-Click · v1.0 adendo · Fevereiro 2026*

|  |
| --- |
| **💡 A Revisão Conceitual — Por que este adendo existe** |
| O documento anterior descreveu Shared Resources como infraestrutura técnica:  bibliotecas de código, scripts, integrações de API.  Este adendo corrige e expande esse entendimento.  A verdade mais profunda é esta:  Shared Resources são CAPACIDADES SOB DEMANDA.  Um agente tem um domínio fixo (definido no SOUL.md e IDENTITY.md).  Mas quando a situação exige — quando sua experiência específica  encontra uma oportunidade fora do seu papel habitual —  ele pode TOMAR EMPRESTADO uma capacidade do workspace compartilhado,  agir com ela, e devolver o resultado ao humano ou ao sistema.  O Comercial Bot não é um copywriter.  Mas ele conhece os clientes melhor do que qualquer outro agente.  Quando ele percebe que três clientes pediram o mesmo produto esta semana,  a skill copy-campanha transforma esse insight em uma campanha rascunhada.  Sem precisar de um agente de marketing. Sem precisar de um humano como intermediário. |

|  |
| --- |
| **PARTE 1 — O MODELO MENTAL: DOMÍNIO × CAPACIDADE** |

## **1.1 Domínio vs. Capacidade**

|  |  |
| --- | --- |
| **DOMÍNIO**  O que o agente FAZ todos os dias.   * Definido em SOUL.md e IDENTITY.md * Imutável no dia a dia — é o papel do agente * Carregado automaticamente em todo ciclo * Exemplo: Comercial Bot faz pipeline, follow-ups, propostas   *→ É o conjunto de skills declaradas no AGENTS.md do agente como permanentes.* | **CAPACIDADE CROSS-DOMAIN**  O que o agente pode fazer quando a situação exige.   * Definida nos Shared Resources — disponível a qualquer agente * Ativada sob demanda, não carregada em todo ciclo * Orientada por humano, por trigger de HOOK, ou por iniciativa do agente * Exemplo: Comercial Bot usa copy-campanha para criar rascunho de campanha   *→ São os recursos do workspace que o agente pode requisitar situacionalmente.* |

## **1.2 Os Três Modos de Orientação**

Um agente pode chegar a uma capacidade cross-domain de três formas. Cada modo tem um fluxo de execução e nível de autonomia diferente.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Modo** | **Quem orienta** | **Como ativa** | **Nível de autonomia** | **Exemplo** |
| 1 — Humano orienta | Usuário humano via mensagem | Instrução direta no canal: "cria uma campanha baseada nos seus clientes" | Baixo — humano está no controle | "@comercial-bot, usa o que você sabe dos clientes pra criar uma campanha de reativação" |
| 2 — HOOK detecta | Sistema detecta padrão via HOOK | Evento acumula evidências → HOOK sugere capacidade relevante | Médio — sistema propõe, humano confirma | Três deals perdidos pelo mesmo motivo → HOOK ativa skill de análise de objeções |
| 3 — Agente propõe | Própria inteligência do agente | Agente percebe oportunidade e propõe ao humano antes de agir | Alto — agente age mas sempre propõe primeiro | Comercial Bot: "Notei que 4 clientes pediram desconto no plano Growth. Posso criar um rascunho de campanha?" |

## **1.3 Regra de Ouro: Propor Antes de Agir**

Para capacidades fora do domínio natural do agente, a regra é sempre a mesma: o agente PROPÕE ao humano o que pretende fazer, e aguarda confirmação antes de executar. Isso preserva o controle humano sem sacrificar a proatividade do agente.

|  |  |
| --- | --- |
| **✓ CORRETO — Agente que propõe**  *"@julia, percebi que três clientes mencionaram o mesmo problema esta semana: custo de aquisição alto no plano Starter. Tenho acesso à skill copy-campanha. Quer que eu monte um rascunho de campanha de upsell direcionada para esse segmento?"*  → Julia confirma → agente executa → resultado postado no canal para revisão. | **✗ ERRADO — Agente que age sem avisar**  *"Criei uma campanha de upsell baseada nos insights dos clientes e já postei no canal #marketing para revisão da equipe."*  → Agente agiu fora do seu domínio sem autorização. Pode causar confusão e desconfiança no time. |

|  |
| --- |
| **PARTE 2 — CASOS DE USO CROSS-DOMAIN CONFIRMADOS** |

Os quatro casos de uso validados para o Facebrasil. Cada um mostra um agente usando capacidade fora do seu domínio natural — com o fluxo completo de orientação, execução e entrega.

|  |  |
| --- | --- |
| 💼→📢 | **Comercial Bot cria rascunho de campanha**  *Agente: Comercial Bot (domínio: vendas) → Capacidade extra: copy-campanha (domínio: marketing)*  Gatilho: Padrão identificado nos clientes: mesmo problema, mesmo segmento  **Resultado: Rascunho de campanha de upsell baseado em inteligência de campo real** |

|  |
| --- |
| **👤 Julia (manager, no canal #geral-vendas):**  "Comercial, você tem visto algum padrão nos clientes desta semana?"  **🤖 Comercial Bot:**  "Sim. Três clientes diferentes (TechCorp, LogTech, Softway) mencionaram  custo de aquisição alto como objeção ao plano Starter.  Todos estão no segmento de SaaS B2B.  Tenho acesso à skill copy-campanha nos Shared Resources.  Posso criar um rascunho de campanha de upsell direcionada para  SaaS B2B que aborde essa objeção diretamente.  Quer que eu monte? Leva uns 2 minutos."  **👤 Julia:**  "Pode fazer."  **🤖 Comercial Bot [ativa skill copy-campanha]:**  Lê MEMORY.md → encontra contexto dos três clientes  Executa skill copy-campanha com: segmento=SaaS B2B, objeção=CAC alto  Usa template de campanha de upsell de COMMANDS/marketing/campanha  **📋 Resultado postado no canal:**  "---  🎯 RASCUNHO DE CAMPANHA — Upsell SaaS B2B  Baseado em: insights de TechCorp, LogTech, Softway  Headline: Reduza seu CAC em 40% sem mudar de canal  Público: empresas SaaS B2B com 10-50 funcionários  Formato sugerido: email + LinkedIn Ads  CTA: Case study gratuito → Demo do plano Growth  ⚠️ Este é um rascunho. Encaminhar para o time de marketing para revisar.  ---"  **✅ Tarefa criada: "Revisar campanha upsell SaaS B2B" → @ana (marketing)** |

|  |  |
| --- | --- |
| ✍️→💼 | **Content Bot sugere pauta baseada no pipeline**  *Agente: Content Bot (domínio: conteúdo editorial) → Capacidade extra: analise-pipeline (domínio: vendas)*  Gatilho: Deal fechado com cliente interessante em segmento emergente  **Resultado: Pauta de case study ou artigo editorial com dados reais de negócio** |

|  |
| --- |
| **🤖 Content Bot [via HOOK on-deal-stage-change → "Fechado Ganho"]:**  Recebe evento: deal Construmax (segmento Construção) fechado  Acessa skill analise-pipeline para entender o contexto do deal:  → Construmax: R$6.500/m, ciclo de 45 dias, objeção inicial era preço  → Segmento Construção: apenas 2 outros clientes ativos  **📋 Content Bot propõe no canal #conteudo:**  "Fechamos a Construmax ontem. Vejo uma oportunidade de conteúdo:  A Construção é nosso segmento de menor penetração (3 clientes)  mas o Construmax fechou R$6.500/m — acima da média.  Um case study sobre como empresas de construção usam o Facebrasil  pode ser um ótimo ancote para prospecção nesse nicho.  Posso criar a pauta. Preciso de autorização do Construmax.  @julia, consegue checar com eles?"  **👤 Julia: "Boa ideia. Já falei com eles, toparam."**  **🤖 Content Bot [ativa capacidade editorial normal]:**  Cria pauta estruturada com ângulo, fontes, prazo  Atribui tarefa ao editor humano para entrevista com Construmax  **✅ Pauta criada: "Case study: Construmax — construção digital no mercado americano"** |

|  |  |
| --- | --- |
| 📢→🎨 | **Ads Bot detecta oportunidade e cria brief criativo**  *Agente: Ads Bot (domínio: performance de mídia) → Capacidade extra: brief-criativo (domínio: criação/design)*  Gatilho: Anomalia positiva detectada: CTR acima do normal em segmento específico  **Resultado: Brief criativo pronto para o time de design escalar o que está funcionando** |

|  |
| --- |
| **🤖 Ads Bot [via HOOK on-kpi-threshold]:**  Detecta: anúncio "Facebrasil para construtoras" com CTR 4.2%  (média do workspace: 1.8%) — anomalia positiva de +133%  Ads Bot normalmente apenas MONITORA e ALERTA.  Mas com acesso à skill brief-criativo, pode ir além:  **📋 Ads Bot propõe no canal #campanhas-meta:**  "⚡ Anomalia positiva detectada:  Anúncio ID #2847 (construtoras) → CTR 4.2% vs. média 1.8%  Gasto até agora: R$320. Orçamento restante: R$4.680.  Recomendação técnica: escalar orçamento neste público.  Posso também criar um brief criativo para 3 variações deste anúncio,  baseado nos elementos visuais e copy que estão gerando o CTR alto.  Quer que eu monte o brief para o time de design?"  **👤 Ana (marketing): "Sim, manda o brief."**  **🤖 Ads Bot [ativa skill brief-criativo]:**  Analisa elementos do anúncio vencedor  Gera brief com: hipótese criativa, variações sugeridas, métricas de sucesso  **📋 Brief criativo postado → tarefa criada para o designer**  **✅ Resultado: 3 variações criadas, duas superaram o original** |

|  |  |
| --- | --- |
| 💼→📊 | **Comercial Bot gera relatório executivo fora do ciclo normal**  *Agente: Comercial Bot (domínio: vendas) → Capacidade extra: relatorio-executivo (domínio: reporting)*  Gatilho: Pergunta direta do CEO no canal — fora do ciclo semanal do Report Bot  **Resultado: Relatório executivo completo entregue em 1 minuto, sem esperar o report-bot** |

|  |
| --- |
| **👤 CEO (canal #diretoria, 11h de uma quarta-feira):**  "Alguém me passa o estado do pipeline agora?  Tenho reunião com investidor em 30 minutos."  **🤖 Comercial Bot:**  [O report-bot geraria isso às 17h — mas o CEO precisa agora]  [Comercial Bot tem access à skill relatorio-executivo nos Shared Resources]  "Vou gerar agora. Um momento."  [ativa skill relatorio-executivo + script pipeline\_report.py]  [busca dados via fbr\_query\_pipeline()]  [formata para o padrão executivo: máx 1 página, bullets, números em destaque]  **📋 Relatório postado 47 segundos depois:**  "📊 Pipeline — quarta 24/02 · 11:02  Total: R$380k ARR potencial · 24 deals ativos  Por stage:  • Negociação: 3 deals · R$19.600/m · risco médio  • Proposta Enviada: 5 deals · R$21.200/m · aguardando resposta  • Qualificação: 4 deals · R$15.900/m · Construmax urgente (demo hoje)  Destaques:  • 7 fechamentos em fevereiro · meta: 10  • Deal de maior valor em risco: Grupo Mercantil (R$8.900/m, 38 dias sem update)  • Forecast conservador para março: R$42k ARR  Gerado por Comercial Bot via skill relatorio-executivo"  **✅ CEO: "Perfeito. Exatamente o que precisava."** |

|  |
| --- |
| **PARTE 3 — COMO ESTRUTURAR SKILLS PARA USO CROSS-DOMAIN** |

Uma skill projetada para uso cross-domain tem características diferentes de uma skill de domínio. Ela precisa ser autocontida, contextualmente agnóstica e documentada para que qualquer agente possa ativá-la sem conhecimento prévio do domínio.

## **3.1 Anatomia de uma Skill Cross-Domain**

|  |
| --- |
| # SKILLS/copy-campanha/SKILL.md  ---  name: copy-campanha  description: Cria rascunho de campanha de marketing a partir de um insight ou segmento  version: 1.0.0  domain: marketing  cross\_domain: true # indica que esta skill é projetada para uso por outros domínios  primary\_agents: [ads-bot, content-bot]  cross\_domain\_agents: [comercial-bot, report-bot] # quem pode usar fora do domínio  requires\_confirmation: true # agente DEVE propor antes de executar  output\_type: draft # rascunho — sempre marcado como "para revisão humana"  metadata:  openclaw:  requires:  env: []  bins: []  ---  ## Skill: Copy de Campanha  ### O que esta skill faz  Gera o rascunho estruturado de uma campanha de marketing:  headline, público-alvo, formato, CTA e ângulo criativo.  Input: um insight, padrão de comportamento, segmento ou oportunidade.  Output: rascunho formatado + tarefa de revisão atribuída ao time de marketing.  ### Instruções para uso cross-domain  Se você (o agente) não é do time de marketing:  1. ANTES de executar: informe ao humano o que você percebeu e o que pretende fazer  2. AGUARDE confirmação explícita ("pode fazer", "vai em frente", etc.)  3. AO EXECUTAR: use os dados que VOCÊ tem (seu domínio é a fonte)  - Comercial Bot: use insights de clientes da MEMORY.md  - Report Bot: use dados de KPIs e tendências  4. AO ENTREGAR: sempre marque como "Rascunho — revisão de marketing necessária"  5. CRIE TAREFA: atribua revisão ao agente ou humano do time de marketing  ### Estrutura do rascunho de campanha  \*\*Título\*\*: [nome interno da campanha]  \*\*Baseado em\*\*: [qual insight/dados fundamentam esta campanha]  \*\*Público-alvo\*\*: [segmento específico com características]  \*\*Problema endereçado\*\*: [dor do público em 1 frase]  \*\*Headline principal\*\*: [título da campanha — direto, orientado a resultado]  \*\*Formato sugerido\*\*: [email / social / ads / conteúdo / combinação]  \*\*CTA\*\*: [ação específica que o público deve tomar]  \*\*Métricas de sucesso\*\*: [como saberemos se funcionou]  ### Tom obrigatório  - Específico: evitar generalidades como "melhore sua performance"  - Baseado em evidência: mencionar o dado/insight que originou a campanha  - Acionável: o rascunho deve ser utilizável, não apenas inspiracional |

## **3.2 Catálogo de Skills Cross-Domain**

Skills marcadas como cross\_domain: true no frontmatter. Disponíveis a qualquer agente declarado em cross\_domain\_agents.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Skill** | **Domínio nativo** | **Quem pode usar (cross)** | **Input necessário** | **Output entregue** |
| copy-campanha | Marketing | Comercial Bot, Report Bot | Insight, segmento, problema identificado | Rascunho de campanha marcado para revisão |
| brief-criativo | Design/Criação | Ads Bot, Content Bot | Referência visual ou copy que está performando | Brief estruturado para designer |
| analise-pipeline | Vendas | Content Bot, Report Bot | Lista de deals ou segmento | Análise de oportunidades e gargalos |
| relatorio-executivo | Reporting | Todos os agentes | Dados brutos de qualquer domínio | Relatório formatado máx 1 página |
| pauta-editorial | Conteúdo | Comercial Bot, Ads Bot | Evento, deal, insight ou tendência | Pauta estruturada para editor humano |
| analise-objecoes | Vendas | Ads Bot, Content Bot | Lista de objeções coletadas | Análise de padrões + sugestão de conteúdo de resposta |
| score-lead | Vendas | Ads Bot, Content Bot | Perfil de empresa ou segmento | Score 0-100 com justificativa |

|  |
| --- |
| **PARTE 4 — ORIENTAÇÃO PELO USUÁRIO: LINGUAGEM NATURAL COMO GATILHO** |

## **4.1 O Usuário Como Diretor de Capacidades**

O modo mais simples e poderoso de ativar uma capacidade cross-domain é o usuário humano dizendo, em linguagem natural, o que quer. O agente interpreta a instrução, identifica qual skill dos Shared Resources é relevante, propõe o plano e executa com confirmação.

O usuário não precisa saber o nome da skill. Ele fala o objetivo. O agente faz a ponte.

|  |
| --- |
| **📋 Exemplos de instruções em linguagem natural → Skill ativada** |
| "Comercial, você conhece bem os clientes. Consegue criar uma campanha pra reativar os que estão dormentes?"  → Skill ativada: copy-campanha | Input: clientes inativos da MEMORY.md  "Content, vi que fechamos bastante cliente de construção. Isso rende um artigo?"  → Skill ativada: pauta-editorial | Input: deals do segmento construção via analise-pipeline  "Ads, você tá vendo as campanhas. Tem algo que a gente deveria fazer diferente no criativo?"  → Skill ativada: brief-criativo | Input: análise dos anúncios com melhor e pior performance  "Comercial, o CEO quer um resumo do pipeline agora. Consegue gerar?"  → Skill ativada: relatorio-executivo | Input: snapshot do pipeline via fbr\_query\_pipeline()  "Alguém consegue me dizer por que estamos perdendo tanto deal em negociação?"  → Skill ativada: analise-objecoes | Input: deals perdidos + motivos registrados na MEMORY.md |

## **4.2 Como o Agente Processa a Instrução Cross-Domain**

|  |
| --- |
| # Ciclo de raciocínio do agente ao receber instrução cross-domain  # 1. RECONHECIMENTO  # Agente identifica que a tarefa está fora do seu SOUL.md / IDENTITY.md habitual  # Verifica se existe skill relevante nos Shared Resources declarados  # 2. AVALIAÇÃO  # Pergunta interna: "Tenho dados suficientes para fazer isso bem?"  # Se sim → propõe ao humano com o plano  # Se não → pede mais contexto antes de propor  # 3. PROPOSTA (obrigatório se cross\_domain: true na skill)  # Formato padrão da proposta:  # - O que percebi / o que tenho  # - O que pretendo fazer (skill + dados que usarei)  # - Quanto tempo leva  # - O que o humano precisa fazer depois (revisão, aprovação, etc.)  # 4. AGUARDA CONFIRMAÇÃO  # Qualquer forma de confirmação: "pode", "vai", "faz", "sim", "ok"  # Timeout: se não respondido em 30min, arquiva e avisa  # 5. EXECUÇÃO  # Ativa a skill com os dados do próprio domínio como input  # Registra a ação no AGENT\_ACTION\_LOG com trigger\_type: "cross\_domain"  # 6. ENTREGA  # Posta resultado no canal, sempre com:  # - Marcação "Rascunho — revisão necessária" (se output\_type: draft)  # - Tarefa criada para o responsável nativo do domínio  # - Link para os dados/insight que fundamentaram a entrega  # 7. MEMÓRIA  # Registra na MEMORY.md: qual cross-domain foi feito, resultado, feedback recebido  # Isso permite ao agente propor de forma mais contextual na próxima vez |

|  |
| --- |
| **PARTE 5 — IMPACTO NA ESTRUTURA DOS MARKDOWNS DOS AGENTES** |

O conceito de capacidades cross-domain exige pequenos ajustes nos markdowns dos agentes para suportar esse modo de operação de forma explícita e segura.

## **5.1 AGENTS.md — Campo cross\_domain\_skills**

|  |
| --- |
| # AGENTS.md — Comercial Bot (seção atualizada)  shared\_resources:  # Skills do domínio próprio — sempre carregadas  skills:  - redacao-comercial  - analise-pipeline  - relatorio-executivo  # Skills cross-domain — disponíveis sob demanda  # O agente NÃO carrega estas automaticamente.  # Ele as usa apenas quando orientado (humano ou HOOK)  # e sempre com proposta + confirmação antes de executar.  cross\_domain\_skills:  - copy-campanha # marketing: gerar campanhas a partir de insights de clientes  - pauta-editorial # conteúdo: sugerir pautas baseadas em deals  - brief-criativo # design: criar brief quando um anúncio de vendas performa bem  # Regras de autonomia para cross-domain  cross\_domain\_policy:  mode: propose\_first # sempre propõe antes de executar  confirmation\_required: true  output\_always\_draft: true # todo output cross-domain é marcado como rascunho  notify\_domain\_owner: true # avisa o agente "dono" do domínio que a skill foi usada |

## **5.2 SOUL.md — Parágrafo sobre Uso Cross-Domain**

Recomendamos adicionar um parágrafo padrão no SOUL.md de cada agente que usa capacidades cross-domain, para moldar o comportamento correto:

|  |
| --- |
| # SOUL.md — trecho a adicionar em todo agente com cross\_domain\_skills  ## Capacidades além do meu domínio  Tenho acesso a skills de outros domínios (marketing, conteúdo, design)  quando a situação — baseada em dados do meu próprio domínio — justifica.  Quando percebo uma dessas oportunidades:  1. Nomeio o que percebi (dado concreto, não suposição)  2. Proponho o que posso fazer com qual skill  3. Aguardo confirmação humana antes de qualquer execução  4. Entrego como rascunho, nunca como produto final  5. Crio tarefa para o responsável nativo do domínio revisar  Minha experiência com clientes é minha contribuição única.  As skills compartilhadas são o idioma com que expresso essa experiência  em formatos que outros times podem usar. |

## **5.3 Tabela Completa: Agente × Capacidades Cross-Domain**

|  |  |  |  |
| --- | --- | --- | --- |
| **Agente (domínio)** | **Cross-domain skills disponíveis** | **Dados que traz do seu domínio** | **Quem recebe o output** |
| Comercial Bot (vendas) | copy-campanha, pauta-editorial, brief-criativo, relatorio-executivo | Insights de clientes, objeções, segmentos, padrões de compra | Marketing (campanha) / Conteúdo (pauta) / Liderança (relatório) |
| Content Bot (conteúdo) | analise-pipeline, score-lead, relatorio-executivo | Temas com alta performance editorial, perguntas frequentes do público | Vendas (leads qualificados) / Marketing (ângulos de campanha) |
| Ads Bot (mídia paga) | brief-criativo, pauta-editorial, analise-objecoes | Dados de CTR, audiências que respondem, copies que convertem | Design (brief) / Conteúdo (pauta) / Vendas (objeções) |
| Report Bot (reporting) | copy-campanha, pauta-editorial | Tendências de KPIs, anomalias, padrões temporais | Marketing (campanhas sazonais) / Conteúdo (temas emergentes) |

*FBR-Click — Adendo: Capacidades Cross-Domain v1.0*

*Fevereiro 2026 · Facebrasil · "A experiência de um agente, o idioma de outro domínio"*