# ChromaDB Code Search UI

A Flask web application for searching, browsing, and visualizing Python code using semantic embeddings and ChromaDB.

## Purpose

This app serves two roles in the course:

1. **Teaching material** — Students ingest this codebase into ChromaDB using AST-based chunking pipelines they build in the labs. The well-structured Python code (models, services, routes, utils) makes it an ideal target for practicing chunking strategies.
2. **Interactive tool** — Once ingested, students launch this app to explore their collections, run searches, and see how their chunking and metadata decisions affect retrieval quality.

## Features

- **Semantic search** — Natural language queries over code using OpenAI embeddings (`text-embedding-3-small`)
- **Regex search** — Structural pattern matching across the codebase with analysis and explanation
- **Collection explorer** — Paginated chunk browser with filters by file path, chunk type, and symbol name
- **Code statistics** — Construct detection, size distributions, and symbol rankings
- **Embedding visualizer** — 2D PCA projections of chunk embeddings to explore clustering
- **Smart suggestions** — Context-aware query suggestions based on collection metadata
- **Query history and bookmarks** — Persistent search history with color-coded bookmarks
- **Interactive tutorials** — Guided tours with spotlight overlays for onboarding

## Project Structure

```
app/
├── app.py                  # Flask application factory and entry point
├── config.py               # Dataclass-based configuration (env vars, defaults)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
│
├── models/                 # Data models
│   ├── chunk.py            # Chunk, ChunkMetadata, ChunkType
│   ├── search_result.py    # SearchResult, SearchResultSet, ResultFormatter
│   └── query_history.py    # QueryRecord, Bookmark, HistoryManager
│
├── routes/                 # Flask blueprints (one per feature)
│   ├── search.py           # Semantic and regex search endpoints
│   ├── collections.py      # Collection CRUD and ingestion triggers
│   ├── explorer.py         # Paginated chunk browsing with filters
│   ├── similarity.py       # Pairwise similarity matrix computation
│   ├── history.py          # Query history and bookmarks API
│   ├── regex_tester.py     # Regex testing and analysis
│   ├── suggestions.py      # Smart query suggestions
│   ├── statistics.py       # Code metrics and analytics
│   ├── visualizer.py       # 2D embedding visualization
│   └── tutorial.py         # Interactive guided tours
│
├── services/               # Business logic layer
│   ├── chroma_client.py    # ChromaDB connection manager (singleton)
│   ├── search_service.py   # Search strategies (semantic + regex)
│   ├── collection_service.py   # Collection management and stats
│   ├── ingestion_service.py    # AST parsing and code chunking pipeline
│   ├── similarity_service.py   # Vector similarity computations
│   ├── statistics_service.py   # Code metrics and analysis
│   ├── visualization_service.py # PCA and random projection reducers
│   ├── suggestion_service.py   # Multi-strategy suggestion generator
│   └── tutorial_service.py     # Tutorial builder and manager
│
├── utils/                  # Utilities and helpers
│   ├── validators.py       # Input validation (queries, paths, regex)
│   ├── regex_engine.py     # Regex analysis and human-readable explanation
│   ├── code_parser.py      # Lightweight regex-based Python parser
│   ├── text_splitter.py    # Token-based text splitting
│   └── formatters.py       # Display formatting (scores, code, paths)
│
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Base layout with navbar and tutorial engine
│   ├── index.html          # Dashboard (collection cards)
│   ├── search.html         # Search interface
│   ├── explorer.html       # Chunk browser
│   └── collection.html     # Collection detail page
│
└── static/
    └── css/style.css       # Custom styles
```

## Design Patterns

The codebase intentionally demonstrates several software design patterns, making it a richer target for code search exercises:

- **Strategy** — `SearchStrategy`, `SimilarityComputer`, `DimensionReducer`, `SuggestionStrategy`
- **Singleton** — `ChromaClientManager` for a single DB connection
- **Factory** — `get_reducer()`, `get_similarity_computer()`, `get_tutorial_builder()`
- **Builder** — Tutorial builders (`DashboardTutorialBuilder`, `CollectionTutorialBuilder`)
- **Facade** — `SearchService`, `SuggestionService`, `StatisticsService` wrapping multiple strategies

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or, with [uv](https://docs.astral.sh/uv/) (a faster drop-in alternative to pip):
   ```bash
   uv venv && source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

2. Configure environment variables (copy `.env.example` to `.env`):
   ```
   OPENAI_API_KEY=sk-your-key-here
   CHROMA_PERSIST_DIR=./chroma_data
   ```

3. Run the app:
   ```bash
   python app.py
   ```

## Dependencies

| Package | Purpose |
|---------|---------|
| flask | Web framework |
| chromadb | Vector database |
| openai | Embedding API |
| tiktoken | Token counting |
| tree-sitter | AST parsing |
| tree-sitter-python | Python grammar for tree-sitter |
| python-dotenv | Environment variable management |
| pathspec | `.gitignore` pattern matching |
