"""Interactive tutorial and onboarding service.

Manages step-by-step guided tours for different pages of the
application. Each tutorial highlights UI elements and explains
their purpose to help new users discover features.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Dict, Optional


class TutorialPage(Enum):
    """Pages that have tutorials available."""
    DASHBOARD = "dashboard"
    COLLECTION = "collection"
    EXPLORER = "explorer"


class HighlightPosition(Enum):
    """Where to position the tooltip relative to the target."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class StepCategory(Enum):
    """Categories of tutorial steps for theming."""
    NAVIGATION = auto()
    ACTION = auto()
    INFORMATION = auto()
    FEATURE = auto()
    TIP = auto()


@dataclass
class TutorialStep:
    """A single step in a guided tutorial.

    Each step targets a CSS selector, shows a tooltip with
    a title and description, and optionally highlights the
    target element with a spotlight effect.
    """
    selector: str
    title: str
    description: str
    position: HighlightPosition = HighlightPosition.BOTTOM
    category: StepCategory = StepCategory.INFORMATION
    icon: str = ""
    pulse: bool = False

    def to_dict(self) -> Dict:
        return {
            "selector": self.selector,
            "title": self.title,
            "description": self.description,
            "position": self.position.value,
            "category": self.category.name.lower(),
            "icon": self.icon,
            "pulse": self.pulse,
        }


@dataclass
class TutorialSequence:
    """An ordered sequence of tutorial steps for a page.

    Contains all the steps for a complete guided tour,
    along with metadata like the welcome message and
    completion text.
    """
    page: TutorialPage
    title: str
    welcome_message: str
    steps: List[TutorialStep] = field(default_factory=list)
    completion_message: str = "You're all set!"
    completion_icon: str = "bi-check-circle"

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def to_dict(self) -> Dict:
        return {
            "page": self.page.value,
            "title": self.title,
            "welcome_message": self.welcome_message,
            "steps": [s.to_dict() for s in self.steps],
            "step_count": self.step_count,
            "completion_message": self.completion_message,
            "completion_icon": self.completion_icon,
        }


class TutorialBuilder(ABC):
    """Abstract builder for creating tutorial sequences.

    Subclasses define the steps for specific pages using
    the builder pattern with fluent method chaining.
    """

    def __init__(self):
        self._steps: List[TutorialStep] = []

    def add_step(self, selector: str, title: str, description: str,
                 position: HighlightPosition = HighlightPosition.BOTTOM,
                 category: StepCategory = StepCategory.INFORMATION,
                 icon: str = "", pulse: bool = False) -> "TutorialBuilder":
        """Add a step and return self for chaining."""
        self._steps.append(TutorialStep(
            selector=selector,
            title=title,
            description=description,
            position=position,
            category=category,
            icon=icon,
            pulse=pulse,
        ))
        return self

    @abstractmethod
    def build(self) -> TutorialSequence:
        """Build the complete tutorial sequence."""
        ...


class DashboardTutorialBuilder(TutorialBuilder):
    """Builds the dashboard page tutorial.

    Guides users through collection management, creation,
    ingestion, and navigation to search/browse features.
    """

    def build(self) -> TutorialSequence:
        self.add_step(
            selector=".navbar-brand",
            title="Welcome to ChromaDB Code Search!",
            description="This app lets you vectorize Python code and search it using semantic queries or regex patterns. Let's take a quick tour!",
            position=HighlightPosition.BOTTOM,
            category=StepCategory.NAVIGATION,
            icon="bi-database",
        ).add_step(
            selector="[data-bs-target='#createModal']",
            title="Create a Collection",
            description="Click here to create a new ChromaDB collection. You can also ingest a directory of Python files directly during creation.",
            position=HighlightPosition.BOTTOM,
            category=StepCategory.ACTION,
            icon="bi-plus-lg",
            pulse=True,
        ).add_step(
            selector=".collection-card",
            title="Your Collections",
            description="Each card shows a collection with its chunk count. Collections store vectorized code chunks that you can search through.",
            position=HighlightPosition.BOTTOM,
            category=StepCategory.INFORMATION,
            icon="bi-collection",
        ).add_step(
            selector=".btn-success",
            title="Search a Collection",
            description="Click 'Search' to open the collection's search page, where you can run semantic queries or regex patterns against the vectorized code.",
            position=HighlightPosition.TOP,
            category=StepCategory.ACTION,
            icon="bi-search",
            pulse=True,
        ).add_step(
            selector=".btn-outline-info",
            title="Browse Chunks",
            description="Click 'Browse' to explore all code chunks in a collection with filtering by file, type, or symbol name.",
            position=HighlightPosition.TOP,
            category=StepCategory.FEATURE,
            icon="bi-code-square",
        )

        return TutorialSequence(
            page=TutorialPage.DASHBOARD,
            title="Dashboard Tour",
            welcome_message="Let's explore the ChromaDB Code Search dashboard!",
            steps=self._steps,
            completion_message="You're ready to go! Create a collection or explore an existing one.",
            completion_icon="bi-rocket-takeoff",
        )


class CollectionTutorialBuilder(TutorialBuilder):
    """Builds the collection/search page tutorial.

    Walks users through semantic search, regex search,
    visualizations, heatmaps, suggestions, and statistics.
    """

    def build(self) -> TutorialSequence:
        self.add_step(
            selector="#semanticTab",
            title="Semantic Search",
            description="Type a natural language query like 'how does validation work?' and ChromaDB will find the most semantically similar code chunks using embeddings.",
            position=HighlightPosition.RIGHT,
            category=StepCategory.FEATURE,
            icon="bi-chat-dots",
        ).add_step(
            selector="#regexTab",
            title="Regex Search",
            description="Switch to regex mode to search with regular expressions. ChromaDB's built-in full-text search handles the pattern matching server-side.",
            position=HighlightPosition.RIGHT,
            category=StepCategory.FEATURE,
            icon="bi-regex",
        ).add_step(
            selector="#suggestionsDetails",
            title="Smart Suggestions",
            description="The app analyzes your code to suggest relevant queries. Click any suggestion chip to instantly run that search!",
            position=HighlightPosition.RIGHT,
            category=StepCategory.TIP,
            icon="bi-lightbulb",
        ).add_step(
            selector="#historyDetails",
            title="Search History",
            description="Your recent searches are saved here. Click any past search to replay it instantly.",
            position=HighlightPosition.RIGHT,
            category=StepCategory.FEATURE,
            icon="bi-clock-history",
        ).add_step(
            selector="#bookmarkDetails",
            title="Bookmarks",
            description="Found a useful result? Click the bookmark icon on any search result to save it for later.",
            position=HighlightPosition.RIGHT,
            category=StepCategory.TIP,
            icon="bi-bookmark-star",
        ).add_step(
            selector="[onclick='showStats()']",
            title="Code Statistics",
            description="Click 'Stats' to see detailed analytics: line counts, code constructs, chunk size distribution, and a leaderboard of the largest symbols.",
            position=HighlightPosition.BOTTOM,
            category=StepCategory.FEATURE,
            icon="bi-bar-chart-line",
        ).add_step(
            selector="[onclick='showViz()']",
            title="Embedding Visualizer",
            description="Click 'Visualize' to see a 2D scatter plot of all embeddings. Similar code clusters together! You can click two points to compare their code.",
            position=HighlightPosition.BOTTOM,
            category=StepCategory.FEATURE,
            icon="bi-diagram-2",
        ).add_step(
            selector="[data-bs-target='#ingestModal']",
            title="Ingest More Code",
            description="Need to add more files? Click 'Ingest' to vectorize another directory into this collection.",
            position=HighlightPosition.BOTTOM,
            category=StepCategory.ACTION,
            icon="bi-upload",
        )

        return TutorialSequence(
            page=TutorialPage.COLLECTION,
            title="Search Page Tour",
            welcome_message="Let's discover all the search and analysis features!",
            steps=self._steps,
            completion_message="You're ready to search! Try a semantic query or click a suggestion to get started.",
            completion_icon="bi-stars",
        )


def get_tutorial_builder(page: TutorialPage) -> TutorialBuilder:
    """Factory function to get the appropriate tutorial builder."""
    builders = {
        TutorialPage.DASHBOARD: DashboardTutorialBuilder,
        TutorialPage.COLLECTION: CollectionTutorialBuilder,
    }
    builder_class = builders.get(page)
    if builder_class is None:
        raise ValueError(f"No tutorial defined for page: {page.value}")
    return builder_class()


@dataclass
class TutorialManager:
    """Manages tutorial sequences for all pages.

    Provides a unified interface to retrieve tutorial data
    for any page in the application.
    """

    def get_tutorial(self, page_name: str) -> Optional[TutorialSequence]:
        """Get the tutorial for a given page name."""
        try:
            page = TutorialPage(page_name)
        except ValueError:
            return None

        builder = get_tutorial_builder(page)
        return builder.build()

    def list_available(self) -> List[Dict]:
        """List all available tutorials with metadata."""
        tutorials = []
        for page in TutorialPage:
            try:
                builder = get_tutorial_builder(page)
                seq = builder.build()
                tutorials.append({
                    "page": page.value,
                    "title": seq.title,
                    "step_count": seq.step_count,
                })
            except ValueError:
                continue
        return tutorials
