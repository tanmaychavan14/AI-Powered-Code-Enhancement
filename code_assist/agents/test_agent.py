



import os
import json
import subprocess
import re
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console

# Import the GeminiClient from utils
from utils.gemini_client import GeminiClient

# Missing imports at top of test_agent.py
from .runners.pytest_runner import PytestRunner
from .runners.jest_runner import JestRunner  
from .runners.junit_runner import JunitRunner

console = Console()

class TestAgent:
    """Agent responsible for test generation and execution"""
    
    def __init__(self):
        self.console = Console()
        self.gemini_client = self._initialize_llm()
        self.llm_available = self.gemini_client is not None
        self.test_runners = {
            'python': PytestRunner(),
            'javascript': JestRunner(),
            'java': JunitRunner()
        }
        self.output_dir = Path("tests/generated")
        self.results_dir = Path("tests/results")
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_llm(self) -> Optional[GeminiClient]:
        """Initialize LLM client with proper error handling"""
        try:
            gemini_client = GeminiClient()
            
            # Test if the client is properly initialized
            if gemini_client.model is None:
                console.print("[red]❌ LLM initialization failed - API key or connection issue[/red]")
                return None
            
            # Test with a simple prompt to verify it's working
            test_response = gemini_client.generate_content("Hello")
            if test_response is None:
                console.print("[red]❌ LLM test failed - server may be down[/red]")
                return None
            
            console.print("[green]✅ LLM (Gemini) successfully initialized and tested[/green]")
            return gemini_client
            
        except ImportError as e:
            console.print(f"[red]❌ Failed to import GeminiClient: {e}[/red]")
            console.print("[yellow]Make sure utils/gemini_client.py exists and is properly configured[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]❌ LLM initialization error: {e}[/red]")
            return None
    
    def _analyze_code_structure(self, content: str, language: str) -> Dict[str, Any]:
        """Analyze code structure to understand functions better"""
        structure = {
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        if language == 'python':
            structure = self._analyze_python_structure(content)
        elif language == 'javascript':
            structure = self._analyze_javascript_structure(content)
        elif language == 'java':
            structure = self._analyze_java_structure(content)
        
        return structure
    
    def _analyze_python_structure(self, content: str) -> Dict[str, Any]:
        """Analyze Python code structure"""
        structure = {
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function signature and docstring
                    args = [arg.arg for arg in node.args.args]
                    docstring = ast.get_docstring(node) or "No docstring available"
                    
                    # Try to understand what the function does from its body
                    body_analysis = self._analyze_function_body(node)
                    
                    structure['functions'].append({
                        'name': node.name,
                        'args': args,
                        'signature': f"{node.name}({', '.join(args)})",
                        'docstring': docstring,
                        'returns': body_analysis.get('returns'),
                        'operations': body_analysis.get('operations', []),
                        'complexity': body_analysis.get('complexity', 'simple')
                    })
                
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                    
                    structure['classes'].append({
                        'name': node.name,
                        'methods': methods,
                        'docstring': ast.get_docstring(node) or "No docstring available"
                    })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        structure['imports'].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        for alias in node.names:
                            structure['imports'].append(f"{node.module}.{alias.name}")
        
        except SyntaxError as e:
            console.print(f"[yellow]⚠️ Syntax error analyzing Python code: {e}[/yellow]")
        
        return structure
    
    def _analyze_javascript_structure(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript code structure - FIXED VERSION (no false positives)"""
        structure = {
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        try:
            # Find function declarations
            func_patterns = [
                r'function\s+(\w+)\s*\(([^)]*)\)\s*{',
                r'const\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{',
                r'const\s+(\w+)\s*=\s*function\s*\(([^)]*)\)\s*{',
                r'let\s+(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*{',
                r'var\s+(\w+)\s*=\s*function\s*\(([^)]*)\)\s*{',
            ]
            
            # Track seen functions to avoid duplicates
            seen_functions = set()
            
            for pattern in func_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                for match in matches:
                    func_name = match.group(1)
                    
                    # Skip duplicates
                    if func_name in seen_functions:
                        continue
                    
                    # Skip loop variables and keywords
                    if func_name in ['for', 'if', 'while', 'i', 'j', 'k', 'x', 'y', 'z']:
                        continue
                    
                    seen_functions.add(func_name)
                    
                    args_str = match.group(2) if match.group(2) else ""
                    
                    # Parse arguments
                    args = []
                    if args_str.strip():
                        args = [arg.strip().split('=')[0].strip() for arg in args_str.split(',')]
                        args = [arg for arg in args if arg and not arg.startswith('...')]
                    
                    # Extract function body
                    func_start = match.end() - 1  # Include opening brace
                    func_body = self._extract_function_body_js(content, func_start)
                    
                    # Analyze operations (use existing analyzer)
                    operations = self._analyze_js_operations(func_body)
                    
                    structure['functions'].append({
                        'name': func_name,
                        'args': args,
                        'signature': f"{func_name}({', '.join(args)})",
                        'docstring': self._extract_js_comment(content, match.start()),
                        'operations': operations,
                        'complexity': self._determine_js_complexity(func_body)
                    })
            
            # Find class declarations
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?\s*{'
            class_matches = re.finditer(class_pattern, content, re.MULTILINE)
            for match in class_matches:
                class_name = match.group(1)
                class_start = match.end() - 1
                class_body = self._extract_function_body_js(content, class_start)
                methods = self._extract_js_methods(class_body)
                
                structure['classes'].append({
                    'name': class_name,
                    'methods': methods,
                    'docstring': self._extract_js_comment(content, match.start())
                })
            
            # Find imports/requires
            import_patterns = [
                r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]',
                r'import\s+[\'"]([^\'"]+)[\'"]',
                r'const\s+.*?=\s*require\([\'"]([^\'"]+)[\'"]\)',
                r'require\([\'"]([^\'"]+)[\'"]\)'
            ]
            
            for pattern in import_patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    structure['imports'].append(match.group(1))
        
        except Exception as e:
            console.print(f"[yellow]⚠️ Error analyzing JavaScript code: {e}[/yellow]")
        
        return structure

    
    def _analyze_java_structure(self, content: str) -> Dict[str, Any]:
        """Analyze Java code structure using regex patterns"""
        structure = {
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        try:
            # Find method declarations
            method_pattern = r'(?:public|private|protected|static|\s)*\s*(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+[\w\s,]+)?\s*{'
            method_matches = re.finditer(method_pattern, content, re.MULTILINE)
            
            for match in method_matches:
                return_type = match.group(1)
                method_name = match.group(2)
                args_str = match.group(3)
                
                # Skip constructors and common non-test methods
                if method_name in ['main', 'toString', 'equals', 'hashCode']:
                    continue
                
                # Parse arguments
                args = []
                if args_str.strip():
                    arg_parts = args_str.split(',')
                    for arg in arg_parts:
                        arg = arg.strip()
                        if arg:
                            # Extract parameter name (last word)
                            parts = arg.split()
                            if len(parts) >= 2:
                                args.append(parts[-1])
                
                # Analyze method body
                method_start = match.end()
                method_body = self._extract_method_body_java(content, method_start)
                operations = self._analyze_java_operations(method_body)
                
                structure['functions'].append({
                    'name': method_name,
                    'args': args,
                    'return_type': return_type,
                    'signature': f"{method_name}({', '.join(args)})",
                    'docstring': self._extract_java_javadoc(content, match.start()),
                    'operations': operations,
                    'complexity': self._determine_java_complexity(method_body)
                })
            
            # Find class declarations
            class_pattern = r'(?:public|private|protected)?\s*class\s+(\w+)(?:\s+extends\s+\w+)?(?:\s+implements\s+[\w\s,]+)?\s*{'
            class_matches = re.finditer(class_pattern, content, re.MULTILINE)
            
            for match in class_matches:
                class_name = match.group(1)
                structure['classes'].append({
                    'name': class_name,
                    'methods': [f['name'] for f in structure['functions']],
                    'docstring': self._extract_java_javadoc(content, match.start())
                })
            
            # Find imports
            import_pattern = r'import\s+(?:static\s+)?([^;]+);'
            import_matches = re.finditer(import_pattern, content)
            
            for match in import_matches:
                structure['imports'].append(match.group(1).strip())
        
        except Exception as e:
            console.print(f"[yellow]⚠️ Error analyzing Java code: {e}[/yellow]")
        
        return structure
    
    def _extract_function_body_js(self, content: str, start_pos: int) -> str:
        """Extract JavaScript function body"""
        brace_count = 0
        i = start_pos
        started = False
        
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
                started = True
            elif content[i] == '}':
                brace_count -= 1
                if started and brace_count == 0:
                    return content[start_pos:i+1]
            i += 1
        
        return content[start_pos:min(start_pos + 500, len(content))]
    
    def _extract_class_body_js(self, content: str, start_pos: int) -> str:
        """Extract JavaScript class body"""
        return self._extract_function_body_js(content, start_pos)
    
    def _extract_method_body_java(self, content: str, start_pos: int) -> str:
        """Extract Java method body"""
        return self._extract_function_body_js(content, start_pos)  # Same logic
    
    def _extract_js_comment(self, content: str, pos: int) -> str:
        """Extract JavaScript comment above function"""
        lines = content[:pos].split('\n')
        comment_lines = []
        
        for line in reversed(lines[-5:]):  # Check last 5 lines
            line = line.strip()
            if line.startswith('//') or line.startswith('*') or line.startswith('/**'):
                comment_lines.insert(0, line)
            elif line == '':
                continue
            else:
                break
        
        return ' '.join(comment_lines) or "No comment available"
    
    def _extract_java_javadoc(self, content: str, pos: int) -> str:
        """Extract Java Javadoc comment above method"""
        lines = content[:pos].split('\n')
        comment_lines = []
        
        for line in reversed(lines[-10:]):  # Check last 10 lines
            line = line.strip()
            if line.startswith('/**') or line.startswith('*') or line.startswith('*/'):
                comment_lines.insert(0, line)
            elif line == '':
                continue
            else:
                break
        
        return ' '.join(comment_lines) or "No Javadoc available"
    
    def _extract_js_methods(self, class_body: str) -> List[str]:
        """Extract method names from JavaScript class body"""
        method_pattern = r'(\w+)\s*\([^)]*\)\s*{'
        matches = re.finditer(method_pattern, class_body)
        return [match.group(1) for match in matches]
    
    def _analyze_js_operations(self, func_body: str) -> List[str]:
        """
        Analyze JavaScript function for REAL operations.
        This implementation removes comments and string literals first to avoid false positives,
        then heuristically detects common operations (string/array ops, arithmetic, control flow, etc.).
        """
        operations: List[str] = []
        
        # Remove single-line (//...) and multi-line (/* ... */) comments
        clean_body = re.sub(r'//.*?$|/\*.*?\*/', '', func_body, flags=re.DOTALL | re.MULTILINE)
        # Remove string literals (single, double and template) to avoid false matches
        clean_body = re.sub(r'(\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"|`(?:\\.|[^\\`])*`)', '', clean_body, flags=re.DOTALL)
        
        # String operations
        if '.split(' in clean_body:
            operations.append('string_split')
        
        if '.join(' in clean_body:
            operations.append('string_join')
        
        if '.toUpperCase(' in clean_body or '.toLowerCase(' in clean_body:
            operations.append('case_conversion')
        
        if '.reverse(' in clean_body:
            operations.append('array_reversal')
        
        if '.trim(' in clean_body:
            operations.append('string_trim')
        
        # Array operations
        if '.push(' in clean_body or '.pop(' in clean_body:
            operations.append('array_modification')
        
        if '.map(' in clean_body or '.filter(' in clean_body or '.reduce(' in clean_body:
            operations.append('array_processing')
        
        # Arithmetic (exclude common loop increments like i++ or i += 1)
        # Only count if it's a real expression (heuristic using return/expression patterns)
        if re.search(r'\breturn\b.*[\+\-\*\/]', clean_body) or re.search(r'=\s*[^=].*[\+\-\*\/]', clean_body):
            if '+' in clean_body:
                operations.append('arithmetic_add')
            if '-' in clean_body:
                operations.append('arithmetic_subtract')
            if '*' in clean_body:
                operations.append('arithmetic_multiply')
            if '/' in clean_body and '//' not in clean_body:
                operations.append('arithmetic_divide')
        
        # Modulo operation
        if re.search(r'\w+\s*%\s*\d+', clean_body):
            operations.append('modulo')
        
        # Comparisons
        if '===' in clean_body or '!==' in clean_body or '==' in clean_body or '!=' in clean_body:
            operations.append('comparison')
        
        # Conditionals
        if re.search(r'\bif\b|\belse\b|\?', clean_body):
            operations.append('conditional')
        
        # Loops
        if re.search(r'\bfor\b|\bwhile\b|\bforEach\b', clean_body):
            operations.append('iteration')
        
        # Return
        if re.search(r'\breturn\b', clean_body):
            operations.append('return_value')
        
        # Logging
        if 'console.' in clean_body:
            operations.append('console_output')
        
        # HTTP
        if 'fetch' in clean_body or 'axios' in clean_body:
            operations.append('http_request')
        
        # JSON
        if 'JSON.parse' in clean_body or 'JSON.stringify' in clean_body:
            operations.append('json_processing')
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(operations))
    
    def _analyze_java_operations(self, method_body: str) -> List[str]:
        """Analyze Java method body for operations"""
        operations = []
        
        if '+' in method_body: operations.append('addition')
        if '-' in method_body: operations.append('subtraction')
        if '*' in method_body: operations.append('multiplication')
        if '/' in method_body: operations.append('division')
        if 'return' in method_body: operations.append('return_value')
        if 'System.out' in method_body: operations.append('output')
        if 'new ' in method_body: operations.append('object_creation')
        if '.equals(' in method_body: operations.append('comparison')
        if 'List<' in method_body or 'ArrayList' in method_body: operations.append('list_processing')
        if 'Map<' in method_body or 'HashMap' in method_body: operations.append('map_processing')
        
        return operations
    
    def _determine_js_complexity(self, func_body: str) -> str:
        """Determine JavaScript function complexity"""
        if 'if' in func_body or 'switch' in func_body: return 'conditional'
        if 'for' in func_body or 'while' in func_body or '.forEach(' in func_body: return 'iterative'
        if 'try' in func_body or 'catch' in func_body: return 'error_handling'
        if 'async' in func_body or 'await' in func_body or 'Promise' in func_body: return 'asynchronous'
        return 'simple'
    
    def _determine_java_complexity(self, method_body: str) -> str:
        """Determine Java method complexity"""
        if 'if' in method_body or 'switch' in method_body: return 'conditional'
        if 'for' in method_body or 'while' in method_body: return 'iterative'
        if 'try' in method_body or 'catch' in method_body: return 'error_handling'
        if 'synchronized' in method_body or 'Thread' in method_body: return 'concurrent'
        return 'simple'
    
    def _analyze_function_body(self, func_node) -> Dict[str, Any]:
        """Analyze Python function body to understand what it does"""
        analysis = {
            'returns': [],
            'operations': [],
            'complexity': 'simple'
        }
        
        try:
            # Count different types of operations
            for node in ast.walk(func_node):
                if isinstance(node, ast.Return):
                    if isinstance(node.value, ast.Constant):
                        analysis['returns'].append(f"constant: {node.value.value}")
                    elif isinstance(node.value, ast.Name):
                        analysis['returns'].append(f"variable: {node.value.id}")
                    else:
                        analysis['returns'].append("expression")
                
                elif isinstance(node, ast.BinOp):
                    if isinstance(node.op, ast.Add):
                        analysis['operations'].append('addition')
                    elif isinstance(node.op, ast.Sub):
                        analysis['operations'].append('subtraction')
                    elif isinstance(node.op, ast.Mult):
                        analysis['operations'].append('multiplication')
                    elif isinstance(node.op, ast.Div):
                        analysis['operations'].append('division')
                
                elif isinstance(node, ast.If):
                    analysis['complexity'] = 'conditional'
                elif isinstance(node, ast.For) or isinstance(node, ast.While):
                    analysis['complexity'] = 'iterative'
                elif isinstance(node, ast.Try):
                    analysis['complexity'] = 'error_handling'
        
        except Exception as e:
            console.print(f"[dim]Could not analyze function body: {e}[/dim]")
        
        return analysis
    
    def generate_tests(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main method to generate and execute tests"""
        try:
            console.print("[bold cyan]🧪 Starting test generation...[/bold cyan]")
            
            # Check LLM availability first
            if not self.llm_available:
                console.print("[red]❌ LLM is not available. Cannot generate meaningful tests.[/red]")
                console.print("[yellow]Please check your GEMINI_API_KEY in .env file or network connection[/yellow]")
                return {
                    'error': 'LLM unavailable - cannot generate quality tests',
                    'files_processed': 0,
                    'tests_generated': 0,
                    'llm_status': 'unavailable'
                }
            
            results = {
                'files_processed': 0,
                'tests_generated': 0,
                'functions_tested': 0, 
                'tests_passed': 0,
                'tests_failed': 0,
                'test_files': [],
                'execution_results': {},
                'errors': [],
                'llm_status': 'available',
                'failed_tests': [],
            }
            
            for file_path, file_data in parsed_data.items():
                if not file_data.get('parsed', False):
                    continue
                
                console.print(f"[dim]Processing: {Path(file_path).name}[/dim]")
                
                # Enhanced code analysis
                enhanced_structure = self._analyze_code_structure(
                    file_data.get('content', ''), 
                    file_data.get('language', '')
                )
                
                # Merge with existing data
                file_data['enhanced_functions'] = enhanced_structure['functions']
                file_data['enhanced_classes'] = enhanced_structure['classes']
                
                console.print("=== ENHANCED DEBUG INFO ===")
                console.print(f"Enhanced functions: {[f['name'] + f['signature'] for f in enhanced_structure['functions']]}")
                console.print(f"Function operations: {[f.get('operations', []) for f in enhanced_structure['functions']]}")
                console.print("===========================")
                
                try:
                    # Generate test file
                    test_result = self._generate_test_file(file_data)
                    
                    if test_result['success']:
                        results['files_processed'] += 1
                        results['tests_generated'] += test_result['test_count']
                        results['test_files'].append(test_result['test_file'])
                        
                        # Execute tests
                        exec_result = self._execute_tests(test_result['test_file'], file_data['language'])
                        results['execution_results'][file_path] = exec_result
                        
                        results['tests_passed'] += exec_result.get('passed', 0)
                        results['tests_failed'] += exec_result.get('failed', 0)
                        
                    else:
                        results['errors'].append(f"{file_path}: {test_result['error']}")
                        
                except Exception as e:
                    results['errors'].append(f"{file_path}: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            return {'error': f"Test generation failed: {str(e)}"}
    
    def _generate_test_file(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test file for a single code file"""
        try:
            language = file_data['language']
            file_path = file_data['file_path']
            
            # Extract testable components - use enhanced data if available
            test_targets = {
                'classes': file_data.get('enhanced_classes', file_data.get('classes', [])),
                'functions': file_data.get('enhanced_functions', file_data.get('functions', [])),
                'imports': file_data.get('imports', [])
            }
            
            if not test_targets['classes'] and not test_targets['functions']:
                return {
                    'success': False,
                    'error': 'No testable components found'
                }
            
            # Check LLM availability before attempting generation
            if not self.llm_available:
                console.print("[red]❌ LLM unavailable - cannot generate quality tests[/red]")
                return {
                    'success': False,
                    'error': 'LLM service unavailable - refusing to generate low-quality fallback tests'
                }
            
            # Try LLM generation with enhanced validation
            test_code = self._generate_test_code_with_enhanced_llm(file_data, test_targets)
            
            if not test_code:
                console.print("[red]❌ LLM failed to generate valid tests[/red]")
                return {
                    'success': False,
                    'error': 'LLM failed to generate meaningful test cases'
                }
            
            # Save test file
            test_file_path = self._save_test_file(test_code, file_path, language)
            
            # ✅ FIX: Count actual test cases in the generated code
            actual_test_count = self._count_actual_tests(test_code, language)
            functions_count = len(test_targets['functions'])
            classes_count = len(test_targets['classes'])
            
            return {
                'success': True,
                'test_file': str(test_file_path),
                'test_count': actual_test_count,  # ✅ Actual test cases generated
                'functions_tested': functions_count,  # ✅ Number of functions being tested
                'classes_tested': classes_count  # ✅ Number of classes being tested
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _count_actual_tests(self, test_code: str, language: str) -> int:
        """Count the actual number of test cases in generated code"""
        count = 0
        
        try:
            if language == 'python':
                # Count test functions (def test_...)
                count = len(re.findall(r'^\s*def\s+test_\w+', test_code, re.MULTILINE))
                
            elif language == 'javascript':
                # Count test() or it() calls
                count = len(re.findall(r'\b(?:test|it)\s*\(', test_code))
                
            elif language == 'java':
                # Count @Test annotations
                count = len(re.findall(r'@Test', test_code))
            
            console.print(f"[dim]Counted {count} actual test cases in generated code[/dim]")
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not count tests accurately: {e}[/yellow]")
            # Fallback to a rough estimate
            count = test_code.count('assert') + test_code.count('expect(') + test_code.count('assertEquals')
        
        return max(count, 1)  # Return at least 1 if code was generated
    
    def _generate_test_code_with_enhanced_llm(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> Optional[str]:
        """Generate test code using LLM with enhanced analysis and validation"""
        try:
            if not self.llm_available:
                console.print("[yellow]LLM not available for test generation[/yellow]")
                return None
            
            language = file_data['language']
            content = file_data['content']
            
            console.print(f"[cyan]🤖 Calling LLM to generate tests for {language}...[/cyan]")
            
            # Create enhanced prompt
            prompt = self._create_enhanced_test_generation_prompt(language, content, test_targets)
            
            console.print(f"[dim]Sending {len(prompt)} chars to LLM[/dim]")
            
            # Generate test code with error handling
            try:
                response = self.gemini_client.generate_content(prompt)
            except Exception as llm_error:
                console.print(f"[red]❌ LLM service error: {llm_error}[/red]")
                console.print("[yellow]This could be due to: API limits, network issues, or server downtime[/yellow]")
                return None
            
            console.print(f"[cyan]LLM Response received: {response is not None}[/cyan]")
            
            if response and hasattr(response, 'text') and response.text:
                console.print(f"[cyan]Response text length: {len(response.text)}[/cyan]")
                console.print(f"[cyan]Response preview: {response.text[:200]}...[/cyan]")
                console.print(f"[green]✅ LLM responded with {len(response.text)} chars[/green]")
                
                # Clean and validate generated code
                test_code = self._clean_generated_code(response.text, language)
                
                # Better validation - check for actual test patterns
                if self._validate_generated_tests(test_code, language):
                    console.print("[green]✅ LLM generated valid tests[/green]")
                    return test_code
                else:
                    console.print("[yellow]⚠️ LLM generated invalid/placeholder tests[/yellow]")
                    # Try one more time with stricter prompt
                    return self._retry_with_stricter_prompt(file_data, test_targets)
            else:
                console.print("[red]❌ LLM returned empty or invalid response[/red]")
                return None
            
        except Exception as e:
            console.print(f"[red]❌ LLM generation failed: {e}[/red]")
            return None

   
    def _validate_generated_tests(self, test_code: str, language: str) -> bool:
        """Validate that generated tests are meaningful, not placeholders"""
        if not test_code or len(test_code.strip()) < 50:
            return False
        
        # Common placeholder patterns across all languages
        bad_patterns = [
            'TODO',
            'NotImplemented',
            'Not implemented',
            'Add your test here',
            'TODO: implement'
        ]
        
        # Language-specific validation
        if language == 'python':
            bad_patterns.extend([
                'assert True',
                'pass  # placeholder',
                'raise NotImplementedError',
                'assert False, "Not implemented"'
            ])
            
            good_patterns = [
                'assert ',
                'assertEqual',
                'assertRaises',
                'pytest.raises'
            ]
            
        elif language == 'javascript':
            bad_patterns.extend([
                'expect(true).toBe(true)',
                'expect(true).toEqual(true)',
                'it.todo(',
                'test.todo(',
                'pending('
            ])
            
            good_patterns = [
                'expect(',
                '.toBe(',
                '.toEqual(',
                '.toThrow(',
                '.toHaveBeenCalled(',
                'describe(',
                'test(',
                'it('
            ]
            
        elif language == 'java':
            bad_patterns.extend([
                'assertTrue(true)',
                'assertFalse(false)',
                'fail("Not implemented")',
                '@Disabled'
            ])
            
            good_patterns = [
                'assertEquals(',
                'assertNotEquals(',
                'assertThrows(',
                'assertTrue(',
                'assertFalse(',
                '@Test'
            ]
        
        else:
            # Generic validation for other languages
            good_patterns = ['assert', 'expect', 'test', 'should']
        
        # Check for placeholder patterns
        for pattern in bad_patterns:
            if pattern in test_code:
                console.print(f"[yellow]Found placeholder pattern: {pattern}[/yellow]")
                return False
        
        # Check for good patterns
        has_good_pattern = any(pattern in test_code for pattern in good_patterns)
        if not has_good_pattern:
            console.print("[yellow]No valid test assertions found[/yellow]")
            return False
        
        # Check if it has actual function calls or meaningful logic
        lines_with_logic = 0
        for line in test_code.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//') and not line.startswith('/*'):
                if any(pattern in line for pattern in ['(', '=', 'assert', 'expect', 'should', 'assertEquals']):
                    lines_with_logic += 1
        
        if lines_with_logic < 3:  # Should have at least 3 lines of actual test logic
            console.print(f"[yellow]Not enough test logic: {lines_with_logic} lines[/yellow]")
            return False
        
        return True
    
    def _create_enhanced_test_generation_prompt(self, language: str, content: str, test_targets: Dict[str, Any]) -> str:
        """Create enhanced prompt with better context for each language"""
        
        if language == 'python':
            function_details = []
            for func in test_targets['functions']:
                detail = f"• {func.get('signature', func['name'])}"
                if func.get('operations'):
                    detail += f" - Operations: {', '.join(func['operations'])}"
                if func.get('docstring') and func['docstring'] != "No docstring available":
                    detail += f" - Purpose: {func['docstring'][:100]}..."
                function_details.append(detail)
            
            return f"""You are an expert Python test engineer. Generate comprehensive pytest test cases.

STRICT RULES:
1. NEVER write placeholder tests (assert True, TODO, etc.)
2. ANALYZE the actual code to understand function behavior
3. Generate REAL test cases with actual expected results
4. Each function needs 3-5 meaningful test cases
5. Use proper pytest patterns and assertions

PYTHON CODE TO ANALYZE:
```python
{content}
```

FUNCTIONS TO TEST (analyze each one carefully):
{chr(10).join(function_details)}

For EACH function above, create tests that:
- Test normal operation with typical inputs
- Test edge cases (empty inputs, boundary values)
- Test error conditions (invalid inputs, exceptions)
- Verify return values and types
- Test different argument combinations if applicable

IMPORTANT: Look at the actual function implementations to understand:
- What parameters they expect
- What they return
- What operations they perform
- What errors they might raise

enerate complete pytest code with:

2. Proper test fixtures if needed
3. Realistic test data
4. Meaningful assertions



Only return the Python test code, no explanations.
Generate complete pytest code with proper imports and realistic test data.
Only return the Python test code, no explanations.
"""
        elif language == 'javascript':
         function_details = []
         for func in test_targets['functions']:
           detail = f"• {func.get('signature', func['name'])}"
           if func.get('operations'):
            detail += f" - Operations: {', '.join(func['operations'])}"
           if func.get('docstring') and func['docstring'] != "No comment available":
            detail += f" - Purpose: {func['docstring'][:100]}..."
           function_details.append(detail)

         return f"""You are an expert JavaScript test engineer.

CRITICAL REQUIREMENTS:
1. The test file MUST be completely self-contained
2. Include ALL function implementations at the TOP of the test file
3. DO NOT use require() or import statements
4. Structure the file as:
   - First: All function/class implementations
   - Then: Jest test cases using those implementations

JAVASCRIPT CODE TO INCLUDE (copy these implementations exactly):
```javascript
{content}
```

FUNCTIONS TO TEST:
{chr(10).join(function_details)}

Generate a SINGLE JavaScript file with this structure:
```javascript
// ============ IMPLEMENTATIONS ============
// Copy ALL functions and classes from above here exactly as they are
// (paste the entire content)

// ============ TEST CASES ============
describe('Test Suite', () => {{
    test('test case 1', () => {{
        // Use the functions defined above
        expect(functionName(args)).toBe(expectedResult);
    }});
    
    // More test cases...
}});
```

IMPORTANT:
- The test file must run standalone with Node.js
- NO external dependencies
- Copy the actual implementation code at the top
- Then write comprehensive Jest tests below
- Generate 3-5 meaningful tests per function

Only return the complete JavaScript code, no explanations.
"""        


            
        
        
        elif language == 'java':
            function_details = []
            for func in test_targets['functions']:
                detail = f"• {func.get('signature', func['name'])}"
                if func.get('return_type'):
                    detail += f" (returns: {func['return_type']})"
                if func.get('operations'):
                    detail += f" - Operations: {', '.join(func['operations'])}"
                if func.get('docstring') and func['docstring'] != "No Javadoc available":
                    detail += f" - Purpose: {func['docstring'][:100]}..."
                function_details.append(detail)
            
            return f"""You are an expert Java test engineer. Generate comprehensive JUnit 5 test cases.

STRICT RULES:
1. NEVER write placeholder tests (assertTrue(true), TODO, etc.)
2. ANALYZE the actual code to understand method behavior
3. Generate REAL test cases with actual expected results
4. Each method needs 3-5 meaningful test cases
5. Use proper JUnit 5 annotations and assertions

JAVA CODE TO ANALYZE:
```java
{content}
```

METHODS TO TEST (analyze each one carefully):
{chr(10).join(function_details)}

For EACH method above, create tests that:
- Test normal operation with typical inputs
- Test edge cases (null inputs, boundary values, empty collections)
- Test error conditions (invalid inputs, expected exceptions)
- Verify return values and types
- Test different parameter combinations if applicable

IMPORTANT: Look at the actual method implementations to understand:
- What parameters they expect
- What they return
- What operations they perform
- What exceptions they might throw

Generate complete JUnit 5 test code with proper imports and realistic test data.
Include proper test class structure with @Test annotations.
Only return the Java test code, no explanations.
"""
        
        return f"Generate comprehensive {language} test cases for the provided code."
    
    def _clean_generated_code(self, generated_text: str, language: str) -> str:
        """Clean and extract code from LLM response"""
        # Remove markdown code blocks if present
        
        # Language-specific patterns
        patterns = [
            rf'```{language}(.*?)```',
            r'```python(.*?)```' if language == 'python' else None,
            r'```javascript(.*?)```' if language == 'javascript' else None,
            r'```js(.*?)```' if language == 'javascript' else None,
            r'```java(.*?)```' if language == 'java' else None,
            r'```(.*?)```'  # General fallback
        ]
        
        # Filter out None patterns
        patterns = [p for p in patterns if p is not None]
        
        for pattern in patterns:
            matches = re.findall(pattern, generated_text, re.DOTALL | re.IGNORECASE)
            if matches:
                # Take the longest match (likely the main code block)
                longest_match = max(matches, key=len)
                return longest_match.strip()
        
        # Return as-is if no code blocks found
        return generated_text.strip()
    
    def _save_test_file(self, test_code: str, original_file_path: str, language: str) -> Path:
        """Save generated test code to appropriate file"""
        original_name = Path(original_file_path).stem
        
        # Determine file extension and directory
        if language == 'python':
            test_file = self.output_dir / 'python' / f"test_{original_name}.py"
        elif language == 'javascript':
            test_file = self.output_dir / 'javascript' / f"{original_name}.test.js"
            console.print(f"[debug]JavaScript test file path: {test_file}[/debug]")
        elif language == 'java':
            test_file = self.output_dir / 'java' / f"{original_name}Test.java"
        else:
            test_file = self.output_dir / f"test_{original_name}.txt"
        
        # Create directory if it doesn't exist
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        console.print(f"[green]📝 Generated test file: {test_file}[/green]")
        return test_file
    
    def _execute_tests(self, test_file_path: str, language: str) -> Dict[str, Any]:
        """Execute tests using appropriate runner"""
        try:
            runner = self.test_runners.get(language)
            if not runner:
                return {
                    'success': False,
                    'error': f'No test runner for language: {language}'
                }
            
            console.print(f"[dim]Executing tests: {Path(test_file_path).name}[/dim]")
            return runner.run_tests(test_file_path)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Test execution failed: {str(e)}'
            }
    
    def check_llm_status(self) -> Dict[str, Any]:
        """Check current LLM availability status"""
        if not self.llm_available:
            return {
                'available': False,
                'status': 'LLM client not initialized',
                'can_generate_tests': False
            }
        
        # Test with a simple prompt
        try:
            test_response = self.gemini_client.generate_content("ping")
            if test_response and hasattr(test_response, 'text'):
                return {
                    'available': True,
                    'status': 'LLM service operational',
                    'can_generate_tests': True
                }
            else:
                return {
                    'available': False,
                    'status': 'LLM service not responding',
                    'can_generate_tests': False
                }
        except Exception as e:
            return {
                'available': False,
                'status': f'LLM service error: {str(e)}',
                'can_generate_tests': False
            }