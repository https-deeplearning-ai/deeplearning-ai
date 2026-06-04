"""Code parsing utilities for extracting structural information."""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict


class DefinitionKind(Enum):
    """Kinds of code definitions that can be extracted."""
    FUNCTION = auto()
    CLASS = auto()
    METHOD = auto()
    PROPERTY = auto()
    DECORATOR = auto()
    IMPORT = auto()

    @property
    def css_class(self) -> str:
        """Map to a CSS class for color coding in the UI."""
        return {
            DefinitionKind.FUNCTION: "text-info",
            DefinitionKind.CLASS: "text-warning",
            DefinitionKind.METHOD: "text-success",
            DefinitionKind.PROPERTY: "text-primary",
            DefinitionKind.DECORATOR: "text-danger",
            DefinitionKind.IMPORT: "text-muted",
        }.get(self, "text-secondary")


@dataclass
class NodeInfo:
    """Information about a parsed AST node for display."""
    name: str
    kind: DefinitionKind
    start_line: int
    end_line: int
    parent_name: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    docstring: Optional[str] = None

    @property
    def qualified_name(self) -> str:
        """Full qualified name (e.g., 'ClassName.method_name')."""
        if self.parent_name:
            return f"{self.parent_name}.{self.name}"
        return self.name

    @property
    def display_signature(self) -> str:
        """Short display signature with decorators."""
        parts = []
        for dec in self.decorators:
            parts.append(f"@{dec}")
        kind_label = self.kind.name.lower()
        parts.append(f"{kind_label} {self.qualified_name}")
        return " ".join(parts) if len(parts) == 1 else "\n".join(parts)

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1


def parse_python_ast(source_code: str) -> List[NodeInfo]:
    """Parse Python source and extract structural information.

    This is a lightweight regex-based parser for display purposes
    (no tree-sitter dependency needed in the UI layer).
    """
    nodes: List[NodeInfo] = []
    lines = source_code.split("\n")
    current_class: Optional[str] = None

    class_pattern = re.compile(r'^class\s+(\w+)')
    func_pattern = re.compile(r'^(\s*)def\s+(\w+)')
    decorator_pattern = re.compile(r'^(\s*)@(\w+)')
    pending_decorators: List[str] = []

    for i, line in enumerate(lines):
        dec_match = decorator_pattern.match(line)
        if dec_match:
            pending_decorators.append(dec_match.group(2))
            continue

        class_match = class_pattern.match(line)
        if class_match:
            current_class = class_match.group(1)
            end = _find_block_end(lines, i)
            nodes.append(NodeInfo(
                name=current_class,
                kind=DefinitionKind.CLASS,
                start_line=i + 1,
                end_line=end + 1,
                decorators=list(pending_decorators),
            ))
            pending_decorators.clear()
            continue

        func_match = func_pattern.match(line)
        if func_match:
            indent = func_match.group(1)
            name = func_match.group(2)
            end = _find_block_end(lines, i)

            if indent and current_class:
                if "property" in pending_decorators:
                    kind = DefinitionKind.PROPERTY
                else:
                    kind = DefinitionKind.METHOD
                parent = current_class
            else:
                kind = DefinitionKind.FUNCTION
                parent = None
                current_class = None

            nodes.append(NodeInfo(
                name=name,
                kind=kind,
                start_line=i + 1,
                end_line=end + 1,
                parent_name=parent,
                decorators=list(pending_decorators),
            ))
            pending_decorators.clear()
            continue

        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not line.startswith(" "):
            current_class = None

        if stripped:
            pending_decorators.clear()

    return nodes


def extract_definitions(source_code: str) -> Dict[str, List[str]]:
    """Extract a summary of definitions organized by kind."""
    nodes = parse_python_ast(source_code)
    result: Dict[str, List[str]] = {}
    for node in nodes:
        kind_name = node.kind.name.lower()
        if kind_name not in result:
            result[kind_name] = []
        result[kind_name].append(node.qualified_name)
    return result


def _find_block_end(lines: List[str], start: int) -> int:
    """Find the last line of a Python block starting at 'start'."""
    if start >= len(lines) - 1:
        return start

    base_indent = len(lines[start]) - len(lines[start].lstrip())
    last_content_line = start

    for i in range(start + 1, len(lines)):
        line = lines[i]
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent:
            break
        last_content_line = i

    return last_content_line
