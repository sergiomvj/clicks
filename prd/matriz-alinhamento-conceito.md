# Matriz de Alinhamento com o Conceito Original

Referencia principal: `prd/fbr-click-conceito.html`.

## Ja alinhado ou parcialmente alinhado

- backend modular com `spaces`, `messages`, `tasks`, `crm`, `agents`, `webhooks` e `git_watcher`
- frontend operacional com login, canais, pipeline, tarefas, approvals e painel de agentes
- 6 agentes nativos com os 7 markdowns obrigatorios no repositorio
- audit log append-only por trigger
- kill switch por workspace com propagacao em tempo real
- webhooks externos com HMAC-SHA256
- stack base de producao com Docker, Nginx, Prometheus e Grafana

## Divergencias que passaram a ter implementacao concreta neste ciclo

- `kpis` agora entram no schema e podem ser consumidos pela UI
- `agent_markdown_cache` agora entra no schema e pode ser sincronizado por agente

## Divergencias ainda abertas e decisao recomendada

- `approvals` vs `agent_approval_requests`
Decisao recomendada: manter a tabela `approvals` como nome tecnico interno e atualizar documentacao final para explicitar equivalencia conceitual.

- `lead_intakes` e `git_watchers` fora da lista das 13 tabelas do conceito
Decisao recomendada: manter ambas por valor operacional real e atualizar o conceito final como extensao da modelagem original.

- dark mode obrigatorio ainda nao refletido no frontend atual
Decisao recomendada: convergir o frontend ao conceito, sem tentar reescrever a IA de navegacao ou a arquitetura de paginas.

- RLS ainda nao implementado em todas as tabelas
Decisao recomendada: convergir implementacao ao conceito, sem excecao.

- JWT de agentes ainda nao fechado no modelo final de rotacao a cada 24h via Redis TTL
Decisao recomendada: convergir implementacao ao conceito.

- stack LLM em 3 camadas ainda nao esta operacional ponta a ponta
Decisao recomendada: convergir implementacao ao conceito, preservando a interface atual do healthcheck.
