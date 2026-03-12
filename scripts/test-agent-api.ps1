param(
    [string]$BaseUrl = 'http://localhost:8000',
    [string]$WorkspaceId = '00000000-0000-0000-0000-000000000001',
    [string]$UserId = '11111111-1111-1111-1111-111111111111',
    [string]$AgentId = '40000000-0000-0000-0000-000000000001'
)

$headers = @{
    'X-Workspace-Id' = $WorkspaceId
    'X-User-Id' = $UserId
}

$tokenBody = @{
    agent_id = $AgentId
    ttl_minutes = 60
} | ConvertTo-Json

$tokenResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/agents/tokens" -Headers $headers -Body $tokenBody -ContentType 'application/json'

$agentHeaders = @{
    'X-Workspace-Id' = $WorkspaceId
    'Authorization' = "Bearer $($tokenResponse.access_token)"
}

$draftBody = @{
    action_type = 'draft_message'
    payload = @{
        channel_id = '30000000-0000-0000-0000-000000000001'
        body = 'Oi Mariana, podemos agendar uma conversa ainda hoje?'
    }
} | ConvertTo-Json -Depth 5

$followUpBody = @{
    action_type = 'create_follow_up_task'
    payload = @{
        deal_id = '60000000-0000-0000-0000-000000000001'
        title = 'Follow-up com lead Acme'
        description = 'Retornar contato em 24h'
        priority = 'high'
    }
} | ConvertTo-Json -Depth 5

$stageSuggestionBody = @{
    action_type = 'suggest_stage_change'
    payload = @{
        deal_id = '60000000-0000-0000-0000-000000000001'
        target_stage = 'proposal'
        reason = 'Lead demonstrou intencao clara de receber proposta.'
    }
} | ConvertTo-Json -Depth 5

$changeStageBody = @{
    action_type = 'change_deal_stage'
    payload = @{
        deal_id = '60000000-0000-0000-0000-000000000001'
        stage = 'proposal'
    }
} | ConvertTo-Json -Depth 5

$sendMessageBody = @{
    action_type = 'send_message'
    payload = @{
        channel_id = '30000000-0000-0000-0000-000000000001'
        body = 'Posso seguir com a proposta?'
    }
} | ConvertTo-Json -Depth 5

$draftResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/agent-api/actions/execute" -Headers $agentHeaders -Body $draftBody -ContentType 'application/json'
$followUpResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/agent-api/actions/execute" -Headers $agentHeaders -Body $followUpBody -ContentType 'application/json'
$stageSuggestionResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/agent-api/actions/execute" -Headers $agentHeaders -Body $stageSuggestionBody -ContentType 'application/json'
$changeStageApprovalResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/agent-api/actions/execute" -Headers $agentHeaders -Body $changeStageBody -ContentType 'application/json'
$approvalDecisionBody = @{ status = 'approved'; decision_notes = 'Pode mover para proposta.' } | ConvertTo-Json
$approvalDecisionResponse = Invoke-RestMethod -Method Patch -Uri "$BaseUrl/api/agents/approvals/$($changeStageApprovalResponse.approval_id)" -Headers $headers -Body $approvalDecisionBody -ContentType 'application/json'
$changeStageExecuteBody = @{
    action_type = 'change_deal_stage'
    payload = @{
        approval_id = $changeStageApprovalResponse.approval_id
        deal_id = '60000000-0000-0000-0000-000000000001'
        stage = 'proposal'
    }
} | ConvertTo-Json -Depth 5
$changeStageExecuteResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/agent-api/actions/execute" -Headers $agentHeaders -Body $changeStageExecuteBody -ContentType 'application/json'
$sendMessageApprovalResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/agent-api/actions/execute" -Headers $agentHeaders -Body $sendMessageBody -ContentType 'application/json'

[pscustomobject]@{
    token_agent = $tokenResponse.agent.slug
    token_expires_at = $tokenResponse.expires_at
    draft_status = $draftResponse.status
    draft_message_id = $draftResponse.message_id
    follow_up_status = $followUpResponse.status
    follow_up_task_id = $followUpResponse.task_id
    stage_suggestion_status = $stageSuggestionResponse.status
    stage_suggestion_task_id = $stageSuggestionResponse.task_id
    stage_suggestion_message_id = $stageSuggestionResponse.message_id
    change_stage_approval_status = $changeStageApprovalResponse.status
    change_stage_approval_id = $changeStageApprovalResponse.approval_id
    approval_decision_status = $approvalDecisionResponse.status
    change_stage_execute_status = $changeStageExecuteResponse.status
    send_message_status = $sendMessageApprovalResponse.status
    send_message_approval_id = $sendMessageApprovalResponse.approval_id
} | ConvertTo-Json -Depth 5
