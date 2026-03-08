# TOOLS

## Ferramentas disponiveis
- FastAPI backend do FBR-Leads
- PostgreSQL 16 com RLS
- Redis 7 para filas e status
- n8n para orquestracao
- FBR-Click para interacao humana
- OpenClaw Gateway para execucao do agente

## Regras de uso
- Sempre respeitar autenticacao, rate limit e isolamento por workspace.
- Preferir APIs internas e logs auditaveis a acoes manuais sem registro.
