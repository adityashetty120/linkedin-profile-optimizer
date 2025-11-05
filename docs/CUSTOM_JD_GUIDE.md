# Custom Job Description - User Guide

## How to Use Custom Job Descriptions in the LinkedIn Profile Optimizer

### Overview

You can now provide job descriptions in **three different ways**:

1. **Paste Custom JD** - Copy/paste any job description
2. **Search Online** - Use Tavily API to fetch real job postings
3. **Use Default** - Pre-defined JDs for common tech roles

---

## Method 1: Paste Custom Job Description

### Steps:

1. **Load Your Profile**
   - Enter your LinkedIn URL in the sidebar
   - Click "🔄 Load Profile"

2. **Set Target Role**
   - Enter the job title (e.g., "Software Engineer")

3. **Select Custom JD Option**
   - In the sidebar, under "📋 Job Description"
   - Select **"Paste Custom JD"** radio button

4. **Paste the Job Description**
   - Copy the full job description from the job posting
   - Paste it into the text area
   - You'll see a confirmation: "✅ Custom JD loaded (X characters)"

5. **Analyze Your Fit**
   - Click **"🎯 Job Match"** button, OR
   - Type questions like:
     - "How well do I match this job?"
     - "What skills am I missing for this role?"
     - "Optimize my profile for this job description"

### Example Custom JD:

```
We are seeking a Senior Full Stack Developer to join our team.

Requirements:
- 5+ years of software development experience
- Strong proficiency in React and Node.js
- Experience with Python and Django
- Knowledge of AWS cloud services
- Familiarity with Docker and Kubernetes
- PostgreSQL and MongoDB database skills

Responsibilities:
- Design and build scalable web applications
- Collaborate with product and design teams
- Mentor junior developers
- Participate in code reviews

Nice to Have:
- Experience with microservices architecture
- CI/CD pipeline experience
- GraphQL knowledge
```

---

## Method 2: Search for Real Job Postings Online

### Prerequisites:

✅ Tavily API key configured in `.env` file:
```env
TAVILY_API_KEY=tvly-your-api-key-here
```

### Steps:

1. **Select Default/Search Online**
   - Choose **"Use Default/Search Online"** radio button

2. **Enter Location (Optional)**
   - Example: "San Francisco, CA"
   - Example: "Remote"
   - Example: "New York"

3. **Enable Online Search**
   - Check ✅ **"🔍 Search for real job postings online"**

4. **Set Target Role & Analyze**
   - Enter job title: "Machine Learning Engineer"
   - Click **"🎯 Job Match"**

### What Happens:

- Tavily searches LinkedIn, Indeed, Glassdoor, etc.
- Returns actual job descriptions from real postings
- Extracts requirements and skills automatically
- Provides AI-generated summary

### Note:

⚠️ If no API key is configured, you'll see:
```
⚠️ Tavily API key not configured. Will use default JD database.
```

---

## Method 3: Use Default Job Descriptions

### Steps:

1. **Select Default/Search Online**
   - Choose **"Use Default/Search Online"** radio button

2. **Leave "Search online" UNCHECKED**

3. **Set Target Role**
   - Choose one of these roles:
     - Data Scientist
     - Software Engineer
     - Data Analyst
     - Product Manager
     - Marketing Manager

4. **Click "🎯 Job Match"**

### What Happens:

- Uses pre-defined comprehensive job descriptions
- Includes common requirements and skills
- Good for general analysis when you don't have a specific JD

---

## Tips & Best Practices

### ✅ DO:

- **Include full job descriptions** - More context = better analysis
- **Copy entire posting** - Include requirements, responsibilities, and nice-to-haves
- **Update target role** - Match it to the JD title
- **Ask specific questions** - "What keywords should I add for ATS?"

### ❌ DON'T:

- **Paste partial JDs** - Missing info leads to incomplete analysis
- **Mix multiple jobs** - Analyze one role at a time
- **Forget to set target role** - Required for job matching
- **Include company-specific info** - Focus on role requirements

---

## Common Questions & Answers

### Q: Can I switch between custom JD and online search?

**A:** Yes! Just select a different option in the radio button. Your previous selection will be cleared.

### Q: How long can the custom JD be?

**A:** No strict limit, but keep it under 5,000 characters for best results. Most job descriptions are 500-2,000 characters.

### Q: What if I don't have a specific job description?

**A:** Use the default option or enable online search to find similar job postings.

### Q: Can I save multiple job descriptions?

**A:** Currently, only one JD can be active at a time. To analyze multiple jobs, paste each one separately and run the analysis.

### Q: Does the custom JD work with all features?

**A:** Yes! Custom JD works with:
- ✅ Job Match analysis
- ✅ Profile optimization
- ✅ Content generation
- ✅ Career counseling

---

## Example Workflow

### Full Stack Developer Analysis:

1. **Load Profile**
   ```
   URL: https://www.linkedin.com/in/johndoe
   ```

2. **Set Target Role**
   ```
   Target Role: Full Stack Developer
   ```

3. **Paste Custom JD**
   ```
   [Copy full job description from Indeed/LinkedIn]
   ```

4. **Ask Questions**
   - "Analyze my fit for this Full Stack Developer role"
   - "What skills do I need to add to my profile?"
   - "Rewrite my headline for this job"
   - "What experience should I highlight?"

5. **Review Results**
   - Match score
   - Skill gaps
   - Optimization recommendations
   - ATS compatibility

---

## Troubleshooting

### Issue: Custom JD not being used

**Solution:**
- Verify "Paste Custom JD" is selected
- Check that text area shows your JD
- Look for "✅ Custom JD loaded" confirmation

### Issue: Online search not working

**Solution:**
- Verify Tavily API key is in `.env` file
- Check the checkbox is enabled
- Ensure you have internet connection
- Check API key validity at https://tavily.com

### Issue: Generic responses

**Solution:**
- Provide more detailed JD
- Include responsibilities AND requirements
- Set target role to match JD title
- Ask more specific questions

---

## Getting Tavily API Key

1. Visit https://tavily.com
2. Sign up for free account
3. Get API key from dashboard
4. Add to `.env` file:
   ```env
   TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
   ```
5. Restart the application

**Free Tier:** 1,000 searches/month

---

## Support

For more help:
- See `docs/TAVILY_INTEGRATION.md` for technical details
- Check `example_tavily_usage.py` for code examples
- Review main `README.md` for setup instructions

---

**Happy optimizing! 🚀**
