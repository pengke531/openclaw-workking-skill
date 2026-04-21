---
name: workking5
description: Start the workking Nepal Instagram discovery runner for Lumbini Province with /workking5.
user-invocable: true
---

# Workking5

`workking5` starts the shared `workking` runner locked to `Lumbini Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Lumbini Province" --trigger-command "/workking5"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
