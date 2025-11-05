"""Job matching agent."""

from typing import Dict, Any
from src.services.llm_service import LLMService
from src.services.job_description_service import JobDescriptionService
from src.utils.helpers import (
    calculate_match_score,
    format_profile_data,
    extract_keywords,
    find_missing_keywords
)


class JobMatcherAgent:
    """Agent for matching profiles with job descriptions."""
    
    def __init__(self, llm_service: LLMService, job_service: JobDescriptionService):
        """
        Initialize job matcher.
        
        Args:
            llm_service: LLM service instance
            job_service: Job description service instance
        """
        self.llm = llm_service
        self.job_service = job_service
    
    def match(
        self,
        profile_data: Dict[str, Any],
        job_title: str,
        custom_jd: str = None,
        location: str = "",
        use_online_search: bool = False
    ) -> Dict[str, Any]:
        """
        Match profile with job description.
        
        Args:
            profile_data: LinkedIn profile data
            job_title: Target job title
            custom_jd: Custom job description (optional)
            location: Location for online job search (optional)
            use_online_search: Whether to search for real job postings online (optional)
            
        Returns:
            Match analysis dictionary
        """
        # Get job description (with optional online search)
        job_data = self.job_service.get_job_description(
            job_title=job_title,
            custom_description=custom_jd,
            location=location,
            use_online_search=use_online_search
        )
        
        # Format profile
        formatted_profile = format_profile_data(profile_data)
        
        # Extract actual skills from profile (not just text keywords)
        profile_skills = self._extract_all_skills(profile_data)
        job_keywords = extract_keywords(job_data["description"])
        
        # Better matching: check if skill appears in job description or vice versa
        matching_skills = self._find_matching_skills(profile_skills, job_data["description"])
        missing_keywords = self._find_missing_skills(profile_skills, job_data["description"], job_keywords)
        
        # Calculate enhanced match score based on skills overlap
        # This is more accurate than pure TF-IDF similarity
        match_score_data = self._calculate_skill_based_match_score(
            profile_skills, 
            matching_skills, 
            missing_keywords,
            job_data["description"]
        )
        
        # Analyze position-specific skills (focus on WHERE used, not endorsements)
        position_skills_map = self._extract_position_skills(profile_data)
        relevant_experience = self._find_relevant_experience(profile_data, job_data["description"])
        
        # Enhanced prompt for better job matching
        enhanced_query = f"""
You are an expert recruiter and ATS (Applicant Tracking System) specialist.

TASK: Analyze how well this candidate's profile matches the job requirements and provide optimization strategies.

JOB TITLE: {job_title}

JOB DESCRIPTION:
{job_data["description"]}

CANDIDATE PROFILE:
{formatted_profile}

EXPERIENCE-SKILLS MAPPING:
{self._format_position_skills(position_skills_map)}

MOST RELEVANT PAST ROLES:
{self._format_relevant_experience(relevant_experience)}

PRELIMINARY MATCH ANALYSIS:
- Match Score: {match_score_data["score"]}/100 (Exact: {match_score_data.get("exact_matches", 0)}, Partial: {match_score_data.get("partial_matches", 0)} of {match_score_data.get("total_requirements", 0)} requirements)
- Matching Skills: {matching_skills[:10]}
- Missing Keywords: {missing_keywords[:15]}

ANALYSIS REQUIREMENTS:
1. **Skills Provenance:** Which skills are PROVEN by actual work experience vs. just listed?
2. **Experience Relevance:** Which past positions directly relate to this role?
3. **Skill Recency:** Are relevant skills from recent roles or outdated positions?
4. **Career Trajectory:** Does the progression align with this target role?
5. **Transferable Skills:** Consider how existing skills (e.g., LangChain) demonstrate ability to learn similar frameworks (PyTorch, TensorFlow)
6. Assess ATS compatibility and keyword optimization
7. Note: Focus on potential and learning capability for entry-level roles

SCORING CONTEXT:
The match score considers:
- Exact skill matches (full credit)
- Related/transferable skills (partial credit - e.g., "LangChain" counts toward "LLM" expertise)
- Foundation skills bonus (having Python + ML fundamentals)
- Missing specific frameworks reduce score but don't disqualify if foundation is strong

OUTPUT FORMAT:
**MATCH ASSESSMENT:** [Overall fit summary - be balanced and consider growth potential for entry-level roles. A 40-50% match can still be "worth applying" if fundamentals are strong]

**PROVEN STRENGTHS:** (Skills + Where Demonstrated)
- [Skill]: Demonstrated at [Company/Role]
- [Skill]: Demonstrated at [Company/Role]

**EXPERIENCE ALIGNMENT:**
- [Past role] → [How it relates to target role]
- [Past role] → [How it relates to target role]

**GAPS TO ADDRESS:**
- [Critical gap with impact assessment]
- [Critical gap with impact assessment]

**OPTIMIZATION RECOMMENDATIONS:**
1. **Highlight:** [Which experience to emphasize + why]
2. **Add Context:** [Where to add proof of claimed skills]
3. **Reframe:** [How to position existing experience]
4. Optional: Seek endorsements for key skills (minor credibility boost)

**KEYWORDS TO ADD:** [Prioritized list of 5-8 missing keywords]

**ATS COMPATIBILITY:** [Score/10 with specific issues]

**INTERVIEW PREP:**
- Talk about: [Specific project/achievement to highlight]
- Prepare for questions on: [Gap areas]

Focus on demonstrable skills over endorsed skills. Real experience trumps endorsements.
Be specific and actionable. Focus on changes that will move the needle.
"""
        
        # Get detailed LLM analysis
        llm_analysis = self.llm.match_job(
            profile_data=formatted_profile,
            job_description=job_data["description"],
            job_title=enhanced_query
        )
        
        return {
            "job_title": job_title,
            "match_score": match_score_data["score"],
            "confidence": match_score_data["confidence"],
            "matching_skills": matching_skills,
            "missing_skills": missing_keywords[:15],
            "detailed_analysis": llm_analysis,
            "job_description": job_data["description"],
            "recommendations": self._extract_improvements(llm_analysis)
        }
    
    def _extract_all_skills(self, profile_data: Dict[str, Any]) -> list:
        """
        Extract ALL skills from profile as complete phrases.
        - Main skills list
        - Skills from each experience
        - Skills from certifications
        Returns lowercase skill names for matching.
        """
        all_skills = set()
        
        # 1. Main skills list
        if profile_data.get('skills'):
            for skill in profile_data['skills']:
                # Keep as complete phrase, just normalize case and clean
                clean_skill = skill.lower().strip()
                if clean_skill:
                    all_skills.add(clean_skill)
        
        # 2. Skills from detailed skills section
        if profile_data.get('skills_detailed'):
            for skill_obj in profile_data['skills_detailed']:
                skill = skill_obj.get('name', '').lower().strip()
                if skill:
                    all_skills.add(skill)
        
        # 3. Skills from experience
        if profile_data.get('experience'):
            for exp in profile_data['experience']:
                if exp.get('skills'):
                    for skill in exp['skills']:
                        clean_skill = skill.lower().strip()
                        if clean_skill:
                            all_skills.add(clean_skill)
        
        # 4. Skills from certifications
        if profile_data.get('certifications'):
            for cert in profile_data['certifications']:
                if cert.get('skills'):
                    for skill in cert['skills']:
                        clean_skill = skill.lower().strip()
                        if clean_skill:
                            all_skills.add(clean_skill)
        
        return list(all_skills)
    
    def _calculate_skill_based_match_score(
        self, 
        profile_skills: list, 
        matching_skills: list, 
        missing_skills: list,
        job_desc: str
    ) -> Dict[str, Any]:
        """
        Calculate match score based on actual skill overlap with nuanced evaluation.
        Considers exact matches, related skills, and transferable knowledge.
        """
        # Extract important requirements from job description
        important_phrases = self._extract_important_phrases(job_desc)
        
        # Count total requirements (unique important phrases + technical keywords)
        job_keywords = extract_keywords(job_desc, top_n=30)
        
        # Filter job keywords to only technical terms
        generic_words = {
            'experience', 'work', 'strong', 'good', 'years', 'team',
            'project', 'develop', 'building', 'data', 'code', 'software',
            'design', 'quality', 'practices', 'familiarity', 'proficiency'
        }
        technical_keywords = [k for k in job_keywords if k.lower() not in generic_words and len(k) > 3]
        
        # Combine important phrases and technical keywords
        all_requirements = set(important_phrases + technical_keywords)
        
        # Count matches with partial credit for related skills
        exact_matches = set()
        partial_matches = set()
        
        # Define skill relationships (if you have A, you get partial credit for B)
        skill_relationships = {
            'machine learning': ['ml', 'deep learning', 'neural networks', 'model'],
            'python': ['python3', 'py', 'scikit-learn', 'tensorflow', 'pytorch'],
            'deep learning': ['neural networks', 'pytorch', 'tensorflow', 'keras'],
            'large language models': ['llm', 'llms', 'fine tuning', 'quantization'],
            'langchain': ['llm', 'large language models'],
            'artificial intelligence': ['ai', 'machine learning', 'ml'],
            'computer vision': ['cv', 'image processing'],
        }
        
        for req in all_requirements:
            req_lower = req.lower()
            matched = False
            
            # Check for exact/direct match
            for skill in profile_skills:
                skill_lower = skill.lower()
                if (req_lower in skill_lower or skill_lower in req_lower or
                    self._are_skills_equivalent(req_lower, skill_lower)):
                    exact_matches.add(req)
                    matched = True
                    break
            
            # Check for partial/related match
            if not matched:
                for skill in profile_skills:
                    skill_lower = skill.lower()
                    # Check if skill gives partial credit for this requirement
                    for base_skill, related in skill_relationships.items():
                        if base_skill in skill_lower and req_lower in related:
                            partial_matches.add(req)
                            matched = True
                            break
                    if matched:
                        break
        
        # Calculate weighted score
        total_reqs = len(all_requirements) if all_requirements else 1
        exact_match_weight = 1.0
        partial_match_weight = 0.5  # Partial matches get 50% credit
        
        exact_score = len(exact_matches) * exact_match_weight
        partial_score = len(partial_matches) * partial_match_weight
        
        # Calculate overall match percentage
        total_match_score = exact_score + partial_score
        max_possible_score = total_reqs * exact_match_weight
        
        if max_possible_score > 0:
            base_score = (total_match_score / max_possible_score) * 100
        else:
            base_score = 0
        
        # Boost score if candidate has fundamental ML skills even if missing specific frameworks
        has_ml_foundation = any(skill in profile_skills for skill in [
            'machine learning', 'python (programming language)', 'python',
            'artificial intelligence (ai)', 'deep learning'
        ])
        
        has_llm_experience = any('llm' in skill.lower() or 'language model' in skill.lower() 
                                 for skill in profile_skills)
        
        # Apply foundation bonuses
        if has_ml_foundation:
            base_score += 10  # +10% for having ML fundamentals
        if has_llm_experience and 'llm' in job_desc.lower():
            base_score += 5   # +5% for LLM experience when job requires it
        
        # Apply experience penalty/bonus based on job description context
        # Don't penalize too heavily for junior roles or internships
        if any(word in job_desc.lower() for word in ['junior', 'entry', 'graduate', '1+ year', '1 year']):
            # For entry-level roles, be more lenient
            pass  # No penalty
        elif '3+' in job_desc or '5+' in job_desc or 'senior' in job_desc.lower():
            # For senior roles, apply penalty if profile is junior
            base_score *= 0.85  # 15% penalty for seniority mismatch
        
        # Cap score at 100
        score = round(min(base_score, 100), 2)
        
        # Determine confidence based on score and match quality
        exact_ratio = len(exact_matches) / total_reqs if total_reqs > 0 else 0
        
        if score >= 70 and exact_ratio >= 0.6:
            confidence = "high"
        elif score >= 50 and exact_ratio >= 0.4:
            confidence = "medium"
        else:
            confidence = "low"
        
        return {
            "score": score,
            "confidence": confidence,
            "exact_matches": len(exact_matches),
            "partial_matches": len(partial_matches),
            "total_requirements": total_reqs
        }
    
    def _are_skills_equivalent(self, skill1: str, skill2: str) -> bool:
        """Check if two skills are equivalent (considering variations/abbreviations)."""
        equivalences = [
            {'ml', 'machine learning', 'machine-learning'},
            {'ai', 'artificial intelligence'},
            {'llm', 'llms', 'large language model', 'large language models'},
            {'nlp', 'natural language processing'},
            {'cv', 'computer vision'},
            {'dl', 'deep learning'},
            {'python', 'python3', 'py'},
            {'tf', 'tensorflow'},
            {'pytorch', 'torch'},
        ]
        
        for equiv_set in equivalences:
            if skill1 in equiv_set and skill2 in equiv_set:
                return True
        
        return False
    
    def _find_matching_skills(self, profile_skills: list, job_desc: str) -> list:
        """
        Find skills from profile that appear in job description.
        Uses intelligent matching to handle variations and abbreviations.
        """
        job_desc_lower = job_desc.lower()
        matching = []
        
        for skill in profile_skills:
            skill_lower = skill.lower()
            
            # Direct substring match (e.g., "machine learning" in job description)
            if skill_lower in job_desc_lower:
                matching.append(skill)
                continue
            
            # Check for common abbreviations and variations
            skill_variations = self._get_skill_variations(skill_lower)
            if any(variation in job_desc_lower for variation in skill_variations):
                matching.append(skill)
                continue
            
            # For multi-word skills (>10 chars), check if all significant words appear
            if len(skill_lower) > 10 and ' ' in skill_lower:
                words = [w for w in skill_lower.split() if len(w) > 3]
                if len(words) >= 2 and all(word in job_desc_lower for word in words):
                    matching.append(skill)
        
        return matching
    
    def _get_skill_variations(self, skill: str) -> list:
        """Get common variations and abbreviations for a skill."""
        variations = [skill]
        
        # Common ML/AI abbreviations
        abbreviations = {
            'machine learning': ['ml', 'machine-learning'],
            'artificial intelligence': ['ai', 'artificial-intelligence'],
            'natural language processing': ['nlp', 'natural-language-processing'],
            'computer vision': ['cv'],
            'deep learning': ['dl', 'deep-learning'],
            'large language model': ['llm', 'large-language-model'],
            'large language models': ['llm', 'llms', 'large-language-models'],
            'python (programming language)': ['python'],
            'python': ['python3', 'py'],
            'tensorflow': ['tf'],
            'pytorch': ['torch'],
            'scikit-learn': ['sklearn', 'scikit learn'],
            'xgboost': ['xgb'],
        }
        
        skill_lower = skill.lower()
        if skill_lower in abbreviations:
            variations.extend(abbreviations[skill_lower])
        
        # Remove parentheses content (e.g., "Python (Programming Language)" -> "Python")
        if '(' in skill:
            clean_skill = skill.split('(')[0].strip().lower()
            if clean_skill != skill_lower:
                variations.append(clean_skill)
        
        return variations
    
    def _find_missing_skills(self, profile_skills: list, job_desc: str, job_keywords: list) -> list:
        """
        Find important skills/keywords from job description that are missing from profile.
        Focus on technical skills and frameworks, not generic words.
        """
        job_desc_lower = job_desc.lower()
        profile_skills_lower = [s.lower() for s in profile_skills]
        missing = []
        
        # First, prioritize important technical phrases (these are most valuable)
        important_phrases = self._extract_important_phrases(job_desc)
        for phrase in important_phrases:
            phrase_lower = phrase.lower()
            if phrase_lower not in profile_skills_lower:
                if not any(phrase_lower in ps or ps in phrase_lower for ps in profile_skills_lower):
                    if phrase not in missing:
                        missing.append(phrase)
        
        # Define generic/common words to skip (not actual skills)
        generic_words = {
            'experience', 'work', 'working', 'strong', 'good', 'knowledge', 
            'understanding', 'ability', 'skills', 'experience', 'years',
            'team', 'project', 'projects', 'develop', 'building', 'using',
            'data', 'code', 'software', 'system', 'systems', 'design',
            'development', 'work', 'build', 'create', 'make', 'use',
            'contribute', 'deliver', 'end', 'quality', 'practices',
            'familiarity', 'proficiency', 'clean', 'tested', 'robust'
        }
        
        # Only add specific technical keywords (not generic words)
        for keyword in job_keywords:
            keyword_lower = keyword.lower()
            
            # Skip generic words
            if keyword_lower in generic_words:
                continue
            
            # Skip short words (usually not meaningful)
            if len(keyword_lower) < 3:
                continue
            
            # Skip if keyword is already in profile skills
            if keyword_lower in profile_skills_lower:
                continue
            
            # Skip if any profile skill contains this keyword
            if any(keyword_lower in profile_skill for profile_skill in profile_skills_lower):
                continue
            
            # Skip if this keyword is contained in any profile skill
            if any(profile_skill in keyword_lower for profile_skill in profile_skills_lower):
                continue
            
            # Only add if it seems technical (contains common tech indicators)
            # or is long enough to be a specific term
            if len(keyword_lower) > 6 or any(tech in keyword_lower for tech in 
                ['py', 'js', 'ml', 'ai', 'api', 'sql', 'framework', 'learn', 
                 'model', 'neural', 'cloud', 'deploy', 'test', 'metric']):
                missing.append(keyword)
        
        return missing
    
    def _extract_important_phrases(self, job_desc: str) -> list:
        """Extract important multi-word technical phrases from job description."""
        import re
        
        # Common important technical phrases patterns
        important_patterns = [
            r'\b(machine learning|deep learning|neural networks?)\b',
            r'\b(natural language processing|nlp)\b',
            r'\b(computer vision|cv)\b',
            r'\b(large language models?|llm|llms)\b',
            r'\b(data pipelines?|data engineering)\b',
            r'\b(model deployment|mlops|ml ops)\b',
            r'\b(a/?b testing|experimentation)\b',
            r'\b(tensorflow|pytorch|scikit-learn|keras|xgboost)\b',
            r'\b(docker|kubernetes|containerization)\b',
            r'\b(aws|azure|gcp|cloud)\b',
            r'\b(rest api|api development|microservices)\b',
            r'\b(ci/?cd|continuous integration)\b',
            r'\b(fine[- ]?tuning|quantization|optimization)\b',
            r'\b(evaluation metrics|model evaluation)\b',
            r'\b(statistics|probability|statistical)\b',
        ]
        
        phrases = []
        job_desc_lower = job_desc.lower()
        
        for pattern in important_patterns:
            matches = re.findall(pattern, job_desc_lower)
            phrases.extend(matches)
        
        return list(set(phrases))
    
    def _extract_position_skills(self, profile_data: Dict[str, Any]) -> list:
        """Extract skills mapped to each position."""
        experience = profile_data.get('experience', [])
        mapping = []
        
        for exp in experience:
            if exp.get('skills'):
                mapping.append({
                    'position': f"{exp.get('title')} at {exp.get('company')}",
                    'duration': exp.get('duration', ''),
                    'is_current': exp.get('is_current', False),
                    'skills': exp.get('skills', [])
                })
        
        return mapping
    
    def _find_relevant_experience(self, profile_data: Dict[str, Any], job_desc: str) -> list:
        """Find most relevant past positions based on job description."""
        experience = profile_data.get('experience', [])
        job_desc_lower = job_desc.lower()
        job_keywords = set(extract_keywords(job_desc_lower))
        
        scored_exp = []
        for exp in experience:
            # Build experience text INCLUDING the skills list
            exp_text_parts = [
                exp.get('title', ''),
                exp.get('description', ''),
                exp.get('company', '')
            ]
            
            # Add skills from this experience
            if exp.get('skills'):
                exp_text_parts.extend(exp.get('skills', []))
            
            exp_text = ' '.join(exp_text_parts).lower()
            exp_keywords = set(extract_keywords(exp_text))
            
            # Get complete skill phrases from the skills list (not split)
            exp_skills = set()
            if exp.get('skills'):
                for skill in exp['skills']:
                    clean_skill = skill.lower().strip()
                    if clean_skill:
                        exp_skills.add(clean_skill)
            
            # Calculate overlap in multiple ways:
            # 1. Text keyword overlap
            text_overlap = job_keywords & exp_keywords
            
            # 2. Check if complete skills appear in job description
            skill_matches = set()
            for skill in exp_skills:
                if skill in job_desc_lower:
                    skill_matches.add(skill)
                # Check variations
                skill_variations = self._get_skill_variations(skill)
                if any(var in job_desc_lower for var in skill_variations):
                    skill_matches.add(skill)
            
            # Combine all matches
            all_matches = text_overlap | skill_matches
            overlap_count = len(all_matches)
            
            if overlap_count > 0:
                scored_exp.append({
                    'position': f"{exp.get('title')} at {exp.get('company')}",
                    'relevance_score': overlap_count,
                    'matching_keywords': list(all_matches)[:8],
                    'duration': exp.get('duration', ''),
                    'is_current': exp.get('is_current', False)
                })
        
        return sorted(scored_exp, key=lambda x: x['relevance_score'], reverse=True)[:3]
    
    def _format_position_skills(self, mapping: list) -> str:
        """Format position-skills mapping for prompt."""
        if not mapping:
            return "No position-specific skills data available"
        
        formatted = []
        for item in mapping[:5]:  # Top 5 positions
            current = " (CURRENT)" if item['is_current'] else ""
            formatted.append(
                f"• {item['position']}{current}\n"
                f"  Skills: {', '.join(item['skills'][:8])}"
            )
        
        return '\n'.join(formatted)
    
    def _format_relevant_experience(self, relevant: list) -> str:
        """Format relevant experience for prompt."""
        if not relevant:
            return "No directly relevant experience found"
        
        formatted = []
        for exp in relevant:
            current = " (CURRENT)" if exp['is_current'] else ""
            formatted.append(
                f"• {exp['position']}{current}\n"
                f"  Relevance: {exp['relevance_score']} matching keywords\n"
                f"  Key matches: {', '.join(exp['matching_keywords'])}"
            )
        
        return '\n'.join(formatted)
    
    def _extract_improvements(self, analysis: str) -> list:
        """Extract improvement suggestions from analysis."""
        lines = analysis.split('\n')
        improvements = []
        
        capture = False
        for line in lines:
            line = line.strip()
            
            # Look for improvement sections
            if any(keyword in line.lower() for keyword in ['improvement', 'suggestion', 'recommendation', 'optimize']):
                capture = True
                continue
            
            if capture and line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    improvements.append(clean_line)
        
        return improvements[:8]