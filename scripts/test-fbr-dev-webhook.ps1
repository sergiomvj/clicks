param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$WorkspaceId = "00000000-0000-0000-0000-000000000001",
  [string]$FbrDevSecret = "replace-with-fbr-dev-secret"
)

function Get-HmacSignature {
  param([string]$Body, [string]$Secret)
  $hmac = [System.Security.Cryptography.HMACSHA256]::new([System.Text.Encoding]::UTF8.GetBytes($Secret))
  $hash = $hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Body))
  return "sha256=" + ([System.BitConverter]::ToString($hash).Replace("-", "").ToLowerInvariant())
}

$body = @{
  workspace_id = $WorkspaceId
  event_type = "lead_created"
  title = "Novo lead vindo do produto"
  description = "Evento de teste vindo do script local"
  external_reference = "dev-event-001"
  lead_name = "Lead Produto"
  email = "produto@empresa.com"
  phone = "+551188887777"
  source_system = "1FBR-Dev"
  metadata = @{ source = "script"; product = "FBR-App"; screen = "pricing" }
} | ConvertTo-Json -Depth 10

$signature = Get-HmacSignature -Body $body -Secret $FbrDevSecret
Invoke-RestMethod -Uri "$BaseUrl/api/v1/dev/events/webhook" -Method Post -ContentType "application/json" -Headers @{ "X-Signature" = $signature } -Body $body | ConvertTo-Json -Depth 10
