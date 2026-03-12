# Guia de Decisao dos Pontos Pendentes

Este documento detalha os pontos que voce marcou como `avaliar em conjunto com a IA` ou `a ser definido em conjunto com a IA`.

A ideia aqui e simples:
- explicar o que cada decisao muda na implementacao
- recomendar um padrao pratico para o MVP
- deixar claro o que eu sugiro assumir agora para nao travar o projeto

---

## 1. Pipeline comercial

### 1.1 Transicoes entre stages

Hoje a resposta preenchida em `transicoes permitidas` ficou diferente da pergunta. Entao aqui vai a regra recomendada.

### O que essa decisao muda

Define:
- validacoes no backend
- botoes e opcoes no frontend
- historico do CRM
- quais eventos voltam para o `1FBR-Leads`

### Recomendacao para o MVP

Stages:
- `first_contact`
- `qualification`
- `proposal`
- `negotiation`
- `follow_up`
- `reengagement`
- `closed_won`
- `closed_lost`
- `cancelled`

Transicoes permitidas:
- `first_contact -> qualification`
- `first_contact -> follow_up`
- `first_contact -> closed_lost`
- `qualification -> proposal`
- `qualification -> follow_up`
- `qualification -> closed_lost`
- `proposal -> negotiation`
- `proposal -> follow_up`
- `proposal -> closed_won`
- `proposal -> closed_lost`
- `negotiation -> closed_won`
- `negotiation -> follow_up`
- `negotiation -> closed_lost`
- `follow_up -> qualification`
- `follow_up -> proposal`
- `follow_up -> negotiation`
- `follow_up -> reengagement`
- `follow_up -> closed_lost`
- `reengagement -> first_contact`
- `reengagement -> qualification`
- `reengagement -> closed_lost`

Estados terminais:
- `closed_won`
- `closed_lost`
- `cancelled`

Minha sugestao:
- nao permitir sair de `closed_won`, `closed_lost` ou `cancelled` sem acao administrativa
- permitir `cancelled` apenas por usuario admin

---

## 2. Motivos de ganho e perda

### O que essa decisao muda

Define:
- campos obrigatorios ao fechar deal
- analytics comercial
- aprendizado do `1FBR-Leads`
- relat�rios de conversao

### Recomendacao para o MVP

Motivos padrao de perda:
- `sem_resposta`
- `sem_budget`
- `sem_fit`
- `concorrente`
- `momento_errado`
- `contato_invalido`
- `nao_quis_avancar`
- `duplicado`

Motivos padrao de ganho:
- `fechamento_comercial`
- `upgrade`
- `renovacao`
- `reativacao`
- `fit_confirmado`

Minha sugestao:
- tornar motivo obrigatorio em `closed_won` e `closed_lost`
- permitir tambem um campo livre `notes`
- devolver para o `1FBR-Leads` tanto o motivo padrao quanto a observacao livre

---

## 3. Approval flow

### 3.1 Tipos de aprovacao

### O que essa decisao muda

Define:
- quando o agente pode agir sozinho
- o que precisa de aprovacao humana
- trilha de auditoria
- risco operacional

### Recomendacao para o MVP

Tipos de aprovacao suportados:
- `send_message`
- `change_deal_stage`
- `merge_duplicate_lead`
- `assign_owner`
- `edit_lead_data`
- `trigger_external_webhook`

Minha sugestao:
- no MVP, exigir aprovacao apenas para acoes que alterem dados sensiveis ou afetem cliente diretamente
- deixar sem aprovacao acoes de leitura, classificacao e sugestao

### 3.2 Quem pode aprovar ou rejeitar

### Recomendacao para o MVP

Pode aprovar:
- `admin`
- `manager`

Pode rejeitar:
- `admin`
- `manager`

Pode apenas visualizar:
- `agent_operator`
- `seller`

Minha sugestao:
- Sergio Castro e Marco Alevato entram como aprovadores globais no MVP
- vendedores comuns nao aprovam acoes de agente inicialmente

### 3.3 Expiracao de aprovacoes

### Recomendacao para o MVP

Sugestao simples:
- `send_message`: 2 horas
- `change_deal_stage`: 8 horas
- `merge_duplicate_lead`: 24 horas
- `assign_owner`: 24 horas
- `edit_lead_data`: 24 horas
- `trigger_external_webhook`: 2 horas

Se quiser simplificar ainda mais:
- tudo expira em 24 horas no MVP

Hoje a implementacao local esta usando `24 horas` como padrao.

### 3.4 Motivo obrigatorio na rejeicao

### Recomendacao para o MVP

Sim, deve ser obrigatorio.

Motivo:
- ajuda o operador a corrigir a solicitacao
- melhora a trilha de auditoria
- evita rejeicoes vagas sem aprendizado

---

## 4. Contrato `1FBR-Leads -> FBR-Click`

### 4.1 Payload final esperado

### O que essa decisao muda

Define:
- schema do webhook
- validacao HMAC
- idempotencia
- regras de fallback de campos ausentes

### Recomendacao para o MVP

Payload sugerido:

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
    "campaign_name": "similarity-campaign",
    "segment": "clinicas"
  },
  "handoff_payload": {
    "source_pipeline": "cold_to_warm",
    "qualification_reason": "engajou com outreach"
  }
}
```

### Campos que eu considero obrigatorios de verdade

Obrigatorios:
- `workspace_id`
- `external_reference`
- `source_system`
- `lead_name`
- pelo menos um entre `email`, `phone` ou `whatsapp`
- `origin`
- `score`
- `temperature`
- `virtual_manager_slug`

Opcionais:
- `company_name`
- `notes`
- `metadata`
- `handoff_payload`

### Minha recomendacao adicional

- usar `external_reference` como chave de idempotencia
- se o lead ja existir, atualizar intake/deal em vez de duplicar
- se vier sem `whatsapp`, `email` e `phone`, rejeitar com `400` em vez de aceitar

### 4.2 Resposta do webhook

Voce definiu que quer apenas `accepted`.

Minha sugestao:
- manter assim no contrato externo
- internamente continuar logando os IDs criados

Resposta sugerida:

```json
{
  "status": "accepted"
}
```

---

## 5. Contrato `FBR-Click -> 1FBR-Leads`

### 5.1 Campos obrigatorios na devolutiva

Como voce quer enviar todas as mudancas de stage, o evento precisa carregar estado suficiente para o `1FBR-Leads` aprender com o funil.

### Recomendacao para o MVP

Payload sugerido:

```json
{
  "external_reference": "lead-123",
  "deal_id": "89949fe6-427f-4942-b621-c3767be8868b",
  "event_type": "deal_stage_changed",
  "stage": "negotiation",
  "previous_stage": "proposal",
  "outcome": null,
  "reason_code": null,
  "reason_notes": null,
  "changed_at": "2026-03-09T18:00:00Z",
  "changed_by_type": "human"
}
```

Quando fechar como ganho ou perda:

```json
{
  "external_reference": "lead-123",
  "deal_id": "89949fe6-427f-4942-b621-c3767be8868b",
  "event_type": "deal_closed",
  "stage": "closed_lost",
  "previous_stage": "negotiation",
  "outcome": "lost",
  "reason_code": "sem_budget",
  "reason_notes": "Cliente adiou investimento para o proximo trimestre.",
  "changed_at": "2026-03-09T18:10:00Z",
  "changed_by_type": "human"
}
```

### Campos obrigatorios recomendados

- `external_reference`
- `deal_id`
- `event_type`
- `stage`
- `previous_stage`
- `changed_at`
- `changed_by_type`

Obrigatorios apenas no fechamento:
- `outcome`
- `reason_code`

---

## 6. Integracao `1FBR-Dev -> FBR-Clicks`

### 6.1 Em qual canal os eventos devem aparecer

### O que essa decisao muda

Define:
- organizacao visual do dashboard
- ru�do operacional
- separacao entre lead comercial e eventos tecnicos

### Recomendacao para o MVP

Criar um space `Operacoes` com estes canais:
- `dev-leads`
- `dev-alertas`

Regra sugerida:
- evento que gera lead vai para `dev-leads`
- evento tecnico interno vai para `dev-alertas`

Se quiser simplificar mais ainda:
- tudo no canal `operacoes/dev-leads` no MVP

### 6.2 Payload de evento

Payload sugerido:

```json
{
  "workspace_id": "00000000-0000-0000-0000-000000000001",
  "source_system": "1FBR-Dev",
  "event_type": "lead_created",
  "title": "Novo lead gerado pelo produto",
  "description": "Usuario solicitou contato comercial a partir da area logada.",
  "external_reference": "dev-lead-001",
  "lead_name": "Joao Silva",
  "email": "joao@empresa.com",
  "phone": "+5511988888888",
  "metadata": {
    "product": "FBR-App",
    "screen": "pricing"
  }
}
```

### 6.3 Secret real

Minha recomendacao:
- usar secret exclusivo por integracao
- nao reaproveitar o mesmo secret do `1FBR-Leads`
- guardar fora do Git

Formato recomendado:
- 32 a 64 caracteres aleatorios

---

## 7. Integracao `1FBR-Suporte -> FBR-Click`

### 7.1 Payload de handoff

Como voce definiu que todo handoff vira `intake`, o contrato pode ser mais simples.

Payload sugerido:

```json
{
  "workspace_id": "00000000-0000-0000-0000-000000000001",
  "source_system": "1FBR-Suporte",
  "external_reference": "ticket-001",
  "lead_name": "Ana Souza",
  "company_name": "Empresa Y",
  "email": "ana@empresay.com",
  "phone": "+5511977777777",
  "priority": "high",
  "notes": "Cliente pediu ajuda e demonstrou interesse comercial.",
  "metadata": {
    "ticket_id": "12345",
    "queue": "upgrade"
  }
}
```

### 7.2 Secret real

Mesma recomendacao do `1FBR-Dev`:
- secret proprio
- 32 a 64 caracteres aleatorios
- armazenado apenas em ambiente

---

## 8. Seguranca dos secrets

Voce ja preencheu um secret real no documento (`TeamFBR123@`).

Minha recomendacao forte:
- trocar esse valor antes de producao
- nao manter secrets reais em markdown versionado
- mover tudo para `.env` local ou gerenciador de segredo

Se quiser, eu posso depois substituir os placeholders do projeto por nomes finais de variaveis, sem gravar os valores reais no Git.

---

## 9. Minhas recomendacoes finais para decidir rapido

Se quisermos decidir isso hoje sem travar a implementacao, eu recomendo assumir o seguinte:

- nome oficial: `FBR-Click`
- stages oficiais: `first_contact`, `qualification`, `proposal`, `negotiation`, `follow_up`, `reengagement`, `closed_won`, `closed_lost`, `cancelled`
- motivo obrigatorio em `won/lost`: sim
- aprovacoes do MVP: `send_message`, `change_deal_stage`, `merge_duplicate_lead`, `assign_owner`, `edit_lead_data`, `trigger_external_webhook`
- aprovadores do MVP: Sergio Castro e Marco Alevato
- expiracao padrao de aprovacao: `24 horas`
- motivo de rejeicao obrigatorio: sim
- resposta do webhook do `1FBR-Leads`: apenas `{ "status": "accepted" }`
- `FBR-Click -> 1FBR-Leads`: enviar toda mudanca de stage
- `1FBR-Dev`: usar canal `operacoes/dev-leads`
- `1FBR-Suporte`: sempre entra como `intake`
- secrets: um por sistema, aleatorio, fora do Git

---

## 10. O que eu consigo fazer depois que voce bater o martelo

Assim que voce validar essas decisoes, eu consigo implementar sem depender de mais definicoes:
- regras formais de transicao de stage
- codigos padrao de ganho e perda
- schema final dos webhooks
- politica de aprovacao por tipo de acao
- canais finais de integracao com `1FBR-Dev`
- endurecimento dos contratos HMAC e eventos de retorno
