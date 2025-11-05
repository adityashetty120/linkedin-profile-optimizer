"""LangGraph workflow definition."""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, AIMessage

from src.graph.state import GraphState
from src.agents import (
    ProfileAnalyzerAgent,
    JobMatcherAgent,
    ContentGeneratorAgent,
    CareerCounselorAgent
)
from src.services import LLMService, LinkedInScraper, JobDescriptionService
from src.memory import MemoryManager


def create_workflow(memory_manager: MemoryManager) -> StateGraph:
    """
    Create the LangGraph workflow.
    
    Args:
        memory_manager: Memory manager instance
        
    Returns:
        Configured StateGraph
    """
    
    # Initialize services
    llm_service = LLMService()
    scraper = LinkedInScraper()
    job_service = JobDescriptionService()
    
    # Initialize agents
    profile_analyzer = ProfileAnalyzerAgent(llm_service)
    job_matcher = JobMatcherAgent(llm_service, job_service)
    content_generator = ContentGeneratorAgent(llm_service)
    career_counselor = CareerCounselorAgent(llm_service)
    
    # Define node functions
    def router_node(state: GraphState) -> GraphState:
        """Route user query to appropriate agent."""
        query = state["user_query"]
        context = memory_manager.get_context_summary()
        
        # Use LLM to determine routing
        agent = llm_service.route_query(query, context)
        
        state["next_agent"] = agent
        return state
    
    def profile_analyzer_node(state: GraphState) -> GraphState:
        """Analyze LinkedIn profile."""
        profile_data = state.get("profile_data")
        query = state["user_query"]
        
        if not profile_data:
            # Check if we have it in memory
            profile_data = memory_manager.get_profile()
            if profile_data:
                state["profile_data"] = profile_data
        
        if profile_data:
            previous_analysis = memory_manager.get_latest_analysis("profile_analysis")
            prev_text = previous_analysis["result"]["detailed_analysis"] if previous_analysis else ""
            
            result = profile_analyzer.analyze(profile_data, query, prev_text)
            state["profile_analysis"] = result
            
            # Save to memory
            memory_manager.add_analysis("profile_analysis", result)
        else:
            state["profile_analysis"] = {
                "error": "No profile data available. Please provide a LinkedIn URL first."
            }
        
        return state
    
    def job_matcher_node(state: GraphState) -> GraphState:
        """Match profile with job description."""
        profile_data = state.get("profile_data") or memory_manager.get_profile()
        target_role = state.get("target_role") or memory_manager.get_target_role()
        custom_jd = state.get("job_description")
        use_online_search = state.get("use_online_search", False)
        location = state.get("job_location", "")
        
        if not profile_data:
            state["job_match_results"] = {
                "error": "No profile data available."
            }
        elif not target_role:
            state["job_match_results"] = {
                "error": "Please specify a target job role."
            }
        else:
            result = job_matcher.match(
                profile_data=profile_data,
                job_title=target_role,
                custom_jd=custom_jd,
                location=location,
                use_online_search=use_online_search
            )
            state["job_match_results"] = result
            
            # Save to memory
            memory_manager.add_analysis("job_match", result)
        
        return state
    
    def content_generator_node(state: GraphState) -> GraphState:
        """Generate improved content."""
        profile_data = state.get("profile_data") or memory_manager.get_profile()
        query = state["user_query"]
        target_role = state.get("target_role") or memory_manager.get_target_role()
        job_desc = state.get("job_description", "")
        
        # Check if user wants suggestions for all sections
        query_lower = query.lower()
        generate_all = any(keyword in query_lower for keyword in [
            'all section', 'every section', 'complete profile', 'entire profile',
            'comprehensive', 'all suggestions', 'full profile'
        ])
        
        if profile_data:
            if generate_all:
                # Generate suggestions for all sections
                result = content_generator.generate_all_sections(
                    profile_data=profile_data,
                    target_role=target_role,
                    job_description=job_desc
                )
                state["generated_content"] = result
            else:
                # Generate for specific section
                section = _extract_section_from_query(query)
                current_content = _get_section_content(profile_data, section)
                
                result = content_generator.generate(
                    section_name=section,
                    current_content=current_content,
                    profile_data=profile_data,
                    target_role=target_role,
                    job_description=job_desc
                )
                state["generated_content"] = result
            
            # Save to memory
            memory_manager.add_analysis("content_generation", result)
        else:
            state["generated_content"] = {
                "error": "Could not determine which section to improve."
            }
        
        return state
    
    def career_counselor_node(state: GraphState) -> GraphState:
        """Provide career counseling."""
        profile_data = state.get("profile_data") or memory_manager.get_profile()
        query = state["user_query"]
        career_goals = state.get("career_goals") or memory_manager.get_career_goals()
        target_role = state.get("target_role") or memory_manager.get_target_role()
        
        if profile_data:
            result = career_counselor.counsel(
                profile_data=profile_data,
                query=query,
                career_goals=career_goals,
                target_role=target_role
            )
            state["career_guidance"] = result
            
            # Save to memory
            memory_manager.add_analysis("career_counseling", result)
        else:
            state["career_guidance"] = {
                "error": "No profile data available."
            }
        
        return state
    
    def response_formatter_node(state: GraphState) -> GraphState:
        """Format the final response."""
        next_agent = state.get("next_agent")
        
        # Get the appropriate result based on agent
        if next_agent == "profile_analyzer":
            result = state.get("profile_analysis", {})
            response = _format_profile_analysis(result)
        elif next_agent == "job_matcher":
            result = state.get("job_match_results", {})
            response = _format_job_match(result)
        elif next_agent == "content_generator":
            result = state.get("generated_content", {})
            response = _format_generated_content(result)
        elif next_agent == "career_counselor":
            result = state.get("career_guidance", {})
            response = _format_career_guidance(result)
        else:
            response = "I'm not sure how to help with that. Could you rephrase your question?"
        
        # Add to messages
        state["messages"].append({
            "role": "assistant",
            "content": response
        })
        
        # Save to memory
        memory_manager.add_message("assistant", response)
        
        return state
    
    # Build the graph
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("router", router_node)
    workflow.add_node("profile_analyzer", profile_analyzer_node)
    workflow.add_node("job_matcher", job_matcher_node)
    workflow.add_node("content_generator", content_generator_node)
    workflow.add_node("career_counselor", career_counselor_node)
    workflow.add_node("response_formatter", response_formatter_node)
    
    # Define edges
    workflow.set_entry_point("router")
    
    # Conditional routing from router
    workflow.add_conditional_edges(
        "router",
        lambda state: state["next_agent"],
        {
            "profile_analyzer": "profile_analyzer",
            "job_matcher": "job_matcher",
            "content_generator": "content_generator",
            "career_counselor": "career_counselor"
        }
    )
    
    # All agents go to response formatter
    workflow.add_edge("profile_analyzer", "response_formatter")
    workflow.add_edge("job_matcher", "response_formatter")
    workflow.add_edge("content_generator", "response_formatter")
    workflow.add_edge("career_counselor", "response_formatter")
    
    # End after formatting
    workflow.add_edge("response_formatter", END)
    
    return workflow


# Helper functions

def _extract_section_from_query(query: str) -> str:
    """Extract which profile section to improve from query."""
    query_lower = query.lower()
    
    if "about" in query_lower or "summary" in query_lower:
        return "about"
    elif "headline" in query_lower:
        return "headline"
    elif "experience" in query_lower:
        return "experience"
    elif "education" in query_lower:
        return "education"
    elif "skills" in query_lower:
        return "skills"
    else:
        return "about"  # Default


def _get_section_content(profile_data: Dict[str, Any], section: str) -> str:
    """Get content from specific profile section."""
    if not profile_data:
        return ""
    
    content = profile_data.get(section, "")
    
    if isinstance(content, list):
        # Format list content
        return "\n".join([str(item) for item in content])
    
    return str(content)


def _format_profile_analysis(result: Dict[str, Any]) -> str:
    """Format profile analysis result."""
    if "error" in result:
        return f"❌ {result['error']}"
    
    response = f"""
📊 **Profile Analysis Results**

**Completeness Score:** {result['completeness_score']}% (Grade: {result['grade']})

**Detailed Analysis:**
{result['detailed_analysis']}

**Missing Sections:** {', '.join(result['missing_sections']) if result['missing_sections'] else 'None'}
**Weak Sections:** {', '.join(result['weak_sections']) if result['weak_sections'] else 'None'}
"""
    
    return response.strip()


def _format_job_match(result: Dict[str, Any]) -> str:
    """Format job match result."""
    if "error" in result:
        return f"❌ {result['error']}"
    
    response = f"""
🎯 **Job Match Analysis: {result['job_title']}**

**Match Score:** {result['match_score']}% (Confidence: {result['confidence']})

**Matching Skills:** {', '.join(result['matching_skills'][:10]) if result['matching_skills'] else 'None identified'}

**Missing Skills:** {', '.join(result['missing_skills'][:10]) if result['missing_skills'] else 'None'}

**Detailed Analysis:**
{result['detailed_analysis']}
"""
    
    return response.strip()


def _format_generated_content(result: Dict[str, Any]) -> str:
    """Format generated content result."""
    if "error" in result:
        return f"❌ {result['error']}"
    
    # Check if this is a comprehensive all-sections result
    if "sections" in result and "priorities" in result:
        return _format_all_sections_content(result)
    
    # Single section format
    section = result.get('section', 'Unknown')
    output = f"""
✨ **Improved {section.title()} Section**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 **Original Content:**
```
{result.get('original_content', 'No content')[:500]}{'...' if len(str(result.get('original_content', ''))) > 500 else ''}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ **Generated Content:**
```
{result.get('generated_content', 'No content generated')}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 **Key Improvements Made:**
"""
    
    improvements = result.get('improvements', [])
    if improvements:
        for i, improvement in enumerate(improvements, 1):
            output += f"{i}. {improvement}\n"
    else:
        output += "• See generated content above\n"
    
    keywords = result.get('keywords_added', [])
    if keywords:
        output += f"\n📌 **Keywords Added:**\n{', '.join(keywords)}\n"
    
    credibility = result.get('credibility_elements', [])
    if credibility:
        output += "\n✅ **Credibility Elements Added:**\n"
        for cred in credibility:
            output += f"• {cred}\n"
    
    tips = result.get('tips', [])
    if tips:
        output += "\n💡 **Additional Tips:**\n"
        for tip in tips:
            output += f"• {tip}\n"
    
    return output.strip()


def _format_all_sections_content(result: Dict[str, Any]) -> str:
    """Format comprehensive all-sections content suggestions."""
    priorities = result.get('priorities', {})
    sections = result.get('sections', {})
    quick_wins = result.get('quick_wins', [])
    advanced_tips = result.get('advanced_tips', [])
    
    # Build response
    response = f"""
🎨 **Comprehensive LinkedIn Profile Optimization Plan**

**Target Role:** {result.get('target_role', 'General professional development')}

{result.get('overall_strategy', '')}

---

## 📊 Section Priorities

"""
    
    # Add priorities with visual indicators
    priority_order = ['HIGH', 'MEDIUM', 'LOW']
    for priority_level in priority_order:
        matching_sections = {name: info for name, info in priorities.items() if info['priority'] == priority_level}
        if matching_sections:
            priority_emoji = "🔴" if priority_level == "HIGH" else "🟡" if priority_level == "MEDIUM" else "🟢"
            response += f"\n### {priority_emoji} {priority_level} Priority\n\n"
            
            for section_name, info in matching_sections.items():
                response += f"**{section_name.title()}**\n"
                response += f"- Reason: {info['reason']}\n"
                response += f"- Impact: {info['impact']}\n\n"
    
    response += "\n---\n\n## ⚡ Quick Wins (Start Here!)\n\n"
    
    if quick_wins:
        for i, win in enumerate(quick_wins, 1):
            response += f"""
**{i}. {win['section']}**
- **Action:** {win['action']}
- **Current:** {win['current_length']}
- **Time:** {win['time']} | **Impact:** {win['impact']}

"""
    else:
        response += "_No major quick wins identified - your profile is in good shape!_\n\n"
    
    response += "\n---\n\n## 📝 Detailed Section Suggestions\n\n"
    
    # Add suggestions for each section
    section_order = ['headline', 'about', 'experience', 'skills', 'education']
    for section_name in section_order:
        if section_name in sections:
            section_data = sections[section_name]
            priority_info = priorities.get(section_name, {})
            priority_emoji = "🔴" if priority_info.get('priority') == "HIGH" else "🟡" if priority_info.get('priority') == "MEDIUM" else "🟢"
            
            response += f"""
### {priority_emoji} {section_name.title()}

**Generated Content:**
```
{section_data.get('generated_content', 'See requirements below')}
```

**Key Improvements Made:**
{chr(10).join([f"• {imp}" for imp in section_data.get('improvements', [])]) if section_data.get('improvements') else '• See generated content above'}

**Keywords Added:** {', '.join(section_data.get('keywords_added', [])[:8]) if section_data.get('keywords_added') else 'Industry-relevant terms'}

**Credibility Elements Added:**
{chr(10).join([f"• {cred}" for cred in section_data.get('credibility_elements', [])]) if section_data.get('credibility_elements') else '• See improvements above'}

**Additional Tips:**
{chr(10).join([f"• {tip}" for tip in section_data.get('tips', [])]) if section_data.get('tips') else '• Focus on implementing the generated content'}

---

"""
    
    response += "\n## 🚀 Advanced Optimization Tips\n\n"
    
    if advanced_tips:
        for tip in advanced_tips:
            response += f"{tip}\n\n"
    
    response += """
---

## 🎯 Next Steps

1. **Start with Quick Wins:** Tackle the high-impact, low-effort changes first
2. **Focus on High Priority Sections:** Address red-flagged sections within the next 24-48 hours
3. **Implement One Section at a Time:** Don't overwhelm yourself - steady progress is key
4. **Get Feedback:** Ask a colleague or mentor to review your changes
5. **Track Results:** Monitor profile views and connection requests after updates

**Remember:** A great LinkedIn profile is never "done" - keep iterating based on your career goals!
"""
    
    return response.strip()


def _format_career_guidance(result: Dict[str, Any]) -> str:
    """Format career guidance result."""
    if "error" in result:
        return f"❌ {result['error']}"
    
    # For simple conversational responses, just return the guidance text
    guidance = result.get('guidance', '')
    skill_gaps = result.get('skill_gaps', [])
    learning_resources = result.get('learning_resources', [])
    next_steps = result.get('next_steps', [])
    
    # If no structured data was extracted, just return the guidance as-is
    if not skill_gaps and not learning_resources and not next_steps:
        return guidance
    
    # If we have structured data, format it nicely
    response = f"{guidance}\n\n"
    
    if skill_gaps:
        response += f"**Skill Gaps Identified:**\n{chr(10).join([f'• {gap}' for gap in skill_gaps])}\n\n"
    
    if learning_resources:
        response += f"**Recommended Learning Resources:**\n{chr(10).join([f'• {res}' for res in learning_resources])}\n\n"
    
    if next_steps:
        response += f"**Next Steps:**\n{chr(10).join([f'{i+1}. {step}' for i, step in enumerate(next_steps)])}"
    
    return response.strip()