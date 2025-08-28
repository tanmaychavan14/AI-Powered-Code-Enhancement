"""
Code Assist Agents Package  
AI agents for various development tasks
"""

__version__ = "1.0.0"
__description__ = "AI agents for Code Assist development companion"

try:
    from .base_agent import BaseAgent
    from .test_agent import TestAgent
    
    __all__ = ['BaseAgent', 'TestAgent']
except ImportError:
    __all__ = []