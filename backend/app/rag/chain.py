import os
from groq import Groq
from app.pipeline.vectorstore import get_retriever

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are RepoMind, an expert code assistant that helps developers understand codebases.

You will be given relevant code chunks from a repository along with a user question.
Your job is to answer the question based ONLY on the provided code context.

Rules:
- Always mention which file(s) the answer comes from
- If the answer spans multiple files, explain how they connect
- If the context doesn't contain enough information, say so honestly
- Keep answers concise but complete
- Use markdown formatting for code snippets
- Never hallucinate code that isn't in the context
"""

def build_context(chunks: list[dict]) -> str:
    parts = []
    for chunk in chunks:
        source = chunk["metadata"]["source"]
        line = chunk["metadata"]["start_line"]
        parts.append(f"[File: {source} | Line: {line}]\n{chunk['content']}")
    return "\n\n---\n\n".join(parts)


def ask(session_id: str, question: str, k: int = 5) -> dict:
    retriever = get_retriever(session_id, k=k)
    chunks = retriever(question)

    if not chunks:
        return {
            "answer": "I couldn't find relevant code for your question. Try rephrasing or asking about a specific file or function.",
            "sources": []
        }

    context = build_context(chunks)

    prompt = f"""Here is the relevant code from the repository:

{context}

---

Question: {question}

Answer based only on the code above:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=1024
    )

    answer = response.choices[0].message.content
    sources = list({chunk["metadata"]["source"] for chunk in chunks})

    return {
        "answer": answer,
        "sources": sources
    }