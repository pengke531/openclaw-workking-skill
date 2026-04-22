---
name: work7
description: Start the workking Nepal Instagram discovery runner for Sudurpashchim Province with /work7.
user-invocable: true
---

# Work7

`work7` starts the shared `workking` runner locked to `Sudurpashchim Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Sudurpashchim Province" --trigger-command "/work7"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
