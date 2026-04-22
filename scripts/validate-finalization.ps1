param(
  [string]$Root = "C:\Projetos\1FBR-Clicks"
)

$ErrorActionPreference = "Stop"

Write-Host "== FBR-CLICK | Validacao de finalizacao local =="

$requiredPaths = @(
  "$Root\prd\tasklist-alinhamento-conceito-original.md",
  "$Root\prd\status-alinhamento-conceito.md",
  "$Root\prd\matriz-alinhamento-conceito.md",
  "$Root\prd\plano-batches-finalizacao-algoritmico.md",
  "$Root\db\migrations\003_concept_alignment.sql",
  "$Root\db\migrations\004_operational_alignment.sql",
  "$Root\app\kpis\routes.py",
  "$Root\frontend\components\dashboard\KpiOverview.tsx"
)

foreach ($path in $requiredPaths) {
  if (-not (Test-Path $path)) {
    throw "Arquivo obrigatorio ausente: $path"
  }
}

$agentDirs = @(
  "$Root\agents\comercial-bot",
  "$Root\agents\report-bot",
  "$Root\agents\onboarding-bot",
  "$Root\agents\approval-bot",
  "$Root\agents\content-bot",
  "$Root\agents\ads-bot"
)

$requiredAgentFiles = @("SOUL.md", "IDENTITY.md", "TASKS.md", "AGENTS.md", "MEMORY.md", "TOOLS.md", "USER.md")

foreach ($agentDir in $agentDirs) {
  if (-not (Test-Path $agentDir)) {
    throw "Diretorio de agente ausente: $agentDir"
  }
  foreach ($file in $requiredAgentFiles) {
    $candidate = Join-Path $agentDir $file
    if (-not (Test-Path $candidate)) {
      throw "Arquivo obrigatorio ausente no agente: $candidate"
    }
  }
}

@'
import subprocess
import sys
from pathlib import Path

root = Path(r"C:\Projetos\1FBR-Clicks")
files = [
    root / "app" / "main.py",
    root / "app" / "core" / "llm.py",
    root / "app" / "core" / "security.py",
    root / "app" / "api" / "dependencies.py",
    root / "app" / "agents" / "service.py",
    root / "app" / "agents" / "routes.py",
    root / "app" / "agents" / "agent_api_routes.py",
    root / "app" / "kpis" / "routes.py",
    root / "app" / "tasks" / "schemas.py",
]
for file in files:
    subprocess.run([sys.executable, "-m", "py_compile", str(file)], check=True)
print("py_compile ok")
'@ | python -

Write-Host "Validacao estrutural concluida com sucesso."
