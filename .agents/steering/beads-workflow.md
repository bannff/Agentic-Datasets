---
inclusion: manual
---
# Beads Workflow & Shell Safety

Full reference for `bd` (beads) issue tracking and non-interactive shell commands.

## Quick Reference

```bash
bd ready --json           # Find available work
bd show <id>              # View issue details
bd update <id> --claim    # Claim work atomically
bd close <id> --reason "" # Complete work
bd sync                   # Sync with git
```

## Non-Interactive Shell Commands

ALWAYS use non-interactive flags to avoid hanging on confirmation prompts:

```bash
cp -f source dest         # NOT: cp source dest
mv -f source dest         # NOT: mv source dest
rm -f file                # NOT: rm file
rm -rf directory          # NOT: rm -r directory
```

## Agent Workflow

1. `bd ready` → find unblocked work
2. `bd update <id> --claim` → claim atomically
3. Work on it
4. `bd close <id> --reason "Done"`

## Session Completion

Work is NOT complete until `git push` succeeds.

1. File issues for remaining work.
2. Run quality gates (ruff, mypy, pytest).
3. Push: `git pull --rebase && bd sync && git push`.
