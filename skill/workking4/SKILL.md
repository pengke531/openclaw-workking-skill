---
name: workking4
description: Start the workking Nepal Instagram discovery runner for Gandaki Province with /workking4.
user-invocable: true
---

# Workking4

`workking4` starts the shared `workking` runner locked to `Gandaki Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Gandaki Province" --trigger-command "/workking4"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
