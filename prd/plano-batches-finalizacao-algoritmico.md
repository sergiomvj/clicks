# Plano Algoritmico de Finalizacao por Batches

Data de referencia: 2026-03-30
Projeto: FBR-CLICK
Fonte de verdade: `prd/fbr-click-conceito.html`, `prd/tasklist-alinhamento-conceito-original.md`, `prd/status-alinhamento-conceito.md`, `docs-go-live-checklist.md`

## Objetivo

Levar o FBR-CLICK do estado atual de alta maturidade local para fechamento real de projeto, com criterio de pronto tecnico, operacional e conceitual.

## Principio de execucao

A finalizacao deve seguir um algoritmo simples:

1. fechar primeiro o que aumenta seguranca e reduz retrabalho estrutural
2. somente depois estabilizar comportamento de agentes e stack LLM
3. homologar integracoes reais antes de chamar go-live
4. liberar producao apenas quando seguranca, observabilidade e restore estiverem validados
5. nenhum batch avanca se o criterio de saida do batch anterior falhar

## Algoritmo mestre

```text
INICIO
  carregar status atual
  enquanto existir pendencia critica interna:
    executar batch elegivel de maior dependencia estrutural
    validar criterio de saida do batch
    se falhar:
      corrigir antes de prosseguir
  enquanto existir pendencia externa bloqueando go-live:
    preparar evidencias, scripts e checklist
    executar homologacao com ambiente real
    registrar bloqueios e responsavel
  se batches internos = completos e homologacao externa = aprovada:
    executar batch final de go-live
  senao:
    manter projeto em pre-go-live controlado
FIM
```

## Regras de governanca

- cada batch deve produzir artefatos verificaveis
- cada batch deve ter dono primario e revisor
- cada batch deve atualizar `prd/status-alinhamento-conceito.md`
- cada batch que tocar comportamento real deve gerar evidencia em log, doc ou script
- se um batch exigir segredo real, VPS ou endpoint externo, ele muda automaticamente para estado `dependencia externa`

## Batch 0 - Preparacao de fechamento

### Objetivo
Congelar o baseline de finalizacao e evitar trabalho em paralelo sem ordem.

### Entradas
- status atual do repositorio
- tasklist de alinhamento
- matriz de divergencias

### Tarefas
- consolidar branch de finalizacao
- revisar arquivos modificados que ainda nao entraram em validacao final
- atualizar `prd/status-alinhamento-conceito.md` com percentual e bloqueios reais
- definir o responsavel por cada sistema externo: `1FBR-Leads`, `1FBR-Dev`, `1FBR-Suporte`, VPS, dominio e SSL

### Saidas esperadas
- baseline unico de finalizacao
- backlog ordenado por dependencia
- responsaveis nomeados

### Criterio de pronto
- existe uma lista unica de pendencias restantes
- existe um responsavel por cada dependencia externa

### Se falhar
- nao iniciar batch 1

## Batch 1 - Fechamento estrutural de banco e modelo conceitual

### Objetivo
Eliminar divergencias de modelagem que impactam seguranca e operacao.

### Tarefas
- decidir definitivamente a equivalencia entre `approvals` e `agent_approval_requests`
- decidir definitivamente o papel de `lead_intakes` e `git_watchers` frente ao conceito original
- revisar schema final e atualizar docs tecnicas com a modelagem aceita
- aplicar e validar migrations `003_concept_alignment.sql` e `004_operational_alignment.sql`
- revisar seeds de `channels` para garantir `general`, `deal`, `task`, `system`, `agent-log`
- revisar semantica de prioridade de `tasks` para `p0` a `p3`

### Artefatos
- migrations aplicadas
- documentacao atualizada
- matriz de divergencias atualizada

### Criterio de pronto
- schema final aceito e documentado
- nenhuma divergencia estrutural critica fica ambigua

### Gate para avancar
- banco local sobe limpo do zero com migrations atuais

## Batch 2 - Seguranca profunda e RLS real

### Objetivo
Fechar o bloco mais sensivel do conceito: isolamento, autenticao e rastreabilidade.

### Tarefas
- desenhar estrategia de RLS sem quebrar o uso atual de `asyncpg`
- escolher abordagem de contexto por workspace no banco
- implementar `ENABLE ROW LEVEL SECURITY` nas tabelas do modelo final
- implementar policies reais por `workspace_id`
- garantir que `agent_action_logs` fique protegido tambem por policy, alem do append-only por trigger
- revisar sessao humana para confirmar `httpOnly`, `secure` e `sameSite=lax`
- endurecer validacao de escopo do agente cruzando token, banco e configuracao versionada
- revisar workflow de approval para acoes de alto impacto
- medir kill switch com alvo menor que 5 segundos
- ampliar testes negativos de webhook, prompt injection e rate limit

### Artefatos
- migrations de RLS
- estrategia de contexto documentada
- testes de seguranca
- evidencias de kill switch

### Criterio de pronto
- tenant isolation validado
- acoes sensiveis exigem approval quando necessario
- escopo de agente nao pode ser burlado por token ou payload

### Gate para avancar
- seguranca precisa estar verde antes de ampliar operacao real dos agentes

## Batch 3 - UX final e aderencia visual completa

### Objetivo
Levar a interface do estado operacional para o estado conceitual final.

### Tarefas
- revisar login e home de entrada para combinar com o dark mode final
- reforcar diferenciacao visual entre humano e agente em mensagens
- refinar sidebar para semantica de hub central do ecossistema
- revisar cards, status, badges, avatares e labels de autoria
- revisar tela de agentes para destacar heartbeat, pausado, approvals e watchers
- revisar copy de telas principais para linguagem final do produto
- revisar consistencia de `Outfit`, `Inter` e `JetBrains Mono`

### Artefatos
- capturas finais das telas principais
- checklist visual por tela

### Criterio de pronto
- uma pessoa nova identifica sem ambiguidade: humano vs agente, estado do agente, tipo de canal e prioridade operacional

### Gate para avancar
- frontend precisa estar visualmente coerente antes da homologacao final com usuarios

## Batch 4 - Operacao real dos 6 agentes nativos

### Objetivo
Tirar os agentes do estado estrutural e levar para operacao real controlada.

### Tarefas
- confirmar owner final por agente
- confirmar escopo final por agente
- confirmar acoes que exigem approval por agente
- registrar todos os agentes no ambiente alvo
- publicar heartbeat real de cada agente em janela controlada
- validar fluxo Git -> markdown cache -> comportamento observavel
- validar ao menos um trigger automatico coerente para cada agente:
  - `comercial-bot`: mudanca de deal ou follow-up
  - `content-bot`: criacao de tarefa de conteudo
  - `ads-bot`: alerta de KPI de campanha
  - `approval-bot`: nova aprovacao pendente
  - `report-bot`: consolidacao periodica
  - `onboarding-bot`: novo membro ou novo lead elegivel

### Artefatos
- logs de heartbeat
- logs de trigger
- evidencias de approval quando aplicavel

### Criterio de pronto
- os 6 agentes executam ao menos um fluxo real autorizado e auditavel

### Gate para avancar
- nenhum go-live sem pelo menos uma rodada controlada dos 6 agentes

## Batch 5 - Stack LLM em 3 camadas operacional

### Objetivo
Fechar a inteligencia em cascata do conceito.

### Tarefas
- definir matriz de uso por camada: Ollama, Claude, OpenAI
- implementar fallback automatico real
- publicar estado das 3 camadas em Redis
- integrar job recorrente que atualiza a saude das camadas
- registrar latencia, falha, fallback e indisponibilidade por camada
- revisar `/health` para refletir o estado real da cascata

### Artefatos
- doc de fallback
- log ou metrica por camada
- evidencia de failover controlado

### Criterio de pronto
- se camada 1 falhar, camada 2 assume; se camada 2 falhar, camada 3 assume; tudo com rastreabilidade

### Gate para avancar
- homologacao externa deve usar a stack LLM final, nao uma simulacao parcial

## Batch 6 - Integracoes reais do ecossistema FBR

### Objetivo
Fechar a camada intersistemas com payloads e endpoints finais.

### Tarefas
- receber endpoints finais de `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte`
- receber e configurar secrets finais fora do repositorio
- executar testes reais de entrada para cada sistema
- executar testes reais de callback de saida para cada sistema
- revisar contratos publicados com exemplos reais homologados
- validar HMAC em cenarios validos e invalidos
- confirmar idempotencia e logs de entrega

### Artefatos
- evidencias por integracao
- payloads homologados
- logs de callback

### Criterio de pronto
- cada integracao entra e sai com autenticacao, log e resultado comprovado

### Gate para avancar
- sem integracoes reais homologadas, o projeto continua em pre-go-live

## Batch 7 - Producao, observabilidade e restore

### Objetivo
Tornar o sistema liberavel com seguranca operacional.

### Tarefas
- provisionar VPS real
- configurar dominio e SSL finais
- subir stack de producao
- validar dashboards de backend, frontend, banco, Redis e agentes
- executar smoke test completo
- executar backup manual e restauracao real
- validar carga com 10 agentes simultaneos
- registrar riscos residuais no runbook

### Artefatos
- links validos de producao
- dashboard acessivel
- relatorio de carga
- relatorio de restore

### Criterio de pronto
- o ambiente alvo responde, monitora, faz backup e restaura

### Gate para avancar
- sem restore real validado, nao liberar go-live

## Batch 8 - Homologacao controlada final

### Objetivo
Executar uma simulacao o mais proxima possivel da operacao real antes do go-live.

### Tarefas
- rodar um lead real controlado do `1FBR-Leads`
- gerar uma aprovacao real de `change_deal_stage`
- validar callback de fechamento
- validar um fluxo de trigger de pelo menos 3 agentes distintos
- validar leitura operacional da UI por usuario humano
- revisar logs e alertas da janela de homologacao

### Artefatos
- checklist de homologacao preenchido
- aceite dos responsaveis

### Criterio de pronto
- a operacao controlada roda de ponta a ponta sem surpresa critica

### Gate para avancar
- se surgir defeito P0 ou P1, voltar ao batch causador

## Batch 9 - Go-live e fechamento do projeto

### Objetivo
Liberar, observar e encerrar o projeto com handoff documentado.

### Tarefas
- executar `docs-go-live-checklist.md`
- fazer liberacao em horario controlado
- observar primeiro ciclo de uso real
- validar que alertas, agents e callbacks seguem saudaveis
- registrar status de go-live no runbook
- consolidar PRDs e tasklists finais
- criar checklist final de aderencia ao conceito
- gerar handoff final de operacao

### Artefatos
- status de go-live
- runbook final
- checklist final de aderencia
- documento de handoff

### Criterio de pronto
- sistema em producao, monitorado, com restore validado e documentacao final entregue

## Matriz de dependencia entre batches

- `Batch 0` desbloqueia todos
- `Batch 1` desbloqueia `Batch 2`, `Batch 3` e parte de `Batch 4`
- `Batch 2` e `Batch 3` devem terminar antes de `Batch 8`
- `Batch 4` depende de `Batch 1` e parte de `Batch 2`
- `Batch 5` deve terminar antes de `Batch 8`
- `Batch 6` depende de terceiros e deve terminar antes de `Batch 9`
- `Batch 7` depende de infra real e deve terminar antes de `Batch 9`
- `Batch 8` depende de `Batch 4`, `Batch 5`, `Batch 6` e `Batch 7`
- `Batch 9` depende de todos os anteriores

## Ordem pratica recomendada

1. `Batch 0`
2. `Batch 1`
3. `Batch 2`
4. `Batch 3`
5. `Batch 4`
6. `Batch 5`
7. `Batch 6`
8. `Batch 7`
9. `Batch 8`
10. `Batch 9`

## Regra de decisao rapida

Use esta heuristica durante a execucao:

- se a tarefa mexe em isolamento, auth ou approval: ela sobe para `Batch 2`
- se a tarefa mexe em clareza humana da operacao: ela sobe para `Batch 3`
- se a tarefa mexe em comportamento automatico de bot: ela sobe para `Batch 4`
- se a tarefa mexe em modelo, fallback ou health de IA: ela sobe para `Batch 5`
- se a tarefa depende de endpoint, secret ou aprovacao externa: ela vai para `Batch 6`
- se a tarefa depende de VPS, dominio, SSL, carga ou restore: ela vai para `Batch 7`
- se a tarefa so faz sentido com ambiente alvo pronto: ela vai para `Batch 8` ou `Batch 9`

## Definicao objetiva de projeto finalizado

O projeto so pode ser considerado finalizado quando todos os itens abaixo forem verdadeiros ao mesmo tempo:

- conceito original esta coberto ou ajustado por decisao formal
- seguranca critica esta verde
- 6 agentes operam com heartbeat, trigger e audit log
- stack LLM em 3 camadas funciona de verdade
- integracoes externas estao homologadas
- producao tem observabilidade, backup e restore validados
- go-live foi executado e registrado
- documentacao final foi consolidada
