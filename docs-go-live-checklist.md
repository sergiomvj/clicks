# Checklist Go-Live - FBR-CLICK

Use esta lista no dia do deploy na VPS. A ordem abaixo foi organizada para execucao procedural, sem pular dependencia entre etapas.

## Fase 1 - Pre-flight local

1. [ ] confirmar que os endpoints reais foram recebidos para `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte`
2. [ ] confirmar os secrets finais fora do repositorio
3. [ ] preencher `.env.production` a partir de `.env.production.example`
4. [ ] executar `./scripts/validate-production-env.ps1 -EnvFile .env.production`
5. [ ] validar `docker compose -f docker-compose.production.yml config`

## Fase 2 - Infra da VPS

1. [ ] acessar a VPS por SSH
2. [ ] confirmar DNS de `click.fbrapps.com` apontando para a VPS
3. [ ] confirmar DNS de `api.click.fbrapps.com` apontando para a VPS
4. [ ] validar acesso ao Postgres gerenciado
5. [ ] validar acesso ao Redis gerenciado
6. [ ] validar acesso ao bucket de backup
7. [ ] rodar `scripts/bootstrap-vps.sh`
8. [ ] confirmar certificados SSL emitidos para frontend e API

## Fase 3 - Subida da stack

1. [ ] copiar o projeto para o diretorio final na VPS
2. [ ] copiar `.env.production` para `.env` na VPS
3. [ ] subir com `docker compose -f docker-compose.production.yml up -d --build`
4. [ ] validar `docker compose -f docker-compose.production.yml ps`
5. [ ] validar `https://api.click.fbrapps.com/health`
6. [ ] validar `https://click.fbrapps.com`
7. [ ] validar `https://click.fbrapps.com/grafana/`
8. [ ] executar `scripts/smoke-deploy.ps1`

## Fase 4 - Bootstrap da aplicacao

1. [ ] fazer login no painel
2. [ ] abrir `/spaces`
3. [ ] abrir `/spaces/[spaceId]/settings/agents`
4. [ ] confirmar kill switch, approvals, watchers e agentes no painel
5. [ ] executar `scripts/register-agents.ps1` contra producao
6. [ ] executar `scripts/register-git-watchers.ps1` contra producao
7. [ ] confirmar os 6 agentes registrados
8. [ ] confirmar os 6 git watchers registrados

## Fase 5 - Integracoes reais

1. [ ] testar handoff de `1FBR-Leads` em `https://api.click.fbrapps.com/api/v1/leads/webhook`
2. [ ] confirmar callback `FBR-CLICK -> 1FBR-Leads`
3. [ ] testar webhook de `1FBR-Dev`
4. [ ] confirmar callback `FBR-CLICK -> 1FBR-Dev`
5. [ ] testar webhook de `1FBR-Suporte`
6. [ ] confirmar callback `FBR-CLICK -> 1FBR-Suporte`

## Fase 6 - Seguranca operacional

1. [ ] ligar e desligar o kill switch
2. [ ] testar um approval real de `change_deal_stage`
3. [ ] testar um approval real de mensagem
4. [ ] validar rate limiting em pelo menos uma rota sensivel
5. [ ] executar backup manual com `scripts/backup-postgres.ps1`
6. [ ] confirmar append-only de `agent_action_logs` sem erro de permissao operacional

## Fase 7 - Liberacao final

1. [ ] executar `docs-validacao-vps.md`
2. [ ] Sergio Castro aprovou
3. [ ] Marco Alevato aprovou
4. [ ] registrar o go-live no runbook interno
