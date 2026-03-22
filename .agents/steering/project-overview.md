# Project Overview

`datasets` provides pipelines to build sophisticated, multi-turn, agentic training data.

## Architecture

1.  **Orchestrator**: Driven by `cli.py` and YAML configuration files, manages the execution of stages.
2.  **Stages (`src/agentic_datasets/stages/`)**: Discrete pipeline steps like `S2M` (Single-to-Multi) or `APIGenMT`.
3.  **Data Models (`src/agentic_datasets/schemas/`)**: Strict Pydantic v2 schemas defining conversations and tool calls.
4.  **Utilities**: Shared tools for chunking and formatting.

## Goal
To maintain a modular, highly scalable repository enforcing strict LOC limits and clean architecture.
