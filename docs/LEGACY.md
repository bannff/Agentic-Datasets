# Legacy directories

The following directories are deprecated and no new code should reference them:

- `PyScience/`
- `cybersecurity_datasets/`
- `cybersecurity_finetuned_models/`

Status: They are .gitignored. Relevant content will be migrated into:

- `examples/` for small, runnable samples
- `src/agentic_datasets/` as proper modules (where applicable)
- Hugging Face datasets for large artifacts

Anything duplicate or out-of-scope will be removed during cleanup. A short log of migrations/deletions will be maintained in this file.

## Migration log

- Archived on YYYY-MM-DD:
	- `PyScience/` -> `archive/legacy/PyScience/`
	- `cybersecurity_datasets/` -> `archive/legacy/cybersecurity_datasets/`
	- `cybersecurity_finetuned_models/` -> `archive/legacy/cybersecurity_finetuned_models/`
  
	See `archive/legacy/MIGRATION_LOG.txt` for script output.