"""Service for fetching and processing job descriptions."""

from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
import json
from src.config.settings import settings


class JobDescriptionService:
    """Service for fetching job descriptions from various sources."""
    
    def __init__(self):
        """Initialize the job description service."""
        self.default_job_descriptions = self._load_default_descriptions()
        self.tavily_api_key = settings.tavily_api_key
    
    def get_job_description(
        self,
        job_title: str,
        custom_description: Optional[str] = None,
        location: str = "",
        use_online_search: bool = False
    ) -> Dict[str, Any]:
        """
        Get job description for a given role.
        
        Args:
            job_title: Job title/role
            custom_description: Custom JD provided by user
            location: Location for online search
            use_online_search: Whether to search online first
            
        Returns:
            Dictionary with job description and metadata
        """
        # Priority 1: Custom description provided by user
        if custom_description:
            return {
                "title": job_title,
                "description": custom_description,
                "source": "user_provided",
                "skills": self._extract_skills_from_text(custom_description)
            }
        
        # Priority 2: Online search (if enabled and API key available)
        if use_online_search and self.tavily_api_key:
            online_jd = self.search_job_online(job_title, location)
            if online_jd:
                return {
                    "title": job_title,
                    "description": online_jd,
                    "source": "tavily_search",
                    "skills": self._extract_skills_from_text(online_jd)
                }
        
        # Priority 3: Default database
        default_jd = self._get_default_jd(job_title)
        if default_jd:
            return default_jd
        
        # Priority 4: Generic fallback
        return self._generate_generic_jd(job_title)
    
    def _load_default_descriptions(self) -> Dict[str, Dict[str, Any]]:
        """Load default job descriptions for common roles."""
        return {
            "data_analyst": {
                "title": "Data Analyst",
                "description": """
                We are seeking a Data Analyst to join our team. The ideal candidate will be responsible for 
                collecting, processing, and performing statistical analyses on large datasets.
                
                Key Responsibilities:
                - Collect and interpret data from various sources
                - Analyze results using statistical techniques
                - Develop and implement databases and data collection systems
                - Identify, analyze, and interpret trends or patterns in complex data sets
                - Create visualizations and reports for stakeholders
                - Work with management to prioritize business and information needs
                
                Required Skills:
                - SQL and database management
                - Python or R for data analysis
                - Data visualization tools (Tableau, Power BI)
                - Excel advanced functions
                - Statistical analysis and modeling
                - Strong analytical and problem-solving skills
                
                Preferred Qualifications:
                - Bachelor's degree in Computer Science, Statistics, or related field
                - 2+ years of experience in data analysis
                - Experience with machine learning is a plus
                """,
                "skills": ["SQL", "Python", "R", "Tableau", "Power BI", "Excel", "Statistics", 
                          "Data Visualization", "ETL", "Data Modeling"],
                "source": "default_database"
            },
            "software_engineer": {
                "title": "Software Engineer",
                "description": """
                We are looking for a Software Engineer to produce and implement functional software solutions.
                
                Key Responsibilities:
                - Design, develop, and implement software applications
                - Write clean, scalable code using programming languages
                - Test and deploy applications and systems
                - Revise, update, refactor and debug code
                - Collaborate with internal teams to identify system requirements
                - Develop technical documentation
                
                Required Skills:
                - Proficiency in Java, Python, C++, or similar languages
                - Experience with web frameworks (Django, React, Angular)
                - Database knowledge (SQL, NoSQL)
                - Version control (Git)
                - Problem-solving aptitude
                - Excellent communication skills
                
                Preferred Qualifications:
                - BS/MS degree in Computer Science or Engineering
                - 3+ years of software development experience
                - Cloud platform experience (AWS, Azure, GCP)
                """,
                "skills": ["Java", "Python", "C++", "JavaScript", "React", "Django", "SQL", 
                          "Git", "AWS", "REST APIs", "Docker", "Agile"],
                "source": "default_database"
            },
            "product_manager": {
                "title": "Product Manager",
                "description": """
                We are seeking a Product Manager to lead product development from conception to launch.
                
                Key Responsibilities:
                - Define product vision and strategy
                - Gather and prioritize product requirements
                - Work closely with engineering, sales, and marketing teams
                - Create product roadmaps
                - Analyze market trends and competitor offerings
                - Define and track key product metrics
                
                Required Skills:
                - Product management experience
                - Strong analytical and problem-solving skills
                - Excellent communication and leadership skills
                - Understanding of Agile methodologies
                - Data-driven decision making
                - Stakeholder management
                
                Preferred Qualifications:
                - Bachelor's degree in Business, Engineering, or related field
                - 4+ years of product management experience
                - Technical background is a plus
                """,
                "skills": ["Product Strategy", "Roadmap Planning", "Agile", "Scrum", 
                          "User Research", "Analytics", "A/B Testing", "Stakeholder Management",
                          "JIRA", "SQL", "Data Analysis"],
                "source": "default_database"
            },
            "data_scientist": {
                "title": "Data Scientist",
                "description": """
                We are looking for a Data Scientist to analyze large amounts of raw information to find patterns.
                
                Key Responsibilities:
                - Identify valuable data sources and automate collection processes
                - Undertake preprocessing of structured and unstructured data
                - Build predictive models and machine learning algorithms
                - Present information using data visualization techniques
                - Propose solutions and strategies to business challenges
                
                Required Skills:
                - Python, R, SQL
                - Machine Learning and Deep Learning
                - Statistical analysis and modeling
                - Big Data platforms (Hadoop, Spark)
                - Data visualization (Matplotlib, Seaborn, Tableau)
                - Strong mathematical skills
                
                Preferred Qualifications:
                - Advanced degree in Statistics, Mathematics, Computer Science
                - 3+ years of experience in data science
                - Experience with cloud platforms
                """,
                "skills": ["Python", "R", "SQL", "Machine Learning", "Deep Learning", 
                          "TensorFlow", "PyTorch", "Scikit-learn", "Spark", "Hadoop",
                          "Statistics", "Data Mining", "NLP"],
                "source": "default_database"
            },
            "marketing_manager": {
                "title": "Marketing Manager",
                "description": """
                We are seeking a Marketing Manager to develop and execute marketing strategies.
                
                Key Responsibilities:
                - Develop marketing strategies and campaigns
                - Manage marketing budget and ROI
                - Oversee social media and content marketing
                - Analyze campaign performance and metrics
                - Collaborate with sales and product teams
                - Manage marketing team and external agencies
                
                Required Skills:
                - Digital marketing expertise
                - SEO/SEM and Google Analytics
                - Social media marketing
                - Content marketing
                - Marketing automation tools
                - Strong analytical skills
                
                Preferred Qualifications:
                - Bachelor's degree in Marketing or Business
                - 5+ years of marketing experience
                - Experience with CRM systems
                """,
                "skills": ["Digital Marketing", "SEO", "SEM", "Google Analytics", 
                          "Social Media Marketing", "Content Strategy", "Email Marketing",
                          "Marketing Automation", "HubSpot", "Brand Management"],
                "source": "default_database"
            }
        }
    
    def _get_default_jd(self, job_title: str) -> Optional[Dict[str, Any]]:
        """Get default job description from database."""
        # Normalize job title
        normalized_title = job_title.lower().replace(" ", "_")
        
        # Check exact match
        if normalized_title in self.default_job_descriptions:
            return self.default_job_descriptions[normalized_title]
        
        # Check partial matches
        for key, jd in self.default_job_descriptions.items():
            if key in normalized_title or normalized_title in key:
                return jd
        
        return None
    
    def _generate_generic_jd(self, job_title: str) -> Dict[str, Any]:
        """Generate a generic job description when specific one isn't found."""
        return {
            "title": job_title,
            "description": f"""
            Job Title: {job_title}
            
            We are seeking a qualified {job_title} to join our team.
            
            This is a generic job description. For more accurate analysis, please provide:
            1. A specific job posting URL, or
            2. Copy and paste the actual job description
            
            Common responsibilities for this role typically include:
            - Contributing to team objectives and deliverables
            - Collaborating with cross-functional teams
            - Staying updated with industry trends and best practices
            - Continuous learning and professional development
            
            Please provide more details for a more accurate analysis.
            """,
            "skills": [],
            "source": "generic"
        }
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract potential skills from job description text."""
        # Common technical skills to look for
        common_skills = [
            "python", "java", "javascript", "sql", "react", "angular", "vue",
            "docker", "kubernetes", "aws", "azure", "gcp", "git", "agile",
            "scrum", "tableau", "power bi", "excel", "machine learning",
            "deep learning", "tensorflow", "pytorch", "spark", "hadoop",
            "rest api", "graphql", "mongodb", "postgresql", "redis",
            "jenkins", "ci/cd", "terraform", "ansible", "linux"
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        return found_skills
    
    def search_job_online(self, job_title: str, location: str = "") -> Optional[str]:
        """
        Search for job descriptions online using Tavily API.
        
        Args:
            job_title: Job title to search
            location: Location filter (optional)
            
        Returns:
            Job description text or None if search fails
        """
        if not self.tavily_api_key:
            print("Warning: Tavily API key not configured. Falling back to default descriptions.")
            return None
        
        try:
            # Construct search query
            query = f"{job_title} job description requirements skills"
            if location:
                query += f" {location}"
            
            # Tavily API endpoint
            url = "https://api.tavily.com/search"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "advanced",  # More comprehensive results
                "include_domains": [
                    "linkedin.com",
                    "indeed.com", 
                    "glassdoor.com",
                    "monster.com",
                    "ziprecruiter.com"
                ],
                "max_results": 5,
                "include_answer": True,  # Get AI-generated summary
                "include_raw_content": True  # Get full content
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract job description from results
            job_description = self._extract_jd_from_tavily_results(data, job_title)
            
            return job_description
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching job online with Tavily: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in job search: {e}")
            return None
    
    def _extract_jd_from_tavily_results(self, data: Dict[str, Any], job_title: str) -> Optional[str]:
        """
        Extract and format job description from Tavily search results.
        
        Args:
            data: Tavily API response
            job_title: Original job title searched
            
        Returns:
            Formatted job description or None
        """
        try:
            job_description_parts = []
            
            # Use Tavily's AI-generated answer if available
            if data.get("answer"):
                job_description_parts.append(f"Overview:\n{data['answer']}\n")
            
            # Extract content from top results
            results = data.get("results", [])
            
            for i, result in enumerate(results[:3], 1):  # Use top 3 results
                title = result.get("title", "")
                content = result.get("content", "")
                url = result.get("url", "")
                
                if content:
                    job_description_parts.append(f"\n--- Source {i}: {title} ---")
                    job_description_parts.append(f"URL: {url}")
                    job_description_parts.append(f"{content}\n")
            
            if job_description_parts:
                full_description = "\n".join(job_description_parts)
                return full_description
            
            return None
            
        except Exception as e:
            print(f"Error extracting job description from Tavily results: {e}")
            return None