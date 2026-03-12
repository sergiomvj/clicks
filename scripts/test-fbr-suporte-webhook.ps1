param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$WorkspaceId = "00000000-0000-0000-0000-000000000001",
  [string]$FbrSuporteSecret = "replace-with-fbr-suporte-secret"
)

function Get-HmacSignature {
  param([string]$Body, [string]$Secret)
  $hmac = [System.Security.Cryptography.HMACSHA256]::new([System.Text.Encoding]::UTF8.GetBytes($Secret))
  $hash = $hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Body))
  return "sha256=" + ([System.BitConverter]::ToString($hash).Replace("-", "").ToLowerInvariant())
}

$body = @{
  workspace_id = $WorkspaceId
  external_reference = "suporte-001"
  lead_name = "Lead Suporte Teste"
  company_name = "Empresa Suporte"
  email = "suporte@empresa.com"
  phone = "+5511888888888"
  priority = "high"
  source_system = "1FBR-Suporte"
  notes = "Lead de teste vindo do suporte"
  metadata = @{ source = "script"; queue = "upgrade" }
} | ConvertTo-Json -Depth 10

$signature = Get-HmacSignature -Body $body -Secret $FbrSuporteSecret
Invoke-RestMethod -Uri "$BaseUrl/api/v1/suporte/handoff/webhook" -Method Post -ContentType "application/json" -Headers @{ "X-Signature" = $signature } -Body $body | ConvertTo-Json -Depth 10
