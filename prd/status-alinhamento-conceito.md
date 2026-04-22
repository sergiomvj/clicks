# Status atual de aderencia ao conceito original

Atualizado em: 2026-03-27

## O que foi fechado localmente nesta rodada

- camada de `kpis` criada no banco, backend e frontend
- `agent_markdown_cache` criado no banco e sincronizado no fluxo de agentes
- matriz formal de divergencias criada em `prd/matriz-alinhamento-conceito.md`
- autenticacao de agentes ajustada para sessao validada em Redis com TTL de 24h
- endpoint de heartbeat de agente publicado em `/api/agent-api/heartbeat`
- monitor de agentes atualizado para exibir heartbeat e estado operacional
- identidade visual global migrada para dark mode coerente com o conceito

## O que ficou bloqueado fora do codigo local

- RLS completo com enforcement real por `workspace_id` no banco
- homologacao com payloads reais de `1FBR-Leads`, `1FBR-Dev` e `1FBR-Suporte`
- deploy final em VPS com dominio e SSL reais
- carga real com 10 agentes simultaneos
- validacao operacional de observabilidade, backup e restore em ambiente alvo

## O que ainda depende de refatoracao interna maior

- enforcement robusto de RLS sem risco de quebrar o pool atual do `asyncpg`
- validacao de escopo cruzando token, banco e configuracao versionada em cada operacao critica
- operacionalizacao real dos 6 agentes com triggers automaticos do conceito
- stack LLM em 3 camadas com fallback real e health publish recorrente

## Leitura honesta do progresso

- produto operacional: alto
- aderencia conceitual local: avancou bastante
- aderencia conceitual total: ainda depende de infra e homologacao externa
## Atualizacao adicional desta rodada

- autorizacao de `agent-api` agora valida a acao tambem contra o escopo presente no token emitido
- migration `004_operational_alignment.sql` aproxima `channels` e `tasks` da semantica do conceito
- prioridades de tarefas passam a seguir `p0` a `p3`, com compatibilidade para aliases antigos
- tipos de canais passam a convergir para `deal`, `task`, `system` e `agent-log`
## Avancos autonomos executados em 2026-03-30

- `app/core/llm.py` agora expõe estado detalhado das 3 camadas e modelo ativo de forma mais próxima ao conceito
- `frontend/components/layout/Sidebar.tsx` foi alinhada para semântica de hub operacional com agrupamento por tipo de canal
- `scripts/validate-finalization.ps1` foi criado para validar estruturalmente o baseline local de finalização

## Limite do que ainda depende de acao externa

Os batches 6 a 9 continuam parcialmente bloqueados por:
- URLs reais dos sistemas externos
- secrets finais fora do repositório
- VPS, dominio e SSL reais
- janela controlada de homologacao e go-live
