param(
  [string]$TargetRoot = "$HOME\\.openclaw"
)

$ErrorActionPreference = "Stop"
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\\install-workking-skill.ps1" -TargetRoot $TargetRoot
