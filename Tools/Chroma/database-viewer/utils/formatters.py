"""Formatting utilities for the web UI display layer."""

import re
import html
from typing import Optional
from datetime import datetime


def format_score(distance: float, style: str = "percentage") -> str:
    """Format a ChromaDB distance score for display.

    Args:
        distance: Raw distance from ChromaDB (lower = more similar).
        style: One of 'percentage', 'decimal', 'badge'.
    """
    percentage = max(0.0, min(100.0, (1.0 - distance) * 100))

    if style == "percentage":
        return f"{percentage:.1f}%"
    elif style == "decimal":
        return f"{distance:.4f}"
    elif style == "badge":
        if percentage >= 80:
            color = "success"
        elif percentage >= 60:
            color = "info"
        elif percentage >= 40:
            color = "warning"
        else:
            color = "secondary"
        return f'<span class="badge bg-{color}">{percentage:.1f}%</span>'
    return f"{percentage:.1f}%"


def format_code_preview(code: str, max_lines: int = 10,
                        show_line_numbers: bool = True) -> str:
    """Format code for preview display with optional line numbers."""
    lines = code.split("\n")
    truncated = len(lines) > max_lines
    display_lines = lines[:max_lines]

    if show_line_numbers:
        width = len(str(len(display_lines)))
        numbered = [
            f"{i+1:>{width}} | {line}"
            for i, line in enumerate(display_lines)
        ]
        result = "\n".join(numbered)
    else:
        result = "\n".join(display_lines)

    if truncated:
        result += f"\n... ({len(lines) - max_lines} more lines)"

    return result


def highlight_regex_matches(code: str, pattern: str,
                            css_class: str = "regex-match") -> str:
    """Wrap regex matches in <mark> tags for HTML display.

    The code is first HTML-escaped for safety, then matches are wrapped.
    """
    try:
        compiled = re.compile(re.escape(pattern) if not _is_valid_regex(pattern) else pattern,
                              re.MULTILINE)
    except re.error:
        return html.escape(code)

    parts = []
    last_end = 0
    for match in compiled.finditer(code):
        parts.append(html.escape(code[last_end:match.start()]))
        escaped_match = html.escape(match.group(0))
        parts.append(f'<mark class="{css_class}">{escaped_match}</mark>')
        last_end = match.end()
    parts.append(html.escape(code[last_end:]))

    return "".join(parts)


def _is_valid_regex(pattern: str) -> bool:
    """Check if a string is a valid regex pattern."""
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False


def format_file_path(path: str, max_length: int = 60) -> str:
    """Shorten file path for display, keeping the meaningful suffix."""
    if len(path) <= max_length:
        return path

    parts = path.split("/")
    for i in range(len(parts)):
        shortened = "/".join(["..."] + parts[i:])
        if len(shortened) <= max_length:
            return shortened

    return "..." + path[-(max_length - 3):]


def format_timestamp(iso_string: Optional[str]) -> str:
    """Format an ISO timestamp string for display."""
    if not iso_string:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%b %d, %Y at %I:%M %p")
    except (ValueError, TypeError):
        return iso_string


def format_count(count: int) -> str:
    """Format a count with thousands separators and singular/plural."""
    if count == 1:
        return "1 chunk"
    formatted = f"{count:,}"
    return f"{formatted} chunks"


def format_byte_size(size_bytes: int) -> str:
    """Format byte size to human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
