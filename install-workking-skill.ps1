param(
  [string]$TargetRoot = "$HOME\\.openclaw",
  [string]$AgentId = "main",
  [switch]$WithConfig
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillsSourceRoot = Join-Path $repoRoot "skill"
$skillDirs = Get-ChildItem -Directory $skillsSourceRoot | Where-Object { $_.Name -like "workking*" }
$patchScript = Join-Path $repoRoot "scripts\\patch_openclaw_exec.py"
$configSource = Join-Path $skillsSourceRoot "workking\\references\\workking.config.example.json"
$configRoot = Join-Path (Join-Path $TargetRoot "data") "workking"
$configTarget = Join-Path $configRoot "workking.config.json"

if (-not (Test-Path $skillsSourceRoot)) {
  throw "missing skills source root: $skillsSourceRoot"
}

if (-not $skillDirs) {
  throw "no workking skill directories found under: $skillsSourceRoot"
}

New-Item -ItemType Directory -Force -Path (Join-Path $TargetRoot "skills") | Out-Null
foreach ($dir in $skillDirs) {
  $skillTarget = Join-Path (Join-Path $TargetRoot "skills") $dir.Name
  if (Test-Path $skillTarget) {
    Remove-Item -Recurse -Force $skillTarget
  }
  Copy-Item -Recurse -Force $dir.FullName $skillTarget
  Write-Host "[workking] installed skill:" $dir.Name "->" $skillTarget
}

if ($WithConfig) {
  New-Item -ItemType Directory -Force -Path $configRoot | Out-Null
  if ((Test-Path $configSource) -and -not (Test-Path $configTarget)) {
    Copy-Item -Force $configSource $configTarget
  }
}

if (Test-Path $patchScript) {
  $patchResult = python $patchScript --target-root $TargetRoot --agent-id $AgentId
  Write-Host "[workking] exec patch:" $patchResult
}

Write-Host "[workking] next: start a new OpenClaw session, then run /workking1 through /workking7"
if ($WithConfig) {
  Write-Host "[workking] optional config copied to: $configTarget"
}
