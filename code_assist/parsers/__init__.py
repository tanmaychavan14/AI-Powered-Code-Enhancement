"""
Code Assist Parsers Package
File parsing utilities for different programming languages
"""

__version__ = "1.0.0"
__description__ = "File parsers for Code Assist AI development companion"

try:
    from .base_parser import BaseParser
    from .python_parser import PythonParser
    from .javascript_parser import JavaScriptParser
    from .java_parser import JavaParser
    
    __all__ = ['BaseParser', 'PythonParser', 'JavaScriptParser', 'JavaParser']
except ImportError:
    __all__ = []