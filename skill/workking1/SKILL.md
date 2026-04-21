---
name: workking1
description: Start the workking Nepal Instagram discovery runner for Koshi Province with /workking1.
user-invocable: true
---

# Workking1

`workking1` starts the shared `workking` runner locked to `Koshi Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Koshi Province" --trigger-command "/workking1"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
