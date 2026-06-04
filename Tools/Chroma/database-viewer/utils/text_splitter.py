"""Text splitting and token estimation utilities."""

from typing import List, Tuple


def estimate_tokens(text: str) -> int:
    """Rough token estimate without loading tiktoken (chars / 4 heuristic)."""
    return max(1, len(text) // 4)


def split_by_tokens(text: str, max_tokens: int = 1000) -> List[str]:
    """Split text into chunks under max_tokens using the rough estimator.

    This is the lightweight version for display purposes.
    The full pipeline in IngestionService uses tiktoken for accuracy.
    """
    if estimate_tokens(text) <= max_tokens:
        return [text]

    lines = text.split("\n")
    chunks: List[str] = []
    current: List[str] = []
    current_est = 0

    for line in lines:
        line_est = estimate_tokens(line) + 1
        if current_est + line_est > max_tokens and current:
            chunks.append("\n".join(current))
            current = []
            current_est = 0
        current.append(line)
        current_est += line_est

    if current:
        chunks.append("\n".join(current))

    return chunks


def truncate_to_tokens(text: str, max_tokens: int = 200) -> Tuple[str, bool]:
    """Truncate text to approximately max_tokens.

    Returns (truncated_text, was_truncated).
    """
    if estimate_tokens(text) <= max_tokens:
        return text, False

    char_limit = max_tokens * 4
    truncated = text[:char_limit]

    last_newline = truncated.rfind("\n")
    if last_newline > char_limit * 0.5:
        truncated = truncated[:last_newline]

    return truncated, True


def count_code_lines(text: str) -> dict:
    """Count code lines, comment lines, and blank lines."""
    lines = text.split("\n")
    code = 0
    comments = 0
    blank = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
        elif stripped.startswith("#"):
            comments += 1
        else:
            code += 1

    return {"code": code, "comments": comments, "blank": blank, "total": len(lines)}
