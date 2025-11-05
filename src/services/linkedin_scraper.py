"""LinkedIn profile scraping service using Apify."""

from typing import Dict, Any, Optional
from apify_client import ApifyClient
from src.config.settings import settings
import time


class LinkedInScraper:
    """Service for scraping LinkedIn profiles using Apify."""
    
    def __init__(self):
        """Initialize Apify client."""
        if not settings.apify_api_key:
            raise ValueError("APIFY_API_KEY not found in environment variables. Please add it to your .env file")
        
        self.client = ApifyClient(settings.apify_api_key)
    
    def scrape_profile(self, profile_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape LinkedIn profile data.
        
        Args:
            profile_url: LinkedIn profile URL (e.g., https://www.linkedin.com/in/username)
            
        Returns:
            Dictionary containing profile data or None if failed
        """
        try:
            # Validate URL
            if not self._is_valid_linkedin_url(profile_url):
                raise ValueError("Invalid LinkedIn profile URL. Please use format: https://www.linkedin.com/in/username")
            
            # Extract username from LinkedIn URL
            username = self._extract_username(profile_url)
            
            # Run the Apify actor 5fajYOBUfeb6fgKlB
            run_input = {
                "usernames": [username],
                "includeEmail": False,
            }
            
            print(f"Scraping LinkedIn profile: {username}")
            
            # Start the actor and wait for it to finish
            run = self.client.actor("5fajYOBUfeb6fgKlB").call(run_input=run_input)
            
            # Check if the run was successful
            if run.get('status') == 'FAILED':
                error_msg = f"Actor run failed: {run.get('statusMessage', 'Unknown error')}"
                raise Exception(error_msg)
            
            # Fetch results from the dataset
            items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
            
            if not items:
                error_msg = "No data returned from Apify actor. Possible reasons:\n"
                error_msg += "- The LinkedIn profile is private or restricted\n"
                error_msg += "- The profile may not exist\n"
                error_msg += f"- Check Apify dashboard for run ID: {run.get('id')}"
                raise Exception(error_msg)
            
            # Get the profile data
            raw_profile = items[0]
            normalized_data = self._normalize_profile_data(raw_profile)
            
            print(f"✓ Profile loaded: {normalized_data.get('full_name')} ({len(normalized_data.get('skills', []))} skills)")
            
            return normalized_data
            
        except ValueError as ve:
            # Validation errors
            raise ve
        except Exception as e:
            # Log and re-raise with clearer message
            print(f"Error scraping profile: {str(e)}")
            raise Exception(f"Failed to scrape profile: {str(e)}")
    
    def _extract_username(self, url: str) -> str:
        """
        Extract username from LinkedIn profile URL.
        
        Args:
            url: LinkedIn profile URL
            
        Returns:
            Username string
        """
        # Remove trailing slash if present
        url = url.rstrip('/')
        
        # Extract username from URL
        # Example: https://www.linkedin.com/in/username -> username
        if "/in/" in url:
            username = url.split("/in/")[-1].split("/")[0]
            return username
        
        return url
    
    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate if URL is a LinkedIn profile URL."""
        return "linkedin.com/in/" in url.lower()
    
    def _normalize_profile_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize scraped profile data into standard format.
        
        Args:
            raw_data: Raw data from Apify actor 5fajYOBUfeb6fgKlB
            
        Returns:
            Normalized profile dictionary
        """
        # Extract basic_info which contains most profile data
        basic_info = raw_data.get("basic_info", {})
        
        # Location can be a dict or string
        location = basic_info.get("location", "")
        if isinstance(location, dict):
            location = location.get("full") or location.get("city") or ""
        
        # Extract skills - comes as a list of objects with name, endorsement_count, etc.
        skills_raw = raw_data.get("skills", [])
        skills = []
        
        if isinstance(skills_raw, list):
            for skill in skills_raw:
                if isinstance(skill, dict):
                    skill_name = skill.get("name", "")
                    if skill_name:
                        skills.append(skill_name)
                elif isinstance(skill, str):
                    skills.append(skill)
        
        return {
            # Personal info - extracted from basic_info
            "full_name": basic_info.get("fullname", ""),
            "headline": basic_info.get("headline", ""),
            "about": basic_info.get("about", ""),
            "location": location,
            "profile_url": basic_info.get("profile_url", "") or raw_data.get("profileUrl", ""),
            
            # Additional basic info
            "first_name": basic_info.get("first_name", ""),
            "last_name": basic_info.get("last_name", ""),
            "public_identifier": basic_info.get("public_identifier", ""),
            "profile_picture_url": basic_info.get("profile_picture_url", ""),
            "background_picture_url": basic_info.get("background_picture_url", ""),
            
            # Flags
            "is_creator": basic_info.get("is_creator", False),
            "is_influencer": basic_info.get("is_influencer", False),
            "is_premium": basic_info.get("is_premium", False),
            "open_to_work": basic_info.get("open_to_work", False),
            "show_follower_count": basic_info.get("show_follower_count", False),
            
            # Experience and education - from top level
            "experience": self._normalize_experience(raw_data.get("experience", [])),
            "education": self._normalize_education(raw_data.get("education", [])),
            
            # Skills and certifications
            "skills": skills,
            "skills_detailed": skills_raw,  # Keep detailed skill info with endorsements
            "certifications": self._normalize_certifications(raw_data.get("certifications", [])),
            "languages": raw_data.get("languages", []),
            
            # Recommendations
            "recommendations": raw_data.get("recommendations", {}),
            
            # Metadata
            "connections": basic_info.get("connection_count", 0),
            "followers": basic_info.get("follower_count", 0),
            "current_company": basic_info.get("current_company", ""),
            "current_company_urn": basic_info.get("current_company_urn", ""),
            "current_company_url": basic_info.get("current_company_url", ""),
            "email": basic_info.get("email", ""),
            "urn": basic_info.get("urn", ""),
            "created_timestamp": basic_info.get("created_timestamp", 0),
            
            # Keep raw data for debugging
            "raw_data": raw_data,
            "basic_info": basic_info,
            "_raw_keys": list(raw_data.keys())
        }
    
    def _normalize_experience(self, positions: list) -> list:
        """Normalize experience data from the new actor format."""
        normalized = []
        
        for pos in positions:
            # Parse start date
            start_date = ""
            start_date_obj = pos.get("start_date", {})
            if isinstance(start_date_obj, dict):
                year = start_date_obj.get("year", "")
                month = start_date_obj.get("month", "")
                if year and month:
                    start_date = f"{month} {year}"
                elif year:
                    start_date = str(year)
            elif start_date_obj:
                start_date = str(start_date_obj)
            
            # Parse end date
            end_date = "Present"
            is_current = pos.get("is_current", False)
            
            if not is_current:
                end_date_obj = pos.get("end_date", {})
                if isinstance(end_date_obj, dict):
                    year = end_date_obj.get("year", "")
                    month = end_date_obj.get("month", "")
                    if year and month:
                        end_date = f"{month} {year}"
                    elif year:
                        end_date = str(year)
                elif end_date_obj:
                    end_date = str(end_date_obj)
            
            normalized.append({
                "title": pos.get("title", ""),
                "company": pos.get("company", ""),
                "company_logo_url": pos.get("company_logo_url", ""),
                "company_linkedin_url": pos.get("company_linkedin_url", ""),
                "description": pos.get("description", ""),
                "start_date": start_date,
                "end_date": end_date,
                "duration": pos.get("duration", ""),
                "location": pos.get("location", ""),
                "employment_type": pos.get("employment_type", ""),
                "is_current": is_current,
                "skills": pos.get("skills", [])  # Skills associated with this position
            })
        
        return normalized
    
    def _normalize_education(self, schools: list) -> list:
        """Normalize education data from the new actor format."""
        normalized = []
        
        for school in schools:
            # Parse start and end dates
            start_date_obj = school.get("start_date", {})
            end_date_obj = school.get("end_date", {})
            
            start_date_str = ""
            end_date_str = ""
            
            if isinstance(start_date_obj, dict):
                year = start_date_obj.get("year", "")
                month = start_date_obj.get("month", "")
                if year and month:
                    start_date_str = f"{month} {year}"
                elif year:
                    start_date_str = str(year)
            
            if isinstance(end_date_obj, dict):
                year = end_date_obj.get("year", "")
                month = end_date_obj.get("month", "")
                if year and month:
                    end_date_str = f"{month} {year}"
                elif year:
                    end_date_str = str(year)
            
            normalized.append({
                "school": school.get("school", ""),
                "degree": school.get("degree", ""),
                "degree_name": school.get("degree_name", ""),
                "field_of_study": school.get("field_of_study", ""),
                "duration": school.get("duration", ""),
                "description": school.get("description", ""),
                "activities": school.get("activities", ""),
                "start_date": start_date_str,
                "end_date": end_date_str,
                "school_linkedin_url": school.get("school_linkedin_url", ""),
                "school_logo_url": school.get("school_logo_url", "")
            })
        
        return normalized
    
    def _normalize_certifications(self, certifications: list) -> list:
        """Normalize certifications data from the new actor format."""
        normalized = []
        
        for cert in certifications:
            # Parse issued date - can be a string like "Jun 2024" or a dict
            issue_date = cert.get("issue_date", "")
            if not issue_date:
                issue_date = cert.get("issued_date", "")
            
            # Handle if it's a dict
            if isinstance(issue_date, dict):
                year = issue_date.get("year", "")
                month = issue_date.get("month", "")
                if year and month:
                    issue_date = f"{month} {year}"
                elif year:
                    issue_date = str(year)
            
            # Parse expiration date
            expiration_date = cert.get("expiration_date", "")
            if isinstance(expiration_date, dict):
                year = expiration_date.get("year", "")
                month = expiration_date.get("month", "")
                if year and month:
                    expiration_date = f"{month} {year}"
                elif year:
                    expiration_date = str(year)
            
            normalized.append({
                "name": cert.get("name", ""),
                "issuer": cert.get("organization", "") or cert.get("issuer", ""),
                "organization_urn": cert.get("organization_urn", ""),
                "credential_id": cert.get("credential_id", ""),
                "credential_url": cert.get("credential_url", ""),
                "issue_date": issue_date,
                "expiration_date": expiration_date,
                "skills": cert.get("skills", [])
            })
        
        return normalized