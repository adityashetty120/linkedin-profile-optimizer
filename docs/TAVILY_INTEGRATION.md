# Tavily API Integration for Job Descriptions

## Overview

The LinkedIn Profile Optimizer now supports **real-time job description fetching** using the Tavily API. This allows the application to search and retrieve actual job postings from major job boards.

## Features

✅ **Real-time job data** from LinkedIn, Indeed, Glassdoor, and more  
✅ **AI-powered summaries** from Tavily's search engine  
✅ **Automatic skill extraction** from job descriptions  
✅ **Fallback system** to default descriptions if search fails  
✅ **Location-based search** for targeted results  

## Setup

### 1. Get Tavily API Key

1. Visit [https://tavily.com](https://tavily.com)
2. Sign up for a free account
3. Get your API key from the dashboard
4. **Free tier**: 1,000 searches/month

### 2. Configure Environment

Add your API key to `.env`:

```env
TAVILY_API_KEY=tvly-your-api-key-here
```

### 3. Verify Configuration

Run the example script:

```bash
python example_tavily_usage.py
```

## Usage

### Basic Usage (Default Descriptions)

```python
from src.services.job_description_service import JobDescriptionService

job_service = JobDescriptionService()

# Uses default job description
jd = job_service.get_job_description(
    job_title="Data Scientist"
)
```

### Using Tavily Online Search

```python
# Search real job postings online
jd = job_service.get_job_description(
    job_title="Machine Learning Engineer",
    location="San Francisco",
    use_online_search=True  # Enable Tavily search
)

print(f"Source: {jd['source']}")  # 'tavily_search'
print(f"Description: {jd['description']}")
print(f"Skills: {jd['skills']}")
```

### Custom Job Description

```python
# Use a custom job description
custom_jd = """
Senior Python Developer needed with experience in:
- Django/Flask frameworks
- PostgreSQL and Redis
- AWS deployment
- Docker containers
"""

jd = job_service.get_job_description(
    job_title="Python Developer",
    custom_description=custom_jd
)
```

### In Job Matcher Agent

```python
from src.agents.job_matcher import JobMatcherAgent
from src.services.llm_service import LLMService
from src.services.job_description_service import JobDescriptionService

llm_service = LLMService()
job_service = JobDescriptionService()
job_matcher = JobMatcherAgent(llm_service, job_service)

# Match profile with online job search
match_result = job_matcher.match(
    profile_data=user_profile,
    job_title="Software Engineer",
    location="Remote",
    use_online_search=True  # Search real job postings
)
```

## Priority System

The service uses a **4-tier fallback system**:

1. **Custom Description** (if provided by user)
   - Source: `user_provided`
   
2. **Tavily Online Search** (if enabled and API key available)
   - Source: `tavily_search`
   - Searches: LinkedIn, Indeed, Glassdoor, Monster, ZipRecruiter
   
3. **Default Database** (pre-defined for common roles)
   - Source: `default_database`
   - Roles: Data Scientist, Software Engineer, Product Manager, Data Analyst, Marketing Manager
   
4. **Generic Fallback** (if no match found)
   - Source: `generic`

## Tavily Search Configuration

The search is optimized for job descriptions:

```python
{
    "search_depth": "advanced",      # Comprehensive results
    "include_domains": [             # Job boards only
        "linkedin.com",
        "indeed.com",
        "glassdoor.com",
        "monster.com",
        "ziprecruiter.com"
    ],
    "max_results": 5,                # Top 5 results
    "include_answer": True,          # AI summary
    "include_raw_content": True      # Full content
}
```

## Response Format

```python
{
    "title": "Software Engineer",
    "description": "Full job description text...",
    "source": "tavily_search",  # or 'user_provided', 'default_database', 'generic'
    "skills": ["Python", "AWS", "Docker", "SQL", ...]
}
```

## Cost & Limits

- **Free tier**: 1,000 searches/month
- **Cost**: $0.005 per search (paid plans)
- **Timeout**: 10 seconds per request
- **Rate limit**: Based on your Tavily plan

## Error Handling

The service handles errors gracefully:

```python
✅ No API key → Falls back to default descriptions
✅ API timeout → Falls back to default descriptions
✅ Network error → Falls back to default descriptions
✅ Invalid response → Falls back to default descriptions
```

All errors are logged but don't break the application.

## Best Practices

1. **Use online search selectively** - Save API calls by using defaults for common roles
2. **Cache results** - Store frequently requested JDs to avoid redundant searches
3. **Provide location** - More specific searches yield better results
4. **Monitor usage** - Track API calls to stay within limits

## Troubleshooting

### API Key Not Working

```bash
# Verify API key is loaded
python -c "from src.config.settings import settings; print(settings.tavily_api_key)"
```

### Online Search Not Activating

```python
# Check all conditions:
jd = job_service.get_job_description(
    job_title="Developer",
    use_online_search=True,  # Must be True
    # tavily_api_key must be set in .env
)
```

### No Results Found

- Try a more general job title
- Remove location to broaden search
- Check if job boards have listings for that role

## Examples

See `example_tavily_usage.py` for complete working examples.

## Support

For issues or questions:
- Tavily API: [https://docs.tavily.com](https://docs.tavily.com)
- Project: Check the main README.md

---

**Note**: This integration is optional. The application works perfectly fine with default job descriptions if you don't configure Tavily API.
