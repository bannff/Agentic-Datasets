from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Optional


def summarize_metrics(path: Path, limit: Optional[int] = None) -> str:
    """Summarize APIGen/tool execution signals from a JSONL file.

    Reports:
    - total records
    - assistant tool_calls count
    - tool messages count
    - backend histogram from tool_output.backend
    - via histogram (e.g., 'strands', 'fallback', 'fallback-synth') from metadata
    """
    tool_calls = 0
    tool_msgs = 0
    total = 0
    backend = Counter()
    via = Counter()

    def _update_backend(m: Dict[str, Any]) -> None:
        out = m.get("tool_output")
        if isinstance(out, dict):
            b = out.get("backend") or out.get("provider")
            if isinstance(b, str) and b:
                backend[b] += 1

    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            total += 1
            md = rec.get("metadata") or {}
            v = md.get("via")
            if isinstance(v, str) and v:
                via[v] += 1
            for m in rec.get("messages", []) or []:
                role = m.get("role")
                if role == "assistant":
                    tcs = m.get("tool_calls") or []
                    if isinstance(tcs, list):
                        tool_calls += len(tcs)
                elif role == "tool":
                    tool_msgs += 1
                    _update_backend(m)
            if limit is not None and total >= limit:
                break

    return json.dumps(
        {
            "records": total,
            "assistant_tool_calls": tool_calls,
            "tool_messages": tool_msgs,
            "backend_counts": backend,
            "via_counts": via,
        },
        indent=2,
        default=lambda x: dict(x) if isinstance(x, Counter) else str(x),
    )
