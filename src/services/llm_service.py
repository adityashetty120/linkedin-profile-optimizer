"""LLM service for AI-powered analysis and generation."""

from typing import Dict, Any, Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from src.config.settings import settings


class LLMService:
    """Service for interacting with Large Language Models."""
    
    def __init__(self, provider: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize LLM service.
        
        Args:
            provider: LLM provider ('google' for Gemini)
            model: Model name (e.g., 'gemini-2.0-flash-exp')
        """
        self.provider = provider or settings.llm_provider
        self.model = model or settings.llm_model
        self.temperature = settings.llm_temperature
        
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on provider."""
        if self.provider == "google":
            return ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=settings.gemini_api_key,
                temperature=self.temperature,
                convert_system_message_to_human=True
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}. Use 'google' for Gemini.")
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            conversation_history: Previous conversation messages
            
        Returns:
            Generated response string
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Add current prompt
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            response = self.llm.invoke(messages)
            
            return response.content
            
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return f"Error: {str(e)}"
    
    def analyze_profile(self, profile_data: str, query: str, previous_analysis: str = "") -> str:
        """Analyze LinkedIn profile."""
        from src.utils.prompts import PROFILE_ANALYSIS_PROMPT
        
        prompt = PROFILE_ANALYSIS_PROMPT.format(
            profile_data=profile_data,
            previous_analysis=previous_analysis,
            query=query
        )
        
        return self.generate_response(prompt)
    
    def match_job(
        self,
        profile_data: str,
        job_description: str,
        job_title: str
    ) -> str:
        """Match profile with job description."""
        from src.utils.prompts import JOB_MATCH_PROMPT
        
        prompt = JOB_MATCH_PROMPT.format(
            profile_data=profile_data,
            job_description=job_description,
            job_title=job_title
        )
        
        return self.generate_response(prompt)
    
    def generate_content(
        self,
        section_name: str,
        current_content: str,
        target_role: str,
        job_description: str,
        query: str
    ) -> str:
        """Generate improved content for profile section."""
        from src.utils.prompts import CONTENT_GENERATION_PROMPT
        
        prompt = CONTENT_GENERATION_PROMPT.format(
            section_name=section_name,
            current_content=current_content,
            target_role=target_role,
            job_description=job_description,
            query=query
        )
        
        return self.generate_response(prompt)
    
    def provide_career_counseling(
        self,
        profile_data: str,
        career_goals: str,
        target_role: str,
        query: str
    ) -> str:
        """Provide career counseling and guidance."""
        from src.utils.prompts import CAREER_COUNSELING_PROMPT
        
        prompt = CAREER_COUNSELING_PROMPT.format(
            profile_data=profile_data,
            career_goals=career_goals,
            target_role=target_role,
            query=query
        )
        
        return self.generate_response(prompt)
    
    def route_query(self, query: str, context: str) -> str:
        """Determine which agent should handle the query."""
        from src.utils.prompts import ROUTER_PROMPT
        
        prompt = ROUTER_PROMPT.format(query=query, context=context)
        
        response = self.generate_response(prompt)
        
        # Extract agent name from response
        response_lower = response.lower().strip()
        
        if "profile_analyzer" in response_lower:
            return "profile_analyzer"
        elif "job_matcher" in response_lower:
            return "job_matcher"
        elif "content_generator" in response_lower:
            return "content_generator"
        elif "career_counselor" in response_lower:
            return "career_counselor"
        else:
            # Default to career counselor for general queries
            return "career_counselor"