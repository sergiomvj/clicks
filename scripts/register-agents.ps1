param(
  [string]$BaseUrl = 'http://localhost:8000',
  [string]$WorkspaceId = '00000000-0000-0000-0000-000000000001'
)

$headers = @{
  'X-Workspace-Id' = $WorkspaceId
  'X-User-Id' = '11111111-1111-1111-1111-111111111111'
}

$agents = @(
  @{ slug = 'comercial-bot'; display_name = 'Comercial Bot'; repository_path = 'agents/comercial-bot' },
  @{ slug = 'report-bot'; display_name = 'Report Bot'; repository_path = 'agents/report-bot' },
  @{ slug = 'onboarding-bot'; display_name = 'Onboarding Bot'; repository_path = 'agents/onboarding-bot' },
  @{ slug = 'approval-bot'; display_name = 'Approval Bot'; repository_path = 'agents/approval-bot' },
  @{ slug = 'content-bot'; display_name = 'Content Bot'; repository_path = 'agents/content-bot' },
  @{ slug = 'ads-bot'; display_name = 'Ads Bot'; repository_path = 'agents/ads-bot' }
)

foreach ($agent in $agents) {
  $body = $agent | ConvertTo-Json
  Invoke-RestMethod -Uri "$BaseUrl/api/agents" -Method Post -Headers $headers -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 10
}
