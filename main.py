"""Simple RAG demo.

Reads sample.txt → chunks it → embeds with ChromaDB → stores → retrieves top 3.

Run:
    uv run python main.py
"""

from pathlib import Path

import chromadb


def main() -> None:
    # Hardcoded settings
    query = "What is RAG and how does chunking help?"
    CHUNK_SIZE = 500
    top_k = 3

    # 1. Read the text file
    text = Path("sample.txt").read_text(encoding="utf-8").strip()

    # 2. Simple chunking - split every 500 characters (no overlap)
    chunks: list[str] = []
    for i in range(0, len(text), CHUNK_SIZE):
        chunk = text[i : i + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)

    print(f"Loaded {len(chunks)} chunk(s)")

    if not chunks:
        print("Nothing to index.")
        return

    # 3+4. Embed + store
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        client.delete_collection("demo")
    except Exception:
        pass
    coll = client.create_collection(name="demo", metadata={"hnsw:space": "cosine"})
    coll.add(documents=chunks, ids=[f"c{j}" for j in range(len(chunks))])

    # 5. Retrieve top 3 most relevant chunks
    results = coll.query(query_texts=[query], n_results=top_k)

    chunks = results.get("documents", [[]])[0] or []
    distances = results.get("distances", [[]])[0] or []

    print(f"\nQuery: {query}")
    print("-" * 50)

    if not chunks:
        print("No results found.")
        return

    for rank, (chunk, distance) in enumerate(zip(chunks, distances), 1):
        # Convert distance to similarity score (1.0 = perfect match for cosine)
        similarity = round(1 - float(distance), 4) if distance is not None else "n/a"
        print(f"\n[{rank}] similarity={similarity}")
        print(chunk)
        print()


if __name__ == "__main__":
    main()
