from app.rag.chain import ask

def query_codebase(session_id: str, question: str) -> dict:
    return ask(session_id, question)