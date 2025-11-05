"""Memory management for maintaining conversation context and user data."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
from src.config.settings import settings


class MemoryManager:
    """Manages session and persistent memory for user interactions."""
    
    def __init__(self, session_id: str):
        """
        Initialize memory manager.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.session_file = settings.profiles_dir / f"session_{session_id}.json"
        
        # Session memory (temporary)
        self.session_memory: Dict[str, Any] = {
            "session_id": session_id,
            "started_at": datetime.now().isoformat(),
            "conversation_history": [],
            "current_profile": None,
            "target_role": None,
            "career_goals": None,
            "analyses": []
        }
        
        # Load existing session if available
        self._load_session()
    
    def _load_session(self):
        """Load existing session data if available."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    loaded_data = json.load(f)
                    self.session_memory.update(loaded_data)
            except Exception as e:
                print(f"Error loading session: {e}")
    
    def save_session(self):
        """Save current session to disk."""
        try:
            self.session_memory["updated_at"] = datetime.now().isoformat()
            with open(self.session_file, 'w') as f:
                json.dump(self.session_memory, f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def add_message(self, role: str, content: str):
        """
        Add message to conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        self.session_memory["conversation_history"].append(message)
        self.save_session()
    
    def get_conversation_history(self, last_n: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get conversation history.
        
        Args:
            last_n: Number of recent messages to return (None for all)
            
        Returns:
            List of conversation messages
        """
        history = self.session_memory["conversation_history"]
        if last_n:
            return history[-last_n:]
        return history
    
    def set_profile(self, profile_data: Dict[str, Any]):
        """
        Store current LinkedIn profile data.
        
        Args:
            profile_data: Profile information
        """
        self.session_memory["current_profile"] = profile_data
        self.session_memory["profile_loaded_at"] = datetime.now().isoformat()
        self.save_session()
    
    def get_profile(self) -> Optional[Dict[str, Any]]:
        """Get stored profile data."""
        return self.session_memory.get("current_profile")
    
    def set_target_role(self, role: str):
        """Set target job role."""
        self.session_memory["target_role"] = role
        self.save_session()
    
    def get_target_role(self) -> Optional[str]:
        """Get target job role."""
        return self.session_memory.get("target_role")
    
    def set_career_goals(self, goals: str):
        """Set career goals."""
        self.session_memory["career_goals"] = goals
        self.save_session()
    
    def get_career_goals(self) -> Optional[str]:
        """Get career goals."""
        return self.session_memory.get("career_goals")
    
    def add_analysis(self, analysis_type: str, result: Any):
        """
        Store analysis result.
        
        Args:
            analysis_type: Type of analysis (profile, job_match, etc.)
            result: Analysis result
        """
        analysis = {
            "type": analysis_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.session_memory["analyses"].append(analysis)
        self.save_session()
    
    def get_latest_analysis(self, analysis_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get most recent analysis.
        
        Args:
            analysis_type: Filter by analysis type (None for any type)
            
        Returns:
            Latest analysis or None
        """
        analyses = self.session_memory.get("analyses", [])
        
        if not analyses:
            return None
        
        if analysis_type:
            filtered = [a for a in analyses if a["type"] == analysis_type]
            return filtered[-1] if filtered else None
        
        return analyses[-1]
    
    def get_context_summary(self) -> str:
        """
        Generate a summary of current context for LLM.
        
        Returns:
            Context summary string
        """
        profile = self.get_profile()
        target_role = self.get_target_role()
        career_goals = self.get_career_goals()
        
        summary_parts = []
        
        if profile:
            summary_parts.append(f"Profile loaded: {profile.get('full_name', 'Unknown')}")
            summary_parts.append(f"Current headline: {profile.get('headline', 'Not set')}")
        
        if target_role:
            summary_parts.append(f"Target role: {target_role}")
        
        if career_goals:
            summary_parts.append(f"Career goals: {career_goals}")
        
        recent_analyses = self.session_memory.get("analyses", [])[-3:]
        if recent_analyses:
            summary_parts.append(f"Recent analyses: {len(recent_analyses)}")
        
        return "\n".join(summary_parts) if summary_parts else "No context available yet."
    
    def clear_session(self):
        """Clear current session data."""
        self.session_memory = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "conversation_history": [],
            "current_profile": None,
            "target_role": None,
            "career_goals": None,
            "analyses": []
        }
        self.save_session()