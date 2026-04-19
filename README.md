# OpenClaw Workking Skill

`workking` is a standalone OpenClaw skill package.

It is not tied to any special agent topology. One agent is enough.

After install, a user can start it directly with:

```text
/workking
```

It is designed for:

- Instagram only
- Nepal only
- personal creators only
- followers `>= 100000`
- local file-based dedup and persistence
- provider rotation on each launch
- fast provider health probes before each cycle
- automatic provider skip when unhealthy
- exactly 8 candidates per cycle
- immediate save on every new qualified creator
- automatic fresh-cycle restart after each new qualified creator
- 15 minute per-cycle cap
- 30 minute no-new-creator stop rule

## Install

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\install-workking-skill.ps1
```

Bash:

```bash
./install-workking-skill.sh
```

## Use

Open a new OpenClaw session, then run:

```text
/workking
```

Other commands:

```text
/workking status
/workking stop
/workking export
```

## Installed path

- `~/.openclaw/skills/workking/SKILL.md`
- `~/.openclaw/skills/workking/scripts/workking_runner.py`
- `~/.openclaw/skills/workking/scripts/workking_store.py`

## Local data path

- `~/.openclaw/data/workking/instagram-nepal/`
