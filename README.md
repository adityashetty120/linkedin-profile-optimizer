# LinkedIn Profile Optimizer 💼

An AI-powered chat system that helps users optimize their LinkedIn profiles, analyze job fit, and receive personalized career guidance.

## 🌟 Features

- **Profile Analysis**: Extract and evaluate LinkedIn profile sections, identifying gaps and inconsistencies
- **Job Fit Analysis**: Compare profiles with job descriptions and generate match scores
- **Content Enhancement**: Generate improved versions of profile sections aligned with industry best practices
- **Career Counseling**: Identify skill gaps and suggest learning resources
- **Memory System**: Maintains context across conversations for personalized experience

## 🏗️ Architecture

The application uses a **multi-agent system** built with **LangGraph**:

### 🤖 Intelligent Agents

1. **Profile Analyzer Agent**
   - Analyzes profile completeness and quality
   - Assigns letter grades (A-F)
   - Identifies improvement opportunities

2. **Job Matcher Agent**
   - Compares profiles with job requirements
   - Calculates semantic similarity scores
   - Finds skill gaps and missing keywords

3. **Content Generator Agent**
   - Rewrites profile sections for maximum impact
   - Optimizes for ATS systems
   - Incorporates relevant keywords naturally

4. **Career Counselor Agent**
   - Provides career guidance and mentorship
   - Suggests skill development paths
   - Recommends learning resources

### 🔄 Workflow
```
User Query → Router → Agent Selection → Processing → Response
     ↓                                       ↓
Memory System                         Context Integration
```

**Powered by**: Google Gemini 2.5 Flash, LangChain, LangGraph

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for:
  - Google Gemini API (for LLM - gemini-2.5-flash)
  - Apify (for LinkedIn scraping)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/linkedin-profile-optimizer.git
cd linkedin-profile-optimizer
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the application:
```bash
streamlit run app.py
```

## 📁 Project Structure
```
linkedin-profile-optimizer/
├── src/
│   ├── agents/          # Agent implementations
│   ├── services/        # External service integrations
│   ├── memory/          # Memory management
│   ├── utils/           # Helper functions and prompts
│   ├── config/          # Configuration
│   └── graph/           # LangGraph workflow
├── data/                # User data storage
├── docs/                # Documentation
├── tests/               # Unit tests
└── app.py               # Main Streamlit app
```

## 🎯 Usage

### Getting Started

1. **Load Profile**: Enter your LinkedIn URL in the sidebar
   - Format: `https://www.linkedin.com/in/your-username`
   - Click "🔄 Load Profile"
   - Wait 10-30 seconds for scraping

2. **Set Goals**: 
   - Enter your **Target Role** (e.g., "Data Analyst")
   - Describe your **Career Goals** (optional)

3. **Start Chatting**: Ask questions in natural language!

### Example Queries

**Profile Analysis**:
- "Analyze my LinkedIn profile"
- "What's my profile completeness score?"
- "Which sections of my profile need improvement?"

**Job Matching**:
- "How well do I match a Data Analyst role?"
- "Compare my profile to this job description: [paste JD]"
- "What skills am I missing for a Software Engineer position?"

**Content Generation**:
- "Generate suggestions for all sections of my LinkedIn profile"
- "Give me comprehensive optimization suggestions for my entire profile"
- "Rewrite my About section for a Product Manager role"
- "Improve my headline to attract recruiters"
- "Optimize my experience section for ATS systems"
- "Help me improve my skills section"

**Career Counseling**:
- "What skills should I learn to become a Senior Developer?"
- "Suggest courses for machine learning career transition"
- "Create a 6-month learning plan for Data Science"

### 💡 Pro Tips

- **Be Specific**: "Rewrite my About section for a Senior Data Analyst role in healthcare" works better than "improve my profile"
- **Iterate**: Start with analysis, then ask follow-up questions
- **Use Context**: The AI remembers your conversation, no need to repeat information
- **Personalize**: Always review and customize AI-generated content before using it

## 🔧 Configuration

Edit `src/config/settings.py` or `.env` file:
```bash
# LLM Configuration
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here
APIFY_API_KEY=your_apify_key_here
```

## 🧪 Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## 📚 Documentation

- [Architecture](docs/architecture.md)
- [Setup Guide](docs/setup_guide.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://python.langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Profile scraping via [Apify](https://apify.com/)
- UI built with [Streamlit](https://streamlit.io/)

## 📊 Tech Stack

- **Frontend**: Streamlit
- **AI Framework**: LangChain, LangGraph
- **LLM**: Google Gemini (gemini-2.0-flash-exp)
- **Web Scraping**: Apify LinkedIn Scraper
- **Data Processing**: pandas, scikit-learn, sentence-transformers
- **Storage**: JSON-based file storage (upgradeable to PostgreSQL/MongoDB)

## 💰 Cost Estimation

With **Gemini 2.0 Flash** (Free Tier):
- ~1500 API calls/day FREE
- Each conversation: ~3-5 API calls
- **Estimate**: 300-500 conversations/day at ZERO cost! 🎉

Paid tier: ~$0.00015 per conversation (extremely affordable)

## ⭐ Why Choose This Tool?

✅ **AI-Powered**: Cutting-edge Gemini 2.0 Flash model  
✅ **Cost-Effective**: Free tier for development & testing  
✅ **Intelligent**: Multi-agent system for specialized tasks  
✅ **Context-Aware**: Remembers your profile & preferences  
✅ **Actionable**: Specific, implementable recommendations  
✅ **ATS-Optimized**: Improves visibility to recruiters  
✅ **Career Guidance**: Not just profile optimization  

## 🎯 Use Cases

- **Job Seekers**: Optimize profile for dream job
- **Career Switchers**: Align profile with new industry
- **Students**: Build strong professional presence
- **Recruiters**: Understand profile quality metrics
- **Career Coaches**: Tool for client consultations

## 📧 Contact

For questions or support, please open an issue on GitHub.