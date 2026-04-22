# Tasklist de Alinhamento Total ao Conceito Original

Fonte de verdade para esta lista: `prd/fbr-click-conceito.html`.

Objetivo: mapear somente o que ainda falta para deixar o projeto 100% aderente ao conceito geral original, considerando o estado atual do repositório em `2026-03-27`.

## Resumo do gap atual

Hoje o projeto ja tem a maior parte da base operacional pronta, mas ainda existem diferencas relevantes entre o conceito original e a implementacao real:

- a identidade visual principal do frontend ainda esta mais clara do que o dark mode obrigatorio descrito no conceito
- o schema real do banco nao espelha integralmente as 13 tabelas e nomes previstos no conceito
- RLS completo em todas as tabelas conceituais ainda nao esta implementado no banco
- a autenticacao de agentes ainda nao esta fechada no modelo conceitual de JWT rotacionado a cada 24h via Redis TTL
- a orquestracao real do stack LLM em 3 camadas ainda nao esta fechada ponta a ponta
- os 6 agentes existem no repositorio, mas ainda faltam operacao real, heartbeat e triggers end-to-end conforme a visao original
- a camada de producao real ainda depende de deploy validado, observabilidade completa e carga controlada

## Prioridade 1 - Fechar divergencias estruturais entre conceito e codigo

- [x] Definir oficialmente quais divergencias do conceito serao mantidas e quais serao eliminadas
Critero de aceite: documento curto em `prd/` listando, para cada diferenca relevante, se o projeto vai convergir para o conceito ou atualizar o conceito para refletir a implementacao real.

- [ ] Alinhar o nome e a modelagem das tabelas do banco ao conceito original
Critero de aceite: schema final cobre explicitamente `workspaces`, `users`, `spaces`, `channels`, `messages`, `tasks`, `deals`, `deal_history`, `agents`, `agent_markdown_cache`, `agent_action_logs`, `agent_approval_requests` e `kpis`, ou existe decisao formal justificando cada substituicao atual.

- [ ] Revisar a tabela `channels` para suportar os tipos previstos no conceito
Critero de aceite: existem tipos e seeds para `general`, `deal`, `task`, `system` e `agent-log`, com uso claro na UI e na API.

- [ ] Revisar a modelagem de `tasks` para refletir prioridades e status previstos no conceito
Critero de aceite: prioridades e status usados em backend e frontend seguem a convencao final do conceito, sem enums ou labels conflitantes.

- [x] Introduzir a camada de `kpis` por space
Critero de aceite: tabela, API e exibicao inicial no frontend mostram target, unidade e status de KPI por space.

- [x] Introduzir cache de markdowns dos agentes com rastreabilidade por `git_sha`
Critero de aceite: existe persistencia do snapshot dos 7 markdowns por agente, incluindo `git_sha`, data de leitura e origem do repositorio.

## Prioridade 2 - Fechar seguranca e isolamento exatamente como o conceito pede

- [ ] Implementar RLS real nas tabelas do modelo final
Critero de aceite: cada tabela conceitual possui `ENABLE ROW LEVEL SECURITY`, policies por `workspace_id` e validacao automatizada cobrindo isolamento cross-tenant.

- [ ] Garantir que append-only de `agent_action_logs` fique protegido tambem pela politica de acesso
Critero de aceite: alem dos triggers contra `UPDATE` e `DELETE`, existem policies e testes que impedem mutacao indevida por perfil de aplicacao.

- [ ] Fechar autenticacao humana no contrato final do conceito
Critero de aceite: sessao humana usa cookie `httpOnly`, `secure` e `sameSite=lax`, sem dependencia de armazenamento inseguro no navegador.

- [x] Fechar autenticacao de agentes em JWT rotacionado a cada 24h via Redis TTL
Critero de aceite: emissao, expiracao, renovacao e revogacao funcionam no ciclo de 24h, com estado de token controlado no Redis e sem TTL arbitrario fora da politica definida.

- [ ] Validar escopo do agente contra configuracao versionada antes de cada acao sensivel
Critero de aceite: a autorizacao do agente cruza token, dados persistidos e arquivos de configuracao do agente antes da execucao.

- [ ] Endurecer o workflow de approval para todas as acoes de alto impacto descritas no conceito
Critero de aceite: fechar deal, editar lead critico, disparar webhook externo e outras acoes classificadas como sensiveis exigem aprovacao humana rastreavel.

- [ ] Medir e garantir SLA do kill switch menor que 5 segundos na operacao real
Critero de aceite: teste controlado comprova propagacao do kill switch para agentes e UI em menos de 5 segundos.

- [ ] Consolidar a protecao anti-prompt-injection no fluxo completo de entrada e execucao
Critero de aceite: mensagens, webhooks e comandos de agentes passam por sanitizacao e existem testes cobrindo entradas maliciosas basicas.

## Prioridade 3 - Alinhar experiencia visual e produto ao conceito

- [x] Migrar o frontend principal para dark mode como linguagem padrao do produto
Critero de aceite: layout principal, login, canais, pipeline, tarefas e painel de agentes seguem tema escuro consistente com tokens do conceito.

- [x] Padronizar tokens visuais do frontend com a identidade do conceito
Critero de aceite: `Orange 500` como cor de marca, `Violet 700` exclusivo para agentes, tipografia `Outfit` e `Inter`, e uso de `JetBrains Mono` em tags, badges e metadados tecnicos.

- [ ] Diferenciar humanos e agentes na mesma superficie com mais clareza
Critero de aceite: mensagens, badges, avatar, status e autoria deixam imediatamente claro quando a origem e humana ou agente.

- [ ] Refatorar a sidebar e as telas principais para refletir a semantica do conceito
Critero de aceite: navegacao e copy reforcam `spaces`, `channels`, agentes ativos, camada de monitoramento e centralidade do FBR-CLICK no ecossistema.

- [x] Adicionar uma visao de metricas alinhada ao conceito
Critero de aceite: frontend mostra pelo menos os indicadores-chave da visao original, incluindo capacidade de leitura rapida operacional.

- [x] Expor visualmente o estado operacional dos agentes com semaforo mais proximo do conceito
Critero de aceite: online, offline, pausado, heartbeat e dependencia de approval aparecem com destaque consistente na UI.

## Prioridade 4 - Fechar arquitetura e operacao dos 6 agentes nativos

- [ ] Colocar os 6 agentes nativos em operacao controlada real
Critero de aceite: `comercial-bot`, `content-bot`, `ads-bot`, `approval-bot`, `report-bot` e `onboarding-bot` executam pelo menos um fluxo real autorizado no ambiente alvo.

- [x] Implementar heartbeat e monitoracao real por agente
Critero de aceite: backend recebe e registra heartbeat, frontend exibe ultimo sinal e existe alerta para agente sem heartbeat.

- [ ] Implementar triggers operacionais reais previstos para cada agente
Critero de aceite: cada agente possui ao menos um trigger automatico funcional coerente com o conceito original.

- [ ] Fechar ownership humano e politica de approvals por agente
Critero de aceite: owners finais, escopos, acoes permitidas e acoes que exigem approval estao definidos, versionados e exibidos na plataforma.

- [ ] Validar ponta a ponta o fluxo Git -> watcher -> cache -> operacao do agente
Critero de aceite: alteracoes nos markdowns do agente sao detectadas, refletidas no cache e impactam o comportamento auditavel do agente.

## Prioridade 5 - Fechar stack LLM em 3 camadas como descrito

- [ ] Implementar estrategia real de selecao e fallback entre Ollama, Claude e OpenAI
Critero de aceite: existe ordem de prioridade clara, timeouts por camada, fallback automatico e registro de qual camada atendeu cada chamada.

- [ ] Publicar health real das 3 camadas no Redis com consumo operacional
Critero de aceite: o estado das camadas e atualizado continuamente e usado pelo backend antes de chamadas sensiveis.

- [ ] Integrar o verificador de saude externo previsto no conceito
Critero de aceite: existe job ou automacao equivalente ao papel do `n8n` no conceito, atualizando status das camadas em intervalo definido.

- [ ] Expor observabilidade minima da camada LLM
Critero de aceite: logs e metricas mostram latencia, falha, fallback e indisponibilidade por camada.

## Prioridade 6 - Fechar integracoes do ecossistema FBR exatamente no padrao alvo

- [ ] Validar payloads reais de entrada e saida com `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte`
Critero de aceite: contratos reais homologados, exemplos atualizados e testes executados com payloads finais de cada sistema.

- [ ] Fechar secrets finais, rotacao e origem de configuracao
Critero de aceite: variaveis sensiveis finais estao definidas para homologacao e producao, sem placeholders operacionais restantes.

- [ ] Garantir HMAC-SHA256 em todos os webhooks externos com testes negativos
Critero de aceite: cada integracao possui cobertura para assinatura valida, invalida, ausente e replay basico.

- [ ] Fechar callbacks de retorno do FBR-CLICK para o ecossistema
Critero de aceite: eventos de saida relevantes chegam aos sistemas consumidores com autenticacao, idempotencia e logs.

## Prioridade 7 - Fechar producao real, observabilidade e readiness

- [ ] Validar deploy real em VPS com dominio e SSL finais
Critero de aceite: ambiente acessivel por dominio definitivo, com certificado valido e smoke test completo bem-sucedido.

- [ ] Publicar monitoracao operacional de backend, frontend, banco, Redis e agentes
Critero de aceite: dashboards e alertas minimos em Grafana e Prometheus cobrem disponibilidade, erro e carga dos componentes centrais.

- [ ] Executar teste de carga com 10 agentes simultaneos
Critero de aceite: relatorio simples registra throughput, falhas, latencia e comportamento do sistema sob carga comparado ao alvo do conceito.

- [ ] Validar backup e restauracao real
Critero de aceite: existe teste de restauracao concluido com tempo medido e evidencias de consistencia minima.

- [ ] Executar checklist final de seguranca pre-go-live
Critero de aceite: checklist preenchido com status, riscos residuais e responsavel por cada pendencia remanescente.

## Prioridade 8 - Fechar documentacao de produto e entrega

- [ ] Atualizar PRDs e tasklists para refletir o estado final decidido
Critero de aceite: `prd-backend`, `prd-frontend`, plano e tasklists nao se contradizem em tabelas, auth, agentes, design ou integracoes.

- [ ] Criar checklist final de aderencia ao conceito original
Critero de aceite: existe um checklist objetivo marcando cada bloco do conceito como `alinhado`, `ajustado por decisao` ou `pendente`.

- [ ] Registrar evidencias de homologacao por area
Critero de aceite: UI, banco, seguranca, agentes, LLM, integracoes e producao possuem evidencias minimas apontando para testes, prints ou logs.

## Ordem sugerida de execucao

- [ ] Primeiro fechar decisao de divergencias estruturais
- [ ] Depois alinhar banco, RLS e seguranca
- [ ] Em seguida alinhar identidade visual e UX ao conceito
- [ ] Depois operacionalizar os 6 agentes e a stack LLM real
- [ ] Por fim homologar integracoes, deploy, observabilidade e checklist final
