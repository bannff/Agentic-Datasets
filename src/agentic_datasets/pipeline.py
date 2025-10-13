from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, List, Optional

from .config import PipelineConfig
from .schemas.messages import ConversationRecord, Message


def _iter_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def ingest(input_path: Path) -> Iterator[dict]:
    if input_path.is_dir():
        for p in sorted(input_path.glob("*.jsonl")):
            yield from _iter_jsonl(p)
    else:
        yield from _iter_jsonl(input_path)


def normalize(records: Iterable[dict]) -> Iterator[ConversationRecord]:
    """Normalize raw dicts into ConversationRecord.

    Accepts multiple legacy shapes in addition to the canonical schema:
    - Canonical: {"messages": [{role, content, ...}], ...}
    - Legacy text: {"text": "User: ...\nAssistant: ..."}
    - Instruct style: {"instruction": str, "output": str}
    - Prompt/completion: {"prompt": str, "completion": str}
    - Q/A: {"question": str, "answer": str}
    If only a single text field is available, it becomes a single user message; later stages can expand.
    """

    def _from_legacy_text(text: str) -> Optional[List[Message]]:
        t = (text or "").strip()
        if not t:
            return None
        # Try to split on role prefixes (case-insensitive)
        lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
        cur_role: Optional[str] = None
        buf: List[str] = []
        messages: List[Message] = []

        def flush() -> None:
            nonlocal buf, cur_role, messages
            if cur_role and buf:
                content = "\n".join(buf).strip()
                if content:
                    role: str = cur_role.lower()
                    if role not in ("system", "user", "assistant", "tool"):
                        role = "user"
                    messages.append(Message(role=role, content=content))
                buf = []

        for ln in lines:
            lower = ln.lower()
            if lower.startswith("user:"):
                flush()
                cur_role = "user"
                buf = [ln.split(":", 1)[1].strip()]
            elif lower.startswith("assistant:") or lower.startswith("assistant "):
                flush()
                cur_role = "assistant"
                buf = [ln.split(":", 1)[1].strip() if ":" in ln else ln]
            elif lower.startswith("system:"):
                flush()
                cur_role = "system"
                buf = [ln.split(":", 1)[1].strip()]
            elif lower.startswith("tool:"):
                flush()
                cur_role = "tool"
                buf = [ln.split(":", 1)[1].strip()]
            else:
                # Continuation of current role block or start as user if none
                if cur_role is None:
                    cur_role = "user"
                buf.append(ln)
        flush()

        if not messages:
            # Fall back to a single user message
            return [Message(role="user", content=t)]
        return messages

    for r in records:
        if isinstance(r, dict) and "messages" in r:
            yield ConversationRecord.model_validate(r)
            continue

        # Try various legacy shapes
        msgs: Optional[List[Message]] = None
        if isinstance(r, dict):
            if isinstance(r.get("text"), str):
                msgs = _from_legacy_text(r.get("text", ""))
            elif isinstance(r.get("instruction"), str) and isinstance(r.get("output"), str):
                msgs = [
                    Message(role="user", content=str(r["instruction"]).strip()),
                    Message(role="assistant", content=str(r["output"]).strip()),
                ]
            elif isinstance(r.get("prompt"), str) and isinstance(r.get("completion"), str):
                msgs = [
                    Message(role="user", content=str(r["prompt"]).strip()),
                    Message(role="assistant", content=str(r["completion"]).strip()),
                ]
            elif isinstance(r.get("question"), str) and isinstance(r.get("answer"), str):
                msgs = [
                    Message(role="user", content=str(r["question"]).strip()),
                    Message(role="assistant", content=str(r["answer"]).strip()),
                ]

        if msgs:
            rid = r.get("id") if isinstance(r, dict) else None
            src = r.get("source") if isinstance(r, dict) else None
            meta = r.get("metadata") if isinstance(r, dict) else None
            yield ConversationRecord(messages=msgs, id=rid, source=src, metadata=meta)
        else:
            # Last resort: attempt direct validation (will raise on bad inputs to surface issues)
            yield ConversationRecord.model_validate(r)


def validate(records: Iterable[ConversationRecord]) -> List[ConversationRecord]:
    out: List[ConversationRecord] = []
    for rec in records:
        out.append(rec)
    return out


def export(records: Iterable[ConversationRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for rec in records:
            # Drop None fields to avoid noisy nulls (e.g., tool_call_id/tool_output when unused)
            f.write(json.dumps(rec.model_dump(exclude_none=True), ensure_ascii=False) + "\n")


def run_pipeline(cfg: PipelineConfig) -> Path:
    raw = ingest(cfg.input_path)
    norm = normalize(raw)
    validated = validate(norm)
    if cfg.max_records is not None:
        items = []
        for i, rec in enumerate(validated):
            if i >= cfg.max_records:
                break
            items.append(rec)
    else:
        items = list(validated)
    export(items, cfg.output_path)
    return cfg.output_path
