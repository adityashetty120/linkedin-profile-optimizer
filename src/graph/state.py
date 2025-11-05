"""Graph state definition for LangGraph."""

from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """State schema for the conversation graph."""
    
    # Messages
    messages: Annotated[List[Dict[str, str]], add_messages]
    
    # User data
    profile_data: Optional[Dict[str, Any]]
    profile_url: Optional[str]
    
    # Career context
    target_role: Optional[str]
    career_goals: Optional[str]
    job_description: Optional[str]
    
    # Job search settings
    use_online_search: Optional[bool]
    job_location: Optional[str]
    
    # Analysis results
    profile_analysis: Optional[Dict[str, Any]]
    job_match_results: Optional[Dict[str, Any]]
    generated_content: Optional[Dict[str, Any]]
    career_guidance: Optional[Dict[str, Any]]
    
    # Routing
    next_agent: Optional[str]
    
    # Session info
    session_id: str
    user_query: str