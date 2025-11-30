# LLM Provider Configuration

This document explains how to configure the LLM provider for the agentic-datasets pipeline.

## Quick Start

The pipeline uses **LiteLLM** to provide a unified interface to 100+ LLM providers. By default, it uses local Ollama.

### Default Configuration (Local Ollama)

```bash
# Install Ollama: https://ollama.com/download
ollama pull qwen3:8b

# Run pipeline with defaults
agentic-datasets run-config examples/pipeline.llm_powered.yaml
```

### Using Environment Variables

```bash
# Local Ollama (default)
export AGENTIC_LLM_MODEL="ollama/qwen3:8b"

# OpenAI
export AGENTIC_LLM_MODEL="openai/gpt-4o"
export OPENAI_API_KEY="sk-..."

# Anthropic
export AGENTIC_LLM_MODEL="anthropic/claude-4-sonnet-20250514"
export ANTHROPIC_API_KEY="sk-ant-..."

# AWS Bedrock
export AGENTIC_LLM_MODEL="bedrock/anthropic.claude-v2"
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

### Using YAML Configuration

```yaml
input: data/input.jsonl
output: data/output.jsonl

# Unified LLM configuration for all stages
llm:
  model: ollama/qwen3:8b  # or openai/gpt-4o, anthropic/claude-4-sonnet-20250514
  temperature: 0.7
  max_tokens: 4096
  # api_base: http://localhost:11434  # For custom Ollama host

stages:
  - name: agentinstruct
    params:
      k_variants: 2
      use_llm: true
  - name: s2m
    params:
      use_llm: true
  - name: apigenmt
    params:
      use_llm: true
      tools: [...]
  - name: reviewinstruct
    params:
      use_llm: true
```

## Supported Providers

| Provider | Model Format | Required Env Vars |
|----------|-------------|-------------------|
| Ollama (local) | `ollama/qwen3:8b`, `ollama/llama3.2` | None (or `OLLAMA_HOST`) |
| OpenAI | `openai/gpt-4o`, `openai/gpt-4o-mini` | `OPENAI_API_KEY` |
| Anthropic | `anthropic/claude-4-sonnet-20250514` | `ANTHROPIC_API_KEY` |
| AWS Bedrock | `bedrock/anthropic.claude-v2` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` |
| Together AI | `together_ai/mistralai/Mixtral-8x7B` | `TOGETHER_API_KEY` |
| Groq | `groq/llama2-70b-4096` | `GROQ_API_KEY` |
| Mistral | `mistral/mistral-medium` | `MISTRAL_API_KEY` |

See [LiteLLM docs](https://docs.litellm.ai/docs/providers) for 100+ more providers.

## Stage-Level Configuration

Each stage supports a `use_llm` parameter to enable/disable LLM reasoning:

```yaml
stages:
  - name: agentinstruct
    params:
      use_llm: true   # Use LLM for transformation (recommended)
      # use_llm: false  # Use simple templates (faster, lower quality)
```

## Disable LLM for Fast Testing

For quick testing without LLM calls:

```yaml
stages:
  - name: agentinstruct
    params:
      use_llm: false
  - name: s2m
    params:
      use_llm: false
  - name: apigenmt
    params:
      use_llm: false
  - name: reviewinstruct
    params:
      use_llm: false
```

## Check Environment

```bash
agentic-datasets doctor
```

This shows:
- Configured LLM provider
- Provider accessibility
- Available tools
- Environment variables
