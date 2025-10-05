from __future__ import annotations

from typing import Iterable, Iterator, List

from langchain_text_splitters import TokenTextSplitter

from ..schemas.messages import ConversationRecord, Message


def chunk_conversation(
    rec: ConversationRecord,
    *,
    model_name: str = "gpt-4o-mini",
    max_tokens: int = 512,
    overlap: int = 50,
) -> List[ConversationRecord]:
    splitter = TokenTextSplitter(
        encoding_name=None,  # let splitter infer from model_name if needed
        model_name=model_name,
        chunk_size=max_tokens,
        chunk_overlap=overlap,
    )

    # Join messages with role tags to keep some context; later we reconstruct as single-message chunks.
    # For agentic datasets, chunks typically preserve order and attribution.
    transcript = "\n".join(f"[{m.role}] {m.content}" for m in rec.messages)
    chunks = splitter.split_text(transcript)

    out: List[ConversationRecord] = []
    for ch in chunks:
        # store as a single assistant-style message chunk; metadata retains original provenance
        out.append(
            ConversationRecord(
                messages=[Message(role="assistant", content=ch)],
                id=rec.id,
                source=rec.source,
                metadata=rec.metadata,
            )
        )
    return out


def chunk_dataset(
    recs: Iterable[ConversationRecord], *, model_name: str = "gpt-4o-mini", max_tokens: int = 512, overlap: int = 50
) -> Iterator[ConversationRecord]:
    for r in recs:
        for c in chunk_conversation(r, model_name=model_name, max_tokens=max_tokens, overlap=overlap):
            yield c
