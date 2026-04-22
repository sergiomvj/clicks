# Procedimentos de Homologacao - FBR-CLICK

Este roteiro assume homologacao controlada em ambiente local, com a stack rodando via Docker.

## Objetivo da homologacao

Validar que o MVP do `FBR-CLICK` opera ponta a ponta nos fluxos criticos:
- entrada de leads
- criacao de deal, canal e tarefa
- operacao comercial no pipeline
- uso controlado de agentes
- approvals, kill switch e auditoria
- visualizacao em tempo real no painel
- help contextual padronizado FBR

## Credenciais e referencias

- frontend: `http://localhost:3000`
- backend: `http://localhost:8000`
- login: `admin@fbr.local`
- senha: `change-me-now`
- workspace: `00000000-0000-0000-0000-000000000001`

## Etapa 1 - Preparacao do ambiente

1. Abrir terminal na raiz do projeto.
2. Subir a stack:

```powershell
docker compose up -d --build
```

3. Confirmar containers principais:

```powershell
docker compose ps
```

Esperado:
- `postgres` healthy
- `redis` healthy
- `openclaw-gateway` healthy
- `fastapi` running/healthy
- `frontend` running

## Etapa 2 - Validacao automatica inicial

1. Rodar o pacote completo de homologacao:

```powershell
.\scripts\homologacao-controlada.ps1
```

2. Confirmar no JSON final:
- `"ok": true`
- todos os checks com `"ok": true`

Se algum item falhar, parar aqui e consultar:
- `docs-runbook.md`
- `docker compose logs fastapi --tail 200`
- `docker compose logs frontend --tail 200`

## Etapa 3 - Acesso ao painel

1. Abrir `http://localhost:3000/login`
2. Fazer login com as credenciais locais.
3. Validar carregamento de:
- `/spaces`
- `/spaces/[spaceId]/channels/[channelId]`
- `/spaces/[spaceId]/pipeline`
- `/spaces/[spaceId]/tasks`
- `/spaces/[spaceId]/settings/agents`

Evidencia esperada:
- painel abre sem erro
- spaces e canais aparecem
- pipeline exibe deals
- tasks aparecem em cards
- agentes e watchers aparecem no painel

## Etapa 4 - Validacao do help padronizado

1. Abrir `Preciso de Ajuda` na tela do canal.
2. Confirmar que o drawer abre sem trocar de rota.
3. Validar os blocos:
- ajuda automatica da pagina atual
- checklist rapido
- proximas acoes
- perguntas sugeridas
- chat com o agente

4. Perguntar algo sobre a tela atual.
5. Trocar para `pipeline` e abrir o help novamente.
6. Confirmar que o contexto foi resetado e que o conteudo mudou para a tela nova.

Evidencia esperada:
- ajuda restrita a rota atual
- frase `Ainda tem duvidas ? Pergunte ao Leon.` visivel
- atalhos contextuais coerentes com a pagina
- chat sem carregar contexto da tela anterior

## Etapa 5 - Fluxo de entrada de lead aquecido

1. Executar o teste do `1FBR-Leads`:

```powershell
.\scripts\test-fbr-leads-webhook.ps1
```

2. Validar no painel comercial:
- novo lead ou lead idempotente processado
- deal presente no pipeline
- canal do deal criado
- tarefa criada
- mensagem inicial criada

3. Validar no backend, se necessario:

```powershell
.\scripts\test-webhooks.ps1
```

Evidencia esperada:
- resposta `accepted`
- pipeline com deal de origem `1FBR-Leads`
- destaque visual da origem quente

## Etapa 6 - Fluxo de operacao comercial

1. Abrir o canal do deal principal.
2. Confirmar visualizacao de:
- mensagens humanas e de agentes
- tarefas do deal
- aprovacoes pendentes quando existirem

3. Mudar o deal para um stage permitido.
4. Confirmar que o painel atualiza.
5. Tentar fechamento sem `reason_code` para validar a protecao.

Evidencia esperada:
- transicoes validas funcionam
- transicoes invalidas sao bloqueadas
- fechamento sem motivo nao passa

## Etapa 7 - Fluxo de agentes

1. Executar o teste da agent API:

```powershell
.\scripts\test-agent-api.ps1
```

2. Validar no painel:
- rascunho criado pelo agente
- tarefa criada pelo agente
- sugestao de mudanca de stage registrada
- approval gerado para acao sensivel

3. Confirmar em `/settings/agents`:
- 6 agentes registrados
- escopo por agente visivel
- approvals obrigatorios visiveis
- git watchers visiveis

Evidencia esperada:
- `draft_message` executado
- `create_follow_up_task` executado
- `suggest_stage_change` executado
- `change_deal_stage` exigindo approval quando aplicavel

## Etapa 8 - Approvals e governanca

1. No painel, aprovar pelo menos um approval.
2. Rejeitar pelo menos um approval.
3. Confirmar atualizacao do status na fila.
4. Ligar o kill switch.
5. Confirmar que novas acoes sensiveis ficam bloqueadas.
6. Desligar o kill switch.

Evidencia esperada:
- approve/reject funcionando pela UI
- kill switch refletido no painel
- comportamento coerente com bloqueio operacional

## Etapa 9 - Realtime

1. Manter duas telas abertas, se possivel:
- canal comercial
- pipeline ou settings/agents

2. Gerar uma mensagem, tarefa ou approval.
3. Confirmar atualizacao sem refresh manual.

Evidencia esperada:
- canal atualiza com websocket
- tasks/pipeline/agents atualizam com websocket de workspace

## Etapa 10 - Integracoes auxiliares

1. Executar:

```powershell
.\scripts\test-fbr-dev-webhook.ps1
.\scripts\test-fbr-suporte-webhook.ps1
```

2. Confirmar retorno `accepted`.
3. Confirmar registro operacional no sistema.

Observacao:
- os callbacks de saida para `1FBR-Dev` e `1FBR-Suporte` ja estao preparados no backend
- a validacao ponta a ponta desses callbacks depende das URLs reais externas

## Etapa 11 - Encerramento da homologacao

Considerar homologacao local aprovada se:
- `scripts/homologacao-controlada.ps1` retornar `ok = true`
- login e navegacao funcionarem
- help contextual funcionar nas telas principais
- entrada de lead funcionar
- pipeline e tarefas refletirem o estado real
- agentes funcionarem com approval quando necessario
- kill switch funcionar
- realtime funcionar

## Itens fora do escopo desta homologacao local

Estes pontos nao impedem a homologacao controlada local, mas impedem considerar o projeto 100% finalizado:
- deploy validado em VPS real
- dominio e SSL reais
- secrets finais
- payloads e endpoints reais externos
- carga e hardening final de producao
