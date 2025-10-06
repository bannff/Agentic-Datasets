#!/bin/bash
# Quick Black formatter fixer
FILES=(
  "src/agentic_datasets/config.py"
  "src/agentic_datasets/cli.py"
  "src/agentic_datasets/orchestrators/strands.py"
  "src/agentic_datasets/pipeline_config.py"
  "src/agentic_datasets/stages/base.py"
  "src/agentic_datasets/schemas/messages.py"
  "src/agentic_datasets/stages/s2m.py"
  "tests/test_catalog.py"
  "src/agentic_datasets/transforms/chunking.py"
  "tests/test_pipeline_config.py"
  "tests/test_stages_pipeline.py"
)

for file in "${FILES[@]}"; do
  echo "Formatting $file..."
  cat "$file" | python3 -c "
import sys
import black
from black import Mode

code = sys.stdin.read()
try:
    formatted = black.format_str(code, mode=Mode(line_length=100))
    print(formatted, end='')
except Exception as e:
    print(code, end='', file=sys.stderr)
" > "${file}.tmp" && mv "${file}.tmp" "$file"
done
