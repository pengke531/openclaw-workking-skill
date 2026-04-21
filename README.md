# OpenClaw Workking Skill

`workking` is a standalone OpenClaw skill package.

It is not tied to any special agent topology. One agent is enough.

The installer also patches the target OpenClaw agent so `/workking` can launch
its Python runner with `exec`. By default it patches the `main` agent.

After install, a user can start it directly with:

```text
/workking1
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
- `openclaw-core` builtin fallback for plain OpenClaw installs
- bounded candidate cap per province window
- per-candidate cooldown to reduce creator lookup frequency
- immediate save on every new qualified creator
- automatic fresh-cycle restart after each new qualified creator
- up to 3 hour run window
- 3 hour no-new-creator stop rule
- fixed province start commands `/workking1` through `/workking7`

## Install

Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Patch a different agent:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1 -AgentId a02
```

Bash:

```bash
./install.sh
```

Patch a different agent:

```bash
AGENT_ID=a02 ./install.sh
```

## Use

Open a new OpenClaw session, then run:

```text
/workking1
```

Other commands:

```text
/workking status
/workking stop
/workking export
```

Fixed province commands:

```text
/workking1  # Koshi Province
/workking2  # Madhesh Province
/workking3  # Bagmati Province
/workking4  # Gandaki Province
/workking5  # Lumbini Province
/workking6  # Karnali Province
/workking7  # Sudurpashchim Province
```

## Installed path

- `~/.openclaw/skills/workking/SKILL.md`
- `~/.openclaw/skills/workking1/SKILL.md`
- `~/.openclaw/skills/workking2/SKILL.md`
- `~/.openclaw/skills/workking3/SKILL.md`
- `~/.openclaw/skills/workking4/SKILL.md`
- `~/.openclaw/skills/workking5/SKILL.md`
- `~/.openclaw/skills/workking6/SKILL.md`
- `~/.openclaw/skills/workking7/SKILL.md`
- `~/.openclaw/skills/workking/scripts/workking_runner.py`
- `~/.openclaw/skills/workking/scripts/workking_store.py`

Only the `~/.openclaw/skills/workking/scripts/` directory contains executable
Python scripts. The `~/.openclaw/data/workking/` tree is for runtime data only.
Do not create or expect runner scripts under the data directory.

## Local data path

- `~/.openclaw/data/workking/instagram-nepal/`
- `~/.openclaw/data/workking/workking.config.json`

## Configuration

No configuration is required for the default install.

Only if someone wants to customize provider order or timeouts, they can copy the
example config manually:

- `~/.openclaw/data/workking/workking.config.json`

Example source:

- `skill/workking/references/workking.config.example.json`

## Province commands

The fixed province command mapping is:

1. `Koshi Province`
2. `Madhesh Province`
3. `Bagmati Province`
4. `Gandaki Province`
5. `Lumbini Province`
6. `Karnali Province`
7. `Sudurpashchim Province`

Default pacing:

- `batch_size`: `5`
- `candidate_cooldown_seconds`: `300`
- `provider_retry_cooldown_seconds`: `30`
- `max_run_seconds`: `10800`

## Current command path

The primary start commands after this fix are:

```text
/workking1
/workking2
/workking3
/workking4
/workking5
/workking6
/workking7
```
