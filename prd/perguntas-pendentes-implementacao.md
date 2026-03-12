# Perguntas Pendentes Para Finalizar o FBR-CLICK

Preencha este documento de forma objetiva. Pode responder logo abaixo de cada pergunta com `Resposta:`.

---

## 1. Regras de negocio e operacao do produto

### 1.1 Naming oficial
- Qual sera o nome oficial do produto na interface, repositorio e dominios?
  Resposta:
- Devemos padronizar como `FBR-CLICK`?
  Resposta:FBR-CLICK

### 1.2 Origens de lead
- Quais origens devem existir oficialmente no MVP?
  Resposta: 1FBR-Leads, redes sociais, site do produto e manual
- Alem de `1FBR-Leads`, redes sociais, site do produto e manual, existe mais alguma origem obrigatoria?
  Resposta:Nào
- Quais origens devem abrir deal automaticamente e quais devem entrar primeiro como intake para qualificacao manual?
  Resposta: 1FBR-Leads deve abrir deal automaticamente, as demais devem entrar primeiro como intake para qualificacao manual 

### 1.3 Handoff do 1FBR-Leads
- Quais campos sao obrigatorios no payload real enviado pelo `1FBR-Leads`?
  Resposta: Nome, email, telefone, whatsapp (importante), empresa (opcional), origem, score, temperatura, metadata, handoff_payload
- O `1FBR-Leads` deve sempre informar o vendedor responsavel ou o `FBR-CLICK` decide isso internamente?
  Resposta: O `1FBR-Leads` deve sempre informar o gestor virtual responsavel
- Quando um lead vier do `1FBR-Leads`, devemos sempre criar:
  - deal
  - canal
  - tarefa
  - mensagem inicial
  Resposta: Sim
- Existe alguma situacao em que o handoff do `1FBR-Leads` nao deve gerar deal automaticamente?
  Resposta: Sim, se o lead ja estiver no sistema
- O que fazer com leads duplicados?
  Resposta: Atualizar o lead existente se ja estiver no sistema, senao criar um novo
- O que fazer com leads que nao tem email?
  Resposta: Classificar como lead frio e enviar para o funil de prospecção
- O que fazer com leads que nao tem telefone?
  Resposta: Classificar como lead frio e enviar para o funil de prospecção
- O que fazer com leads que nao tem whatsapp?
  Resposta: Classificar como lead frio e enviar para o funil de prospecção
- O que fazer com leads que nao tem empresa?
  Resposta: Adicionar sem empresa
- O que fazer com leads que nao tem score?
  Resposta: Adicionar com score 0
- O que fazer com leads que nao tem temperatura?
  Resposta: Adicionar com temperatura 0
- O que fazer com leads que nao tem metadata?
  Resposta: Adicionar com metadata vazia
- O que fazer com leads que nao tem handoff_payload?
  Resposta: Adicionar com handoff_payload vazio
- O que fazer com leads que nao tem origem?
  Resposta: Adicionar com origem desconhecida
- O que fazer com leads que nao tem vendedor responsavel?
  Resposta: Adicionar com vendedor responsavel padrao 
- O que fazer com leads que nao tem canal?
  Resposta: Adicionar com canal padrao
- O que fazer com leads que nao tem tarefa?
  Resposta: Adicionar com tarefa padrao
- O que fazer com leads que nao tem mensagem inicial?
  Resposta: Adicionar com mensagem inicial padrao
- O que fazer com leads que nao tem status?
  Resposta: Adicionar com status padrao
- O que fazer com leads que nao tem stage?
  Resposta: Adicionar com stage padrao
- O que fazer com leads que nao tem motivo?
  Resposta: Adicionar com motivo padrao
- O que fazer com leads que nao tem data de criacao?
  Resposta: Adicionar com data de criacao atual
- O que fazer com leads que nao tem data de atualizacao?
  Resposta: Adicionar com data de atualizacao atual
- O que fazer com leads que nao tem data de vencimento?
  Resposta: Adicionar com data de vencimento atual
- O que fazer com leads que nao tem data de perda?
  Resposta: Adicionar com data de perda atual
- O que fazer com leads que nao tem data de ganho?
  Resposta: Adicionar com data de ganho atual
- O que fazer com leads que nao tem data de cancelamento?
  Resposta: Adicionar com data de cancelamento atual
- O que fazer com leads que nao tem data de expiracao?
  Resposta: Adicionar com data de expiracao atual
- O que fazer com leads que nao tem data de criacao?
  Resposta: Adicionar com data de criacao atual
- O que fazer com leads que nao tem data de atualizacao?
  Resposta: Adicionar com data de atualizacao atual
- O que fazer com leads que nao tem data de vencimento?
  Resposta: Adicionar com data de vencimento atual
- O que fazer com leads que nao tem data de perda?
  Resposta: Adicionar com data de perda atual
- O que fazer com leads que nao tem data de ganho?
  Resposta: Adicionar com data de ganho atual
- O que fazer com leads que nao tem data de cancelamento?
  Resposta: Adicionar com data de cancelamento atual
- O que fazer com leads que nao tem data de expiracao?
  Resposta: Adicionar com data de expiracao atual
- O que fazer com leads que nao tem data de criacao?
  Resposta: Adicionar com data de criacao atual
- O que fazer com leads que nao tem data de atualizacao?
  Resposta: Adicionar com data de atualizacao atual
- O que fazer com leads que nao tem data de vencimento?
  Resposta: Adicionar com data de vencimento atual
- O que fazer com leads que nao tem data de perda?
  Resposta: Adicionar com data de perda atual
- O que fazer com leads que nao tem data de ganho?
  Resposta: Adicionar com data de ganho atual
- O que fazer com leads que nao tem data de cancelamento?
  Resposta: Adicionar com data de cancelamento atual
- O que fazer com leads que nao tem data de expiracao?
  Resposta: Adicionar com data de expiracao atual


### 1.4 Pipeline comercial
- Quais stages oficiais do pipeline devem existir no MVP?
  Resposta: Primeiro contato, Qualificacao, Proposta, Negociacao, Fechamento, Follow-up, Reengajamento, Cancelado, Perdido, Ganho 
- Quais transicoes sao permitidas entre stages?
  Resposta: 1FBR-Leads deve abrir deal automaticamente, as demais devem entrar primeiro como intake para qualificacao manual 
- `deal.won` e `deal.lost` precisam exigir motivo obrigatorio?
  Resposta: Sim
  - Quais motivos padrao de perda devemos cadastrar?
  Resposta: Avaliar em conjunto com o time comercial
- Quais motivos padrao de ganho devemos cadastrar?
  Resposta: Avaliar em conjunto com o time comercial

### 1.5 Tarefas e automacoes
- Quais tarefas padrao devem ser criadas automaticamente quando um lead aquecido entra?
  Resposta:Classificar como lead quente, enviar mensagem inicial, criar tarefa de follow-up
- Existe SLA por origem de lead?
  Resposta: Sim
- O sistema deve priorizar leads do `1FBR-Leads` acima das demais origens na interface?
  Resposta: Sim

### 1.6 Agentes
- Quais agentes entram de verdade no MVP 1?
  Resposta: Agente Comercial, Agente de Prospecção, Agente de Qualificação, Agente de Vendas, Agente de Pós-venda, Agente de Suporte, Agente de Marketing, Agente de Vendas, Agente de Pós-venda, Agente de Suporte, Agente de Marketing

- `comercial-bot` e `report-bot` entram obrigatoriamente agora?
  Resposta:Sim
- Quais acoes cada agente pode executar sem aprovacao humana?
  Resposta: Apenas as que estiverem dentro do escopo de cada agente 
- Quais acoes devem sempre exigir aprovacao humana?
  Resposta: As que estiverem fora do escopo de cada agente
- Quem sao os owners humanos de cada agente?
  Resposta: Sergio Castro e Marco Alevato são os owners humanos de todos os agentes

### 1.7 Approval flow
- Quais tipos de aprovacao o sistema precisa suportar no MVP?
  Resposta: Avaliar em conjunto com a IA por ocasião da implementação
- Quem pode aprovar ou rejeitar?
  Resposta: Avaliar em conjunto com a IA por ocasião da implementação
- Aprovações expiram? Se sim, em quanto tempo?
  Resposta: Avaliar em conjunto com a IA por ocasião da implementação
- Ao rejeitar, o motivo deve ser obrigatorio?
  Resposta: Avaliar em conjunto com a IA por ocasião da implementação 

---

## 2. Integracoes reais entre sistemas

### 2.1 1FBR-Leads -> FBR-CLICK
- Qual e o endpoint real que o `1FBR-Leads` vai chamar?
  Resposta: https://click.fbrapps.com/api/v1/leads/webhook
- Qual secret real sera usado no HMAC?
  Resposta:TeamFBR123@
- Qual o payload final esperado? Se ja existir, cole um exemplo real.
  Resposta: A ser definido em conjunto com a IA por ocasião da implementação
- O `1FBR-Leads` espera resposta sincronica apenas com `accepted`, ou precisa receber IDs criados no `FBR-CLICK`?
  Resposta: resposta sincronica apenas com `accepted`

### 2.2 FBR-CLICK  -> 1FBR-Leads
- Qual endpoint real do `1FBR-Leads` deve receber `deal.won` e `deal.lost`?
  Resposta: https://leads.fbrapps.com/api/v1/leads/webhook
- Quais campos sao obrigatorios na devolutiva?
  Resposta: A ser definido em conjunto com a IA por ocasião da implementação
- O `1FBR-Leads` quer receber apenas o desfecho final ou tambem mudancas intermediarias do pipeline?
  Resposta: Todas as mudanças de stage do deal para incremento de conhecimento do lead

### 2.3 1FBR-Dev -> FBR-CLICK
- Quais eventos reais do `1FBR-Dev` devem chegar no `FBR-CLICK` no MVP?
  Resposta: Todos os eventos que geram leads
- Em qual canal esses eventos devem aparecer?
  Resposta: A ser definido em conjunto com a IA por ocasião da implementação
- Existe payload real ou exemplo de evento?
  Resposta: A ser definido em conjunto com a IA por ocasião da implementação
- Qual secret real sera usado?
  Resposta: A ser definido em conjunto com a IA por ocasião da implementação

### 2.4 1FBR-Suporte -> FBR-CLICK
- Quais tipos de handoff do `1FBR-Suporte` entram no `FBR-CLICK`?
  Resposta: Todos os handoffs
- Devem virar intake, deal ou somente mensagem no canal?
  Resposta: intake
- Existe payload real ou exemplo?
  Resposta: A ser definido em conjunto com a IA por ocasião da implementação
- Qual secret real sera usado?
  Resposta: A ser definido em conjunto com a IA por ocasião da implementação

### 2.5 OpenClaw real
- Onde o OpenClaw real vai rodar?
  Resposta: Numa VPS separada
- O scaffold atual sera substituido por um gateway oficial separado ou mantido como adaptador local?
  Resposta: gateway oficial
- Qual estrategia de JWT de agentes sera usada em producao?
  Resposta: Tokens de curta duracao por agente  

---

## 3. Infraestrutura, deploy e operacao

### 3.1 Ambiente de producao
- Qual VPS ou conjunto de VPSs sera usado para o `FBR-CLICK`?
  Resposta: VPS com 16gb de ram e 8 processadores Intel Xeon mas será compartilhada com o 1FBR-Leads
- O banco sera local em container ou gerenciado externamente?
  Resposta: Gerenciado externamente
- Redis sera local ou gerenciado externamente?
  Resposta: Gerenciado externamente

### 3.2 Dominio e SSL
- Qual dominio final do sistema?
  Resposta: click.fbrapps.com
- Qual subdominio do frontend?
  Resposta: click.fbrapps.com
- Qual subdominio da API?
  Resposta: api.click.fbrapps.com
- SSL sera com Certbot no proprio host?
  Resposta: Sim

### 3.3 Secrets e ambiente
- Quem vai fornecer os secrets reais do `.env`?
  Resposta: Sim
- Onde os secrets de producao serao armazenados?
  Resposta: Em um arquivo .env local
- Existe separacao de ambiente `dev`, `staging` e `prod`?
  Resposta: Sim

### 3.4 Backup e observabilidade
- Onde os backups do Postgres devem ser armazenados?
  Resposta: Num Bucket S3 ou equivalente na propria VPS 
- Qual frequencia de backup voce quer no MVP?
  Resposta: A cada 24 horas
- Quem vai acessar Grafana e Prometheus?
  Resposta: Apenas a equipe de desenvolvimento
- Quais alertas precisam existir obrigatoriamente?
  Resposta: Apenas alertas de indisponibilidade do sistema

### 3.5 Go-live
- O que define “projeto finalizado” para voce?
  Resposta: Que o sistema esteja funcionando conforme o esperado
- O que define “MVP pronto para uso interno”?
  Resposta: Que o sistema esteja funcionando conforme o esperado
- Quais testes voce considera obrigatorios antes de colocar no ar?
  Resposta: Testes de integracao com os sistemas existentes
- Quem precisa aprovar o handoff final?
  Resposta: Sergio Castro e Marco Alevato

---

## 4. Prioridades finais

- Se eu tiver que otimizar o restante por impacto, qual ordem voce prefere?
  Resposta: Operacao comercial com `1FBR-Leads`
- O que e mais importante agora:
  - operacao comercial com `1FBR-Leads`
  - agentes
  - integracao com `1FBR-Dev`
  - integracao com `1FBR-Suporte`
  - producao
  Resposta: Operacao comercial com `1FBR-Leads`
