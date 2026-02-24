# Especificação Técnica: Integração FBR-Click × OpenClaw

Este documento detalha os endpoints, configurações e o passo a passo necessário para conectar o gateway do OpenClaw à plataforma FBR-Click.

## 1. Endpoints de API (REST)

A API do FBR-Click deve expor os seguintes recursos para os agentes:

### 1.1 Autenticação e Handshake
*   **POST** `/api/agents/handshake`
    *   **Finalidade:** Validar o token de agente e obter as configurações de conexão.
    *   **Payload:** `{ "agent_token": "string", "git_sha": "string" }`
    *   **Resposta:** `{ "ws_url": "wss://...", "workspace_id": "string", "authorized_channels": [] }`

### 1.2 Execução de Ações
*   **POST** `/api/agents/action`
    *   **Finalidade:** Executar uma action (enviar mensagem, criar tarefa) via REST.
    *   **Payload:** `{ "type": "SEND_MESSAGE", "channel_id": "string", "content": "..." }`
    *   **Headers:** `Authorization: Bearer <JWT_AGENTE>`

## 2. Conexão Real-Time (WebSocket)

A integração principal ocorre via WebSocket bidirecional no gateway dedicado:
*   **URL:** `wss://fbr-click.com/agents/gateway/ws`
*   **Protocolo:** Socket.io ou nativo WS.

### Eventos do Servidor (FBR-Click → Agente):
- `message_received`: Nova mensagem onde o agente foi mencionado ou tem permissão.
- `task_assigned`: Uma tarefa foi atribuída ao agente.
- `config_reload`: Instrução para o agente recarregar os arquivos Markdown do Git.

## 3. Configuração do Ambiente (Step-by-Step)

### Passo 1: Preparação do Repositório do Agente
1. Crie um repositório Git privado.
2. Adicione os 7 arquivos base: `SOUL.md`, `IDENTITY.md`, `TASKS.md`, `AGENTS.md`, `MEMORY.md`, `TOOLS.md`, `USER.md`.
3. Configure o Webhook do GitHub para apontar para `https://fbr-click.com/api/webhooks/git`.

### Passo 2: Registro no Painel Admin
1. Acesse **Configurações > Agentes**.
2. Clique em **Novo Agente** e insira a URL do Repositório Git.
3. O sistema gerará um `FBR_AGENT_TOKEN` único. **Salve-o com segurança.**

### Passo 3: Inicialização do OpenClaw Gateway
Configure o arquivo `openclaw.json` (ou variáveis de ambiente) no seu servidor local/VPS:

```json
{
  "platform": "fbr-click",
  "token": "SEU_FBR_AGENT_TOKEN",
  "workspace_id": "ID_DO_WORKSPACE",
  "shared_resources_path": "/opt/fbr-click/shared"
}
```

## 4. Segurança

- **Rotação de Tokens:** O JWT do agente deve expirar a cada 24 horas. O gateway OpenClaw deve renovar automaticamente usando o `FBR_AGENT_TOKEN`.
- **RBAC:** Todas as ações via API são validadas contra o campo `canais_permitidos` no arquivo `AGENTS.md` cacheado pelo FBR-Click.
