param(
  [string]$TargetRoot = "$HOME\\.openclaw",
  [string]$AgentId = "main"
)

$ErrorActionPreference = "Stop"

$required = @(
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking1") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking2") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking3") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking4") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking5") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking6") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking7") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "work1") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "work2") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "work3") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "work4") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "work5") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "work6") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "work7") "SKILL.md"),
  (Join-Path (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking") "scripts") "workking_runner.py"),
  (Join-Path (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking") "scripts") "workking_store.py")
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
if (-not ($config.agents.list -is [System.Array]) -or $config.agents.list.Count -eq 0) {
  throw "no patchable agents found in $configPath"
}
foreach ($item in $config.agents.list) {
  if (-not ($item.tools.alsoAllow -contains "exec")) {
    throw "agent '$($item.id)' is still missing exec in tools.alsoAllow"
  }
}

$runtimeAgent = $null
foreach ($item in $config.agents.list) {
  if ($item.id -eq "workking-runtime" -or $item.name -eq "workking-runtime") {
    $runtimeAgent = $item
    break
  }
}
if ($null -eq $runtimeAgent) {
  throw "missing runtime agent 'workking-runtime' in $configPath"
}

$env:OPENCLAW_STATE_DIR = $TargetRoot
python (Join-Path (Join-Path (Join-Path (Join-Path $TargetRoot "skills") "workking") "scripts") "workking_store.py") status | Out-Host
