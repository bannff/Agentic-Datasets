# Contributing to Agentic Datasets

Welcome! We're excited to have you contribute to the future of AI training data.

## Working with AI Agents

This repository is optimized for **AI-Native Development**. 
- See [AGENTS.md](AGENTS.md) for specialized agent instructions.
- We use [Beads](.beads/README.md) for local, git-native issue tracking.
- We use GitHub Issues, Discussions, and Projects for public coordination.

## Development Setup

1. Clone the repository.
2. Create a virtual environment: `python -m venv .venv`
3. Install in editable mode: `pip install -e .[dev]`
4. Install pre-commit hooks: `pre-commit install`

## Workflow

1. **Find Work**: Check [GitHub Issues](https://github.com/danielrodrigo/datasets/issues) or [Beads](.beads/README.md).
2. **Open a Discussion**: For new features or significant changes, start a [Discussion](https://github.com/danielrodrigo/datasets/discussions).
3. **Create a Branch**: `git checkout -b feature/your-feature-name`.
4. **Link to Issue**: Ensure your PR links to a relevant issue.
5. **Quality Gates**: Ensure `ruff`, `mypy`, and `pytest` pass.

## Code Style

- Follow the [Strands-first](.kiro/steering/datasets.md) patterns.
- Keep files under 150 lines.
- Use Pydantic v2 for data schemas.

---
**Thank you for contributing!**
