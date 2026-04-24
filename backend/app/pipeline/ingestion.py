import os
import shutil
import hashlib
from pathlib import Path
from git import Repo, GitCommandError
from app.config import (
    REPOS_TEMP_DIR,
    MAX_REPO_SIZE_MB,
    SUPPORTED_EXTENSIONS,
    EXCLUDED_DIRS,
    EXCLUDED_FILES
)


def get_repo_id(github_url: str) -> str:
    """Generate a unique ID for a repo URL."""
    return hashlib.md5(github_url.encode()).hexdigest()[:12]


def clone_repo(github_url: str) -> tuple[str, str]:
    """
    Clone a public GitHub repo to a temp directory.
    Returns (repo_path, repo_id)
    """
    repo_id = get_repo_id(github_url)
    repo_path = os.path.join(REPOS_TEMP_DIR, repo_id)

    # If already cloned, reuse it
    if os.path.exists(repo_path):
        print(f"[ingestion] Repo already cloned at {repo_path}, reusing.")
        return repo_path, repo_id

    os.makedirs(REPOS_TEMP_DIR, exist_ok=True)

    try:
        print(f"[ingestion] Cloning {github_url}...")
        Repo.clone_from(github_url, repo_path, depth=1)  # depth=1 = faster, no history
        print(f"[ingestion] Cloned to {repo_path}")
    except GitCommandError as e:
        raise ValueError(f"Failed to clone repository: {str(e)}")

    # Check repo size
    size_mb = get_dir_size_mb(repo_path)
    if size_mb > MAX_REPO_SIZE_MB:
        shutil.rmtree(repo_path)
        raise ValueError(f"Repo too large: {size_mb:.1f}MB (limit: {MAX_REPO_SIZE_MB}MB)")

    return repo_path, repo_id


def get_dir_size_mb(path: str) -> float:
    """Calculate total directory size in MB."""
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total += os.path.getsize(fp)
    return total / (1024 * 1024)


def walk_files(repo_path: str) -> list[dict]:
    """
    Walk the repo and return list of file metadata dicts.
    Each dict: { path, relative_path, extension, content }
    """
    files = []
    repo_root = Path(repo_path)

    for file_path in repo_root.rglob("*"):
        # Skip directories
        if not file_path.is_file():
            continue

        # Skip excluded directories anywhere in path
        path_parts = set(file_path.parts)
        if path_parts & EXCLUDED_DIRS:
            continue

        # Skip excluded filenames
        if file_path.name in EXCLUDED_FILES:
            continue

        # Skip unsupported extensions
        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            continue

        # Skip files over 100KB (likely generated/minified)
        if file_path.stat().st_size > 100 * 1024:
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Skip empty files
        if not content.strip():
            continue

        relative_path = str(file_path.relative_to(repo_root))

        files.append({
            "path": str(file_path),
            "relative_path": relative_path,
            "extension": file_path.suffix,
            "content": content,
            "size_bytes": file_path.stat().st_size
        })

    print(f"[ingestion] Found {len(files)} files to process")
    return files


def get_file_tree(repo_path: str) -> dict:
    """
    Build a nested dict representing the file tree.
    Used by the /tree API endpoint.
    """
    tree = {}
    repo_root = Path(repo_path)

    for file_path in repo_root.rglob("*"):
        if not file_path.is_file():
            continue

        path_parts = set(file_path.parts)
        if path_parts & EXCLUDED_DIRS:
            continue

        if file_path.suffix not in SUPPORTED_EXTENSIONS:
            continue

        relative = file_path.relative_to(repo_root)
        parts = relative.parts

        current = tree
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = "file"

    return tree


def cleanup_repo(repo_id: str):
    """Delete a cloned repo from temp storage."""
    repo_path = os.path.join(REPOS_TEMP_DIR, repo_id)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
        print(f"[ingestion] Cleaned up {repo_path}")