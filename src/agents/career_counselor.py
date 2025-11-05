"""Career counseling agent."""

from typing import Dict, Any, Optional
from src.services.llm_service import LLMService
from src.utils.helpers import format_profile_data


class CareerCounselorAgent:
    """Agent for providing career guidance and counseling."""
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize career counselor.
        
        Args:
            llm_service: LLM service instance
        """
        self.llm = llm_service
    
    def counsel(
        self,
        profile_data: Dict[str, Any],
        query: str,
        career_goals: Optional[str] = None,
        target_role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Provide career counseling and guidance.
        
        Args:
            profile_data: LinkedIn profile data
            query: User's question or concern
            career_goals: Stated career goals
            target_role: Target job role
            
        Returns:
            Counseling response dictionary
        """
        formatted_profile = format_profile_data(profile_data)
        
        # Analyze skill evolution (ignore endorsements)
        skill_evolution = self._analyze_skill_evolution(profile_data)
        
        # Check if this is a simple conversational query or a comprehensive guidance request
        query_lower = query.lower()
        is_comprehensive = any(keyword in query_lower for keyword in [
            'full guidance', 'complete guidance', 'career plan', 'skill gap analysis',
            'learning path', 'career roadmap', 'comprehensive', 'detailed guidance'
        ])
        
        # Enhanced prompt based on query type
        if is_comprehensive:
            enhanced_query = f"""
You are a senior career counselor with expertise in tech and professional development.

TASK: Provide comprehensive career guidance and a personalized development roadmap.

CURRENT PROFILE:
{formatted_profile}

SKILL EVOLUTION ANALYSIS:
- Recent skills (last 2 years): {', '.join(skill_evolution['recent_skills'][:8])}
- Older skills: {', '.join(skill_evolution['older_skills'][:8])}
- Consistently used across roles: {', '.join(skill_evolution['consistent_skills'][:8])}
- Skill acquisition rate: {skill_evolution['new_skills_per_year']} new skills/year (avg)

CAREER GOALS: {career_goals or "Not specified - please infer from profile"}
TARGET ROLE: {target_role or "Not specified"}
USER QUESTION: {query}

COMPREHENSIVE ANALYSIS REQUIRED:
Focus on practical skill development and career trajectory. Endorsements are optional - what matters is building real competency and demonstrating it through work.

OUTPUT FORMAT:
**CAREER ASSESSMENT:**
[2-3 sentences on current positioning and trajectory - include skill evolution insights]

**SKILL GAP ANALYSIS:**
1. [Critical gap - considering current skill trajectory]
2. [Important gap - based on recent vs. target skills]
3. [Nice-to-have skill - explain why it matters]

**LEARNING ROADMAP:** (Prioritized by current skill base and market demand)
**Immediate (0-3 months):** (Build on recent skills)
- [Resource leveraging existing knowledge + practical project suggestion]
- [Resource leveraging existing knowledge + practical project suggestion]

**Short-term (3-6 months):** (Fill critical gaps with hands-on practice)
- [Resource + practical project suggestion]
- [Resource + practical project suggestion]

**Long-term (6-12 months):** (Advanced capabilities + portfolio building)
- [Resource + real-world application idea]

**ACTION PLAN:**
1. [Leverage current momentum in: {skill_evolution['recent_skills'][0] if skill_evolution['recent_skills'] else 'N/A'}]
2. [Build demonstrable experience in: ...]
3. [Document work on resume/portfolio: ...]
4. Optional later: Seek endorsements from colleagues (minor boost)

**TIMELINE:** [Realistic timeline based on skill acquisition velocity]

**SKILL PORTFOLIO STRATEGY:**
- Keep sharp: [Skills to maintain through practice]
- Sunset: [Outdated skills to deprioritize]
- Acquire: [New skills to add with hands-on projects]
- Demonstrate: [How to show these skills in action]

**NETWORKING SUGGESTIONS:** [Specific communities/events to join]

The goal is building real competency, not just collecting endorsements. Focus on doing the work.
Be realistic, supportive, and specific. Tailor advice to their experience level.
"""
        else:
            # Simple conversational query
            enhanced_query = f"""
You are a friendly and knowledgeable career counselor.

PROFILE CONTEXT:
{formatted_profile}

CAREER GOALS: {career_goals or "Not specified"}
TARGET ROLE: {target_role or "Not specified"}

USER QUESTION: {query}

Provide a helpful, conversational response that:
- Directly answers their question
- Relates to their profile and goals
- Is encouraging and actionable
- Stays concise (2-4 paragraphs max)
- Offers 1-2 specific next steps

Keep it friendly, professional, and personalized to their situation.
"""
        
        counseling_response = self.llm.provide_career_counseling(
            profile_data=formatted_profile,
            career_goals=career_goals or "Not specified",
            target_role=target_role or "Not specified",
            query=enhanced_query
        )
        
        # Only extract structured data for comprehensive requests
        if is_comprehensive:
            return {
                "guidance": counseling_response,
                "skill_gaps": self._extract_skill_gaps(counseling_response),
                "learning_resources": self._extract_learning_resources(counseling_response),
                "next_steps": self._extract_next_steps(counseling_response),
                "timeline": self._extract_timeline(counseling_response)
            }
        else:
            # For simple queries, just return the response without structured extraction
            return {
                "guidance": counseling_response,
                "skill_gaps": [],
                "learning_resources": [],
                "next_steps": [],
                "timeline": None
            }
    
    def _extract_skill_gaps(self, response: str) -> list:
        """Extract identified skill gaps."""
        lines = response.split('\n')
        gaps = []
        capture = False
        for line in lines:
            line = line.strip()
            
            if any(keyword in line.lower() for keyword in ['skill gap', 'missing skill', 'need to learn']):
                capture = True
                continue
            
            if capture and any(keyword in line.lower() for keyword in ['learning', 'resource', 'next step']):
                break
            
            if capture and line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    gaps.append(clean_line)
                
        return gaps[:8]
            
    def _extract_learning_resources(self, response: str) -> list:
        """Extract recommended learning resources."""
        lines = response.split('\n')
        resources = []
        
        capture = False
        for line in lines:
            line = line.strip()
            
            if any(keyword in line.lower() for keyword in ['learning', 'resource', 'course', 'certification']):
                capture = True
                continue
            
            if capture and any(keyword in line.lower() for keyword in ['next step', 'timeline', 'career']):
                break
            
            if capture and line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    resources.append(clean_line)
        
        return resources[:6]
    
    def _extract_next_steps(self, response: str) -> list:
        """Extract actionable next steps."""
        lines = response.split('\n')
        steps = []
        
        capture = False
        for line in lines:
            line = line.strip()
            
            if any(keyword in line.lower() for keyword in ['next step', 'action', 'recommendation']):
                capture = True
                continue
            
            if capture and 'timeline' in line.lower():
                break
            
            if capture and line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    steps.append(clean_line)
        
        return steps[:5]
    
    def _extract_timeline(self, response: str) -> str:
        """Extract suggested timeline."""
        lines = response.split('\n')
        
        for i, line in enumerate(lines):
            if 'timeline' in line.lower():
                # Get the next few lines
                timeline_lines = []
                for j in range(i, min(i + 5, len(lines))):
                    if lines[j].strip():
                        timeline_lines.append(lines[j].strip())
                return ' '.join(timeline_lines)
        
        return "Timeline not specified"
    
    def _analyze_skill_evolution(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how skills have evolved across positions."""
        experience = profile_data.get('experience', [])
        current_year = 2025
        
        recent_skills = set()
        older_skills = set()
        skill_timeline = {}
        
        for exp in experience:
            exp_skills = exp.get('skills', [])
            start_year = self._extract_year(exp.get('start_date', ''))
            
            if start_year and current_year - start_year <= 2:
                recent_skills.update(exp_skills)
            elif start_year:
                older_skills.update(exp_skills)
            
            for skill in exp_skills:
                if skill not in skill_timeline:
                    skill_timeline[skill] = []
                skill_timeline[skill].append(exp.get('title', ''))
        
        # Find consistently used skills
        consistent = {skill for skill, positions in skill_timeline.items() if len(positions) >= 2}
        
        # Calculate skill acquisition rate
        years_of_experience = len(experience) if experience else 1
        new_skills_per_year = len(recent_skills) / 2 if recent_skills else 0
        
        return {
            'recent_skills': list(recent_skills),
            'older_skills': list(older_skills - recent_skills),
            'consistent_skills': list(consistent),
            'new_skills_per_year': round(new_skills_per_year, 1),
            'skill_timeline': skill_timeline
        }
    
    def _extract_year(self, date_str: str) -> Optional[int]:
        """Extract year from date string."""
        import re
        if not date_str:
            return None
        match = re.search(r'\b(20\d{2})\b', date_str)
        return int(match.group(1)) if match else None