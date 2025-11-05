"""Profile analysis agent."""

from typing import Dict, Any
from datetime import datetime
from src.services.llm_service import LLMService
from src.utils.helpers import (
    calculate_profile_completeness, 
    format_profile_data,
    validate_experience_dates
)


class ProfileAnalyzerAgent:
    """Agent for analyzing LinkedIn profiles."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize profile analyzer.
        
        Args:
            llm_service: LLM service instance
        """
        self.llm = llm_service
    
    def analyze(
        self,
        profile_data: Dict[str, Any],
        query: str = "Analyze this profile",
        previous_analysis: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze LinkedIn profile and provide feedback.
        
        Args:
            profile_data: LinkedIn profile data
            query: Specific analysis query
            previous_analysis: Previous analysis for context
            
        Returns:
            Analysis results dictionary
        """
        # Calculate completeness score
        completeness = calculate_profile_completeness(profile_data)
        
        # Validate experience dates
        date_issues = []
        if profile_data.get("experience"):
            date_issues = validate_experience_dates(profile_data["experience"])
        
        # Analyze skills quality (focus on experience-linkage)
        skills_analysis = self._analyze_skills_quality(profile_data)
        
        # Format profile for LLM
        formatted_profile = format_profile_data(profile_data)
        
        # Get current date for context
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Add date validation context if there are real issues
        date_validation_note = ""
        if date_issues:
            date_validation_note = "\n\nDATE VALIDATION ALERTS (Real Issues Found):\n"
            for issue in date_issues:
                date_validation_note += f"- {issue['position']}: {issue['issue']} (Start: {issue.get('start_date', 'N/A')}, Current Date: {issue.get('current_date', 'N/A')})\n"
        
        # Enhanced prompt for better analysis
        enhanced_query = f"""
You are an expert LinkedIn profile strategist and career consultant with 10+ years of experience.

IMPORTANT CONTEXT:
- Today's date is: {current_date}
- When analyzing dates, remember that dates before {current_date} are in the PAST, not the future
- "is_current": false means the position has ENDED (not ongoing)
- "is_current": true means the position is ONGOING/CURRENT
- Format "Mar 2025" or "Jul 2024" are PAST dates if they are before {current_date}
- Do NOT flag past dates as "future dates" or date inconsistencies
- Education sections that show "Period: [start] - [end]" or "Duration: [dates]" ALREADY INCLUDE graduation dates
- Do NOT suggest adding graduation dates if they are already visible in the education section
{date_validation_note}

**SKILLS OVERVIEW:**
- Total Skills: {skills_analysis['total_skills']}
- Skills Demonstrated in Experience: {skills_analysis['linked_skills']} ({skills_analysis['proof_rate']:.0f}%)
- Skills Without Work History Proof: {skills_analysis['orphan_skills']}
{f"- Note: {skills_analysis['endorsed_skills']} skills have endorsements (optional but helpful)" if skills_analysis['endorsed_skills'] > 0 else ""}

TASK: Conduct a comprehensive analysis of this LinkedIn profile.

PROFILE DATA:
{formatted_profile}

PREVIOUS ANALYSIS (if any):
{previous_analysis if previous_analysis else "None - this is a fresh analysis"}

USER QUERY: {query}

ANALYSIS REQUIREMENTS:
1. Evaluate profile strength across all sections (headline, summary, experience, skills, education)
2. **PRIMARY CONCERN:** Skills should be backed by actual work experience (not just listed)
3. Identify specific weaknesses with concrete examples
4. Assess ATS (Applicant Tracking System) optimization
5. Check for quantifiable achievements and impact metrics
6. Evaluate keyword density and industry relevance
7. Review professional branding consistency
8. Endorsements are a minor plus but NOT critical

OUTPUT FORMAT:
**Overall Assessment:** [Brief 2-3 sentence summary]

**Strengths:**
- [Specific strength with example]
- [Specific strength with example]

**Weaknesses:**
- [Specific weakness with example]
- [Specific weakness with example]

**Skills Credibility:**
- ✓ Well-demonstrated: [Skills backed by experience]
- ⚠ Needs proof: [Skills listed but no work history showing their use]
- Optional: Consider getting endorsements for key skills (minor improvement)

**Priority Improvements:**
1. [Actionable recommendation]
2. [Actionable recommendation]
3. [Actionable recommendation]

**ATS Score:** [X/10 with brief explanation]

**Keywords Analysis:** [Missing critical keywords for their industry]

Keep recommendations actionable, specific, and professional. Focus on high-impact changes.
Keep the tone constructive. Endorsements are optional - the real issue is when skills lack ANY proof from work history.
"""
        
        # Get LLM analysis
        llm_analysis = self.llm.analyze_profile(
            profile_data=formatted_profile,
            query=enhanced_query,
            previous_analysis=previous_analysis
        )
        
        return {
            "completeness_score": completeness["score"],
            "grade": completeness["grade"],
            "missing_sections": completeness["missing_sections"],
            "weak_sections": completeness["weak_sections"],
            "detailed_analysis": llm_analysis,
            "recommendations": self._extract_recommendations(llm_analysis)
        }
    
    def _analyze_skills_quality(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze skills quality - PRIMARY focus on experience linkage."""
        skills_detailed = profile_data.get('skills_detailed', [])
        
        total = len(skills_detailed)
        endorsed = sum(1 for s in skills_detailed if s.get('endorsement_count', 0) > 0)
        linked = sum(1 for s in skills_detailed if s.get('related_experiences'))
        orphan = sum(1 for s in skills_detailed 
                    if not s.get('related_experiences'))  # Don't care about endorsements here
        
        return {
            'total_skills': total,
            'endorsed_skills': endorsed,  # Track but don't emphasize
            'linked_skills': linked,
            'orphan_skills': orphan,
            'endorsement_rate': (endorsed / total * 100) if total > 0 else 0,
            'proof_rate': (linked / total * 100) if total > 0 else 0  # This is what matters
        }
    
    def _extract_recommendations(self, analysis: str) -> list:
        """Extract actionable recommendations from analysis."""
        # Simple extraction - split by numbered lists or bullet points
        lines = analysis.split('\n')
        recommendations = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering or bullets
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    recommendations.append(clean_line)
        
        return recommendations[:10]  # Limit to top 10