param(
  [string]$TargetRoot = "$HOME\\.openclaw",
  [string]$AgentId = "main"
)

$ErrorActionPreference = "Stop"
powershell -ExecutionPolicy Bypass -File "$PSScriptRoot\\install-workking-skill.ps1" -TargetRoot $TargetRoot -AgentId $AgentId
