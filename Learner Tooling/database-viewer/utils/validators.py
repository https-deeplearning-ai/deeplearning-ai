"""Input validation utilities for the web application."""

import re
import os
from typing import Tuple, Optional
from pathlib import Path


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


def validate_collection_name(name: str) -> Tuple[bool, str]:
    """Validate a ChromaDB collection name.

    Rules: 3-63 chars, alphanumeric + hyphens/underscores,
    must start with a letter or underscore.
    Returns (is_valid, error_message).
    """
    if not name:
        return False, "Collection name is required"
    if len(name) < 3:
        return False, "Collection name must be at least 3 characters"
    if len(name) > 63:
        return False, "Collection name must be at most 63 characters"
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*$', name):
        return False, (
            "Collection name must start with a letter or underscore "
            "and contain only letters, numbers, hyphens, and underscores"
        )
    if ".." in name:
        return False, "Collection name cannot contain consecutive periods"
    return True, ""


def validate_search_query(query: str, min_length: int = 2,
                          max_length: int = 500) -> Tuple[bool, str]:
    """Validate a semantic search query string."""
    if not query or not query.strip():
        return False, "Search query cannot be empty"
    stripped = query.strip()
    if len(stripped) < min_length:
        return False, f"Query must be at least {min_length} characters"
    if len(stripped) > max_length:
        return False, f"Query must be at most {max_length} characters"
    return True, ""


def validate_regex_pattern(pattern: str) -> Tuple[bool, str]:
    """Validate that a string is a compilable regex pattern."""
    if not pattern or not pattern.strip():
        return False, "Regex pattern cannot be empty"
    try:
        re.compile(pattern)
        return True, ""
    except re.error as e:
        return False, f"Invalid regex pattern: {e}"


def validate_directory_path(path: str) -> Tuple[bool, str]:
    """Validate that a path points to an existing readable directory."""
    if not path or not path.strip():
        return False, "Directory path is required"
    p = Path(path.strip())
    if not p.exists():
        return False, f"Path does not exist: {path}"
    if not p.is_dir():
        return False, f"Path is not a directory: {path}"
    if not os.access(p, os.R_OK):
        return False, f"Directory is not readable: {path}"
    return True, ""


def validate_pagination(offset: int, limit: int,
                        max_limit: int = 100) -> Tuple[int, int]:
    """Sanitize and clamp pagination parameters.

    Returns (safe_offset, safe_limit).
    """
    safe_offset = max(0, offset)
    safe_limit = max(1, min(limit, max_limit))
    return safe_offset, safe_limit


def sanitize_html(text: str) -> str:
    """Remove HTML tags and dangerous content from user input."""
    cleaned = re.sub(r'<[^>]+>', '', text)
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
    return cleaned.strip()
