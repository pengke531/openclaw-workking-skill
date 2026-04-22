---
name: workking6
description: Start the full Nepal Instagram creator discovery workflow for Karnali Province with /workking6.
user-invocable: true
---

# Workking6

`workking6` runs the full `workking` workflow locked to `Karnali Province`.

## Non-negotiable rules

- The user has already invoked this command.
- Do not ask for confirmation.
- Do not tell the user to run a terminal command manually.
- Do not stop at "exec is unavailable".
- If `exec` is available, start the runner.
- If `exec` is unavailable or the runner cannot be launched, continue the same workflow directly in this session with the available tools.

## Primary start command

Try this first:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Karnali Province" --trigger-command "/workking6"
```

## Direct fallback workflow

If the command above cannot be executed, continue manually in this turn.

Current province scope:

- `Karnali Province`

Hard requirements:

- Instagram only
- Nepal only
- province scope must stay `Karnali Province`
- personal creator only
- followers `>= 100000`
- unclear geography, persona, or followers = `EVIDENCE_GAP`
- never register first and fix later

Local data root:

- `~/.openclaw/data/workking/instagram-nepal/`

Files to use:

- `registry/index.json`
- `registry/creators/*.json`
- `evidence/reviews/*.json`
- `runtime/state.json`
- `exports/pending_submissions.json`

Direct workflow steps:

1. Read `registry/index.json` first and ignore every stored Instagram handle and stored profile URL.
2. Search Instagram only within `Karnali Province`. Do not search Nepal broadly and filter later.
3. Process exactly one candidate in this invocation when operating without the runner.
4. Verify geography, persona, and follower evidence.
5. If qualified and non-duplicate, immediately update:
   - `registry/creators/*.json`
   - `registry/index.json`
   - `evidence/reviews/*.json`
   - `exports/pending_submissions.json`
6. If duplicate, update only the existing creator record followers and `updated_at`, and write an evidence review record.
7. If screened fail or `EVIDENCE_GAP`, write an evidence review record only.
8. Keep the run state under `runtime/state.json` consistent with:
   - `trigger_command = "/workking6"`
   - `last_active_province = "Karnali Province"`
   - `candidate_cooldown_seconds = 180`
   - `max_candidate_searches = 50`

Required creator fields:

- `creator_name`
- `profile_url`
- `followers`
- `status`
- `updated_at`

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
