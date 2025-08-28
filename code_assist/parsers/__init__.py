"""
Code Assist Parsers Package
File parsing utilities for different programming languages
"""

__version__ = "1.0.0"
__description__ = "File parsers for Code Assist AI development companion"

try:
    from .base_parser import BaseParser
    from .python_parser import PythonParser
    
    __all__ = ['BaseParser', 'PythonParser']
except ImportError:
    __all__ = []