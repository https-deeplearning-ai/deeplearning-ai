"""Smart query suggestion service.

Analyzes collection metadata to generate contextual search
suggestions, including semantic queries derived from code
patterns and regex patterns for common code constructs.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional, Set, Tuple

import chromadb


class SuggestionCategory(Enum):
    """Categories of query suggestions."""
    SYMBOL = auto()
    PATTERN = auto()
    CONCEPT = auto()
    REGEX = auto()
    FILE = auto()


@dataclass
class Suggestion:
    """A single query suggestion with context."""
    query: str
    category: SuggestionCategory
    description: str
    mode: str = "semantic"  # "semantic" or "regex"
    relevance: float = 1.0

    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "category": self.category.name.lower(),
            "description": self.description,
            "mode": self.mode,
            "relevance": round(self.relevance, 2),
        }


@dataclass
class SuggestionSet:
    """A collection of categorized suggestions."""
    suggestions: List[Suggestion] = field(default_factory=list)
    collection_name: str = ""

    @property
    def by_category(self) -> Dict[str, List[Suggestion]]:
        """Group suggestions by category."""
        groups: Dict[str, List[Suggestion]] = {}
        for s in self.suggestions:
            key = s.category.name.lower()
            if key not in groups:
                groups[key] = []
            groups[key].append(s)
        return groups

    @property
    def semantic_suggestions(self) -> List[Suggestion]:
        return [s for s in self.suggestions if s.mode == "semantic"]

    @property
    def regex_suggestions(self) -> List[Suggestion]:
        return [s for s in self.suggestions if s.mode == "regex"]

    def to_dict(self) -> Dict:
        return {
            "collection": self.collection_name,
            "total": len(self.suggestions),
            "suggestions": [s.to_dict() for s in self.suggestions],
            "by_category": {
                k: [s.to_dict() for s in v]
                for k, v in self.by_category.items()
            },
        }


class SuggestionStrategy(ABC):
    """Abstract base for suggestion generation strategies."""

    @abstractmethod
    def generate(self, metadata: List[Dict]) -> List[Suggestion]:
        """Generate suggestions from collection metadata."""
        ...

    @abstractmethod
    def strategy_name(self) -> str:
        """Return the name of this strategy."""
        ...


class SymbolSuggestionStrategy(SuggestionStrategy):
    """Generate suggestions based on discovered symbols.

    Analyzes function and class names to suggest natural language
    queries that would find related code through semantic search.
    """

    # Maps name patterns to descriptive query templates
    NAME_PATTERNS: List[Tuple[str, str, str]] = [
        (r"validate|check|verify|assert", "validation",
         "How is {symbol} validated?"),
        (r"parse|extract|tokenize|split", "parsing",
         "How does the parsing work in {symbol}?"),
        (r"format|render|display|show", "formatting",
         "How is {symbol} formatted for display?"),
        (r"create|build|make|generate|factory", "creation",
         "How are {noun} objects created?"),
        (r"search|find|query|lookup|match", "search",
         "How does search work in {symbol}?"),
        (r"compute|calculate|score|measure", "computation",
         "How is the {noun} computed?"),
        (r"convert|transform|map|reduce", "transformation",
         "How are values transformed in {symbol}?"),
        (r"load|save|store|persist|serialize", "persistence",
         "How is data persisted in {symbol}?"),
        (r"init|setup|configure|connect", "initialization",
         "How is {symbol} initialized?"),
        (r"test|assert|expect|mock", "testing",
         "How is {symbol} tested?"),
    ]

    def strategy_name(self) -> str:
        return "symbol_analysis"

    def generate(self, metadata: List[Dict]) -> List[Suggestion]:
        suggestions = []
        seen_queries: Set[str] = set()

        symbols = self._extract_symbols(metadata)

        for symbol, chunk_type in symbols:
            for pattern, concept, template in self.NAME_PATTERNS:
                if re.search(pattern, symbol, re.IGNORECASE):
                    noun = self._to_noun(symbol)
                    query = template.format(symbol=symbol, noun=noun)

                    if query not in seen_queries:
                        seen_queries.add(query)
                        suggestions.append(Suggestion(
                            query=query,
                            category=SuggestionCategory.SYMBOL,
                            description=f"Based on {chunk_type}: {symbol}",
                            relevance=0.9,
                        ))
                    break  # Only first match per symbol

        return suggestions[:8]

    @staticmethod
    def _extract_symbols(metadata: List[Dict]) -> List[Tuple[str, str]]:
        """Extract unique (symbol, chunk_type) pairs."""
        seen = set()
        symbols = []
        for meta in metadata:
            symbol = meta.get("symbol", "")
            chunk_type = meta.get("chunk_type", "")
            if symbol and symbol not in seen:
                seen.add(symbol)
                symbols.append((symbol, chunk_type))
        return symbols

    @staticmethod
    def _to_noun(symbol: str) -> str:
        """Convert a symbol name to a readable noun phrase."""
        # CamelCase to words
        words = re.sub(r"([a-z])([A-Z])", r"\1 \2", symbol)
        # snake_case to words
        words = words.replace("_", " ").strip()
        return words.lower()


class PatternSuggestionStrategy(SuggestionStrategy):
    """Generate suggestions based on code patterns detected.

    Looks for design patterns, architectural patterns, and
    Python idioms in the metadata to suggest meaningful queries.
    """

    # (symbol_pattern, query, description)
    DESIGN_PATTERNS: List[Tuple[str, str, str]] = [
        (r"Singleton|_instance|__new__",
         "How is the singleton pattern implemented?",
         "Detected singleton pattern usage"),
        (r"Factory|create_|build_|get_\w+_instance",
         "How does the factory pattern work here?",
         "Detected factory pattern usage"),
        (r"Strategy|ABC|abstractmethod",
         "How is the strategy pattern used?",
         "Detected strategy/ABC pattern usage"),
        (r"Observer|listener|on_\w+|emit|subscribe",
         "How does event handling work?",
         "Detected observer/event pattern"),
        (r"Decorator|wrapper|@\w+",
         "How are decorators used in this codebase?",
         "Detected decorator pattern usage"),
        (r"Iterator|__iter__|__next__|yield",
         "How is iteration implemented?",
         "Detected iterator pattern usage"),
        (r"Builder|with_\w+|set_\w+.*return self",
         "How does the builder pattern work?",
         "Detected builder pattern usage"),
    ]

    def strategy_name(self) -> str:
        return "pattern_detection"

    def generate(self, metadata: List[Dict]) -> List[Suggestion]:
        suggestions = []
        all_symbols = " ".join(
            meta.get("symbol", "") for meta in metadata
        )

        seen = set()
        for pattern, query, description in self.DESIGN_PATTERNS:
            if re.search(pattern, all_symbols, re.IGNORECASE):
                if query not in seen:
                    seen.add(query)
                    suggestions.append(Suggestion(
                        query=query,
                        category=SuggestionCategory.PATTERN,
                        description=description,
                        relevance=0.95,
                    ))

        return suggestions


class ConceptSuggestionStrategy(SuggestionStrategy):
    """Generate high-level conceptual queries.

    Creates queries about architecture, error handling,
    data flow, and other cross-cutting concerns.
    """

    CONCEPT_QUERIES: List[Tuple[str, str, str]] = [
        ("chunk_type", "class_definition",
         "What are the main abstractions in this codebase?"),
        ("chunk_type", "function_definition",
         "How is input validated before processing?"),
        ("chunk_type", "class_definition",
         "How is error handling structured?"),
        ("chunk_type", "function_definition",
         "What utility functions are available?"),
        ("chunk_type", "gap",
         "How are modules organized and configured?"),
    ]

    def strategy_name(self) -> str:
        return "concept_mining"

    def generate(self, metadata: List[Dict]) -> List[Suggestion]:
        suggestions = []
        available_types = {meta.get("chunk_type", "") for meta in metadata}

        seen = set()
        for meta_key, meta_value, query in self.CONCEPT_QUERIES:
            if meta_value in available_types and query not in seen:
                seen.add(query)
                suggestions.append(Suggestion(
                    query=query,
                    category=SuggestionCategory.CONCEPT,
                    description=f"Based on {meta_value} chunks found",
                    relevance=0.8,
                ))

        return suggestions


class RegexSuggestionStrategy(SuggestionStrategy):
    """Generate useful regex pattern suggestions.

    Provides common code search regex patterns tailored
    to the types of code found in the collection.
    """

    REGEX_SUGGESTIONS: List[Tuple[str, str, str, str]] = [
        ("class_definition", r"class\s+\w+\(.*ABC.*\)",
         "Abstract base classes", "Find all ABCs"),
        ("class_definition", r"class\s+\w+\(Enum\)",
         "Enum definitions", "Find all enums"),
        ("function_definition", r"def\s+__\w+__",
         "Dunder methods", "Find all magic methods"),
        ("function_definition", r"def\s+_\w+",
         "Private methods", "Find private methods"),
        ("function_definition", r"@(staticmethod|classmethod|property)",
         "Decorated methods", "Find decorated methods"),
        ("function_definition", r"def\s+validate_\w+|def\s+check_\w+",
         "Validation functions", "Find validators"),
        ("gap", r"from\s+\w+\s+import",
         "Import statements", "Find all imports"),
        ("function_definition", r"raise\s+\w+Error|raise\s+\w+Exception",
         "Exception raising", "Find error throwing"),
        ("class_definition", r"@dataclass",
         "Dataclass definitions", "Find all dataclasses"),
        ("function_definition", r"def\s+to_dict|def\s+from_",
         "Serialization methods", "Find serializers"),
    ]

    def strategy_name(self) -> str:
        return "regex_patterns"

    def generate(self, metadata: List[Dict]) -> List[Suggestion]:
        suggestions = []
        available_types = {meta.get("chunk_type", "") for meta in metadata}

        for required_type, pattern, description, label in self.REGEX_SUGGESTIONS:
            if required_type in available_types:
                suggestions.append(Suggestion(
                    query=pattern,
                    category=SuggestionCategory.REGEX,
                    description=description,
                    mode="regex",
                    relevance=0.85,
                ))

        return suggestions


class FileSuggestionStrategy(SuggestionStrategy):
    """Generate suggestions based on file structure.

    Analyzes file paths to suggest queries about specific
    modules, directories, or architectural layers.
    """

    # Maps directory names to semantic queries
    DIRECTORY_QUERIES: Dict[str, str] = {
        "models": "What data models are defined?",
        "services": "How do the service classes work?",
        "routes": "What API endpoints are available?",
        "utils": "What utility functions exist?",
        "config": "How is the application configured?",
        "templates": "How is the UI structured?",
    }

    def strategy_name(self) -> str:
        return "file_analysis"

    def generate(self, metadata: List[Dict]) -> List[Suggestion]:
        suggestions = []
        directories = self._extract_directories(metadata)

        for dir_name in directories:
            dir_lower = dir_name.lower()
            if dir_lower in self.DIRECTORY_QUERIES:
                suggestions.append(Suggestion(
                    query=self.DIRECTORY_QUERIES[dir_lower],
                    category=SuggestionCategory.FILE,
                    description=f"Based on {dir_name}/ directory",
                    relevance=0.75,
                ))

        return suggestions

    @staticmethod
    def _extract_directories(metadata: List[Dict]) -> Set[str]:
        """Extract unique directory names from file paths."""
        directories = set()
        for meta in metadata:
            path = meta.get("path", "")
            parts = path.replace("\\", "/").split("/")
            for part in parts[:-1]:  # Exclude filename
                if part and not part.startswith("."):
                    directories.add(part)
        return directories


@dataclass
class SuggestionService:
    """Orchestrates multiple suggestion strategies.

    Combines symbol analysis, pattern detection, conceptual queries,
    regex suggestions, and file-based suggestions into a single
    unified suggestion set.
    """
    strategies: List[SuggestionStrategy] = field(default_factory=lambda: [
        SymbolSuggestionStrategy(),
        PatternSuggestionStrategy(),
        ConceptSuggestionStrategy(),
        RegexSuggestionStrategy(),
        FileSuggestionStrategy(),
    ])

    def get_suggestions(
        self,
        collection: chromadb.Collection,
        max_suggestions: int = 20,
    ) -> SuggestionSet:
        """Generate suggestions by analyzing collection metadata."""
        result = collection.get(include=["metadatas"])
        metadata = result.get("metadatas", [])

        if not metadata:
            return SuggestionSet(
                collection_name=collection.name,
            )

        all_suggestions: List[Suggestion] = []

        for strategy in self.strategies:
            generated = strategy.generate(metadata)
            all_suggestions.extend(generated)

        # Sort by relevance and deduplicate
        all_suggestions.sort(key=lambda s: s.relevance, reverse=True)
        seen_queries: Set[str] = set()
        deduped: List[Suggestion] = []
        for s in all_suggestions:
            if s.query not in seen_queries:
                seen_queries.add(s.query)
                deduped.append(s)

        return SuggestionSet(
            suggestions=deduped[:max_suggestions],
            collection_name=collection.name,
        )
