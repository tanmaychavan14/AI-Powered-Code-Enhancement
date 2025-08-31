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
                console.print(f"[yellow]⚠️ Syntax error analyzing code: {e}[/yellow]")
        
        return structure
    
    def _analyze_function_body(self, func_node) -> Dict[str, Any]:
        """Analyze function body to understand what it does"""
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
                'tests_passed': 0,
                'tests_failed': 0,
                'test_files': [],
                'execution_results': {},
                'errors': [],
                'llm_status': 'available'
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
            
            return {
                'success': True,
                'test_file': str(test_file_path),
                'test_count': len(test_targets['classes']) + len(test_targets['functions'])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_test_code_with_enhanced_llm(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> Optional[str]:
        """Generate test code using LLM with enhanced analysis and validation"""
        try:
            if not self.llm_available:
                console.print("[yellow]LLM not available for test generation[/yellow]")
                return None
            
            language = file_data['language']
            content = file_data['content']
            
            console.print(f"[cyan]🤖 Calling LLM to generate tests...[/cyan]")
            
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

    def _retry_with_stricter_prompt(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> Optional[str]:
        """Retry with even stricter, more explicit prompt"""
        try:
            if not self.llm_available:
                return None
                
            content = file_data['content']
            language = file_data['language']
            
            # Show actual function signatures to LLM
            function_details = []
            for func in test_targets['functions']:
                details = f"Function: {func.get('signature', func['name'])}"
                if func.get('operations'):
                    details += f" (performs: {', '.join(func['operations'])})"
                if func.get('args'):
                    details += f" (takes args: {', '.join(func['args'])})"
                function_details.append(details)
            
            strict_prompt = f"""
CRITICAL: I need you to generate REAL, WORKING test cases. No placeholders allowed.

ANALYZE THIS EXACT CODE:
```python
{content}
```

FUNCTIONS TO TEST:
{chr(10).join(function_details)}

REQUIREMENTS - ABSOLUTE MUSTS:
1. Look at each function's actual implementation
2. Understand what parameters it expects
3. Generate tests that call functions with correct arguments
4. Use real assertions with expected values
5. NO "assert True", NO "TODO", NO placeholders

EXAMPLE OF WHAT I WANT:
```python
def test_add_positive_numbers():
    result = add(5, 3)
    assert result == 8

def test_add_negative_numbers():
    result = add(-2, -3) 
    assert result == -5

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

Generate EXACTLY this style - real function calls, real expected values:
"""
            
            console.print("[dim]🔄 Retrying with stricter prompt...[/dim]")
            
            try:
                response = self.gemini_client.generate_content(strict_prompt)
            except Exception as llm_error:
                console.print(f"[red]❌ LLM retry failed: {llm_error}[/red]")
                return None
            
            if response and hasattr(response, 'text') and response.text:
                test_code = self._clean_generated_code(response.text, language)
                if self._validate_generated_tests(test_code, language):
                    console.print("[green]✅ Strict retry successful[/green]")
                    return test_code
            
            console.print("[red]❌ Strict retry also failed to generate valid tests[/red]")
            return None
            
        except Exception as e:
            console.print(f"[red]Strict retry error: {e}[/red]")
            return None

    def _validate_generated_tests(self, test_code: str, language: str) -> bool:
        """Validate that generated tests are meaningful, not placeholders"""
        if not test_code or len(test_code.strip()) < 50:
            return False
        
        # Check for placeholder patterns
        bad_patterns = [
            'assert True',
            'TODO',
            'pass  # placeholder',
            'NotImplemented',
            'raise NotImplementedError',
            '# Add your test here',
            '# TODO: implement',
            'assert False, "Not implemented"'
        ]
        
        for pattern in bad_patterns:
            if pattern in test_code:
                console.print(f"[yellow]Found placeholder pattern: {pattern}[/yellow]")
                return False
        
        if language == 'python':
            # Check for actual test patterns
            good_patterns = [
                'assert ',
                'assertEqual',
                'assertRaises',
                'pytest.raises'
            ]
            
            has_good_pattern = any(pattern in test_code for pattern in good_patterns)
            if not has_good_pattern:
                console.print("[yellow]No valid test assertions found[/yellow]")
                return False
        
        # Check if it has actual function calls or meaningful logic
        lines_with_logic = 0
        for line in test_code.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('def ') and not line.startswith('"""'):
                if any(pattern in line for pattern in ['(', '=', 'assert', 'expect', 'should']):
                    lines_with_logic += 1
        
        if lines_with_logic < 5:  # Should have at least 5 lines of actual test logic
            console.print(f"[yellow]Not enough test logic: {lines_with_logic} lines[/yellow]")
            return False
        
        return True
    
    def _create_enhanced_test_generation_prompt(self, language: str, content: str, test_targets: Dict[str, Any]) -> str:
        """Create enhanced prompt with better context"""
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

Generate complete pytest code with proper imports and realistic test data.
Only return the Python test code, no explanations.
"""
        
        return f"Generate comprehensive {language} test cases for the provided code."
    
    def _clean_generated_code(self, generated_text: str, language: str) -> str:
        """Clean and extract code from LLM response"""
        # Remove markdown code blocks if present
        
        # Extract code between ```language and ```
        pattern = rf'```{language}(.*?)```'
        matches = re.findall(pattern, generated_text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            return matches[0].strip()
        
        # Try python specifically
        if language == 'python':
            pattern = r'```python(.*?)```'
            matches = re.findall(pattern, generated_text, re.DOTALL | re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Try general code blocks
        pattern = r'```(.*?)```'
        matches = re.findall(pattern, generated_text, re.DOTALL)
        
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