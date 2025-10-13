"""Local stub tools for deterministic execution in APIGenMT tests.

Each tool function follows a simple convention compatible with strands_tools:
- Input: a dict with keys {"input": <arguments dict>, "toolUseId": <id str>}
- Output: a dict with a "content" list of dicts containing {"text": str}

These tools are intentionally offline and deterministic.
"""

from __future__ import annotations

from typing import Any, Dict


def _mk_content(text: str) -> Dict[str, Any]:
    return {"content": [{"text": text}]}


def search_cve(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mock CVE search tool.

    Args:
        payload: {"input": {"keyword": str}, "toolUseId": str}
    Returns:
        Dict with content list containing a short deterministic text.
    """
    args = (payload or {}).get("input", {})
    keyword = str(args.get("keyword", "")).strip() or "unknown"
    text = (
        f"Results for CVE search keyword '{keyword}':\n"
        f"- CVE-2024-0001 ({keyword})\n- CVE-2024-0002 ({keyword})\n- CVE-2024-0003 ({keyword})"
    )
    return _mk_content(text)


def dns_lookup(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Mock DNS lookup tool.

    Args:
        payload: {"input": {"hostname": str}, "toolUseId": str}
    Returns:
        Dict with content list containing a short deterministic text.
    """
    args = (payload or {}).get("input", {})
    hostname = str(args.get("hostname", "")).strip() or "example.com"
    text = (
        f"DNS lookup for {hostname}:\nA 203.0.113.10\nAAAA 2001:db8::10\nNS ns1.{hostname}\nTXT 'stub-record'"
    )
    return _mk_content(text)
