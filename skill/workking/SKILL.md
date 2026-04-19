---
name: workking
description: Start a long-running Instagram creator discovery workflow for Nepal using /workking. Use this skill whenever the user wants persistent Instagram-only scouting, qualification, local dedup, file-based storage, provider rotation, or stop-rule-controlled creator discovery. This skill is single-agent friendly and does not depend on any special agent architecture.
user-invocable: true
---

# Workking

`workking` is a generic OpenClaw skill for long-running Instagram creator
discovery with strict local state.

Direct command:

- `/workking`

Supported forms:

- `/workking`
- `/workking start`
- `/workking status`
- `/workking stop`
- `/workking export`

Treat omitted input as `start`.

## Scope

This skill is only for:

- Instagram
- Nepal
- personal creators only
- followers `>= 100000`

Hard gate:

- if geography, personal identity, or followers are not clear enough, classify
  the result as `EVIDENCE_GAP`

Never register first and repair later.

## Data root

All local state lives under:

`~/.openclaw/data/workking/instagram-nepal/`

Important files:

- `registry/index.json`
- `registry/creators/*.json`
- `evidence/reviews/*.json`
- `runtime/state.json`
- `exports/pending_submissions.json`

## Command handling

### `/workking` or `/workking start`

1. Use `exec` to start the deterministic runner:

```powershell
python {baseDir}/scripts/workking_runner.py start
```

2. Return only the runner summary.

The runner is the hard control layer. It enforces:

- every cycle searches exactly 8 candidates before verification
- every cycle must stay under 15 minutes
- if 30 minutes pass without a new unique qualified creator, the run stops
- every time one qualified and non-duplicate creator is found, it is stored
  immediately and the runner launches a fresh cycle automatically
- before every cycle, the local registry index is read and used as the ignore
  list
- every new start rotates the preferred provider automatically

Provider policy:

- if one provider is down, rate-limited, or noisy, move to the next provider
- do not block the whole run on one crawler
- next launch must rotate the preferred provider automatically

Use any available tools in this priority order:

1. `agent-reach`
2. `autoglm-browser-agent`
3. `search` or `tavily`
4. direct web search or profile pages

If the host has API keys configured, prefer these external providers in the
same order returned by `provider_order`:

- `apify`
- `brightdata`

### Qualification workflow

For each candidate, verify all of:

1. geography is Nepal
2. account is clearly a person / creator / influencer / public figure / personal blogger
3. followers on the Instagram profile are at least `100000`

If qualified:

1. create a JSON payload file under:

`~/.openclaw/data/workking/instagram-nepal/tmp/`

2. use:

```powershell
python {baseDir}/scripts/workking_store.py upsert-qualified --payload <payload.json>
```

If duplicate, screened fail, or evidence gap:

```powershell
python {baseDir}/scripts/workking_store.py record-review --payload <payload.json>
```

## Payload schema

Use this exact JSON shape for both commands:

```json
{
  "creator_name": "Display Name",
  "profile_url": "https://www.instagram.com/example/",
  "followers": "154K",
  "decision": "QUALIFIED",
  "geography_status": "PASS",
  "persona_status": "PASS",
  "followers_status": "PASS",
  "geography_evidence": "Why Nepal is clear",
  "persona_evidence": "Why this is a personal creator",
  "followers_evidence": "What follower value is shown on profile",
  "evidence_summary": "Short summary",
  "evidence_refs": ["optional source notes"]
}
```

Allowed decisions:

- `QUALIFIED`
- `DUPLICATE`
- `SCREENED_FAIL`
- `EVIDENCE_GAP`

## Stop handling

When no new unique qualified creator has been stored for 30 minutes:

```powershell
python {baseDir}/scripts/workking_store.py finish-run --stop-reason "no new unique qualified creator for 30 minutes"
```

Then stop cleanly and report a short summary only.

If the user runs `/workking stop`:

```powershell
python {baseDir}/scripts/workking_runner.py stop
```

### `/workking status`

```powershell
python {baseDir}/scripts/workking_runner.py status
```

### `/workking export`

```powershell
python {baseDir}/scripts/workking_runner.py export --format markdown
```

## Important behavior

- single-agent only; do not assume managers, subagents, or OPC roles
- always read local registry first
- ignore already stored creators during search
- store each newly qualified creator immediately
- after each new qualified creator, restart the cycle with a fresh search
- keep chat output short; the files are the source of truth
