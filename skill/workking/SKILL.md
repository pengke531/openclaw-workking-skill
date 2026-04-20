---
name: workking
description: Start or control the workking Instagram Nepal discovery runner with /workking. Use this skill whenever the user wants the persistent Instagram-only discovery workflow, local dedup, provider rotation, or file-based creator storage.
user-invocable: true
---

# Workking

`workking` is a single-agent OpenClaw skill for long-running Instagram creator
discovery in Nepal.

Supported commands:

- `/workking`
- `/workking start`
- `/workking status`
- `/workking stop`
- `/workking export`

Treat omitted input as `start`.

## Non-negotiable rules

- If this skill is active in the current turn, the user has already invoked it.
- Do not ask the user to type `/workking` again.
- Do not ask "Should I proceed?".
- Do not print a shell command and wait for confirmation.
- Run the requested script command immediately in the same turn.

## Script paths

Only these script paths are valid:

- `{baseDir}/scripts/workking_runner.py`
- `{baseDir}/scripts/workking_store.py`

Never invent alternate paths under `~/.openclaw/data/workking/`.

## Exact commands

Use only direct script commands like these:

```powershell
python {baseDir}/scripts/workking_runner.py start
python {baseDir}/scripts/workking_runner.py status
python {baseDir}/scripts/workking_runner.py stop
python {baseDir}/scripts/workking_runner.py export --format markdown
python {baseDir}/scripts/workking_store.py status
```

Never use:

- `python -c`
- inline Python
- `cd ... && ...`
- ad-hoc subprocess wrappers

## Start behavior

For `/workking` or `/workking start`, run:

```powershell
python {baseDir}/scripts/workking_runner.py start
```

Return only the actual exec result or a short runner summary.

## Status behavior

For `/workking status`, run:

```powershell
python {baseDir}/scripts/workking_runner.py status
```

## Stop behavior

For `/workking stop`, run:

```powershell
python {baseDir}/scripts/workking_runner.py stop
```

## Export behavior

For `/workking export`, run:

```powershell
python {baseDir}/scripts/workking_runner.py export --format markdown
```

## Workflow constraints

The runner and store scripts are the source of truth. They enforce the workflow.
Do not replace them with manual browsing or improvised shell logic.

Current workflow requirements:

- store every newly qualified non-duplicate creator immediately
- always read the local registry first and ignore existing creators
- rotate providers on each new run and skip unhealthy providers automatically
- run for up to 3 hours total
- rotate Nepal province focus every 30 minutes
- keep Instagram-only, Nepal-only, personal-creator-only, `followers >= 100000`
- keep `EVIDENCE_GAP` as a hard block
