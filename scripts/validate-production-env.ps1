param(
  [string]$EnvFile = '.env.production'
)

if (-not (Test-Path $EnvFile)) {
  throw "Arquivo $EnvFile nao encontrado."
}

$requiredKeys = @(
  'APP_ENV',
  'APP_DOMAIN',
  'DATABASE_URL_ASYNCPG',
  'REDIS_URL',
  'SESSION_SECRET',
  'JWT_SECRET',
  'OPENCLAW_AGENT_JWT_SECRET',
  'BACKEND_URL',
  'NEXT_PUBLIC_WS_URL',
  'DASHBOARD_EMAIL',
  'DASHBOARD_PASSWORD',
  'DASHBOARD_USER_ID',
  'DASHBOARD_WORKSPACE_ID',
  'OPENCLAW_GATEWAY_URL',
  'FBR_LEADS_WEBHOOK_SECRET',
  'FBR_DEV_WEBHOOK_SECRET',
  'FBR_SUPORTE_WEBHOOK_SECRET',
  'FBR_LEADS_API_URL',
  'FBR_DEV_API_URL',
  'FBR_SUPORTE_API_URL',
  'GRAFANA_ADMIN_USER',
  'GRAFANA_ADMIN_PASSWORD'
)

$values = @{}
Get-Content $EnvFile | ForEach-Object {
  if (-not $_ -or $_.Trim().StartsWith('#') -or $_ -notmatch '=') {
    return
  }
  $parts = $_.Split('=', 2)
  $values[$parts[0].Trim()] = $parts[1].Trim()
}

$results = foreach ($key in $requiredKeys) {
  $value = $values[$key]
  $isPresent = -not [string]::IsNullOrWhiteSpace($value)
  $looksPlaceholder = $isPresent -and ($value -match 'replace-me|replace-with|change-me-now|USER:PASSWORD@HOST|^$')

  [pscustomobject]@{
    key = $key
    present = $isPresent
    placeholder = $looksPlaceholder
    ok = $isPresent -and -not $looksPlaceholder
  }
}

$results | ConvertTo-Json -Depth 5
if (($results | Where-Object { -not $_.ok }).Count -gt 0) {
  exit 1
}
