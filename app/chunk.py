"""Simple fixed-size chunking (no overlap).

Matches the style used in the original demo: 500 characters, clean cuts.
"""

from __future__ import annotations

CHUNK_SIZE = 500


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE) -> list[str]:
    """Split text into fixed-size chunks with no overlap.

    - Strips the input.
    - Drops empty chunks.
    - Very simple and predictable.
    """
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i : i + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks
