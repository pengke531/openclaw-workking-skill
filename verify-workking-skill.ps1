param(
  [string]$TargetRoot = "$HOME\\.openclaw",
  [string]$AgentId = "main"
)

$ErrorActionPreference = "Stop"

$skillRoot = Join-Path (Join-Path $TargetRoot "skills") "workking"
$required = @(
  (Join-Path $skillRoot "SKILL.md"),
  (Join-Path (Join-Path $skillRoot "scripts") "workking_runner.py"),
  (Join-Path (Join-Path $skillRoot "scripts") "workking_store.py")
)

foreach ($path in $required) {
  if (-not (Test-Path $path)) {
    throw "missing required file: $path"
  }
}

$configPath = Join-Path $TargetRoot "openclaw.json"
if (-not (Test-Path $configPath)) {
  throw "missing openclaw config: $configPath"
}

$config = Get-Content -Raw $configPath | ConvertFrom-Json
$agent = $null
foreach ($item in $config.agents.list) {
  if ($item.id -eq $AgentId -or $item.name -eq $AgentId) {
    $agent = $item
    break
  }
}
if ($null -eq $agent -and $config.agents.list.Count -gt 0) {
  $agent = $config.agents.list[0]
}
if ($null -eq $agent) {
  throw "no patchable agent found in $configPath"
}
if (-not ($agent.tools.alsoAllow -contains "exec")) {
  throw "agent '$($agent.id)' is still missing exec in tools.alsoAllow"
}

$env:OPENCLAW_STATE_DIR = $TargetRoot
python (Join-Path (Join-Path $skillRoot "scripts") "workking_store.py") status | Out-Host
