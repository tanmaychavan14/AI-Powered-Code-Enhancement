#!/usr/bin/env python3
"""
JavaScript Parser
Specialized parser for JavaScript/TypeScript files
"""

from .base_parser import BaseParser
import re

class JavaScriptParser(BaseParser):
    """JavaScript/TypeScript-specific parser"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.js', '.jsx', '.ts', '.tsx', '.mjs']
        self.language = "javascript"
    
    def parse(self, content, file_path):
        """Parse JavaScript file and extract functions, classes, imports, etc."""
        base_data = super().parse(content, file_path)
        
        # Add JavaScript-specific parsing
        js_data = {
            'functions': self._extract_functions(content),
            'classes': self._extract_classes(content),
            'imports': self._extract_imports(content),
            'exports': self._extract_exports(content),
            'variables': self._extract_variables(content),
            'arrow_functions': self._extract_arrow_functions(content),
            'complexity': self._analyze_complexity(content),
            'is_typescript': file_path.endswith(('.ts', '.tsx')),
            'is_react': file_path.endswith(('.jsx', '.tsx')) or 'react' in content.lower()
        }
        
        base_data.update(js_data)
        return base_data
    
    def _extract_functions(self, content):
        """Extract function declarations and expressions"""
        functions = []
        lines = content.split('\n')
        
        # Regular function declarations
        func_pattern = r'^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)'
        # Function expressions
        func_expr_pattern = r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\([^)]*\)'
        # Method definitions in classes/objects
        method_pattern = r'^\s*(?:static\s+)?(?:async\s+)?(\w+)\s*\([^)]*\)\s*{'
        
        for i, line in enumerate(lines):
            # Function declarations
            match = re.search(func_pattern, line)
            if match:
                func_name = match.group(1)
                functions.append({
                    'name': func_name,
                    'line': i + 1,
                    'type': 'declaration',
                    'signature': line.strip(),
                    'is_async': 'async' in line,
                    'is_exported': 'export' in line,
                    'docstring': self._get_jsdoc(lines, i)
                })
                continue
            
            # Function expressions
            match = re.search(func_expr_pattern, line)
            if match:
                func_name = match.group(1)
                functions.append({
                    'name': func_name,
                    'line': i + 1,
                    'type': 'expression',
                    'signature': line.strip(),
                    'is_async': 'async' in line,
                    'is_exported': False,
                    'docstring': self._get_jsdoc(lines, i)
                })
                continue
            
            # Method definitions (in classes or objects)
            match = re.search(method_pattern, line)
            if match:
                method_name = match.group(1)
                # Skip constructor and common non-method patterns
                if method_name not in ['if', 'for', 'while', 'switch', 'catch']:
                    functions.append({
                        'name': method_name,
                        'line': i + 1,
                        'type': 'method',
                        'signature': line.strip(),
                        'is_async': 'async' in line,
                        'is_static': 'static' in line,
                        'is_exported': False,
                        'docstring': self._get_jsdoc(lines, i)
                    })
        
        return functions
    
    def _extract_arrow_functions(self, content):
        """Extract arrow function expressions"""
        arrow_functions = []
        lines = content.split('\n')
        
        # Arrow function patterns
        arrow_patterns = [
            r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*',
            r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(\w+)\s*=>\s*',
            r'^\s*(\w+):\s*(?:async\s+)?\([^)]*\)\s*=>\s*'
        ]
        
        for i, line in enumerate(lines):
            for pattern in arrow_patterns:
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1)
                    arrow_functions.append({
                        'name': func_name,
                        'line': i + 1,
                        'signature': line.strip(),
                        'is_async': 'async' in line,
                        'is_single_expression': '=>' in line and '{' not in line,
                        'docstring': self._get_jsdoc(lines, i)
                    })
                    break
        
        return arrow_functions
    
    def _extract_classes(self, content):
        """Extract class definitions"""
        classes = []
        lines = content.split('\n')
        
        class_pattern = r'^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?'
        
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                extends_class = match.group(2) if match.group(2) else None
                implements_interfaces = []
                
                if match.group(3):
                    implements_interfaces = [iface.strip() for iface in match.group(3).split(',')]
                
                classes.append({
                    'name': class_name,
                    'line': i + 1,
                    'extends': extends_class,
                    'implements': implements_interfaces,
                    'is_exported': 'export' in line,
                    'is_abstract': 'abstract' in line,
                    'docstring': self._get_jsdoc(lines, i),
                    'methods': self._extract_class_methods(lines, i)
                })
        
        return classes
    
    def _extract_class_methods(self, lines, class_start_line):
        """Extract methods from a class definition"""
        methods = []
        brace_count = 0
        in_class = False
        
        for i in range(class_start_line, len(lines)):
            line = lines[i]
            
            # Track braces to know when we're inside the class
            brace_count += line.count('{') - line.count('}')
            
            if i == class_start_line and '{' in line:
                in_class = True
            elif in_class and brace_count <= 0:
                break
            
            if in_class and i > class_start_line:
                # Method pattern within class
                method_match = re.search(r'^\s*(?:static\s+)?(?:async\s+)?(\w+)\s*\([^)]*\)', line)
                if method_match:
                    method_name = method_match.group(1)
                    if method_name not in ['if', 'for', 'while', 'switch']:
                        methods.append({
                            'name': method_name,
                            'line': i + 1,
                            'is_static': 'static' in line,
                            'is_async': 'async' in line,
                            'is_constructor': method_name == 'constructor'
                        })
        
        return methods
    
    def _extract_imports(self, content):
        """Extract import statements with details"""
        imports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # ES6 import statements
            if stripped.startswith('import '):
                import_data = {
                    'line': i + 1,
                    'statement': stripped,
                    'type': 'es6'
                }
                
                # import defaultExport from "module"
                default_import = re.search(r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']', stripped)
                if default_import:
                    import_data.update({
                        'default_import': default_import.group(1),
                        'module': default_import.group(2)
                    })
                
                # import { named } from "module"
                named_import = re.search(r'import\s+{([^}]+)}\s+from\s+["\']([^"\']+)["\']', stripped)
                if named_import:
                    named_items = [item.strip() for item in named_import.group(1).split(',')]
                    import_data.update({
                        'named_imports': named_items,
                        'module': named_import.group(2)
                    })
                
                # import * as namespace from "module"
                namespace_import = re.search(r'import\s+\*\s+as\s+(\w+)\s+from\s+["\']([^"\']+)["\']', stripped)
                if namespace_import:
                    import_data.update({
                        'namespace': namespace_import.group(1),
                        'module': namespace_import.group(2)
                    })
                
                imports.append(import_data)
            
            # CommonJS require statements
            elif 'require(' in stripped:
                require_match = re.search(r'(?:const|let|var)\s+(?:{([^}]+)}|(\w+))\s*=\s*require\(["\']([^"\']+)["\']\)', stripped)
                if require_match:
                    imports.append({
                        'line': i + 1,
                        'statement': stripped,
                        'type': 'commonjs',
                        'destructured': require_match.group(1).split(',') if require_match.group(1) else None,
                        'variable': require_match.group(2) if require_match.group(2) else None,
                        'module': require_match.group(3)
                    })
        
        return imports
    
    def _extract_exports(self, content):
        """Extract export statements"""
        exports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # export default
            if stripped.startswith('export default'):
                exports.append({
                    'type': 'default',
                    'line': i + 1,
                    'statement': stripped
                })
            
            # export { named }
            elif stripped.startswith('export {'):
                named_match = re.search(r'export\s+{([^}]+)}', stripped)
                if named_match:
                    named_exports = [item.strip() for item in named_match.group(1).split(',')]
                    exports.append({
                        'type': 'named',
                        'exports': named_exports,
                        'line': i + 1,
                        'statement': stripped
                    })
            
            # export const/let/var/function/class
            elif re.match(r'export\s+(const|let|var|function|class)', stripped):
                exports.append({
                    'type': 'declaration',
                    'line': i + 1,
                    'statement': stripped
                })
        
        return exports
    
    def _extract_variables(self, content):
        """Extract variable declarations"""
        variables = []
        lines = content.split('\n')
        
        var_patterns = [
            r'^\s*(const|let|var)\s+(\w+)\s*=',
            r'^\s*(const|let|var)\s+{([^}]+)}\s*=',  # Destructuring
            r'^\s*(const|let|var)\s+\[([^\]]+)\]\s*='  # Array destructuring
        ]
        
        for i, line in enumerate(lines):
            for pattern in var_patterns:
                match = re.search(pattern, line)
                if match:
                    var_type = match.group(1)
                    if len(match.groups()) > 1:
                        var_name = match.group(2)
                        is_destructured = '{' in var_name or '[' in var_name
                        
                        variables.append({
                            'name': var_name,
                            'type': var_type,
                            'line': i + 1,
                            'is_destructured': is_destructured,
                            'statement': line.strip()
                        })
                    break
        
        return variables
    
    def _get_jsdoc(self, lines, line_index):
        """Extract JSDoc comment before a function/class"""
        if line_index == 0:
            return None
        
        # Look backwards for JSDoc comment
        for i in range(line_index - 1, max(0, line_index - 10), -1):
            stripped = lines[i].strip()
            if stripped.endswith('*/'):
                # Found end of JSDoc, now find the start
                jsdoc_lines = []
                for j in range(i, max(0, i - 20), -1):
                    jsdoc_lines.insert(0, lines[j])
                    if lines[j].strip().startswith('/**'):
                        return '\n'.join(jsdoc_lines)
                break
            elif stripped and not stripped.startswith('*') and not stripped.startswith('//'):
                break
        
        return None
    
    def _analyze_complexity(self, content):
        """Analyze code complexity indicators"""
        lines = content.split('\n')
        complexity = {
            'if_statements': 0,
            'loops': 0,
            'try_blocks': 0,
            'switch_statements': 0,
            'ternary_operators': 0,
            'callbacks': 0,
            'promises': 0,
            'async_await': 0
        }
        
        for line in lines:
            stripped = line.strip()
            
            # Control structures
            if re.search(r'\bif\s*\(', stripped):
                complexity['if_statements'] += 1
            if re.search(r'\b(for|while)\s*\(', stripped):
                complexity['loops'] += 1
            if stripped.startswith('try'):
                complexity['try_blocks'] += 1
            if re.search(r'\bswitch\s*\(', stripped):
                complexity['switch_statements'] += 1
            
            # Ternary operators
            if '?' in stripped and ':' in stripped:
                complexity['ternary_operators'] += 1
            
            # Async patterns
            if 'callback' in stripped.lower() or '.callback(' in stripped:
                complexity['callbacks'] += 1
            if '.then(' in stripped or '.catch(' in stripped:
                complexity['promises'] += 1
            if 'async' in stripped or 'await' in stripped:
                complexity['async_await'] += 1
        
        return complexity