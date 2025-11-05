"""Helper functions for data processing and analysis."""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def sanitize_text(text: str) -> str:
    """Clean and sanitize text input."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()


def calculate_profile_completeness(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate profile completeness score and identify missing sections."""
    
    required_sections = {
        "about": 15,
        "headline": 10,
        "experience": 30,
        "education": 15,
        "skills": 20,
        "certifications": 10
    }
    
    score = 0
    missing_sections = []
    weak_sections = []
    
    for section, weight in required_sections.items():
        section_data = profile_data.get(section, "")
        
        if not section_data or (isinstance(section_data, list) and len(section_data) == 0):
            missing_sections.append(section)
        elif isinstance(section_data, str) and len(section_data) < 50:
            weak_sections.append(section)
            score += weight * 0.3  # Partial credit
        elif isinstance(section_data, list) and len(section_data) < 2:
            weak_sections.append(section)
            score += weight * 0.5
        else:
            score += weight
    
    return {
        "score": round(score, 2),
        "missing_sections": missing_sections,
        "weak_sections": weak_sections,
        "grade": get_grade(score)
    }


def get_grade(score: float) -> str:
    """Convert numerical score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def calculate_match_score(profile_text: str, job_description: str) -> Dict[str, Any]:
    """Calculate semantic similarity between profile and job description."""
    
    if not profile_text or not job_description:
        return {"score": 0, "confidence": "low"}
    
    try:
        # Use TF-IDF vectorization
        vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        vectors = vectorizer.fit_transform([profile_text, job_description])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        
        # Convert to percentage
        score = round(similarity * 100, 2)
        
        # Determine confidence
        if score >= 70:
            confidence = "high"
        elif score >= 50:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "score": score,
            "confidence": confidence,
            "similarity_matrix": similarity
        }
    except Exception as e:
        print(f"Error calculating match score: {e}")
        return {"score": 0, "confidence": "error", "error": str(e)}


def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """Extract top keywords from text using TF-IDF."""
    
    if not text:
        return []
    
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=top_n)
        vectorizer.fit([text])
        keywords = vectorizer.get_feature_names_out()
        return list(keywords)
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return []


def find_missing_keywords(profile_keywords: List[str], job_keywords: List[str]) -> List[str]:
    """Find keywords in job description that are missing from profile."""
    profile_set = set(k.lower() for k in profile_keywords)
    job_set = set(k.lower() for k in job_keywords)
    return list(job_set - profile_set)


def format_profile_data(raw_profile: Dict[str, Any]) -> str:
    """Format profile data into readable text for LLM processing."""
    
    formatted = []
    
    # Headline
    if raw_profile.get("headline"):
        formatted.append(f"Headline: {raw_profile['headline']}")
    
    # About
    if raw_profile.get("about"):
        formatted.append(f"\nAbout:\n{raw_profile['about']}")
    
    # Experience
    if raw_profile.get("experience"):
        formatted.append("\nExperience:")
        for exp in raw_profile["experience"]:
            title = exp.get('title', 'N/A')
            company = exp.get('company', 'N/A')
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', 'Present')
            is_current = exp.get('is_current', False)
            
            # Format the experience entry with clear date information
            date_range = f"{start_date} - {end_date}" if start_date else "Date not specified"
            status = " (CURRENT POSITION)" if is_current else " (ENDED)"
            
            formatted.append(f"- {title} at {company}")
            formatted.append(f"  Period: {date_range}{status}")
            
            if exp.get("description"):
                formatted.append(f"  {exp['description']}")
            if exp.get("duration"):
                formatted.append(f"  Duration: {exp['duration']}")
    
    # Education
    if raw_profile.get("education"):
        formatted.append("\nEducation:")
        for edu in raw_profile["education"]:
            degree = edu.get('degree', 'N/A')
            school = edu.get('school', 'N/A')
            start_date = edu.get('start_date', '')
            end_date = edu.get('end_date', '')
            duration = edu.get('duration', '')
            field_of_study = edu.get('field_of_study', '')
            
            # Format the education entry with complete information
            formatted.append(f"- {degree} from {school}")
            
            if field_of_study and field_of_study not in degree:
                formatted.append(f"  Field of Study: {field_of_study}")
            
            # Show dates if available
            if start_date or end_date or duration:
                if duration:
                    formatted.append(f"  Duration: {duration}")
                elif start_date and end_date:
                    formatted.append(f"  Period: {start_date} - {end_date}")
                elif start_date:
                    formatted.append(f"  Start Date: {start_date}")
                elif end_date:
                    formatted.append(f"  Graduation Date: {end_date}")
    
    # Skills
    if raw_profile.get("skills"):
        skills = raw_profile["skills"]
        if isinstance(skills, list):
            formatted.append(f"\nSkills: {', '.join(skills)}")
        else:
            formatted.append(f"\nSkills: {skills}")
    
    # Certifications
    if raw_profile.get("certifications"):
        formatted.append("\nCertifications:")
        for cert in raw_profile["certifications"]:
            formatted.append(f"- {cert.get('name', 'N/A')}")
    
    return "\n".join(formatted)


def parse_experience_duration(duration_str: str) -> int:
    """Parse experience duration string and return months."""
    if not duration_str:
        return 0
    
    try:
        # Extract years and months
        years = re.search(r'(\d+)\s*(?:year|yr)', duration_str, re.IGNORECASE)
        months = re.search(r'(\d+)\s*(?:month|mo)', duration_str, re.IGNORECASE)
        
        total_months = 0
        if years:
            total_months += int(years.group(1)) * 12
        if months:
            total_months += int(months.group(1))
        
        return total_months
    except Exception:
        return 0


def calculate_total_experience(experiences: List[Dict[str, Any]]) -> Dict[str, int]:
    """Calculate total years and months of experience."""
    total_months = sum(
        parse_experience_duration(exp.get("duration", ""))
        for exp in experiences
    )
    
    years = total_months // 12
    months = total_months % 12
    
    return {"years": years, "months": months, "total_months": total_months}


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse date string from LinkedIn profile into datetime object.
    Supports formats like 'Mar 2025', 'March 2025', '2025', etc.
    
    Args:
        date_str: Date string from LinkedIn
        
    Returns:
        datetime object or None if parsing fails
    """
    if not date_str or date_str.lower() == 'present':
        return None
    
    try:
        # Try different date formats
        formats = [
            "%b %Y",      # Mar 2025
            "%B %Y",      # March 2025
            "%Y",         # 2025
            "%m/%Y",      # 03/2025
            "%m-%Y",      # 03-2025
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        return None
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None


def validate_experience_dates(experiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate experience dates and check for inconsistencies.
    Returns list of issues found.
    
    Args:
        experiences: List of experience dictionaries
        
    Returns:
        List of validation issues
    """
    issues = []
    current_date = datetime.now()
    
    for i, exp in enumerate(experiences):
        title = exp.get('title', 'Unknown')
        company = exp.get('company', 'Unknown')
        start_date_str = exp.get('start_date', '')
        end_date_str = exp.get('end_date', '')
        is_current = exp.get('is_current', False)
        
        # Parse dates
        start_date = parse_date_string(start_date_str)
        end_date = parse_date_string(end_date_str) if not is_current else current_date
        
        # Check if start date is in the future
        if start_date and start_date > current_date:
            issues.append({
                'position': f"{title} at {company}",
                'issue': 'Start date appears to be in the future',
                'start_date': start_date_str,
                'current_date': current_date.strftime("%b %Y")
            })
        
        # Check if end date is before start date
        if start_date and end_date and end_date < start_date:
            issues.append({
                'position': f"{title} at {company}",
                'issue': 'End date is before start date',
                'start_date': start_date_str,
                'end_date': end_date_str
            })
    
    return issues


def generate_session_id() -> str:
    """Generate a unique session ID."""
    from uuid import uuid4
    return str(uuid4())


def save_json(data: Any, filepath: str) -> bool:
    """Save data as JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False


def load_json(filepath: str) -> Optional[Dict]:
    """Load JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None


def timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")