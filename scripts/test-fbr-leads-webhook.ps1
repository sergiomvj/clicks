param(
  [string]$BaseUrl = "http://localhost:8000",
  [string]$WorkspaceId = "00000000-0000-0000-0000-000000000001",
  [string]$FbrLeadsSecret = "replace-with-fbr-leads-secret"
)

function Get-HmacSignature {
  param([string]$Body, [string]$Secret)
  $hmac = [System.Security.Cryptography.HMACSHA256]::new([System.Text.Encoding]::UTF8.GetBytes($Secret))
  $hash = $hmac.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Body))
  return "sha256=" + ([System.BitConverter]::ToString($hash).Replace("-", "").ToLowerInvariant())
}

$body = @{
  workspace_id = $WorkspaceId
  external_reference = "lead-test-001"
  source_system = "1FBR-Leads"
  lead_name = "Teste Lead FBR-Leads"
  email = "teste@empresa.com"
  phone = "+5511999999999"
  whatsapp = "+5511999999999"
  company_name = "Empresa Teste"
  origin = "similarity_outreach"
  score = 88
  temperature = "warm"
  virtual_manager_slug = "gestor-comercial-1"
  notes = "Lead de teste automatizado"
  metadata = @{ source = "script"; campaign_name = "similarity-campaign" }
  handoff_payload = @{ source_pipeline = "cold_to_warm"; qualification_reason = "engajou com outreach" }
} | ConvertTo-Json -Depth 10

$signature = Get-HmacSignature -Body $body -Secret $FbrLeadsSecret
Invoke-RestMethod -Uri "$BaseUrl/api/v1/leads/webhook" -Method Post -ContentType "application/json" -Headers @{ "X-Signature" = $signature } -Body $body | ConvertTo-Json -Depth 10
