param(
  [string]$TargetRoot = "$HOME\\.openclaw",
  [string]$AgentId = "main",
  [switch]$WithConfig
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillSource = Join-Path $repoRoot "skill\\workking"
$skillTarget = Join-Path $TargetRoot "skills\\workking"
$patchScript = Join-Path $repoRoot "scripts\\patch_openclaw_exec.py"
$configSource = Join-Path $skillSource "references\\workking.config.example.json"
$configRoot = Join-Path (Join-Path $TargetRoot "data") "workking"
$configTarget = Join-Path $configRoot "workking.config.json"

if (-not (Test-Path $skillSource)) {
  throw "missing skill source: $skillSource"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $skillTarget) | Out-Null
if (Test-Path $skillTarget) {
  Remove-Item -Recurse -Force $skillTarget
}
Copy-Item -Recurse -Force $skillSource $skillTarget
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

Write-Host "[workking] installed to: $skillTarget"
Write-Host "[workking] next: start a new OpenClaw session, then run /workking"
if ($WithConfig) {
  Write-Host "[workking] optional config copied to: $configTarget"
}
