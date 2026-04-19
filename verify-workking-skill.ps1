param(
  [string]$TargetRoot = "$HOME\\.openclaw"
)

$ErrorActionPreference = "Stop"

$skillRoot = Join-Path (Join-Path $TargetRoot "skills") "workking"
$required = @(
  (Join-Path $skillRoot "SKILL.md"),
  (Join-Path (Join-Path $skillRoot "scripts") "workking_store.py")
)

foreach ($path in $required) {
  if (-not (Test-Path $path)) {
    throw "missing required file: $path"
  }
}

python (Join-Path (Join-Path $skillRoot "scripts") "workking_store.py") status | Out-Host
