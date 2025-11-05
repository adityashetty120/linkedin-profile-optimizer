# LinkedIn Profile Optimizer 💼

AI-powered conversational assistant that analyzes LinkedIn profiles, matches them with job descriptions, and provides personalized career guidance using multi-agent architecture.

## 🌟 Features

- **Profile Analysis** - Evaluate profile completeness, assign grades, identify gaps
- **Job Matching** - Compare profiles with job descriptions, calculate match scores, find missing skills
- **Content Generation** - Rewrite profile sections optimized for ATS systems
- **Career Guidance** - Personalized skill development recommendations and learning paths
- **Persistent Memory** - Context-aware conversations using session-based memory

## 🏗️ Architecture

Multi-agent system built with **LangGraph** and **Google Gemini**:

**Agents:**
1. **Profile Analyzer** - Analyzes profile quality and completeness
2. **Job Matcher** - Matches profiles with job requirements
3. **Content Generator** - Optimizes profile content for ATS
4. **Career Counselor** - Provides personalized career guidance

**Workflow:** `User Query → Router → Agent → LLM Processing → Memory Storage → Response`

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [Google Gemini API Key](https://ai.google.dev/) (Free tier available)
- [Apify API Key](https://apify.com/) (for LinkedIn scraping)
- [Tavily API Key](https://tavily.com/) (optional, for online job search)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/adityashetty120/linkedin-profile-optimizer.git
cd linkedin-profile-optimizer

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your API keys:
# GEMINI_API_KEY=your_key_here
# APIFY_API_KEY=your_key_here
# TAVILY_API_KEY=your_key_here (optional)

# 5. Run application
streamlit run app.py
```

## 📁 Project Structure
```
linkedin-profile-optimizer/
├── app.py              # Streamlit UI
├── src/
│   ├── agents/         # 4 specialized agents
│   ├── services/       # LLM, scraper, job search
│   ├── memory/         # Session memory & checkpointing
│   ├── graph/          # LangGraph workflow & state
│   ├── config/         # Settings & environment
│   └── utils/          # Prompts & helpers
├── data/               # Session storage (JSON)
└── docs/               # Documentation
```

## 🎯 Usage

1. **Load Profile** - Enter LinkedIn URL → Click "Load Profile" (10-30s)
2. **Analyze Profile** - Click "� Analyze Profile" for comprehensive evaluation
3. **Set Goals** - Add target role and career aspirations
4. **Add Job Description** - Paste custom JD or enable online search
5. **Job Fit Analysis** - Click "🎯 Job Fit Analysis" for match score
6. **Chat** - Ask follow-up questions in natural language

### Example Queries

- "Analyze my LinkedIn profile"
- "How well do I match this Data Analyst role?"
- "Rewrite my About section for Product Manager"
- "What skills should I learn for Senior Developer?"
- "Create a 6-month learning plan for Data Science"
- "Optimize my headline for ATS systems"

## 🔧 Configuration

Key settings in `.env`:
```bash
GEMINI_API_KEY=your_key          # Required
APIFY_API_KEY=your_key           # Required
TAVILY_API_KEY=your_key          # Optional (for online job search)
LLM_MODEL=gemini-2.5-flash       # Default model
LLM_TEMPERATURE=0.6              # Response creativity (0-1)
```

## 📊 Tech Stack

| Component | Technology |
|-----------|-----------|
| **UI** | Streamlit |
| **AI Framework** | LangChain, LangGraph |
| **LLM** | Google Gemini 2.5 Flash |
| **Scraping** | Apify LinkedIn Scraper |
| **Memory** | JSON file storage |
| **Embeddings** | sentence-transformers |

## 💰 Cost Estimation

**Gemini 2.5 Flash Free Tier:**
- 1,500 requests/day FREE
- ~3-5 API calls per conversation
- **≈ 300-500 conversations/day at $0 cost**

Paid tier: ~$0.00015/conversation (when you exceed free tier)

## 📚 Documentation

- [Architecture Details](docs/architecture.md)
- [Setup Guide](docs/setup_guide.md)

## 🤝 Contributing

Contributions welcome! Open an issue or submit a PR.

## � License

MIT License - See LICENSE file for details.