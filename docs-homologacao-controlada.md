# Homologacao Controlada - FBR-CLICK

Objetivo: usar o MVP em ambiente controlado, com validacao funcional minima e risco operacional reduzido.

## Antes de abrir para homologacao

1. subir a stack local com `docker compose up -d --build`
2. executar `scripts/homologacao-controlada.ps1`
3. confirmar que o resultado final veio com `"ok": true`

## Roteiro sugerido de uso

1. abrir `http://localhost:3000/login`
2. entrar com `admin@fbr.local` e `change-me-now`
3. validar `/spaces`
4. validar `/spaces/[spaceId]/channels/[channelId]`
5. validar `/spaces/[spaceId]/pipeline`
6. validar `/spaces/[spaceId]/settings/agents`
7. abrir `Preciso de Ajuda` em pelo menos tres telas para confirmar ajuda contextual, checklist e chat do Leon

## Fluxos funcionais que devem ser demonstrados

### 1. Entrada de lead aquecido
- enviar handoff do `1FBR-Leads`
- confirmar criacao de `lead_intake`, `deal`, `channel`, `task` e mensagem inicial
- confirmar destaque visual no pipeline

### 2. Operacao comercial
- abrir o canal do deal
- validar mensagens e tarefas existentes
- mover o deal entre stages permitidos
- validar que fechamento exige `reason_code`

### 3. Agentes
- validar agentes registrados no painel
- validar watchers visiveis por repositorio
- validar que `draft_message` cria rascunho real
- validar que `change_deal_stage` exige approval quando necessario

### 4. Governanca
- aprovar e rejeitar pelo menos um approval
- ligar e desligar o kill switch
- validar audit log e fila de approvals

### 5. Help padronizado FBR
- abrir o drawer `Preciso de Ajuda` sem trocar de rota
- confirmar que a ajuda automatica corresponde a pagina atual
- confirmar que existem perguntas sugeridas e proximas acoes
- confirmar a frase `Ainda tem duvidas ? Pergunte ao Leon.`
- trocar de tela e validar que o contexto do chat foi resetado

## Criterio minimo para considerar MVP pronto para homologacao

- frontend acessivel
- backend saudavel
- webhooks locais aceitando
- `agent-api` executando fluxo principal
- approvals operando
- pipeline e tarefas atualizando em tempo real
- agentes e git watchers registrados
- help contextual funcionando nas telas principais

## Se algo falhar

1. rodar novamente `scripts/homologacao-controlada.ps1`
2. verificar `docs-runbook.md`
3. checar `docker compose logs fastapi --tail 200`
4. checar `docker compose logs frontend --tail 200`
