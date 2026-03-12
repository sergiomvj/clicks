# Contratos de Integracao - FBR-CLICK

Este documento consolida os contratos publicos das integracoes externas do FBR-CLICK.

## 1. 1FBR-Leads -> FBR-CLICK

Endpoint publico:
- `POST /api/v1/leads/webhook`

Resposta esperada:

```json
{ "status": "accepted" }
```

Payload:

```json
{
  "workspace_id": "00000000-0000-0000-0000-000000000001",
  "external_reference": "lead-123",
  "source_system": "1FBR-Leads",
  "lead_name": "Maria Silva",
  "email": "maria@empresa.com",
  "phone": "+5511999999999",
  "whatsapp": "+5511999999999",
  "company_name": "Empresa X",
  "origin": "similarity_outreach",
  "score": 82,
  "temperature": "warm",
  "virtual_manager_slug": "gestor-comercial-1",
  "notes": "Lead aquecido e pronto para abordagem.",
  "metadata": {
    "campaign_name": "similarity-campaign"
  },
  "handoff_payload": {
    "source_pipeline": "cold_to_warm"
  }
}
```

Obrigatorios:
- `workspace_id`
- `external_reference`
- `source_system`
- `lead_name`
- ao menos um entre `email`, `phone` ou `whatsapp`
- `origin`
- `score`
- `temperature`
- `virtual_manager_slug`

Script de teste:
- `scripts/test-fbr-leads-webhook.ps1`

## 2. 1FBR-Dev -> FBR-CLICK

Endpoint publico:
- `POST /api/v1/dev/events/webhook`

Resposta esperada:

```json
{ "status": "accepted" }
```

Payload:

```json
{
  "workspace_id": "00000000-0000-0000-0000-000000000001",
  "event_type": "lead_created",
  "title": "Novo lead vindo do produto",
  "description": "Usuario solicitou contato comercial a partir do produto.",
  "external_reference": "dev-event-001",
  "lead_name": "Lead Produto",
  "email": "produto@empresa.com",
  "phone": "+551188887777",
  "source_system": "1FBR-Dev",
  "metadata": {
    "product": "FBR-App",
    "screen": "pricing"
  }
}
```

Obrigatorios:
- `workspace_id`
- `event_type`
- `title`
- `external_reference`
- `lead_name`
- ao menos um entre `email` ou `phone`
- `source_system`

Callback preparado de volta para `1FBR-Dev`:
- URL configurada por `FBR_DEV_API_URL`
- assinatura HMAC por `FBR_DEV_WEBHOOK_SECRET`
- payload normalizado:

```json
{
  "workspace_id": "00000000-0000-0000-0000-000000000001",
  "source_system": "FBR-CLICK",
  "event_type": "dev_event_received",
  "status": "accepted",
  "reference_id": "dev-event-001",
  "related_entity_id": "message-id",
  "occurred_at": "2026-03-10T12:00:00Z"
}
```

Script de teste:
- `scripts/test-fbr-dev-webhook.ps1`

## 3. 1FBR-Suporte -> FBR-CLICK

Endpoint publico:
- `POST /api/v1/suporte/handoff/webhook`

Resposta esperada:

```json
{ "status": "accepted" }
```

Payload:

```json
{
  "workspace_id": "00000000-0000-0000-0000-000000000001",
  "external_reference": "suporte-001",
  "lead_name": "Lead Suporte Teste",
  "company_name": "Empresa Suporte",
  "email": "suporte@empresa.com",
  "phone": "+5511888888888",
  "priority": "high",
  "source_system": "1FBR-Suporte",
  "notes": "Lead de teste vindo do suporte",
  "metadata": {
    "queue": "upgrade"
  }
}
```

Obrigatorios:
- `workspace_id`
- `external_reference`
- `lead_name`
- ao menos um entre `email` ou `phone`
- `source_system`

Callback preparado de volta para `1FBR-Suporte`:
- URL configurada por `FBR_SUPORTE_API_URL`
- assinatura HMAC por `FBR_SUPORTE_WEBHOOK_SECRET`
- payload normalizado:

```json
{
  "workspace_id": "00000000-0000-0000-0000-000000000001",
  "source_system": "FBR-CLICK",
  "event_type": "support_handoff_received",
  "status": "accepted",
  "reference_id": "suporte-001",
  "related_entity_id": "intake-id",
  "occurred_at": "2026-03-10T12:00:00Z"
}
```

Script de teste:
- `scripts/test-fbr-suporte-webhook.ps1`

## 4. Assinatura

Todos os endpoints publicos usam:
- header `X-Signature`
- formato `sha256=<hexdigest>`
- HMAC-SHA256 com o secret dedicado da integracao

## 5. Script consolidado

Para validar os tres contratos de uma vez:
- `scripts/test-webhooks.ps1`
