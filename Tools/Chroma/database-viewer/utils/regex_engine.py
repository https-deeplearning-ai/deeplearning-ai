"""Regex analysis engine for pattern testing and explanation.

Provides detailed regex match analysis including group extraction,
pattern complexity scoring, and human-readable explanations of
common regex constructs.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict, Tuple


class PatternComplexity(Enum):
    """Complexity rating for a regex pattern."""
    SIMPLE = auto()
    MODERATE = auto()
    COMPLEX = auto()
    ADVANCED = auto()


@dataclass
class MatchSpan:
    """A single match occurrence with position information."""
    start: int
    end: int
    text: str
    line_number: int
    groups: Dict[str, str] = field(default_factory=dict)

    @property
    def length(self) -> int:
        return self.end - self.start

    def to_dict(self) -> dict:
        return {
            "start": self.start,
            "end": self.end,
            "text": self.text,
            "line_number": self.line_number,
            "length": self.length,
            "groups": self.groups,
        }


@dataclass
class MatchResult:
    """Complete result of testing a pattern against text."""
    pattern: str
    text_length: int
    matches: List[MatchSpan] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def match_count(self) -> int:
        return len(self.matches)

    @property
    def is_valid(self) -> bool:
        return self.error is None

    @property
    def unique_matches(self) -> List[str]:
        """Deduplicated match texts."""
        seen = set()
        unique = []
        for m in self.matches:
            if m.text not in seen:
                seen.add(m.text)
                unique.append(m.text)
        return unique

    @property
    def coverage_percentage(self) -> float:
        """Percentage of the text covered by matches."""
        if self.text_length == 0:
            return 0.0
        matched_chars = sum(m.length for m in self.matches)
        return min(100.0, (matched_chars / self.text_length) * 100)

    def to_dict(self) -> dict:
        return {
            "pattern": self.pattern,
            "match_count": self.match_count,
            "unique_count": len(self.unique_matches),
            "coverage_pct": round(self.coverage_percentage, 1),
            "matches": [m.to_dict() for m in self.matches],
            "unique_matches": self.unique_matches[:20],
            "is_valid": self.is_valid,
            "error": self.error,
        }


class PatternAnalyzer:
    """Analyzes regex patterns for complexity and potential issues.

    Examines pattern constructs to provide a complexity rating
    and identify common pitfalls like catastrophic backtracking.
    """

    # Regex constructs mapped to complexity weights
    CONSTRUCT_WEIGHTS: Dict[str, Tuple[str, int]] = {
        r"\\.": ("escape sequence", 1),
        r"\[.*?\]": ("character class", 1),
        r"\((?!\?)": ("capture group", 2),
        r"\(\?:": ("non-capture group", 2),
        r"\(\?P<": ("named group", 3),
        r"\(\?=": ("lookahead", 4),
        r"\(\?!": ("negative lookahead", 4),
        r"\(\?<=": ("lookbehind", 5),
        r"\(\?<!": ("negative lookbehind", 5),
        r"[+*]{2,}": ("nested quantifier", 5),
        r"\{(\d+),(\d+)?\}": ("bounded quantifier", 2),
        r"[|]": ("alternation", 1),
    }

    def analyze(self, pattern: str) -> Dict:
        """Analyze a pattern and return complexity info."""
        try:
            compiled = re.compile(pattern)
        except re.error as e:
            return {
                "is_valid": False,
                "error": str(e),
                "complexity": None,
                "group_count": 0,
                "named_groups": [],
                "constructs": [],
            }

        constructs = self._detect_constructs(pattern)
        total_weight = sum(w for _, w in constructs)
        complexity = self._rate_complexity(total_weight)
        named_groups = list(compiled.groupindex.keys())

        return {
            "is_valid": True,
            "error": None,
            "complexity": complexity.name.lower(),
            "complexity_score": total_weight,
            "group_count": compiled.groups,
            "named_groups": named_groups,
            "constructs": [name for name, _ in constructs],
        }

    def _detect_constructs(self, pattern: str) -> List[Tuple[str, int]]:
        """Detect regex constructs present in the pattern."""
        found = []
        for construct_pattern, (name, weight) in self.CONSTRUCT_WEIGHTS.items():
            if re.search(construct_pattern, pattern):
                found.append((name, weight))
        return found

    @staticmethod
    def _rate_complexity(total_weight: int) -> PatternComplexity:
        """Rate pattern complexity based on total construct weight."""
        if total_weight <= 2:
            return PatternComplexity.SIMPLE
        elif total_weight <= 5:
            return PatternComplexity.MODERATE
        elif total_weight <= 10:
            return PatternComplexity.COMPLEX
        return PatternComplexity.ADVANCED


class RegexExplainer:
    """Generates human-readable explanations of regex patterns.

    Maps common regex tokens to plain English descriptions,
    useful for learners who are new to regular expressions.
    """

    TOKEN_EXPLANATIONS: Dict[str, str] = {
        r"\d": "any digit (0-9)",
        r"\D": "any non-digit",
        r"\w": "any word character (letter, digit, underscore)",
        r"\W": "any non-word character",
        r"\s": "any whitespace (space, tab, newline)",
        r"\S": "any non-whitespace",
        r"\b": "word boundary",
        r"\B": "non-word boundary",
        r".": "any character except newline",
        r"^": "start of line",
        r"$": "end of line",
        r"*": "zero or more of the previous",
        r"+": "one or more of the previous",
        r"?": "zero or one of the previous (optional)",
        r"|": "OR (either side matches)",
    }

    COMMON_PATTERNS: Dict[str, str] = {
        r"def\s+\w+": "Python function definitions",
        r"class\s+\w+": "Python class definitions",
        r"import\s+\w+": "Python import statements",
        r"#.*$": "Python comments",
        r'\"\"\".*?\"\"\"': "Python docstrings",
        r"@\w+": "Python decorators",
        r"self\.\w+": "Python instance attributes",
        r"\w+\s*=\s*": "variable assignments",
        r"def\s+__\w+__": "Python dunder methods",
        r"raise\s+\w+": "Python raise statements",
    }

    def explain(self, pattern: str) -> Dict:
        """Generate a human-readable explanation of the pattern."""
        tokens = self._tokenize_explanations(pattern)
        common_match = self._match_common_pattern(pattern)

        return {
            "pattern": pattern,
            "tokens": tokens,
            "common_pattern": common_match,
            "summary": self._build_summary(tokens, common_match),
        }

    def _tokenize_explanations(self, pattern: str) -> List[Dict[str, str]]:
        """Break down pattern into explained tokens."""
        tokens = []
        for token, explanation in self.TOKEN_EXPLANATIONS.items():
            if token in pattern:
                tokens.append({"token": token, "meaning": explanation})
        return tokens

    def _match_common_pattern(self, pattern: str) -> Optional[str]:
        """Check if the pattern matches a well-known code search pattern."""
        for common, description in self.COMMON_PATTERNS.items():
            if pattern.strip() == common or common in pattern:
                return description
        return None

    @staticmethod
    def _build_summary(tokens: List[Dict], common: Optional[str]) -> str:
        """Build a one-line summary of what the pattern does."""
        if common:
            return f"This pattern matches {common}."
        if not tokens:
            return "This pattern matches literal text."
        parts = [t["meaning"] for t in tokens[:3]]
        return f"Uses: {', '.join(parts)}."


@dataclass
class RegexTester:
    """Main class for testing regex patterns against text.

    Combines matching, analysis, and explanation into a single interface.
    """
    analyzer: PatternAnalyzer = field(default_factory=PatternAnalyzer)
    explainer: RegexExplainer = field(default_factory=RegexExplainer)

    def test(self, pattern: str, text: str,
             max_matches: int = 100) -> MatchResult:
        """Test a pattern against text and return detailed results."""
        try:
            compiled = re.compile(pattern, re.MULTILINE)
        except re.error as e:
            return MatchResult(
                pattern=pattern,
                text_length=len(text),
                error=str(e),
            )

        matches = []
        lines = text.split("\n")
        line_offsets = self._compute_line_offsets(lines)

        for match in compiled.finditer(text):
            if len(matches) >= max_matches:
                break

            line_num = self._offset_to_line(match.start(), line_offsets)
            groups = {}
            for name, value in match.groupdict().items():
                if value is not None:
                    groups[name] = value
            for i, group in enumerate(match.groups(), 1):
                if group is not None and str(i) not in groups:
                    groups[f"group_{i}"] = group

            matches.append(MatchSpan(
                start=match.start(),
                end=match.end(),
                text=match.group(0),
                line_number=line_num,
                groups=groups,
            ))

        return MatchResult(
            pattern=pattern,
            text_length=len(text),
            matches=matches,
        )

    def full_analysis(self, pattern: str, text: str) -> Dict:
        """Run test + analysis + explanation in one call."""
        result = self.test(pattern, text)
        analysis = self.analyzer.analyze(pattern)
        explanation = self.explainer.explain(pattern)

        return {
            **result.to_dict(),
            "analysis": analysis,
            "explanation": explanation,
        }

    @staticmethod
    def _compute_line_offsets(lines: List[str]) -> List[int]:
        """Compute the character offset where each line starts."""
        offsets = [0]
        for line in lines[:-1]:
            offsets.append(offsets[-1] + len(line) + 1)
        return offsets

    @staticmethod
    def _offset_to_line(offset: int, line_offsets: List[int]) -> int:
        """Convert a character offset to a 1-based line number."""
        for i in range(len(line_offsets) - 1, -1, -1):
            if offset >= line_offsets[i]:
                return i + 1
        return 1
