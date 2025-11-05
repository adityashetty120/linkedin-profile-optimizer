"""Custom checkpointer for LangGraph state persistence."""

from typing import Dict, Any, Optional
from langgraph.checkpoint import BaseCheckpointSaver
from langgraph.checkpoint.base import Checkpoint
import json
from pathlib import Path
from src.config.settings import settings


class CustomCheckpointer(BaseCheckpointSaver):
    """Custom checkpointer for saving LangGraph state."""
    
    def __init__(self, checkpoint_dir: Optional[Path] = None):
        """
        Initialize checkpointer.
        
        Args:
            checkpoint_dir: Directory for storing checkpoints
        """
        self.checkpoint_dir = checkpoint_dir or settings.profiles_dir / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def put(self, config: Dict[str, Any], checkpoint: Checkpoint) -> None:
        """
        Save a checkpoint.
        
        Args:
            config: Configuration dictionary
            checkpoint: Checkpoint to save
        """
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        checkpoint_file = self.checkpoint_dir / f"{thread_id}.json"
        
        try:
            checkpoint_data = {
                "config": config,
                "state": checkpoint,
            }
            
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
    
    def get(self, config: Dict[str, Any]) -> Optional[Checkpoint]:
        """
        Load a checkpoint.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Loaded checkpoint or None
        """
        thread_id = config.get("configurable", {}).get("thread_id", "default")
        checkpoint_file = self.checkpoint_dir / f"{thread_id}.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
                return checkpoint_data.get("state")
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return None
    
    def list(self, config: Dict[str, Any]) -> list:
        """
        List all checkpoints for a thread.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            List of checkpoints
        """
        # Simple implementation - returns single checkpoint if exists
        checkpoint = self.get(config)
        return [checkpoint] if checkpoint else []