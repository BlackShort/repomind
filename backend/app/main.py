from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import os

app = FastAPI(title="RepoMind API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "DELETE", "PUT","PATCH", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok"}