# Storage Layout

Default data root:

- `~/.openclaw/data/workking/instagram-nepal/`

Files:

- `registry/index.json`: dedup index by handle and profile URL
- `registry/creators/*.json`: qualified creators only
- `evidence/reviews/*.json`: every reviewed candidate, including duplicates and evidence gaps
- `runtime/state.json`: current run state and provider cursor
- `exports/pending_submissions.json`: simple three-column pending output source
- `tmp/*.json`: temporary payload files during a run
