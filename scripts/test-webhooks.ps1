param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$WorkspaceId = "00000000-0000-0000-0000-000000000001",
  [string]$FbrLeadsSecret = "replace-with-fbr-leads-secret",
  [string]$FbrDevSecret = "replace-with-fbr-dev-secret",
  [string]$FbrSuporteSecret = "replace-with-fbr-suporte-secret"
)

function Wait-ForHealth {
  param([string]$HealthUrl)
  for ($i = 0; $i -lt 20; $i++) {
    try {
      $response = Invoke-RestMethod -Uri $HealthUrl -Method Get -TimeoutSec 3
      if ($response.status -eq 'ok') { return }
    } catch { Start-Sleep -Seconds 1 }
  }
  throw "Backend did not become healthy in time."
}

Wait-ForHealth -HealthUrl "$BaseUrl/health"
Write-Output "Testing FBR-Leads webhook..."
powershell -ExecutionPolicy Bypass -File .\scripts\test-fbr-leads-webhook.ps1 -BaseUrl $BaseUrl -WorkspaceId $WorkspaceId -FbrLeadsSecret $FbrLeadsSecret
Write-Output "Testing FBR-Dev webhook..."
powershell -ExecutionPolicy Bypass -File .\scripts\test-fbr-dev-webhook.ps1 -BaseUrl $BaseUrl -WorkspaceId $WorkspaceId -FbrDevSecret $FbrDevSecret
Write-Output "Testing FBR-Suporte webhook..."
powershell -ExecutionPolicy Bypass -File .\scripts\test-fbr-suporte-webhook.ps1 -BaseUrl $BaseUrl -WorkspaceId $WorkspaceId -FbrSuporteSecret $FbrSuporteSecret
