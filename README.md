# FBR-Leads

Bootstrap inicial do projeto FBR-Leads seguindo os PRDs em `prd/` e as regras locais em `.agent/rules/`.

## Features

### Foundation Bootstrap

Estrutura inicial do backend FastAPI, compose da infraestrutura local, templates de ambiente e proxy Nginx para o Batch 1.

Fluxo:
1. Ajustar variaveis em `.env`.
2. Subir a stack com `docker compose up --build`.
3. Validar `GET /health` via Nginx ou FastAPI.

### Database Bootstrap

Migrations SQL locais para extensoes, auth shim, schema principal, RLS, triggers, indexes e seed do workspace inicial.

Fluxo:
1. O container `postgres` executa os arquivos de `db/migrations` na primeira inicializacao.
2. As tabelas e policies ficam prontas para o Batch 3.
3. O seed cria owner, workspace, dominio e ICP de teste.

### Domains API

Primeiro modulo do Batch 3 com rotas protegidas por `X-Agent-Id` e `X-Workspace-Id` para listar dominios, cadastrar dominio, avancar fase e consultar status de saude.

Fluxo:
1. O caller envia `X-Agent-Id` nas rotas `/api/*`.
2. O caller envia `X-Workspace-Id` com um workspace existente.
3. A API responde com os dominios e o `health_status` calculado.

### Leads Pipeline API

Pipeline inicial de leads com ingest em lote, filtros, detalhe, validacao de email, enriquecimento basico e scoring heuristico.

Fluxo:
1. O caller envia um lote para `POST /api/leads/ingest`.
2. A API persiste os leads no workspace informado.
3. O caller pode validar, enriquecer e pontuar cada lead nas rotas dedicadas.

### Campaigns, Dispatch and Webhooks

Camada inicial de campanhas com criacao, geracao de email, dispatch por dominio ativo e processamento de webhooks Postal e FBR-Click com HMAC.

Fluxo:
1. O caller cria a campanha em `POST /api/campaigns`.
2. O caller gera o email em `POST /api/campaigns/{id}/write-email`.
3. O caller dispara o envio em `POST /api/campaigns/{id}/dispatch`.
4. Postal e FBR-Click notificam a API nas rotas `/api/webhooks/*`.

### Audit Log Basico

Acoes principais de campanhas passam pelo `agent_action_logs` como append-only com `workspace_id`, `agent_id`, payload e resultado.

Fluxo:
1. A rota protegida recebe `X-Agent-Id`.
2. A aplicacao executa a acao.
3. O `action_logger` grava o evento no banco.

### OpenClaw Scaffold

Gateway local de scaffold na porta `3500` e repositorios dos agentes com os 7 markdowns obrigatorios para acelerar o Batch 4 sem bloquear a estrutura do projeto.

Fluxo:
1. O container `openclaw-gateway` sobe e responde em `/health`.
2. As pastas em `agents/` servem como base versionada para revisao e evolucao.
3. O gateway oficial completo ainda pode substituir esse scaffold depois.

### Dashboard Next.js Scaffold

Frontend inicial com App Router, `iron-session`, middleware para `/dashboard/*`, proxy autenticado via `/api/proxy` e paginas base do painel.

Fluxo:
1. O usuario autentica em `/login`.
2. O cookie httpOnly libera acesso ao dashboard.
3. Toda chamada ao backend passa por `/api/proxy/[...path]` com `X-Workspace-Id` e `X-Agent-Id`.

### LLM Health Routing

Camada inicial para consultar o status das tres layers de LLM no Redis e expor a layer ativa no health check.

Fluxo:
1. n8n publica status em chaves `llm:layer*:status`.
2. FastAPI le o Redis.
3. `/health` retorna a camada ativa e o modelo selecionado.
