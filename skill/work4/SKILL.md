---
name: work4
description: Start the workking Nepal Instagram discovery runner for Gandaki Province with /work4.
user-invocable: true
---

# Work4

`work4` starts the shared `workking` runner locked to `Gandaki Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Gandaki Province" --trigger-command "/work4"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
