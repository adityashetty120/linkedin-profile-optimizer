# Setup Guide

## Prerequisites

- Python 3.8+
- pip package manager
- Virtual environment (venv/conda)

## Required API Keys

| Service | Purpose | Free Tier |
|---------|---------|-----------|
| [Google Gemini](https://ai.google.dev/) | LLM (AI responses) | 1,500 calls/day |
| [Apify](https://apify.com/) | LinkedIn scraping | $5 free credit |
| [Tavily](https://tavily.com/) | Online job search (optional) | 1,000 calls/month |

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/adityashetty120/linkedin-profile-optimizer.git
cd linkedin-profile-optimizer
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Get API Keys

**Google Gemini API:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

**Apify API:**
1. Visit [Apify Console](https://console.apify.com/account/integrations)
2. Sign up (free tier available)
3. Go to Settings → Integrations
4. Copy API token

**Tavily API (Optional):**
1. Visit [Tavily](https://app.tavily.com/)
2. Sign up for free account
3. Copy API key from dashboard

### 5. Configure Environment
```bash
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
```

Edit `.env`:
```bash
GEMINI_API_KEY=your_gemini_key_here
APIFY_API_KEY=apify_api_xxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxx  # Optional

LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.6
```

### 6. Run Application
```bash
streamlit run app.py
```

Access at: `http://localhost:8501`

## Configuration Options

### LLM Model Selection
```bash
LLM_MODEL=gemini-2.5-flash       # Default (fastest, latest)
# LLM_MODEL=gemini-1.5-flash     # Alternative (balanced)
# LLM_MODEL=gemini-1.5-pro       # Premium (more capable)
```

### Temperature Control
```bash
LLM_TEMPERATURE=0.6              # Default
# 0.0-0.3: Focused, deterministic
# 0.4-0.7: Balanced (recommended)
# 0.8-1.0: Creative, varied
```

### Custom Port
```bash
streamlit run app.py --server.port 8502
```

## Troubleshooting

### ❌ Import Errors
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### ❌ LinkedIn Scraping Fails

**Causes:**
- Invalid URL format (use: `https://www.linkedin.com/in/username`)
- Private profile settings
- Apify rate limits or insufficient credits

**Fix:**
- Verify URL format
- Check Apify dashboard for errors/credits
- Wait 1 minute and retry

### ❌ Gemini API Errors

**Causes:**
- Invalid API key
- Rate limit exceeded (1,500/day on free tier)
- Network issues

**Fix:**
```bash
# Verify key in .env
echo %GEMINI_API_KEY%  # Windows
# echo $GEMINI_API_KEY  # macOS/Linux
```
- Check [Google AI Studio](https://aistudio.google.com/) for usage limits

### ❌ Port Already in Use
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### ❌ Streamlit Not Found
```bash
# Ensure virtual environment is activated
where python  # Windows
# which python  # macOS/Linux

# Should show venv path
pip install streamlit
```

### 🗑️ Clear Session Data
```bash
# Windows
del data\user_profiles\session_*.json

# macOS/Linux
# rm data/user_profiles/session_*.json
```

## Testing (Optional)

```bash
# Test imports
python -c "import streamlit; import langchain; import langgraph; print('✅ All packages OK')"

# Run tests if available
pytest tests/ -v

# Check Python version
python --version  # Should be 3.8+
```

## Quick Reference

| Task | Command |
|------|---------|
| Activate venv | `venv\Scripts\activate` (Windows) |
| Run app | `streamlit run app.py` |
| Change port | `streamlit run app.py --server.port 8502` |
| Clear cache | `streamlit cache clear` |
| View logs | Check terminal output |

## Next Steps

✅ Load your LinkedIn profile  
✅ Set target role and career goals  
✅ Try "Analyze my profile"  
✅ Experiment with job matching  
✅ Customize prompts in `src/utils/prompts.py`

📖 **Further Reading:**
- [Architecture](architecture.md) - System design details
- [README](../README.md) - Usage examples and features