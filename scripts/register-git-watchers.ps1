param(
  [string]$BaseUrl = 'http://localhost:8000',
  [string]$WorkspaceId = '00000000-0000-0000-0000-000000000001',
  [string]$UserId = '11111111-1111-1111-1111-111111111111'
)

$headers = @{
  'X-Workspace-Id' = $WorkspaceId
  'X-User-Id' = $UserId
}

$watchers = @(
  @{ repository_path = '/app/agents/comercial-bot'; branch = 'main'; status = 'idle'; agent_id = '40000000-0000-0000-0000-000000000001' },
  @{ repository_path = '/app/agents/report-bot'; branch = 'main'; status = 'idle'; agent_id = '40000000-0000-0000-0000-000000000002' },
  @{ repository_path = '/app/agents/onboarding-bot'; branch = 'main'; status = 'idle' },
  @{ repository_path = '/app/agents/approval-bot'; branch = 'main'; status = 'idle' },
  @{ repository_path = '/app/agents/content-bot'; branch = 'main'; status = 'idle' },
  @{ repository_path = '/app/agents/ads-bot'; branch = 'main'; status = 'idle' }
)

foreach ($watcher in $watchers) {
  $body = $watcher | ConvertTo-Json
  Invoke-RestMethod -Uri "$BaseUrl/api/git-watcher" -Method Post -Headers $headers -ContentType 'application/json' -Body $body | ConvertTo-Json -Depth 10
}
