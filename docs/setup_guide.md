# Setup Guide

## Prerequisites

### Required
- Python 3.8 or higher
- pip package manager
- Virtual environment tool (venv or conda)

### API Keys
You'll need API keys for:
1. **Google Gemini API** (for AI capabilities - gemini-2.0-flash-exp)
2. **Apify** (for LinkedIn scraping)

## Step-by-Step Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/linkedin-profile-optimizer.git
cd linkedin-profile-optimizer
```

### 2. Create Virtual Environment

**Using venv:**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Using conda:**
```bash
conda create -n linkedin-optimizer python=3.10
conda activate linkedin-optimizer
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Get API Keys

#### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Select or create a Google Cloud project
5. Copy the API key

#### Apify API Key
1. Go to [Apify](https://apify.com/)
2. Sign up for a free account
3. Go to Settings → Integrations
4. Copy your API token

### 5. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` file:
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
APIFY_API_KEY=apify_api_xxxxxxxxxxxxxxxxxxxxxxxx

# LLM Configuration
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.7
```

### 6. Test Installation
```bash
# Test imports
python -c "import streamlit; import langchain; import langgraph; print('All packages installed successfully!')"

# Run tests
pytest tests/ -v
```

### 7. Run the Application
```bash
streamlit run app.py
```

The application should open in your browser at `http://localhost:8501`

## Configuration Options

### LLM Provider Selection

**For Google Gemini:**
```bash
LLM_PROVIDER=google
LLM_MODEL=gemini-2.5-flash  # Latest Gemini 2.5 Flash model
```

**Alternative Gemini Models:**
- `gemini-1.5-pro`: More capable, higher cost
- `gemini-1.5-flash`: Balanced performance
- `gemini-2.5-flash`: Latest, fastest model with enhanced capabilities

### Adjusting Temperature

- Lower (0.0-0.3): More focused, deterministic responses
- Medium (0.4-0.7): Balanced creativity and consistency
- Higher (0.8-1.0): More creative, varied responses
```bash
LLM_TEMPERATURE=0.7
```

### Custom Data Directory
```bash
DATABASE_PATH=data/user_profiles/profiles.db
```

## Troubleshooting

### Issue: Import Errors

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Apify Scraping Fails

**Possible Causes:**
1. Invalid LinkedIn URL format
2. Profile privacy settings
3. Apify API rate limits

**Solution:**
- Ensure URL format: `https://www.linkedin.com/in/username`
- Check Apify dashboard for errors
- Wait if rate limited

### Issue: LLM API Errors

**Possible Causes:**
1. Invalid API key
2. Insufficient credits
3. Rate limiting

**Solution:**
- Verify API key in `.env`
- Check account balance/credits
- Implement retry logic or wait

### Issue: Streamlit Port Already in Use

**Solution:**
```bash
streamlit run app.py --server.port 8502
```

### Issue: Memory/Performance Issues

**Solution:**
- Reduce conversation history length
- Clear old session data:
```bash
rm -rf data/user_profiles/session_*.json
```
- Use faster Gemini model (gemini-1.5-flash)

## Development Setup

### Enable Debug Mode
```bash
DEBUG=True
```

### Install Development Dependencies
```bash
pip install pytest pytest-cov black flake8 mypy
```

### Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

### Run Linting
```bash
black src/ tests/
flake8 src/ tests/
mypy src/
```

## Deployment

### Deploy to Streamlit Cloud

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Add secrets in dashboard (API keys)
5. Deploy!


## Next Steps

- Read [Architecture Documentation](architecture.md)
- Explore example queries in README
- Customize prompts in `src/utils/prompts.py`
- Add new job descriptions in `src/services/job_description_service.py`
````