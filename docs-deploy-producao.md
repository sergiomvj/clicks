# Deploy Producao - FBR-CLICK

## Dominio final

- frontend: `https://click.fbrapps.com`
- api: `https://api.click.fbrapps.com`

## Premissas

- VPS compartilhada com o `1FBR-Leads`
- Postgres gerenciado externamente
- Redis gerenciado externamente
- OpenClaw em VPS separada
- SSL com Certbot no proprio host
- producao usa `docker-compose.production.yml`

## Arquivos de producao

- compose: `docker-compose.production.yml`
- ambiente: `.env.production.example`
- nginx: `nginx/production.conf`
- bootstrap da VPS: `scripts/bootstrap-vps.sh`
- backup: `scripts/backup-postgres.ps1`
- smoke test: `scripts/smoke-deploy.ps1`
- validacao de ambiente: `scripts/validate-production-env.ps1`
- roteiro de validacao: `docs-validacao-vps.md`
- checklist: `docs-go-live-checklist.md`

## Variaveis obrigatorias de producao

- `APP_ENV=production`
- `APP_DOMAIN=click.fbrapps.com`
- `DATABASE_URL_ASYNCPG`
- `REDIS_URL`
- `SESSION_SECRET`
- `JWT_SECRET`
- `OPENCLAW_AGENT_JWT_SECRET`
- `FBR_LEADS_WEBHOOK_SECRET`
- `FBR_DEV_WEBHOOK_SECRET`
- `FBR_SUPORTE_WEBHOOK_SECRET`
- `FBR_LEADS_API_URL=https://leads.fbrapps.com/api/v1/leads/webhook`
- `FBR_DEV_API_URL`
- `FBR_SUPORTE_API_URL`
- `GRAFANA_ADMIN_USER`
- `GRAFANA_ADMIN_PASSWORD`

## Sequencia recomendada

1. rodar `scripts/bootstrap-vps.sh` na VPS
2. copiar `.env.production.example` para `.env.production` e preencher os valores reais
3. validar com `scripts/validate-production-env.ps1 -EnvFile .env.production`
4. copiar `.env.production` para `.env` na VPS
5. copiar o projeto para o diretorio final da VPS
6. validar `docker compose -f docker-compose.production.yml config`
7. subir stack com `docker compose -f docker-compose.production.yml up -d --build`
8. validar `https://click.fbrapps.com` e `https://api.click.fbrapps.com/health`
9. rodar smoke test com `scripts/smoke-deploy.ps1`
10. executar `docs-validacao-vps.md`
11. agendar backup diario com `scripts/backup-postgres.ps1`
12. executar `docs-go-live-checklist.md`

## Backup diario

Script:

```powershell
.\scripts\backup-postgres.ps1 -OutputDir .\backups -Bucket s3://SEU-BUCKET/fbr-click
```

Variaveis esperadas no ambiente:
- `PGHOST`
- `PGPORT`
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

## Smoke test pos-deploy

Script:

```powershell
.\scripts\smoke-deploy.ps1
```

Valida:
- frontend
- API health
- Grafana

## Riscos a validar antes do go-live

- segredo real do `1FBR-Leads` fora de markdown versionado
- callback `FBR-CLICK -> 1FBR-Leads` respondendo em producao
- callback `FBR-CLICK -> 1FBR-Dev` respondendo em producao
- callback `FBR-CLICK -> 1FBR-Suporte` respondendo em producao
- rotacao de tokens dos agentes
- indisponibilidade do Postgres e Redis gerenciados
