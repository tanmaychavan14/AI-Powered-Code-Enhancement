#!/usr/bin/env python3
"""
Python Parser
Specialized parser for Python files
"""

from .base_parser import BaseParser
import ast
import re

class PythonParser(BaseParser):
    """Python-specific parser with AST support"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.py', '.pyw']
        self.language = "python"
    
    def parse(self, content, file_path):
        """Parse Python file and extract functions, classes, imports"""
        base_data = super().parse(content, file_path)
        
        # Add Python-specific parsing
        python_data = {
            'functions': self._extract_functions(content),
            'classes': self._extract_classes(content),
            'imports': self._extract_imports(content),
            'decorators': self._extract_decorators(content),
            'docstrings': self._extract_docstrings(content),
            'complexity': self._analyze_complexity(content)
        }
        
        base_data.update(python_data)
        return base_data
    
    def _extract_functions(self, content):
        """Extract function definitions using regex and AST"""
        functions = []
        
        # Simple regex approach
        func_pattern = r'^\s*def\s+(\w+)\s*\([^)]*\):'
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line)
            if match:
                func_name = match.group(1)
                # Get function signature
                signature = line.strip()
                
                # Try to get docstring
                docstring = self._get_function_docstring(lines, i + 1)
                
                functions.append({
                    'name': func_name,
                    'line': i + 1,
                    'signature': signature,
                    'docstring': docstring,
                    'is_private': func_name.startswith('_'),
                    'is_dunder': func_name.startswith('__') and func_name.endswith('__')
                })
        
        return functions
    
    def _extract_classes(self, content):
        """Extract class definitions"""
        classes = []
        class_pattern = r'^\s*class\s+(\w+)(?:\([^)]*\))?:'
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.match(class_pattern, line)
            if match:
                class_name = match.group(1)
                
                # Extract inheritance info
                inheritance = []
                if '(' in line and ')' in line:
                    inherit_part = line[line.find('(')+1:line.find(')')]
                    inheritance = [cls.strip() for cls in inherit_part.split(',') if cls.strip()]
                
                # Get class docstring
                docstring = self._get_function_docstring(lines, i + 1)
                
                classes.append({
                    'name': class_name,
                    'line': i + 1,
                    'inheritance': inheritance,
                    'docstring': docstring,
                    'is_private': class_name.startswith('_')
                })
        
        return classes
    
    def _extract_imports(self, content):
        """Extract import statements with details"""
        imports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if stripped.startswith('import ') and not stripped.startswith('import '):
                # Handle "import module" statements
                modules = stripped[7:].split(',')
                for module in modules:
                    imports.append({
                        'type': 'import',
                        'module': module.strip(),
                        'alias': None,
                        'line': i + 1,
                        'statement': stripped
                    })
            
            elif stripped.startswith('from ') and ' import ' in stripped:
                # Handle "from module import item" statements
                parts = stripped.split(' import ')
                module = parts[0][5:].strip()  # Remove 'from '
                items = parts[1].split(',')
                
                for item in items:
                    item = item.strip()
                    alias = None
                    if ' as ' in item:
                        item, alias = item.split(' as ')
                        alias = alias.strip()
                    
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'item': item.strip(),
                        'alias': alias,
                        'line': i + 1,
                        'statement': stripped
                    })
        
        return imports
    
    def _extract_decorators(self, content):
        """Extract decorator usage"""
        decorators = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('@'):
                decorator_name = stripped[1:].split('(')[0]  # Remove @ and params
                decorators.append({
                    'name': decorator_name,
                    'line': i + 1,
                    'full_decorator': stripped
                })
        
        return decorators
    
    def _extract_docstrings(self, content):
        """Extract module and function docstrings"""
        docstrings = []
        lines = content.split('\n')
        
        # Look for triple-quoted strings
        in_docstring = False
        docstring_start = 0
        quote_type = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    in_docstring = True
                    docstring_start = i
                    quote_type = '"""' if '"""' in stripped else "'''"
                    
                    # Check if it's a one-line docstring
                    if stripped.endswith(quote_type) and len(stripped) > 6:
                        docstrings.append({
                            'content': stripped[3:-3],
                            'start_line': i + 1,
                            'end_line': i + 1,
                            'type': 'single_line'
                        })
                        in_docstring = False
            else:
                if quote_type in stripped:
                    docstring_content = '\n'.join(lines[docstring_start:i+1])
                    docstrings.append({
                        'content': docstring_content,
                        'start_line': docstring_start + 1,
                        'end_line': i + 1,
                        'type': 'multi_line'
                    })
                    in_docstring = False
        
        return docstrings
    
    def _get_function_docstring(self, lines, start_line):
        """Get docstring for a function starting from given line"""
        if start_line >= len(lines):
            return None
        
        # Look for the next non-empty line
        for i in range(start_line, min(start_line + 5, len(lines))):
            stripped = lines[i].strip()
            if stripped:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    quote = '"""' if '"""' in stripped else "'''"
                    if stripped.endswith(quote) and len(stripped) > 6:
                        return stripped[3:-3]
                    # Multi-line docstring handling would go here
                break
        
        return None
    
    def _analyze_complexity(self, content):
        """Basic complexity analysis"""
        lines = content.split('\n')
        complexity_indicators = {
            'if_statements': 0,
            'loops': 0,
            'try_blocks': 0,
            'nested_functions': 0
        }
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('if ') or ' if ' in stripped:
                complexity_indicators['if_statements'] += 1
            if stripped.startswith('for ') or stripped.startswith('while '):
                complexity_indicators['loops'] += 1
            if stripped.startswith('try:'):
                complexity_indicators['try_blocks'] += 1
            if '    def ' in line or '\tdef ' in line:  # Nested function
                complexity_indicators['nested_functions'] += 1
        
        return complexity_indicators