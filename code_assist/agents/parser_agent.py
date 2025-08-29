#!/usr/bin/env python3
"""
Parser Agent - Handles language detection and file parsing
Coordinates with language-specific parsers
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List  # Added List import here
from rich.console import Console

console = Console()

class ParserAgent:
    """Agent responsible for language detection and coordinating parsing"""
    
    def __init__(self):
        self.language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript', 
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java'
        }
        
        self.parsers = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Initialize language-specific parsers with fallback"""
        try:
            from parsers.python_parser import PythonParser
            self.parsers['python'] = PythonParser()
        except ImportError:
            console.print("[yellow]Python parser not available, using fallback[/yellow]")
            self.parsers['python'] = self._create_fallback_parser('python')
        
        try:
            from parsers.javascript_parser import JavaScriptParser
            self.parsers['javascript'] = JavaScriptParser()
        except ImportError:
            console.print("[yellow]JavaScript parser not available, using fallback[/yellow]")
            self.parsers['javascript'] = self._create_fallback_parser('javascript')
        
        try:
            from parsers.java_parser import JavaParser
            self.parsers['java'] = JavaParser()
        except ImportError:
            console.print("[yellow]Java parser not available, using fallback[/yellow]")
            self.parsers['java'] = self._create_fallback_parser('java')
    
    def _create_fallback_parser(self, language):
        """Create fallback parser for specific language"""
        class FallbackParser:
            def __init__(self, lang):
                self.language = lang
            
            def parse(self, content, file_path):
                # Basic parsing - extract classes and functions using simple regex
                import re
                
                classes = []
                functions = []
                imports = []
                
                lines = content.split('\n')
                
                if self.language == 'python':
                    # Python-specific patterns
                    class_pattern = r'^\s*class\s+(\w+).*:'
                    function_pattern = r'^\s*def\s+(\w+)\s*\([^)]*\).*:'
                    import_pattern = r'^\s*(import|from)\s+[\w\.]+'
                    
                elif self.language == 'javascript':
                    # JavaScript-specific patterns
                    class_pattern = r'^\s*class\s+(\w+)'
                    function_pattern = r'^\s*(function\s+(\w+)|(\w+)\s*[=:]\s*function|(\w+)\s*\([^)]*\)\s*[=]*\s*>)'
                    import_pattern = r'^\s*(import|require)'
                    
                elif self.language == 'java':
                    # Java-specific patterns
                    class_pattern = r'^\s*(public\s+|private\s+|protected\s+)*class\s+(\w+)'
                    function_pattern = r'^\s*(public\s+|private\s+|protected\s+|static\s+)*[\w\<\>\[\]]+\s+(\w+)\s*\([^)]*\)'
                    import_pattern = r'^\s*import\s+'
                
                for i, line in enumerate(lines):
                    # Find classes
                    class_match = re.search(class_pattern, line)
                    if class_match:
                        class_name = class_match.group(1) if self.language == 'python' else class_match.group(2)
                        classes.append({
                            'name': class_name,
                            'line': i + 1,
                            'type': 'class'
                        })
                    
                    # Find functions
                    func_match = re.search(function_pattern, line)
                    if func_match:
                        if self.language == 'python':
                            func_name = func_match.group(1)
                        elif self.language == 'javascript':
                            func_name = func_match.group(2) or func_match.group(3) or func_match.group(4)
                        else:  # java
                            func_name = func_match.group(2)
                        
                        if func_name:
                            functions.append({
                                'name': func_name,
                                'line': i + 1,
                                'type': 'function'
                            })
                    
                    # Find imports
                    if re.search(import_pattern, line):
                        imports.append(line.strip())
                
                return {
                    'file_path': file_path,
                    'language': self.language,
                    'content': content,
                    'classes': classes,
                    'functions': functions,
                    'imports': imports,
                    'lines': len(lines),
                    'chars': len(content),
                    'parsed': True
                }
        
        return FallbackParser(language)
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        try:
            path = Path(file_path)
            extension = path.suffix.lower()
            language = self.language_map.get(extension, 'unknown')
            
            console.print(f"[dim]Detected language: {language} for {path.name}[/dim]")
            return language
            
        except Exception as e:
            console.print(f"[yellow]Language detection error: {e}[/yellow]")
            return 'unknown'
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single file using appropriate parser"""
        try:
            # Detect language
            language = self.detect_language(file_path)
            
            if language == 'unknown':
                return {
                    'error': f'Unsupported file type: {Path(file_path).suffix}',
                    'parsed': False
                }
            
            # Get appropriate parser
            parser = self.parsers.get(language)
            if not parser:
                return {
                    'error': f'No parser available for language: {language}',
                    'parsed': False
                }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse content
            parsed_result = parser.parse(content, file_path)
            
            return parsed_result
            
        except FileNotFoundError:
            return {
                'error': f'File not found: {file_path}',
                'parsed': False
            }
        except UnicodeDecodeError:
            return {
                'error': f'Cannot read file (encoding issue): {file_path}',
                'parsed': False
            }
        except Exception as e:
            return {
                'error': f'Parsing error: {str(e)}',
                'parsed': False
            }
    
    def parse_multiple_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """Parse multiple files and return combined results"""
        results = {}
        
        for file_path in file_paths:
            try:
                parsed_result = self.parse_file(file_path)
                results[file_path] = parsed_result
            except Exception as e:
                results[file_path] = {
                    'error': str(e),
                    'parsed': False
                }
        
        return results
    
    def get_project_structure(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract high-level project structure"""
        structure = {
            'languages': {},
            'total_files': len(parsed_data),
            'total_classes': 0,
            'total_functions': 0,
            'files_by_language': {}
        }
        
        for file_path, data in parsed_data.items():
            if data.get('parsed', False):
                language = data.get('language', 'unknown')
                
                # Count by language
                if language not in structure['languages']:
                    structure['languages'][language] = 0
                structure['languages'][language] += 1
                
                # Group files by language
                if language not in structure['files_by_language']:
                    structure['files_by_language'][language] = []
                structure['files_by_language'][language].append(file_path)
                
                # Count classes and functions
                structure['total_classes'] += len(data.get('classes', []))
                structure['total_functions'] += len(data.get('functions', []))
        
        return structure