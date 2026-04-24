import os
import chromadb
from chromadb.config import Settings
from app.pipeline.embedder import embed_texts, embed_query
from app.config import CHROMA_PERSIST_DIR


def get_chroma_client():
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )


def build_vectorstore(chunks: list[dict], session_id: str):
    if not chunks:
        raise ValueError("No chunks provided")

    print(f"[vectorstore] Embedding {len(chunks)} chunks for session {session_id}...")

    client = get_chroma_client()

    existing = [c.name for c in client.list_collections()]
    if session_id in existing:
        client.delete_collection(session_id)
        print(f"[vectorstore] Deleted existing collection for {session_id}")

    collection = client.create_collection(
        name=session_id,
        metadata={"hnsw:space": "cosine"}
    )

    texts = [chunk["content"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [f"{session_id}_{i}" for i in range(len(chunks))]

    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_ids = ids[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]
        batch_embeddings = embed_texts(batch_texts)

        collection.add(
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        print(f"[vectorstore] Batch {i // batch_size + 1} done")

    print(f"[vectorstore] Done. {len(chunks)} chunks stored.")
    return session_id


def session_exists(session_id: str) -> bool:
    client = get_chroma_client()
    existing = [c.name for c in client.list_collections()]
    return session_id in existing


def get_retriever(session_id: str, k: int = 5):
    if not session_exists(session_id):
        raise ValueError(f"Session {session_id} not found.")

    client = get_chroma_client()
    collection = client.get_collection(session_id)

    def retriever(query: str) -> list[dict]:
        query_embedding = embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas"]
        )
        docs = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            docs.append({"content": doc, "metadata": meta})
        return docs

    return retriever