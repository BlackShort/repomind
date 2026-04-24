from app.pipeline.ingestion import clone_repo, walk_files
from app.pipeline.chunker import chunk_file
from app.pipeline.vectorstore import build_vectorstore, get_retriever, session_exists
from app.rag.chain import ask

url = "https://github.com/BlackShort/study-planner"
repo_path, repo_id = clone_repo(url)

files = walk_files(repo_path)
all_chunks = []
for f in files:
    chunks = chunk_file(f)
    all_chunks.extend(chunks)

if not session_exists(repo_id):
    build_vectorstore(all_chunks, repo_id)

# Test the full RAG chain
questions = [
    "What does this project do?",
]

for q in questions:
    print(f"\n{'='*60}")
    print(f"Q: {q}")
    print('='*60)
    result = ask(repo_id, q)
    print(f"A: {result['answer']}")
    print(f"Sources: {result['sources']}")