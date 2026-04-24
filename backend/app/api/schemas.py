from pydantic import BaseModel

class IngestRequest(BaseModel):
    github_url: str

class QueryRequest(BaseModel):
    session_id: str
    question: str