---
inclusion: always
---
# Companion-X Memory Operations

Agents in this repository utilize the `companion-x` memory brick for long-term state persistence.

## Tools

Use `mcp_companion_x_call_brick_tool` with `brick_name: "memory"`.

### Storing Memory
```json
{
  "tool_name": "memory_store",
  "arguments": {
    "content": "Description of the discovery or state",
    "metadata": {"tags": ["dataset-gen", "error-pattern"]},
    "user_id": "kiro-agent"
  }
}
```

### Retrieving Memory
```json
{
  "tool_name": "memory_retrieve",
  "arguments": {
    "query": "search query",
    "user_id": "kiro-agent"
  }
}
```

## Guidelines
- Store significant architectural decisions or recurring error patterns.
- Always include relevant tags for easier retrieval.
- Avoid storing transient session state that belongs in short-term context.
