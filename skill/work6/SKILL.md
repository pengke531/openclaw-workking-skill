---
name: work6
description: Start the full Nepal Instagram creator discovery workflow for Karnali Province with /work6.
user-invocable: true
---

# Work6

`work6` runs the full `workking` workflow locked to `Karnali Province`.

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
python {baseDir}/../workking/scripts/workking_runner.py start --province "Karnali Province" --trigger-command "/work6"
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
   The search page is only for surfacing a candidate. Before any verification, open the candidate's Instagram personal profile page using this sequence: canonical profile URL first if already surfaced, then `https://www.instagram.com/<handle>/`, then `https://instagram.com/<handle>/`.
   If one profile URL variant fails, try the next variant immediately. Do not use search pages, posts, reels, or location pages as follower evidence.
   If all profile-page variants fail, or the page is blocked by login, checkpoint, suspension, challenge, timeout, or blank browser load, treat that attempt as page-open failure, do not guess follower evidence, and move on.
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
   - `trigger_command = "/work6"`
   - `last_active_province = "Karnali Province"`
   - `candidate_cooldown_seconds = 300`
   - `max_candidate_searches = 50`

Required creator fields:

- `creator_name`
- `profile_url`
- `followers`
- `status`
- `updated_at`

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
