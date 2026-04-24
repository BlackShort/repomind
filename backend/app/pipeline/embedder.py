from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model():
    global _model
    if _model is None:
        print("[embedder] Loading sentence-transformers model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[embedder] Model loaded.")
    return _model

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    return embeddings.tolist()

def embed_query(query: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode([query], normalize_embeddings=True)
    return embedding[0].tolist()