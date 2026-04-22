---
name: work2
description: Start the workking Nepal Instagram discovery runner for Madhesh Province with /work2.
user-invocable: true
---

# Work2

`work2` starts the shared `workking` runner locked to `Madhesh Province`.

- Do not ask the user to type another command.
- Do not ask for confirmation.
- Do not print the shell command without executing it.
- Run only this command:

```powershell
python {baseDir}/../workking/scripts/workking_runner.py start --province "Madhesh Province" --trigger-command "/work2"
```

Use `/workking status`, `/workking stop`, and `/workking export` for control commands.
