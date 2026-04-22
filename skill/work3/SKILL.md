---
name: work3
description: Start the workking Nepal Instagram discovery runner for Bagmati Province with /work3.
user-invocable: true
---

# Work3

`work3` starts the shared `workking` runner locked to `Bagmati Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Bagmati Province" --trigger-command "/work3"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
