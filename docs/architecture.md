# System Architecture

## Overview

Multi-agent system built with **LangGraph** where specialized agents handle profile analysis, job matching, content generation, and career counseling. Routes user queries intelligently and maintains conversation context through persistent memory.

## Architecture Layers

### 1. Frontend (Streamlit)
- Conversational UI with chat interface
- Sidebar for profile loading and configuration
- Session state management
- Real-time streaming responses

### 2. Multi-Agent System

| Agent | Responsibility |
|-------|---------------|
| **Profile Analyzer** | Evaluates completeness, assigns grades, identifies gaps |
| **Job Matcher** | Calculates match scores, finds missing skills, compares with JD |
| **Content Generator** | Rewrites sections, optimizes for ATS, adds keywords |
| **Career Counselor** | Career guidance, skill development paths, learning resources |

### 3. Service Layer
- **LLM Service** - Google Gemini API integration (gemini-2.5-flash)
- **LinkedIn Scraper** - Apify actor for profile extraction
- **Job Description Service** - Default JD database + Tavily search (optional)

### 4. Memory System
- **Memory Manager** - Session-based conversation context
- **Checkpointer** - LangGraph state persistence
- **JSON Storage** - File-based user profile and session data

### 5. LangGraph Workflow

```
User Query
    ↓
Router Node (LLM determines agent)
    ↓
Agent Node (Process query)
    ↓
Response Formatter
    ↓
Memory Storage → User Response
```

**Key Features:**
- Dynamic agent routing based on query intent
- State management via `GraphState` class
- Memory integration for context-aware responses
- Checkpointing for conversation persistence

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **UI** | Streamlit |
| **Framework** | LangChain, LangGraph |
| **LLM** | Google Gemini 2.5 Flash |
| **Scraping** | Apify (LinkedIn Profile Scraper actor) |
| **Embeddings** | sentence-transformers |
| **Storage** | JSON files (session-based) |
| **Config** | python-dotenv, pydantic-settings |

## Design Patterns

**1. Multi-Agent Pattern**
- Independent, specialized agents
- Coordinated via LangGraph state graph
- Router-based dynamic agent selection

**2. Memory Pattern**
- Session-based conversation context
- Profile and analysis caching
- JSON persistence for user data

**3. Service Pattern**
- External APIs abstracted into services
- Separation of concerns (scraping, LLM, job search)
- Easy to swap implementations

**4. State Management**
- LangGraph `GraphState` with typed fields
- Immutable state transitions
- Memory checkpointing for resumability

## Data Flow Details

### Profile Loading
```
LinkedIn URL → Apify API → Raw JSON → MemoryManager → GraphState
```

### Query Processing
```
User Query → LLM Router → Agent Selection → Agent Processing
    ↓                                              ↓
Memory Context                            LLM Service (Gemini)
    ↓                                              ↓
Previous Analyses                          Formatted Response
    ↓                                              ↓
    └──────────────── Memory Storage ←─────────────┘
```

### Job Matching
```
Custom JD / Online Search (Tavily) → Job Description Service
    ↓
Profile + JD → Job Matcher Agent → Similarity Score + Gap Analysis
```

## Security & Privacy

✅ API keys in `.env` (not committed)  
✅ Session isolation (UUID-based)  
✅ Local data storage  
✅ No profile data logging  
✅ Secure API communication (HTTPS)

## Scalability Considerations

**Current:**
- File-based storage (good for single user)
- Synchronous processing
- Local session management

**Future Enhancements:**
- PostgreSQL/MongoDB for multi-user support
- Redis for caching and faster retrieval
- Async processing with background workers
- Rate limiting and request queuing
- Analytics dashboard for insights


