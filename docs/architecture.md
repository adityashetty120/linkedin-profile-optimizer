# System Architecture

## Overview

The LinkedIn Profile Optimizer is built using a multi-agent architecture powered by LangGraph, with each agent specializing in specific tasks.

## Components

### 1. Frontend Layer (Streamlit)
- User interface for profile input and chat interaction
- Session state management
- Real-time response display

### 2. Agent Layer
Four specialized agents handle different tasks:

#### Profile Analyzer Agent
- Evaluates profile completeness
- Identifies gaps and weak sections
- Provides actionable feedback

#### Job Matcher Agent
- Compares profiles with job descriptions
- Calculates semantic similarity scores
- Identifies missing skills and keywords

#### Content Generator Agent
- Rewrites profile sections
- Optimizes for ATS systems
- Incorporates relevant keywords

#### Career Counselor Agent
- Provides career guidance
- Identifies skill gaps
- Suggests learning paths

### 3. Service Layer
- **LLM Service**: Handles AI model interactions
- **LinkedIn Scraper**: Integrates with Apify for profile extraction
- **Job Description Service**: Manages job description retrieval

### 4. Memory Layer
- **Session Memory**: Temporary conversation context
- **Persistent Memory**: Long-term user data storage
- **Checkpointer**: LangGraph state persistence

### 5. Workflow (LangGraph)
Orchestrates the flow between agents:
1. Router determines which agent to use
2. Selected agent processes the query
3. Response formatter prepares the output
4. Memory system stores the interaction

## Data Flow
User Input → Router → Agent Selection → Processing → Response Formatting → Output
                ↓                           ↓
          Memory Storage              Results Cache
````

## Technology Stack

- **Frontend**: Streamlit
- **AI Framework**: LangChain, LangGraph
- **LLM Providers**: Google Gemini (gemini-2.5-flash)
- **Web Scraping**: Apify LinkedIn Scraper
- **Data Processing**: pandas, scikit-learn, sentence-transformers
- **Storage**: JSON-based file storage

## Design Patterns

### Multi-Agent Pattern
Each agent is independent and specialized, coordinated through LangGraph's state management.

### Memory Pattern
Implements both short-term (session) and long-term (persistent) memory for context retention.

### Service Pattern
External integrations are abstracted into service classes for maintainability.

## Security Considerations

- API keys stored in environment variables
- User data stored locally with session isolation
- No sensitive profile data transmitted except through secure APIs

## Scalability

- Stateless agent design allows horizontal scaling
- Memory system can be migrated to database (PostgreSQL, Redis)
- Agent processing can be parallelized for multiple users

## Future Enhancements

1. Database integration (PostgreSQL)
2. Caching layer (Redis)
3. Async processing for better performance
4. Advanced analytics dashboard
5. Multi-language support
````


