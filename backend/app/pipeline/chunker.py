from tree_sitter_languages import get_language, get_parser
from typing import Optional


# Map file extensions to tree-sitter language names
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "c",
}

# Node types that represent meaningful code blocks per language
MEANINGFUL_NODE_TYPES = {
    "python": ["function_definition", "class_definition", "decorated_definition"],
    "javascript": ["function_declaration", "class_declaration", "arrow_function", "method_definition", "export_statement"],
    "typescript": ["function_declaration", "class_declaration", "method_definition", "export_statement", "interface_declaration", "type_alias_declaration"],
    "tsx": ["function_declaration", "class_declaration", "method_definition", "export_statement"],
    "java": ["method_declaration", "class_declaration", "constructor_declaration", "interface_declaration"],
    "go": ["function_declaration", "method_declaration", "type_declaration"],
    "rust": ["function_item", "impl_item", "struct_item", "trait_item"],
    "cpp": ["function_definition", "class_specifier"],
    "c": ["function_definition"],
}

MAX_CHUNK_CHARS = 1500
MIN_CHUNK_CHARS = 50


def chunk_file(file: dict) -> list[dict]:
    """
    Main entry point. Chunks a file dict into smaller pieces.
    Returns list of chunk dicts with content + metadata.
    """
    extension = file["extension"]
    content = file["content"]
    relative_path = file["relative_path"]

    # Try AST-based chunking for supported languages
    language_name = EXTENSION_TO_LANGUAGE.get(extension)
    if language_name:
        chunks = _ast_chunk(content, language_name, relative_path)
        if chunks:
            return chunks

    # Fallback: line-based chunking for .md, .json, .yaml, unsupported langs
    return _line_chunk(content, relative_path)


def _ast_chunk(content: str, language_name: str, relative_path: str) -> list[dict]:
    """
    Use tree-sitter to parse code and extract meaningful blocks
    like functions and classes as individual chunks.
    """
    try:
        language = get_language(language_name)
        parser = get_parser(language_name)
        tree = parser.parse(bytes(content, "utf-8"))
        root = tree.root_node

        node_types = MEANINGFUL_NODE_TYPES.get(language_name, [])
        chunks = []

        _extract_nodes(root, content, node_types, relative_path, chunks)

        # If tree-sitter found nothing meaningful, fall back to line chunking
        if not chunks:
            return []

        return chunks

    except Exception as e:
        print(f"[chunker] AST parsing failed for {relative_path}: {e}")
        return []


def _extract_nodes(node, content: str, node_types: list, relative_path: str, chunks: list):
    """
    Recursively walk AST nodes and extract meaningful ones as chunks.
    """
    if node.type in node_types:
        chunk_text = content[node.start_byte:node.end_byte]

        # Skip tiny fragments
        if len(chunk_text.strip()) < MIN_CHUNK_CHARS:
            return

        # If chunk is too large, don't extract it as one — recurse into children
        if len(chunk_text) > MAX_CHUNK_CHARS:
            for child in node.children:
                _extract_nodes(child, content, node_types, relative_path, chunks)
            return

        chunks.append(_make_chunk(chunk_text, relative_path, node.type, node.start_point[0] + 1))
        return  # Don't recurse into already-extracted nodes

    # Recurse into children for non-matching nodes
    for child in node.children:
        _extract_nodes(child, content, node_types, relative_path, chunks)


def _line_chunk(content: str, relative_path: str) -> list[dict]:
    """
    Fallback chunker: splits content into fixed line-window chunks with overlap.
    Used for markdown, JSON, YAML, and unsupported languages.
    """
    lines = content.splitlines()
    chunks = []
    window = 60   # lines per chunk
    overlap = 10  # lines overlap between chunks

    start = 0
    while start < len(lines):
        end = min(start + window, len(lines))
        chunk_text = "\n".join(lines[start:end])

        if len(chunk_text.strip()) >= MIN_CHUNK_CHARS:
            chunks.append(_make_chunk(chunk_text, relative_path, "text_block", start + 1))

        start += window - overlap

    return chunks


def _make_chunk(content: str, relative_path: str, node_type: str, start_line: int) -> dict:
    """Build a standardized chunk dict."""
    return {
        "content": content.strip(),
        "metadata": {
            "source": relative_path,
            "node_type": node_type,
            "start_line": start_line,
            "language": relative_path.split(".")[-1] if "." in relative_path else "unknown"
        }
    }