param(
  [string]$TargetRoot = "$HOME\\.openclaw"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$skillSource = Join-Path $repoRoot "skill\\workking"
$skillTarget = Join-Path $TargetRoot "skills\\workking"

if (-not (Test-Path $skillSource)) {
  throw "missing skill source: $skillSource"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $skillTarget) | Out-Null
if (Test-Path $skillTarget) {
  Remove-Item -Recurse -Force $skillTarget
}
Copy-Item -Recurse -Force $skillSource $skillTarget

Write-Host "[workking] installed to: $skillTarget"
Write-Host "[workking] next: start a new OpenClaw session, then run /workking"
