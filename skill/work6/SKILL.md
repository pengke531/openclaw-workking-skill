---
name: work6
description: Start the workking Nepal Instagram discovery runner for Karnali Province with /work6.
user-invocable: true
---

# Work6

`work6` starts the shared `workking` runner locked to `Karnali Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Karnali Province" --trigger-command "/work6"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
