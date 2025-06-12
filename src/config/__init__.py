"""
Configuration module for the Paper Processing System.

This module provides centralized configuration management for AI models,
database settings, and other system-wide parameters.
"""

from .ai_models import (
    AI_MODELS,
    get_text_model,
    get_table_model,
    get_image_model,
    get_metadata_model,
    get_default_model,
    get_model_config_summary
)

__all__ = [
    'AI_MODELS',
    'get_text_model',
    'get_table_model',
    'get_image_model',
    'get_metadata_model', 
    'get_default_model',
    'get_model_config_summary'
]
