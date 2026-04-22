param(
  [string]$BaseUrl = 'http://localhost:8000',
  [string]$FrontendUrl = 'http://localhost:3000/login',
  [string]$WorkspaceId = '00000000-0000-0000-0000-000000000001',
  [string]$UserId = '11111111-1111-1111-1111-111111111111',
  [string]$FbrLeadsSecret = 'replace-with-fbr-leads-secret',
  [string]$FbrDevSecret = 'replace-with-fbr-dev-secret',
  [string]$FbrSuporteSecret = 'replace-with-fbr-suporte-secret'
)

$results = New-Object System.Collections.Generic.List[object]

function Add-Result {
  param(
    [string]$Name,
    [bool]$Ok,
    [string]$Detail
  )

  $results.Add([pscustomobject]@{
    name = $Name
    ok = $Ok
    detail = $Detail
  }) | Out-Null
}

function Invoke-Step {
  param(
    [string]$Name,
    [scriptblock]$Action
  )

  try {
    $detail = & $Action
    Add-Result -Name $Name -Ok $true -Detail ([string]$detail)
  } catch {
    Add-Result -Name $Name -Ok $false -Detail $_.Exception.Message
  }
}

function Invoke-Json {
  param(
    [string]$Method,
    [string]$Uri,
    [hashtable]$Headers = @{},
    [object]$Body = $null
  )

  if ($null -eq $Body) {
    return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -ContentType 'application/json'
  }

  return Invoke-RestMethod -Method $Method -Uri $Uri -Headers $Headers -Body ($Body | ConvertTo-Json -Depth 10) -ContentType 'application/json'
}

$headers = @{
  'X-Workspace-Id' = $WorkspaceId
  'X-User-Id' = $UserId
}

Invoke-Step -Name 'frontend_login_page' -Action {
  $response = Invoke-WebRequest -Uri $FrontendUrl -UseBasicParsing -TimeoutSec 15
  if ($response.StatusCode -ne 200) { throw "status $($response.StatusCode)" }
  'login page 200'
}

Invoke-Step -Name 'backend_health' -Action {
  $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method Get -TimeoutSec 10
  if ($response.status -ne 'ok') { throw 'health returned non-ok' }
  'health ok'
}

Invoke-Step -Name 'register_agents' -Action {
  $output = powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\register-agents.ps1 -BaseUrl $BaseUrl -WorkspaceId $WorkspaceId 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) { throw $output }
  'agents registered'
}

Invoke-Step -Name 'register_git_watchers' -Action {
  $output = powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\register-git-watchers.ps1 -BaseUrl $BaseUrl -WorkspaceId $WorkspaceId -UserId $UserId 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) { throw $output }
  'git watchers registered'
}

Invoke-Step -Name 'spaces_bundle' -Action {
  $response = Invoke-Json -Method Get -Uri "$BaseUrl/api/spaces" -Headers $headers
  if ($response.spaces.Count -lt 1) { throw 'no spaces returned' }
  "spaces=$($response.spaces.Count) channels=$($response.channels.Count)"
}

Invoke-Step -Name 'git_watcher_list' -Action {
  $response = Invoke-Json -Method Get -Uri "$BaseUrl/api/git-watcher" -Headers $headers
  if ($response.watchers.Count -lt 6) { throw "expected >= 6 watchers, got $($response.watchers.Count)" }
  "watchers=$($response.watchers.Count)"
}

Invoke-Step -Name 'webhooks_bundle' -Action {
  $output = powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-webhooks.ps1 -BaseUrl $BaseUrl -WorkspaceId $WorkspaceId -FbrLeadsSecret $FbrLeadsSecret -FbrDevSecret $FbrDevSecret -FbrSuporteSecret $FbrSuporteSecret 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) { throw $output }
  'webhooks accepted'
}

Invoke-Step -Name 'agent_api_flow' -Action {
  $output = powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\test-agent-api.ps1 -BaseUrl $BaseUrl -WorkspaceId $WorkspaceId -UserId $UserId 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) { throw $output }
  'agent api flow ok'
}

Invoke-Step -Name 'crm_meta' -Action {
  $response = Invoke-Json -Method Get -Uri "$BaseUrl/api/deals/meta" -Headers $headers
  if ($response.stages.Count -lt 5) { throw 'crm meta incomplete' }
  "stages=$($response.stages.Count)"
}

Invoke-Step -Name 'approvals_queue' -Action {
  $response = Invoke-Json -Method Get -Uri "$BaseUrl/api/agents/approvals" -Headers $headers
  "approvals=$($response.approvals.Count)"
}

$summary = [pscustomobject]@{
  generated_at = (Get-Date).ToString('s')
  ok = ($results | Where-Object { -not $_.ok }).Count -eq 0
  checks = $results
}

$summary | ConvertTo-Json -Depth 6
if (-not $summary.ok) {
  exit 1
}
