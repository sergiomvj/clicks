# Validacao Final VPS - FBR-CLICK

## Objetivo

Executar uma pre-validacao objetiva antes do go-live real na VPS.

## Ordem sugerida

1. validar o arquivo de ambiente com:

```powershell
.\scripts\validate-production-env.ps1 -EnvFile .env.production
```

2. validar o compose de producao:

```powershell
docker compose -f docker-compose.production.yml config
```

3. subir a stack de producao na VPS:

```powershell
docker compose -f docker-compose.production.yml up -d --build
```

4. executar smoke HTTP externo:

```powershell
.\scripts\smoke-deploy.ps1
```

## O que o validador de ambiente checa

- variaveis obrigatorias preenchidas
- placeholders ainda nao substituidos
- segredos criticos ausentes
- URLs de integracao nao definidas

## O que ainda depende de ambiente real

- DNS resolvendo para a VPS
- SSL emitido pelo Certbot
- endpoints reais de `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte`
- secrets finais fora do repositorio
- Postgres e Redis gerenciados acessiveis
