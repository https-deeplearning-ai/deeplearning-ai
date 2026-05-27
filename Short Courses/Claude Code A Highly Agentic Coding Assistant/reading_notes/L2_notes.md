# Lesson 2: Setup & Codebase Understanding

## How to Run the RAG Chatbot Application?
- Fork this [repo](https://github.com/https-deeplearning-ai/starting-ragchatbot-codebase.git)
- Clone the forked repo to your local machine
- Follow the instructions in the [README.md file](https://github.com/https-deeplearning-ai/starting-ragchatbot-codebase/blob/main/README.md):
    - If you're using Windows, use Git Bash to run all the commands of the readme file (requires [Git for Windows](https://git-scm.com/downloads/win)). In VS Code, make sure to choose `Git Bash` when you open the terminal.
    - The RAG chatbot application is powered by Claude Sonnet 4 for which you need to specify an Anthropic API key ([Anthropic Console](https://console.anthropic.com/login?returnTo=%2F%3F)). You may choose to enter a fake key and run the application to see how it looks like, but the answers to the queries will fail.  
- You can keep the application running in the background, while going through the lessons. 


## Codebase Exploration

Here are some suggested questions to Claude Code:

<details>
<summary>Give me an overview of this codebase</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

Course Materials RAG System Overview

This is a Retrieval-Augmented Generation (RAG) system designed for querying course materials using semantic search and AI-powered responses.

Architecture

Backend (Python/FastAPI):
  - app.py - FastAPI server with CORS/proxy support, serves frontend and API endpoints
  - rag_system.py - Main orchestrator coordinating all components
  - vector_store.py - ChromaDB integration for semantic search
  - ai_generator.py - Anthropic Claude integration for response generation
  - document_processor.py - Text processing and chunking
  - search_tools.py - Tool-based search functionality
  - session_manager.py - Conversation history management
  - models.py - Pydantic models (Course, Lesson, CourseChunk)

Frontend (HTML/CSS/JavaScript):
  - Modern web interface with chat functionality
  - Course statistics sidebar
  - Suggested questions
  - Markdown response rendering

Data Storage:
  - ChromaDB vector database (/chroma_db/)
  - Course documents in /docs/ (txt, pdf, docx support)

Key Features

  - Semantic search across course materials using sentence transformers
  - AI-powered responses with Claude Sonnet 4
  - Session-based conversation history
  - Tool-based search architecture
  - Course analytics and statistics
  - Automatic document processing and chunking
  - Web interface with real-time chat

Dependencies

Python 3.13+, ChromaDB, Anthropic API, FastAPI, sentence-transformers, uvicorn

The system loads course documents on startup and provides both API endpoints (/api/query, /api/courses) and a web interface at http://localhost:8000.

</div>
</details>

<details>
<summary>What are the key data models?</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

The key data models are defined using Pydantic:

  1. Course (models.py:10-15)
  - title: Course name (used as unique identifier)
  - course_link: Optional URL to course
  - instructor: Optional instructor name
  - lessons: List of Lesson objects

  2. Lesson (models.py:4-8)
  - lesson_number: Sequential number (0, 1, 2...)
  - title: Lesson title
  - lesson_link: Optional URL to specific lesson

  3. CourseChunk (models.py:17-22)
  - content: Text content of the chunk
  - course_title: Parent course identifier
  - lesson_number: Optional lesson association
  - chunk_index: Position within document

  4. SearchResults (vector_store.py:8-32)
  - documents: List of retrieved text chunks
  - metadata: Associated metadata for each chunk
  - distances: Similarity scores
  - error: Optional error message

  These models create a hierarchical structure: Course → Lessons → CourseChunks, enabling structured storage and retrieval of
   educational content with proper context preservation.

</div>
</details>

<details>
<summary>Explain how the documents are processed</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

The document processing system in this codebase works through several key components:

Document Processing Flow

1. Document Reading & Structure Parsing (document_processor.py:13-21)
  - Reads files with UTF-8 encoding, falls back to error-ignoring mode if needed
  - Expects structured format with course metadata in first 3 lines:
    - Line 1: Course Title
    - Line 2: Course Link
    - Line 3: Course Instructor

2. Text Chunking (document_processor.py:25-91)
  - Splits documents into sentence-based chunks with configurable size and overlap
  - Uses regex to detect sentence boundaries while handling abbreviations
  - Maintains context overlap between chunks for better retrieval

3. Course Structure Extraction (document_processor.py:97-259)
  - Parses lesson markers (e.g., "Lesson 0: Introduction")
  - Extracts lesson titles and optional lesson links
  - Creates structured Course and Lesson objects
  - Generates CourseChunk objects with lesson context

4. Vector Storage (vector_store.py:34-267)
  - Uses ChromaDB with sentence transformer embeddings
  - Maintains two collections:
    - course_catalog: Course metadata for semantic search
    - course_content: Actual chunked content for retrieval
  - Supports filtered search by course name and lesson number

Key Features:
  - Preserves lesson structure and adds contextual information to chunks
  - Handles edge cases like files without lesson markers
  - Enables semantic search across courses and within specific lessons
  - Maintains metadata for linking back to original content

The system transforms raw course transcripts into searchable, contextually-aware chunks stored in a vector database for RAG applications.

</div>
</details>

<details>
<summary>What is the format of the document expected by the document_processor?</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

Based on the document_processor.py code, the expected document format is:

  Required Structure:
  Course Title: [title]
  Course Link: [url]
  Course Instructor: [instructor]

  Lesson 0: [lesson title]
  Lesson Link: [optional lesson url]
  [lesson content...]

  Lesson 1: [lesson title]
  Lesson Link: [optional lesson url]
  [lesson content...]

  Key Format Rules:
  - Lines 1-3: Course metadata (title, link, instructor)
  - Lesson markers: Must start with "Lesson [number]: [title]" (case-insensitive)
  - Lesson links: Optional "Lesson Link: [url]" immediately after lesson marker
  - Content: Everything else becomes lesson content until next lesson marker

  Example:
  Course Title: Introduction to Python
  Course Link: https://example.com/python-course
  Course Instructor: John Doe

  Lesson 0: Getting Started
  Lesson Link: https://example.com/lesson0
  Welcome to Python programming. In this lesson we'll cover...

  Lesson 1: Variables and Data Types
  Basic data types in Python include strings, integers...

  Fallback Behavior:
  - If no lesson markers found, treats entire content after line 3 as one document
  - Missing metadata lines use defaults (filename for title, "Unknown" for instructor)
  - Empty lines and whitespace are handled gracefully

  The processor extracts this structure into Course/Lesson objects and creates contextual chunks for vector storage.


</div>
</details>

<details>
<summary>How are the course chunks loaded to the database?</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

Course chunks are loaded to the database through this process:

  1. Document Processing (rag_system.py:39)
  course, course_chunks = self.document_processor.process_course_document(file_path)
  - DocumentProcessor reads file and creates CourseChunk objects with content, metadata, and lesson context

  2. Vector Store Addition (rag_system.py:45, vector_store.py:162-180)
  self.vector_store.add_course_content(course_chunks)
  - Extracts content from each chunk
  - Creates metadata with course title, lesson number, and chunk index
  - Generates unique IDs: {course_title}_{chunk_index}
  - Adds to ChromaDB course_content collection with embeddings

  3. Loading Triggers:

  Startup Loading (app.py:88-98)
  - Automatically loads all documents from ../docs folder on server startup
  - Calls rag_system.add_course_folder()

  Batch Folder Processing (rag_system.py:52-94)
  - Processes all .txt, .pdf, .docx files in a folder
  - Checks for existing courses to avoid duplicates
  - Can optionally clear existing data first

  Key Steps in ChromaDB Storage:
  1. Documents → chunk content strings
  2. Metadata → course/lesson/chunk info
  3. IDs → unique identifiers per chunk
  4. Embeddings → generated automatically by sentence transformer

  The system ensures no duplicate courses and maintains referential integrity between course metadata and co

</div>
</details>

<details>
<summary>Trace the process of handling user's query from frontend to backend</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

Frontend → Backend Flow

  1. Frontend User Interaction (script.js:45-96)
  - User types query and clicks send or presses Enter
  - sendMessage() disables input, adds user message to chat
  - Makes POST request to /api/query with query and session_id

  2. FastAPI Endpoint (app.py:56-74)
  - Receives POST to /api/query with QueryRequest model
  - Creates new session if none provided: rag_system.session_manager.create_session()
  - Calls rag_system.query(request.query, session_id)

  3. RAG System Processing (rag_system.py:102-140)
  - Formats query into prompt: "Answer this question about course materials: {query}"
  - Retrieves conversation history from session manager
  - Calls AI generator with tools and conversation context
  - Gets sources from tool manager after AI completes
  - Updates conversation history with Q&A pair

  4. AI Generation (ai_generator.py:43-80)
  - Creates Claude API call with system prompt and conversation history
  - Includes search tools if available
  - Sends query to Anthropic Claude API
  - Handles tool calls (search) if AI decides to use them

  5. Tool Execution (when AI calls search)
  - AI can call search tool with specific course/lesson filters
  - Tool manager executes vector store search
  - Returns relevant course chunks to AI
  - AI synthesizes results into final response

  6. Response Path Back
  - AI generator returns response string
  - RAG system returns (response, sources) tuple
  - FastAPI formats as QueryResponse JSON
  - Frontend receives JSON, updates session_id if new
  - Displays response with optional sources in chat

  Key Features:
  - Session management maintains conversation context
  - Tool-based architecture allows AI to search when needed
  - Vector store enables semantic search across course content
  - Error handling at each layer with graceful fallbacks

</div>
</details>

<details>
<summary>Draw a diagram that illustrates this flow</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

RAG SYSTEM QUERY FLOW DIAGRAM
================================

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FRONTEND      │    │    FASTAPI       │    │   RAG SYSTEM    │
│   (script.js)   │    │    (app.py)      │    │ (rag_system.py) │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │ 1. POST /api/query    │                       │
         │ {query, session_id}   │                       │
         ├──────────────────────▶│                       │
         │                       │ 2. rag_system.query() │
         │                       ├──────────────────────▶│
         │                       │                       │
         │                       │                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ SESSION MANAGER │    │   AI GENERATOR   │    │   TOOL MANAGER  │
│(session_mgr.py) │    │ (ai_generator.py)│    │(search_tools.py)│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                       ▲                       │
         │ 3. get_history()      │ 4. generate_response() │
         │                       │    + tools             │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE SONNET 4                             │
│  System: "You are an AI assistant with course search tool..."   │
│  Tools: [CourseSearchTool]                                      │
│  Query: "Answer this question about course materials: ..."     │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 5. Tool Decision
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ COURSE SEARCH   │    │   VECTOR STORE   │    │    CHROMADB     │
│     TOOL        │    │ (vector_store.py)│    │                 │
│(search_tools.py)│    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │ 6. execute(query,     │                       │
         │    course_name,       │                       │
         │    lesson_number)     │                       │
         ├──────────────────────▶│ 7. search()          │
         │                       ├──────────────────────▶│
         │                       │                       │
         │                       │                       │
         │                       │ ┌─────────────────────┤
         │                       │ │ course_catalog      │
         │                       │ │ - Course resolution │
         │                       │ │                     │
         │                       │ │ course_content      │
         │                       │ │ - Semantic search   │
         │                       │ └─────────────────────┤
         │                       │                       │
         │                       │ 8. SearchResults      │
         │ 9. Formatted results  │◀──────────────────────┤
         │◀──────────────────────┤                       │
         │                       │                       │

         │ 10. Tool results back to Claude
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLAUDE SONNET 4                             │
│  Synthesizes tool results into final answer                    │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ 11. Final response
                                 ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   RAG SYSTEM    │    │    FASTAPI       │    │   FRONTEND      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │ 12. (response,        │                       │
         │     sources)          │                       │
         ├──────────────────────▶│ 13. QueryResponse     │
         │                       │ {answer, sources,     │
         │                       │  session_id}          │
         │                       ├──────────────────────▶│
         │                       │                       │
         │                       │                       │ 14. Update UI
         │                       │                       │ - Add message
         │                       │                       │ - Show sources
         │                       │                       │ - Store session

FLOW SUMMARY:
1. User query → FastAPI endpoint
2. RAG system gets conversation history  
3. AI Generator calls Claude with tools
4. Claude decides to use CourseSearchTool
5. Tool searches ChromaDB collections
6. Results formatted and returned to Claude
7. Claude synthesizes final answer
8. Response flows back through layers
9. Frontend displays answer with sources
```

KEY ARCHITECTURE POINTS:
========================

**Dual ChromaDB Collections**: 
- `course_catalog` for name resolution
- `course_content` for semantic search

**Tool-Based Search**: 
- Claude decides when to search vs. use general knowledge

**Session Continuity**: 
- Conversation history maintained across queries

**Error Handling**: 
- Each layer handles failures gracefully

**Source Tracking**: 
- Search results include course/lesson context for UI

DETAILED COMPONENT BREAKDOWN:
============================

Frontend (script.js):
- Handles user input and displays responses
- Manages session state and loading animations
- Renders sources and markdown content

FastAPI (app.py):
- Provides REST API endpoints
- Handles request/response serialization
- Manages CORS and static file serving

RAG System (rag_system.py):
- Main orchestrator coordinating all components
- Manages session creation and conversation history
- Routes queries through AI generator with tools

AI Generator (ai_generator.py):
- Interfaces with Claude Sonnet 4 API
- Handles tool calling workflow
- Manages conversation context and system prompts

Search Tools (search_tools.py):
- Implements CourseSearchTool for semantic search
- Formats search results with course/lesson context
- Tracks sources for UI display

Vector Store (vector_store.py):
- ChromaDB wrapper with dual collection strategy
- Provides course name resolution and content search
- Uses sentence-transformers for embeddings

Session Manager (session_manager.py):
- Maintains conversation history per session
- Provides context for follow-up questions

</div>
</details>


<details>
<summary>Explain how the text is transformed into chunks? What is the size of each chunk?</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**
Looking at the chunking process in document_processor.py:25-91:

  Text Chunking Process

  1. Text Preprocessing (lines 28-29)
  - Normalizes whitespace: re.sub(r'\s+', ' ', text.strip())
  - Removes extra spaces and line breaks

  2. Sentence Splitting (lines 31-38)
  - Uses regex to split on sentence boundaries: (?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s+(?=[A-Z])
  - Handles abbreviations (avoids splitting on "Mr.", "Dr.", etc.)
  - Splits on periods, exclamation marks, question marks followed by capital letters

  3. Chunk Building Algorithm (lines 40-91)
  - Sentence-based chunking: Builds chunks by adding complete sentences
  - Size limit: Stops adding sentences when current_size + sentence_length > chunk_size
  - Overlap calculation: Uses configurable overlap between chunks for context preservation

  Chunk Size Configuration

  The chunk size comes from config.py settings:

⏺ Read(backend/config.py)
  ⎿  Read 30 lines (ctrl+r to expand)

⏺ Chunk Configuration

  - Chunk Size: 800 characters (config.py:19)
  - Chunk Overlap: 100 characters (config.py:20)

  Chunking Strategy

  Smart Sentence Boundaries:
  - Never splits mid-sentence - always completes sentences
  - If a single sentence exceeds 800 chars, it becomes its own chunk
  - Maintains readability and context

  Overlap Implementation (lines 67-83):
  - Counts backwards from end of current chunk
  - Includes previous sentences up to 100 characters
  - Ensures context continuity between chunks
  - Prevents information loss at chunk boundaries

  Context Enhancement (lines 184-188, 232-234):
  - First chunk of each lesson: "Lesson {N} content: {chunk}"
  - Other chunks: "Course {title} Lesson {N} content: {chunk}"
  - Adds lesson/course context for better retrieval

  Example Process:
  Input: "This is sentence one. This is sentence two. This is sentence three."
  ↓
  Chunks with 800 char limit, 100 char overlap:
  - Chunk 1: "Lesson 1 content: This is sentence one. This is sentence two."
  - Chunk 2: "This is sentence two. This is sentence three." (overlap)

  This approach balances chunk size for embedding efficiency while preserving semantic meaning and context.



</div>
</details>

<details>
<summary>Describe the api endpoints</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

Based on app.py, the API has these endpoints:

  API Endpoints

  POST /api/query

  Purpose: Process user queries and return AI-generated responses

  Request Model (app.py:38-41):
  {
    "query": "string",
    "session_id": "string" // optional
  }

  Response Model (app.py:43-47):
  {
    "answer": "string",
    "sources": ["string"],
    "session_id": "string"
  }

  Process (app.py:56-74):
  - Creates new session if none provided
  - Calls RAG system to process query
  - Returns AI response with sources and session ID
  - Handles errors with 500 status code

  GET /api/courses

  Purpose: Get course analytics and statistics

  Response Model (app.py:49-52):
  {
    "total_courses": 0,
    "course_titles": ["string"]
  }

  Process (app.py:76-86):
  - Calls rag_system.get_course_analytics()
  - Returns course count and list of all course titles
  - Used by frontend to display available courses

  Static File Serving

  Mount: "/" → ../frontend/ (app.py:119)
  - Serves frontend HTML, CSS, JS files
  - Uses custom DevStaticFiles class with no-cache headers for development
  - Enables SPA routing with html=True

  Middleware Configuration

  CORS (app.py:24-32):
  - Allows all origins (allow_origins=["*"])
  - Enables credentials and all methods/headers
  - Required for frontend-backend communication

  TrustedHost (app.py:18-22):
  - Allows all hosts (allowed_hosts=["*"])
  - Handles proxy configurations

  Startup Event (app.py:88-98)

  - Automatically loads documents from ../docs folder
  - Processes course files into vector database
  - Logs loading progress and errors

  The API follows REST principles with clear request/response models and proper error handling.
</div>
</details>

<details>
<summary>How can I run the application?</summary>

<div style="margin-left: 20px;">

**Sample Answer from Claude Code**

Based on the codebase, here are the ways to run the application:

  **Quick Start (Recommended)**

  chmod +x run.sh
  ./run.sh

  **Manual Start**

  cd backend
  uv run uvicorn app:app --reload --port 8000

  **Prerequisites**

  1. Make sure you have uv installed
  2. Install dependencies: uv sync
  3. Create a .env file with your Anthropic API key:
  ANTHROPIC_API_KEY=your_anthropic_api_key_here

  The application will be available at:
  - Web Interface: http://localhost:8000
  - API Documentation: http://localhost:8000/docs

</div>
</details>


## Summary of Claude Code Commands

### Managing Project Memory

- `/init`: Claude Code scans your codebase and creates CLAUDE.md file inside your project directory.
    -  CLAUDE.md guides Claude through your codebase, pointing out important commands, architecture and coding style. It's automatically included in the context each time you launch Claude Code.
    - Here's an [example](https://github.com/https-deeplearning-ai/ragchatbot-codebase/blob/main/CLAUDE.md) of a CLAUDE.md file generated by `init` for the RAG chatbot example.

- `#`: Use `#` to quickly add a memory. Useful when you see Claude Code repeats an error.
    - **Example 1**: since the project is a `uv` project, we added these to CLAUDE.md file using `#`:
        - `#`use uv to run python files or add any dependencies
    - **Example 2**: you can inform Claude Code about the database schema, in this case since you have a vector database, you can inform Claude Code about the collections stored in the vector database:
        - `#`The vector database has two collections:
            - `course_catalog`:
                - stores course titles for name resolution
                - metadata for each course: title, instructor, course_link, lesson_count, lessons_json (list of lessons: lesson_number, lesson_title, lesson_link)
            - `course_content`:
                - stores text chunks for semantic search
                - metadata for each chunk: course_title, lesson_number, chunk_index

### Managing the Context of Claude Code

| Command | Description |
|---------|-------------|
| `/clear` | clears current conversation history |
| `/compact` | summarizes current conversation history |
| `ESC` | interrupt Claude to redirect or correct it |
| `ESC ESC` | rewind the conversation to an earlier point in time |

You can use regular bash command within Claude Code, but you need to start the command with `!` (for example: `!pwd`). You can type `exit` to quit Claude Code. 

