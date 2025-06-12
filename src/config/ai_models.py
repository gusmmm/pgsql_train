"""
Central AI Model Configura    # Text Section Extraction Model
    TEXT_EXTRACTION_MODEL: str = "gemini-2.5-flash-preview-05-20"
    
    # Table Extraction and Analysis Model  
    TABLE_EXTRACTION_MODEL: str = "gemini-2.5-flash-preview-05-20"
    
    # Image Analysis and Description Model
    IMAGE_ANALYSIS_MODEL: str = "gemini-2.5-flash-preview-05-20"
    
    # Paper Metadata Extraction Model (from ai_extractor.py)
    METADATA_EXTRACTION_MODEL: str = "gemini-2.5-flash-preview-05-20"per Processing System.

This module provides centralized configuration for all AI models used across
different extraction agents. This allows for easy model management and updates
without modifying individual agent files.

Usage:
    from src.config.ai_models import AI_MODELS
    
    # Use specific model for text extraction
    model = AI_MODELS.TEXT_EXTRACTION_MODEL
    
    # Or access all models
    all_models = AI_MODELS.get_all_models()
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class AIModelConfig:
    """
    Central configuration for AI models used across all extraction agents.
    
    This class follows the project's OOP patterns and provides a single source
    of truth for model configurations across the paper processing system.
    """
    
    # Text Section Extraction Model
    TEXT_EXTRACTION_MODEL: str = "gemini-2.5-flash-preview-04-17"
    
    # Table Extraction and Analysis Model
    TABLE_EXTRACTION_MODEL: str = "gemini-2.5-flash-preview-04-17"

    # Image Analysis and Description Model
    IMAGE_ANALYSIS_MODEL: str = "gemini-2.5-flash-preview-04-17"

    # Paper Metadata Extraction Model (from ai_extractor.py)
    METADATA_EXTRACTION_MODEL: str = "gemini-2.5-flash-preview-04-17"

    # General Purpose Model (fallback)
    DEFAULT_MODEL: str = "gemini-2.0-flash"
    
    # Model Configuration Parameters
    DEFAULT_TEMPERATURE: float = 0.1
    DEFAULT_MAX_TOKENS: int = 1048576
    
    # Advanced Model Options (for future use)
    # Pro models for complex analysis
    TEXT_EXTRACTION_PRO_MODEL: str = "gemini-2.5-pro-preview-06-05"
    TABLE_EXTRACTION_PRO_MODEL: str = "gemini-2.5-pro-preview-06-05"
    IMAGE_ANALYSIS_PRO_MODEL: str = "gemini-2.5-pro-preview-06-05"

    # Experimental models (for testing new features)
    EXPERIMENTAL_MODEL: str = "gemini-2.5-flash-preview-05-20"
    
    def get_model_for_agent(self, agent_type: str) -> str:
        """
        Get the appropriate model for a specific agent type.
        
        Args:
            agent_type: Type of agent ('text', 'table', 'image', 'metadata')
            
        Returns:
            Model name string
        """
        model_mapping = {
            'text': self.TEXT_EXTRACTION_MODEL,
            'table': self.TABLE_EXTRACTION_MODEL, 
            'image': self.IMAGE_ANALYSIS_MODEL,
            'metadata': self.METADATA_EXTRACTION_MODEL,
            'default': self.DEFAULT_MODEL
        }
        
        return model_mapping.get(agent_type.lower(), self.DEFAULT_MODEL)
    
    def get_pro_model_for_agent(self, agent_type: str) -> str:
        """
        Get the pro/advanced model for a specific agent type.
        
        Args:
            agent_type: Type of agent ('text', 'table', 'image')
            
        Returns:
            Pro model name string
        """
        pro_model_mapping = {
            'text': self.TEXT_EXTRACTION_PRO_MODEL,
            'table': self.TABLE_EXTRACTION_PRO_MODEL,
            'image': self.IMAGE_ANALYSIS_PRO_MODEL,
        }
        
        return pro_model_mapping.get(agent_type.lower(), self.DEFAULT_MODEL)
    
    def get_all_models(self) -> Dict[str, str]:
        """
        Get all configured models as a dictionary.
        
        Returns:
            Dictionary of all model configurations
        """
        return asdict(self)
    
    def update_model(self, agent_type: str, model_name: str) -> bool:
        """
        Update model configuration for a specific agent.
        
        Args:
            agent_type: Type of agent to update
            model_name: New model name
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            model_attr_mapping = {
                'text': 'TEXT_EXTRACTION_MODEL',
                'table': 'TABLE_EXTRACTION_MODEL',
                'image': 'IMAGE_ANALYSIS_MODEL', 
                'metadata': 'METADATA_EXTRACTION_MODEL',
                'default': 'DEFAULT_MODEL'
            }
            
            attr_name = model_attr_mapping.get(agent_type.lower())
            if attr_name and hasattr(self, attr_name):
                setattr(self, attr_name, model_name)
                return True
            return False
            
        except Exception:
            return False


# Global instance - single source of truth for all model configurations
AI_MODELS = AIModelConfig()


# Dynamic model access functions for backward compatibility
def get_text_model() -> str:
    """Get current text extraction model"""
    return AI_MODELS.TEXT_EXTRACTION_MODEL

def get_table_model() -> str:
    """Get current table extraction model"""
    return AI_MODELS.TABLE_EXTRACTION_MODEL

def get_image_model() -> str:
    """Get current image analysis model"""
    return AI_MODELS.IMAGE_ANALYSIS_MODEL

def get_metadata_model() -> str:
    """Get current metadata extraction model"""
    return AI_MODELS.METADATA_EXTRACTION_MODEL

def get_default_model() -> str:
    """Get current default model"""
    return AI_MODELS.DEFAULT_MODEL

# For agents that need direct access, use AI_MODELS.get_model_for_agent(agent_type)


def get_model_config_summary() -> str:
    """
    Get a human-readable summary of current model configurations.
    
    Returns:
        Formatted string with all model configurations
    """
    config = AI_MODELS.get_all_models()
    
    summary = "🤖 AI Model Configuration Summary\n"
    summary += "=" * 50 + "\n"
    summary += f"Text Extraction Model:     {config['TEXT_EXTRACTION_MODEL']}\n"
    summary += f"Table Extraction Model:    {config['TABLE_EXTRACTION_MODEL']}\n" 
    summary += f"Image Analysis Model:      {config['IMAGE_ANALYSIS_MODEL']}\n"
    summary += f"Metadata Extraction Model: {config['METADATA_EXTRACTION_MODEL']}\n"
    summary += f"Default Model:             {config['DEFAULT_MODEL']}\n"
    summary += "\n🚀 Pro Models:\n"
    summary += f"Text Pro Model:            {config['TEXT_EXTRACTION_PRO_MODEL']}\n"
    summary += f"Table Pro Model:           {config['TABLE_EXTRACTION_PRO_MODEL']}\n"
    summary += f"Image Pro Model:           {config['IMAGE_ANALYSIS_PRO_MODEL']}\n"
    summary += "\n⚙️  Configuration:\n"
    summary += f"Default Temperature:       {config['DEFAULT_TEMPERATURE']}\n"
    summary += f"Default Max Tokens:        {config['DEFAULT_MAX_TOKENS']}\n"
    
    return summary


# Example usage and testing
if __name__ == "__main__":
    print(get_model_config_summary())
    
    # Example of testing model retrieval (non-destructive)
    print("\n🔧 Testing model retrieval...")
    print(f"Text model: {AI_MODELS.get_model_for_agent('text')}")
    print(f"Table model: {AI_MODELS.get_model_for_agent('table')}")
    print(f"Image model: {AI_MODELS.get_model_for_agent('image')}")
    print(f"Metadata model: {AI_MODELS.get_model_for_agent('metadata')}")
    
    # Example of pro model retrieval
    print(f"\nPro models:")
    print(f"Text pro model: {AI_MODELS.get_pro_model_for_agent('text')}")
    print(f"Table pro model: {AI_MODELS.get_pro_model_for_agent('table')}")
    print(f"Image pro model: {AI_MODELS.get_pro_model_for_agent('image')}")
    
    # Example of update functionality (for demonstration only)
    print(f"\n🔧 Testing model update functionality...")
    original_image_model = AI_MODELS.get_model_for_agent('image')
    print(f"Original image model: {original_image_model}")
    
    # Test update
    success = AI_MODELS.update_model('image', 'gemini-2.5-pro')
    print(f"Update successful: {success}")
    print(f"Updated image model: {AI_MODELS.get_model_for_agent('image')}")
    
    # Restore original model
    AI_MODELS.update_model('image', original_image_model)
    print(f"Restored image model: {AI_MODELS.get_model_for_agent('image')}")
