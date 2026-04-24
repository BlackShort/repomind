from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
REPOS_TEMP_DIR = os.getenv("REPOS_TEMP_DIR", "./tmp_repos")
MAX_REPO_SIZE_MB = int(os.getenv("MAX_REPO_SIZE_MB", 50))

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".cpp", ".c",
    ".md", ".json", ".yaml", ".yml", ".env.example"
}

EXCLUDED_DIRS = {
    "node_modules", ".git", "dist", "build",
    "__pycache__", ".next", "venv", ".venv",
    "coverage", ".pytest_cache"
}

EXCLUDED_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "poetry.lock", ".DS_Store"
}