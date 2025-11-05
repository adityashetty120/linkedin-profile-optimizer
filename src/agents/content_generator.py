"""Content generation agent."""

from typing import Dict, Any, Optional, List
from src.services.llm_service import LLMService
from src.utils.helpers import format_profile_data


class ContentGeneratorAgent:
    """Agent for generating and optimizing profile content."""
    
    # LinkedIn profile sections that can be optimized
    PROFILE_SECTIONS = ['headline', 'about', 'experience', 'skills', 'education']
    
    def __init__(self, llm_service: LLMService):
        """
        Initialize content generator.
        
        Args:
            llm_service: LLM service instance
        """
        self.llm = llm_service
    
    def generate_all_sections(
        self,
        profile_data: Dict[str, Any],
        target_role: Optional[str] = None,
        job_description: str = "",
        focus_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive suggestions for all LinkedIn profile sections.
        
        Args:
            profile_data: Full profile context
            target_role: Target job role
            job_description: Job description for context
            focus_sections: Specific sections to focus on (default: all)
            
        Returns:
            Dictionary with suggestions for all sections, prioritized by impact
        """
        sections_to_generate = focus_sections or self.PROFILE_SECTIONS
        work_context = self._extract_work_context(profile_data)
        
        # Determine section priorities based on current state
        section_priorities = self._prioritize_sections(profile_data, work_context)
        
        all_suggestions = {
            "target_role": target_role or "General professional development",
            "overall_strategy": self._generate_overall_strategy(profile_data, target_role, job_description),
            "sections": {},
            "priorities": section_priorities,
            "quick_wins": [],
            "advanced_tips": []
        }
        
        # Generate suggestions for each section
        for section in sections_to_generate:
            current_content = self._get_current_section_content(profile_data, section)
            suggestion = self.generate(
                section_name=section,
                current_content=current_content,
                profile_data=profile_data,
                target_role=target_role,
                job_description=job_description
            )
            all_suggestions["sections"][section] = suggestion
        
        # Identify quick wins
        all_suggestions["quick_wins"] = self._identify_quick_wins(profile_data, work_context)
        
        # Add advanced optimization tips
        all_suggestions["advanced_tips"] = self._generate_advanced_tips(profile_data, target_role)
        
        return all_suggestions
    
    def _get_current_section_content(self, profile_data: Dict[str, Any], section: str) -> str:
        """Extract current content for a specific section."""
        if section == 'headline':
            return profile_data.get('headline', '')
        elif section == 'about':
            return profile_data.get('about', '')
        elif section == 'experience':
            experiences = profile_data.get('experience', [])
            if experiences:
                # Format first experience as example
                exp = experiences[0]
                return f"{exp.get('title', '')} at {exp.get('company', '')}\n{exp.get('description', 'No description')}"
            return "No experience entries"
        elif section == 'skills':
            skills = profile_data.get('skills', [])
            return ', '.join(skills[:10]) if skills else "No skills listed"
        elif section == 'education':
            education = profile_data.get('education', [])
            if education:
                edu = education[0]
                return f"{edu.get('degree', '')} in {edu.get('field_of_study', '')} from {edu.get('school', '')}"
            return "No education entries"
        return ""
    
    def _prioritize_sections(self, profile_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Determine which sections need the most attention."""
        priorities = {}
        
        # Headline priority
        headline = profile_data.get('headline', '')
        headline_priority = "HIGH" if len(headline) < 50 or not any(
            keyword in headline.lower() for keyword in ['engineer', 'developer', 'analyst', 'manager']
        ) else "MEDIUM"
        priorities['headline'] = {
            "priority": headline_priority,
            "reason": "Short or lacks role clarity" if headline_priority == "HIGH" else "Could be more compelling",
            "impact": "Very High - First thing recruiters see"
        }
        
        # About priority
        about = profile_data.get('about', '')
        about_priority = "HIGH" if len(about) < 200 else "MEDIUM" if len(about) < 500 else "LOW"
        priorities['about'] = {
            "priority": about_priority,
            "reason": "Too brief" if about_priority == "HIGH" else "Could add more impact" if about_priority == "MEDIUM" else "Good length, focus on quality",
            "impact": "Very High - Your value proposition"
        }
        
        # Experience priority
        experiences = profile_data.get('experience', [])
        missing_descriptions = sum(1 for exp in experiences if not exp.get('description'))
        exp_priority = "HIGH" if missing_descriptions > 0 else "MEDIUM"
        priorities['experience'] = {
            "priority": exp_priority,
            "reason": f"{missing_descriptions} positions lack descriptions" if missing_descriptions > 0 else "Add more metrics and achievements",
            "impact": "Critical - Shows your actual accomplishments"
        }
        
        # Skills priority
        skills = profile_data.get('skills', [])
        skills_detailed = profile_data.get('skills_detailed', [])
        skills_with_proof = sum(1 for skill in skills_detailed if skill.get('related_experiences'))
        skills_priority = "MEDIUM" if len(skills) < 10 or skills_with_proof < len(skills) * 0.5 else "LOW"
        priorities['skills'] = {
            "priority": skills_priority,
            "reason": "Need more skills or better proof" if skills_priority == "MEDIUM" else "Optimize skill presentation",
            "impact": "High - ATS optimization and credibility"
        }
        
        # Education priority (usually lowest unless missing)
        education = profile_data.get('education', [])
        edu_priority = "HIGH" if not education else "LOW"
        priorities['education'] = {
            "priority": edu_priority,
            "reason": "Missing education info" if edu_priority == "HIGH" else "Add relevant coursework or achievements",
            "impact": "Medium - Supports qualifications"
        }
        
        return priorities
    
    def _generate_overall_strategy(self, profile_data: Dict[str, Any], target_role: Optional[str], job_description: str) -> str:
        """Generate high-level strategy for profile optimization."""
        work_context = self._extract_work_context(profile_data)
        
        strategy = f"""
**Profile Optimization Strategy:**

**Your Brand Positioning:**
Current Position: {work_context['current_title']} at {work_context['current_company']}
Target Role: {target_role or 'Career advancement in current field'}

**Key Themes to Emphasize:**
1. **Company Brand Leverage:** Highlight your experience at {', '.join(work_context['companies'][:2])}
2. **Technical Depth:** Focus on skills where you have proven experience
3. **Impact & Results:** Quantify achievements from your {work_context['total_experience_years']} years of experience

**Content Philosophy:**
- SHOW, don't just tell: Every claim should be backed by specific examples
- Quantify everything: Numbers make impact tangible
- Context matters: Explain the "why" and "how," not just "what"
- ATS + Human: Optimize for both algorithms and recruiters

**Recommended Approach:**
1. Start with quick wins (headline, about section)
2. Deep-dive into experience descriptions
3. Optimize skills presentation with proof points
4. Polish education with relevant achievements
"""
        return strategy.strip()
    
    def _identify_quick_wins(self, profile_data: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify easy, high-impact improvements."""
        quick_wins = []
        
        # Headline quick wins
        headline = profile_data.get('headline', '')
        if len(headline) < 80:
            quick_wins.append({
                "section": "Headline",
                "action": f"Add your top skill or achievement to reach 80+ characters",
                "current_length": f"{len(headline)} chars",
                "time": "2 minutes",
                "impact": "High"
            })
        
        # About section quick wins
        about = profile_data.get('about', '')
        if 'helped' not in about.lower() and 'delivered' not in about.lower():
            quick_wins.append({
                "section": "About",
                "action": "Add 1-2 specific achievements with metrics (e.g., 'Delivered X resulting in Y% improvement')",
                "current_length": f"{len(about)} chars",
                "time": "10 minutes",
                "impact": "Very High"
            })
        
        # Experience quick wins
        experiences = profile_data.get('experience', [])
        for i, exp in enumerate(experiences[:2]):  # Top 2 positions
            if not exp.get('description') or len(exp.get('description', '')) < 100:
                quick_wins.append({
                    "section": f"Experience ({exp.get('title', 'Position')})",
                    "action": f"Add 3-4 bullet points with PAR format (Problem-Action-Result) for your role at {exp.get('company', 'company')}",
                    "current_length": f"{len(exp.get('description', ''))} chars",
                    "time": "15 minutes",
                    "impact": "Critical"
                })
        
        # Skills quick wins
        skills_detailed = profile_data.get('skills_detailed', [])
        unproven_skills = [s for s in skills_detailed if not s.get('related_experiences')]
        if len(unproven_skills) > 3:
            quick_wins.append({
                "section": "Skills & Experience",
                "action": f"Add {len(unproven_skills)} skills to your experience descriptions to prove proficiency",
                "current_length": f"{len(unproven_skills)} unproven skills",
                "time": "20 minutes",
                "impact": "High"
            })
        
        return quick_wins
    
    def _generate_advanced_tips(self, profile_data: Dict[str, Any], target_role: Optional[str]) -> List[str]:
        """Generate advanced optimization tips."""
        tips = [
            "**SEO Optimization:** Use your target role keywords in the first 3 lines of your About section for better search visibility",
            "**Story Arc:** Structure your About section as: Hook → Journey → Expertise → Impact → Call-to-Action",
            "**Proof Points:** For every skill claim, add 'where' (company) and 'impact' (result)",
            "**Engagement Hooks:** End your About section with a conversation starter (e.g., 'Let's discuss...' or 'Reach out if...')",
            "**Visual Hierarchy:** Use line breaks, emojis (sparingly), and formatting to make long sections scannable",
            "**Social Proof:** If you have notable achievements (awards, publications, speaking), mention them early",
            "**Custom URL:** Ensure your LinkedIn URL is customized (linkedin.com/in/yourname) for professionalism"
        ]
        
        if target_role:
            tips.insert(0, f"**Role Alignment:** Mirror {target_role} job posting keywords in your headline and first paragraph")
        
        return tips
    
    def generate(
        self,
        section_name: str,
        current_content: str,
        profile_data: Dict[str, Any],
        target_role: Optional[str] = None,
        job_description: str = ""
    ) -> Dict[str, Any]:
        """
        Generate improved content for a profile section.
        
        Args:
            section_name: Section to improve (about, headline, etc.)
            current_content: Current section content
            profile_data: Full profile context
            target_role: Target job role
            job_description: Job description for context
            
        Returns:
            Generated content dictionary
        """
        # Extract company/role context (endorsements not relevant here)
        work_context = self._extract_work_context(profile_data)
        
        # Enhanced prompt for better content generation
        enhanced_query = f"""
You are an expert LinkedIn content writer and personal branding specialist.

TASK: Rewrite the {section_name} section to maximize impact and engagement.

TARGET ROLE: {target_role or "General professional development"}

CURRENT CONTENT:
{current_content or "No existing content"}

WORK HISTORY CONTEXT:
{self._format_work_context(work_context)}

JOB DESCRIPTION (for context):
{job_description if job_description else "Not provided"}

FULL PROFILE CONTEXT:
{format_profile_data(profile_data)}

WRITING GUIDELINES:
1. **Leverage company brands:** Mention recognizable companies from work history
2. **Quantify with context:** Use metrics from actual experience
3. **Skills proof:** Reference skills with WHERE and HOW they were used
4. Use strong action verbs and concrete examples
5. Incorporate keywords naturally (NO keyword stuffing)
6. Maintain professional yet approachable tone
7. Keep headline under 120 characters, summary under 2,000 characters
8. Focus on demonstrable achievements, not just claims
9. Use first-person voice for summary/about section

SECTION-SPECIFIC REQUIREMENTS:
{self._get_section_requirements(section_name, work_context)}

CRITICAL: You MUST follow this EXACT output format with all sections clearly marked:

═══════════════════════════════════════
**REWRITTEN {section_name.upper()}:**
[Your improved content here - write the complete rewritten section]
═══════════════════════════════════════

**KEY IMPROVEMENTS MADE:**
1. [First specific improvement with example]
2. [Second specific improvement with example]
3. [Third specific improvement with example]

**KEYWORDS ADDED:**
keyword1, keyword2, keyword3, keyword4, keyword5

**CREDIBILITY ELEMENTS ADDED:**
- Company leverage: [specific example]
- Metrics: [specific numbers added]
- Skills proof: [specific skills with context]

**ADDITIONAL TIPS:**
- [Actionable tip 1]
- [Actionable tip 2]
- [Actionable tip 3]

Make it compelling, authentic, and ATS-friendly. Root ALL claims in actual experience.
"""
        
        generated_content = self.llm.generate_content(
            section_name=section_name,
            current_content=current_content or "No content provided",
            target_role=target_role or "general improvement",
            job_description=job_description,
            query=enhanced_query
        )
        
        # Parse the structured response
        parsed = self._parse_structured_response(generated_content)
        
        return {
            "section": section_name,
            "original_content": current_content,
            "generated_content": parsed.get("rewritten_content", generated_content),
            "improvements": parsed.get("improvements", []),
            "keywords_added": parsed.get("keywords", []),
            "credibility_elements": parsed.get("credibility", []),
            "tips": parsed.get("tips", []),
            "raw_response": generated_content  # Keep for debugging
        }
    
    def _extract_work_context(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant work context for content generation."""
        experience = profile_data.get('experience', [])
        
        companies = [exp.get('company', '') for exp in experience[:3]]  # Top 3
        current_role = experience[0] if experience else {}
        key_skills = []
        
        # Get skills with proof from recent positions
        for exp in experience[:3]:
            exp_skills = exp.get('skills', [])
            for skill in exp_skills:
                key_skills.append({
                    'skill': skill,
                    'company': exp.get('company', ''),
                    'role': exp.get('title', '')
                })
        
        return {
            'companies': companies,
            'current_title': current_role.get('title', ''),
            'current_company': current_role.get('company', ''),
            'proven_skills': key_skills[:10],
            'total_experience_years': len(experience)
        }
    
    def _format_work_context(self, context: Dict[str, Any]) -> str:
        """Format work context for prompt."""
        formatted = f"""
Current Position: {context['current_title']} at {context['current_company']}
Key Companies: {', '.join(context['companies'])}
Years of Experience: ~{context['total_experience_years']}

Proven Skills (with context):
"""
        for skill_data in context['proven_skills']:
            formatted += f"• {skill_data['skill']}: Used at {skill_data['company']} as {skill_data['role']}\n"
        
        return formatted
    
    def _get_section_requirements(self, section: str, context: Dict[str, Any]) -> str:
        """Get section-specific writing requirements."""
        requirements = {
            'headline': f"""
**HEADLINE REQUIREMENTS (Max 120 characters):**
Current Position Context: {context['current_title']} at {context['current_company']}

Structure Options:
1. **Formula:** [Role] | [Key Skill/Tech] | [Value Proposition]
   Example: "{context['current_title']} | AI/ML Specialist | Building Scalable ML Systems"

2. **Impact-First:** [What You Do] helping [Who] achieve [What]
   Example: "Building ML Solutions | Helping teams deploy production-ready AI systems"

3. **Brand + Value:** [Role] at [Top Company] | [Specialization]
   Example: "{context['current_title']} at {context['current_company']} | Computer Vision & NLP Expert"

MUST Include:
- Your current or target role title
- 1-2 key technical skills or areas of expertise
- Credibility signal (company name, achievement, or value proposition)

AVOID:
- Generic terms like "passionate," "innovative" without context
- Buzzwords without backing (e.g., "thought leader")
- Multiple special characters or emoji spam
""",
            'about': f"""
**ABOUT SECTION REQUIREMENTS (300-2000 characters, sweet spot: 600-1000):**

Structure (Use this framework):

**PARAGRAPH 1 - THE HOOK (2-3 sentences):**
- Lead with your impact or unique value proposition
- Include your role and specialization
- Mention your top company brand: {context['companies'][0] if context['companies'] else 'your company'}
Example: "I build intelligent systems that solve real-world problems at scale. As a {context['current_title']} at {context['current_company']}, I specialize in [specific area] with a focus on [measurable impact]."

**PARAGRAPH 2 - YOUR EXPERTISE (3-4 sentences):**
- Technical depth: List 3-5 core competencies with context
- Proven skills from experience: {', '.join([s['skill'] for s in context.get('proven_skills', [])[:5]])}
- Include WHERE you used these skills (company/project names)
Example: "My expertise spans Python ML development, computer vision, and LLM deployment—skills I've applied across projects at {context['companies'][0] if context['companies'] else 'various companies'}. I've [specific achievement with metric]."

**PARAGRAPH 3 - KEY ACHIEVEMENTS (2-3 sentences):**
- 2-3 quantified accomplishments from your experience
- Use metrics: "increased," "reduced," "delivered," "scaled"
- Reference specific companies/projects for credibility

**PARAGRAPH 4 - CURRENT FOCUS & CTA (2 sentences):**
- What you're working on now or seeking next
- Call-to-action: How people should connect with you
Example: "Currently exploring opportunities in [target area]. Let's connect if you're working on [relevant topic]."

MUST Include:
- Company names from your experience ({', '.join(context['companies'][:2])})
- At least 2 quantified achievements
- 5-7 key technical skills naturally integrated
- First-person voice (I, my, me)

AVOID:
- Generic statements without proof
- Listing skills without context (save for Skills section)
- Redundant experience details (save for Experience section)
""",
            'experience': f"""
**EXPERIENCE SECTION REQUIREMENTS:**
For EACH position, use this structure:

**Format: PAR (Problem-Action-Result) or STAR (Situation-Task-Action-Result)**

**3-5 Bullet Points per Role:**

Bullet 1 - SCOPE/CONTEXT:
"Worked as [role] in [team/department], focusing on [main responsibility] for [company/product]"

Bullets 2-4 - ACHIEVEMENTS (Use PAR):
• **Problem:** What challenge did you face?
• **Action:** What specific actions/technologies did you use?
• **Result:** What was the quantified outcome?

Example Format:
"• Reduced model inference time by 40% through optimizing PyTorch pipeline, enabling real-time predictions for 100K+ daily users"
"• Built RAG-based chatbot using LangChain and OpenAI API, improving customer query resolution by 60%"
"• Led team of 3 developers to migrate legacy system to React/Next.js, delivering 25% performance improvement"

**For Each Position:**
1. Start with strong action verbs: Built, Developed, Led, Implemented, Optimized, Delivered
2. Include specific technologies/skills used
3. ALWAYS quantify: percentages, numbers, timeframes, scale
4. Show progression across roles

**Skills to Highlight from Your Experience:**
{chr(10).join([f"• {s['skill']} (from {s['company']})" for s in context.get('proven_skills', [])[:8]])}

MUST Include per Position:
- 1-2 specific technologies/tools
- At least 1 quantified metric
- Context (team size, user scale, business impact)

AVOID:
- Vague responsibilities ("Responsible for...")
- No metrics or outcomes
- Same bullet structure for every position
- Just listing technologies without showing impact
""",
            'skills': f"""
**SKILLS SECTION OPTIMIZATION:**

**Current Situation:**
- Total Skills: {len(context.get('proven_skills', []))} with work history proof
- Goal: Show 20-30 relevant skills with clear proficiency levels

**Categorization Strategy:**
Organize by skill type (LinkedIn allows custom order):

**1. Core Technical Skills (8-10):**
Primary technologies you use daily: {', '.join([s['skill'] for s in context.get('proven_skills', [])[:6]])}

**2. Domain Expertise (5-7):**
Specialized knowledge areas (e.g., Machine Learning, Computer Vision, NLP, MLOps)

**3. Tools & Frameworks (5-8):**
Specific tools (e.g., PyTorch, TensorFlow, React, AWS, Docker)

**4. Professional Skills (3-5):**
Soft skills WITH proof (e.g., Team Leadership - mention leading X people)

**Proof Strategy:**
For TOP 10 skills, ensure they appear in your experience descriptions:
- Mention the skill
- Show WHERE you used it (company)
- Demonstrate HOW you used it (specific project/achievement)

**Endorsement Note (Optional, Low Priority):**
While endorsements are visible, actual work experience proof matters infinitely more.
Focus on updating your experience descriptions rather than collecting endorsements.

MUST DO:
- Reorder skills to show most relevant ones first (for target role)
- Remove outdated/irrelevant skills
- Ensure top 10 skills are mentioned in experience section

AVOID:
- Listing 50+ skills (looks unfocused)
- Skills with zero context in your experience
- Overemphasizing endorsement counts (work proof > social proof)
""",
            'education': f"""
**EDUCATION SECTION REQUIREMENTS:**

For EACH degree/certification:

**Basic Info (Auto-filled):**
- Degree/Certification name
- Institution
- Dates
- Field of study

**Description (Add This):**
**What to Include:**
1. **Relevant Coursework (if recent graduate):**
   "Relevant coursework: Machine Learning, Deep Learning, Computer Vision, Natural Language Processing"

2. **Key Projects (1-2 with metrics):**
   "• Capstone Project: Built [project] using [technologies], achieving [metric]"
   "• Thesis: Researched [topic], resulting in [outcome/publication]"

3. **Honors/Awards:**
   "Dean's List," "Graduated with Honors," "GPA: X.X/4.0 (if > 3.5)"

4. **Leadership/Activities:**
   "President of AI/ML Club," "Led team of X students in [competition]"

**For Certifications:**
- Link to credential (if available)
- Key skills gained
- How you've applied the learning

Example:
"Bachelor of Technology in Artificial Intelligence
Shah And Anchor Kutchhi Engineering College • 2021-2025

Key Projects:
• Developed RAG-based Q&A system using LangChain, achieving 85% accuracy
• Built computer vision model for object detection with 92% mAP

Relevant Coursework: Deep Learning, NLP, Computer Vision, MLOps
Activities: Website Team Lead at R&D Cell, AI Amplify Competition (2nd Runner Up)"

MUST Include:
- 1-2 significant projects (if recent graduate)
- Relevant coursework aligned with target role
- Any honors, awards, or leadership roles

AVOID:
- Leaving education description blank
- Only listing degree without context
- Irrelevant extracurriculars
"""
        }
        
        return requirements.get(section.lower(), "Follow general best practices for professional content.")
    
    def _parse_structured_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into structured sections."""
        import re
        
        result = {
            "rewritten_content": "",
            "improvements": [],
            "keywords": [],
            "credibility": [],
            "tips": []
        }
        
        # Extract rewritten content
        rewritten_match = re.search(
            r"\*\*REWRITTEN.*?:\*\*\s*═*\s*(.*?)(?=\*\*KEY IMPROVEMENTS|$)", 
            response, 
            re.DOTALL | re.IGNORECASE
        )
        if rewritten_match:
            result["rewritten_content"] = rewritten_match.group(1).strip().strip('═').strip()
        
        # Extract improvements (numbered list)
        improvements_match = re.search(
            r"\*\*KEY IMPROVEMENTS MADE:\*\*\s*(.*?)(?=\*\*KEYWORDS|$)",
            response,
            re.DOTALL | re.IGNORECASE
        )
        if improvements_match:
            improvements_text = improvements_match.group(1)
            result["improvements"] = [
                line.strip().lstrip('1234567890.-•').strip()
                for line in improvements_text.split('\n')
                if line.strip() and any(c.isalpha() for c in line)
            ][:5]
        
        # Extract keywords (comma-separated)
        keywords_match = re.search(
            r"\*\*KEYWORDS ADDED:\*\*\s*(.*?)(?=\*\*CREDIBILITY|\*\*ADDITIONAL|$)",
            response,
            re.DOTALL | re.IGNORECASE
        )
        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            result["keywords"] = [
                k.strip() 
                for k in re.split(r'[,\n]', keywords_text)
                if k.strip() and len(k.strip()) > 2
            ][:15]
        
        # Extract credibility elements (bullet list)
        credibility_match = re.search(
            r"\*\*CREDIBILITY ELEMENTS ADDED:\*\*\s*(.*?)(?=\*\*ADDITIONAL|$)",
            response,
            re.DOTALL | re.IGNORECASE
        )
        if credibility_match:
            credibility_text = credibility_match.group(1)
            result["credibility"] = [
                line.strip().lstrip('-•').strip()
                for line in credibility_text.split('\n')
                if line.strip() and ':' in line
            ][:5]
        
        # Extract tips (bullet list)
        tips_match = re.search(
            r"\*\*ADDITIONAL TIPS:\*\*\s*(.*?)$",
            response,
            re.DOTALL | re.IGNORECASE
        )
        if tips_match:
            tips_text = tips_match.group(1)
            result["tips"] = [
                line.strip().lstrip('-•').strip()
                for line in tips_text.split('\n')
                if line.strip() and any(c.isalpha() for c in line)
            ][:5]
        
        # Fallback: if parsing failed, extract whatever we can
        if not result["rewritten_content"]:
            # Just take the first substantial paragraph as the rewritten content
            paragraphs = [p.strip() for p in response.split('\n\n') if len(p.strip()) > 100]
            if paragraphs:
                result["rewritten_content"] = paragraphs[0]
        
        return result
    
    def _extract_rewritten_content(self, response: str) -> str:
        """Extract the rewritten content from LLM response."""
        # Look for content between markers or after specific headers
        lines = response.split('\n')
        content_lines = []
        capture = False
        
        for line in lines:
            if any(marker in line.lower() for marker in ['rewritten', 'improved', 'new version']):
                capture = True
                continue
            
            if capture and any(marker in line.lower() for marker in ['improvement', 'keyword', 'tip']):
                break
            
            if capture and line.strip():
                content_lines.append(line.strip())
        
        return '\n'.join(content_lines) if content_lines else response
    
    def _extract_improvements(self, response: str) -> list:
        """Extract list of improvements made."""
        lines = response.split('\n')
        improvements = []
        
        for line in lines:
            line = line.strip()
            if 'improvement' in line.lower() and ':' in line:
                improvements.append(line.split(':', 1)[1].strip())
            elif line.startswith('-') and 'improve' in line.lower():
                improvements.append(line.lstrip('- ').strip())
        
        return improvements[:5]
    
    def _extract_keywords_added(self, response: str) -> list:
        """Extract keywords that were added."""
        lines = response.split('\n')
        keywords = []
        
        for line in lines:
            if 'keyword' in line.lower() and ':' in line:
                keyword_text = line.split(':', 1)[1].strip()
                keywords.extend([k.strip() for k in keyword_text.split(',')])
        
        return keywords[:10]
    
    def _extract_tips(self, response: str) -> list:
        """Extract additional tips."""
        lines = response.split('\n')
        tips = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('Tip') or 'additional' in line.lower():
                tips.append(line.lstrip('Tip: ').strip())
        
        return tips[:3]