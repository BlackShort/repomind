from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.api.schemas import IngestRequest, QueryRequest
from app.pipeline.ingestion import clone_repo, walk_files, get_file_tree
from app.pipeline.chunker import chunk_file
from app.pipeline.vectorstore import build_vectorstore, session_exists
from app.rag.chain import ask

router = APIRouter()


@router.post("/ingest")
def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Clone and index a GitHub repository.
    Returns session_id to use for subsequent queries.
    """
    try:
        repo_path, session_id = clone_repo(request.github_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if session_exists(session_id):
        # Already indexed — return immediately
        tree = get_file_tree(repo_path)
        return {
            "session_id": session_id,
            "status": "already_indexed",
            "file_tree": tree
        }

    # Index in the same request (acceptable for small repos)
    try:
        files = walk_files(repo_path)
        all_chunks = []
        for f in files:
            chunks = chunk_file(f)
            all_chunks.extend(chunks)

        build_vectorstore(all_chunks, session_id)
        tree = get_file_tree(repo_path)

        return {
            "session_id": session_id,
            "status": "indexed",
            "total_files": len(files),
            "total_chunks": len(all_chunks),
            "file_tree": tree
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
def query(request: QueryRequest):
    """
    Ask a question about an indexed repository.
    """
    if not session_exists(request.session_id):
        raise HTTPException(
            status_code=404,
            detail="Session not found. Please ingest the repository first."
        )

    try:
        result = ask(request.session_id, request.question)
        return {
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tree/{session_id}")
def tree(session_id: str):
    """
    Returns the file tree for an indexed session.
    """
    if not session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found.")

    # Find the repo path from tmp_repos
    import os
    from app.config import REPOS_TEMP_DIR
    repo_path = os.path.join(REPOS_TEMP_DIR, session_id)

    if not os.path.exists(repo_path):
        raise HTTPException(status_code=404, detail="Repo files not found locally.")

    return {"file_tree": get_file_tree(repo_path)}


@router.get("/sessions")
def list_sessions():
    """
    List all indexed sessions.
    """
    import chromadb
    from app.config import CHROMA_PERSIST_DIR
    from chromadb.config import Settings

    client = chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False)
    )
    sessions = [c.name for c in client.list_collections()]
    return {"sessions": sessions}