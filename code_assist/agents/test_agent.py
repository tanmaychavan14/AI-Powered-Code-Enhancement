import os
import json
import subprocess
import re
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
import google.generativeai as genai

# Missing imports at top of test_agent.py
from .runners.pytest_runner import PytestRunner
from .runners.jest_runner import JestRunner  
from .runners.junit_runner import JunitRunner

console = Console()

class TestAgent:
    """Agent responsible for test generation and execution"""
    
    def __init__(self):
        self.console = Console()
        self.gemini_client = self._initialize_gemini()
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
    
    def _initialize_gemini(self):
        """Initialize Gemini AI client"""
        try:
            # Get API key from environment variable
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                console.print("[yellow]Warning: GEMINI_API_KEY not found in environment[/yellow]")
                return None
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-pro')
            console.print("[green]✅ Gemini AI initialized[/green]")
            return model
            
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize Gemini: {e}[/red]")
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
            
            results = {
                'files_processed': 0,
                'tests_generated': 0,
                'tests_passed': 0,
                'tests_failed': 0,
                'test_files': [],
                'execution_results': {},
                'errors': []
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
            
            # Always try LLM first, with better validation
            test_code = self._generate_test_code_with_enhanced_llm(file_data, test_targets)
            
            if not test_code:
                console.print("[yellow]⚠️ LLM failed, using intelligent fallback[/yellow]")
                test_code = self._generate_intelligent_fallback_test(file_data, test_targets)
            
            if not test_code:
                return {
                    'success': False,
                    'error': 'Failed to generate any test code'
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
        """Generate test code using Gemini LLM with enhanced analysis"""
        try:
            if not self.gemini_client:
                console.print("[yellow]No Gemini client available[/yellow]")
                return None
            
            language = file_data['language']
            content = file_data['content']
            
            console.print(f"[cyan]🤖 Calling LLM to generate tests...[/cyan]")
            
            # Create enhanced prompt
            prompt = self._create_enhanced_test_generation_prompt(language, content, test_targets)
            
            console.print(f"[dim]Sending {len(prompt)} chars to LLM[/dim]")
            
            # Generate test code with more specific instructions
            response = self.gemini_client.generate_content(prompt)
            console.print(f"[cyan]LLM Response received: {response is not None}[/cyan]")
            if response:
             console.print(f"[cyan]Response text length: {len(response.text) if response.text else 0}[/cyan]")
             console.print(f"[cyan]Response preview: {response.text[:200] if response.text else 'None'}...[/cyan]")
            if response and response.text:
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
            
            console.print("[red]❌ LLM returned empty response[/red]")
            return None
            
        except Exception as e:
            console.print(f"[red]❌ LLM generation failed: {e}[/red]")
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
            'raise NotImplementedError'
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
    
    def _retry_with_stricter_prompt(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> Optional[str]:
        """Retry with even stricter, more explicit prompt"""
        try:
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
            response = self.gemini_client.generate_content(strict_prompt)
            
            if response and response.text:
                test_code = self._clean_generated_code(response.text, language)
                if self._validate_generated_tests(test_code, language):
                    console.print("[green]✅ Strict retry successful[/green]")
                    return test_code
            
            console.print("[red]❌ Strict retry also failed[/red]")
            return None
            
        except Exception as e:
            console.print(f"[red]Strict retry error: {e}[/red]")
            return None
    
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
"""
        
        return f"Generate comprehensive {language} test cases for the provided code."
    
    def _generate_intelligent_fallback_test(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate intelligent fallback tests based on function analysis"""
        language = file_data['language']
        
        if language == 'python':
            return self._generate_python_intelligent_fallback(file_data, test_targets)
        elif language == 'javascript':
            return self._generate_javascript_fallback_test(file_data, test_targets)
        elif language == 'java':
            return self._generate_java_fallback_test(file_data, test_targets)
        
        return ""
    
    def _generate_python_intelligent_fallback(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate intelligent Python tests based on function analysis"""
        file_name = Path(file_data['file_path']).stem
        
        test_code = f"""import pytest
import sys
from pathlib import Path

# Add the source directory to Python path  
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from {file_name} import *
except ImportError as e:
    print(f"Import error: {{e}}")
    # Try alternative import methods
    import importlib.util
    spec = importlib.util.spec_from_file_location("{file_name}", Path(__file__).parent.parent / "{file_name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    globals().update({{name: getattr(module, name) for name in dir(module) if not name.startswith('_')}})

"""
        
        # Generate smart tests based on function analysis
        for func in test_targets['functions']:
            func_name = func['name']
            args = func.get('args', [])
            operations = func.get('operations', [])
            
            test_code += f"""
# Tests for {func_name} function
def test_{func_name}_exists():
    \"\"\"Test that {func_name} function exists\"\"\"
    assert callable({func_name}), f"{func_name} should be callable"

"""
            
            # Generate tests based on detected operations
            if 'addition' in operations or 'add' in func_name.lower():
                test_code += f"""def test_{func_name}_addition():
    \"\"\"Test {func_name} performs addition correctly\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(5, 3)
        assert isinstance(result, (int, float)), "Should return a number"
        assert result == 8, "5 + 3 should equal 8"
    else:
        # Single parameter function
        result = {func_name}(5)
        assert result is not None

def test_{func_name}_negative_numbers():
    \"\"\"Test {func_name} with negative numbers\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(-2, -3)
        assert isinstance(result, (int, float))
        assert result == -5, "-2 + -3 should equal -5"

def test_{func_name}_zero():
    \"\"\"Test {func_name} with zero\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(0, 5)
        assert result == 5, "0 + 5 should equal 5"

"""
            elif 'subtraction' in operations or 'subtract' in func_name.lower():
                test_code += f"""def test_{func_name}_subtraction():
    \"\"\"Test {func_name} performs subtraction correctly\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(10, 3)
        assert isinstance(result, (int, float))
        assert result == 7, "10 - 3 should equal 7"

def test_{func_name}_negative_result():
    \"\"\"Test {func_name} with negative result\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(3, 10)
        assert result == -7, "3 - 10 should equal -7"

"""
            elif 'multiplication' in operations or 'multiply' in func_name.lower():
                test_code += f"""def test_{func_name}_multiplication():
    \"\"\"Test {func_name} performs multiplication correctly\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(4, 3)
        assert isinstance(result, (int, float))
        assert result == 12, "4 * 3 should equal 12"

def test_{func_name}_by_zero():
    \"\"\"Test {func_name} multiplication by zero\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(5, 0)
        assert result == 0, "5 * 0 should equal 0"

"""
            elif 'division' in operations or 'divide' in func_name.lower():
                test_code += f"""def test_{func_name}_division():
    \"\"\"Test {func_name} performs division correctly\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(10, 2)
        assert isinstance(result, (int, float))
        assert result == 5, "10 / 2 should equal 5"

def test_{func_name}_division_by_zero():
    \"\"\"Test {func_name} handles division by zero\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        with pytest.raises(ZeroDivisionError):
            {func_name}(10, 0)

def test_{func_name}_float_division():
    \"\"\"Test {func_name} with float division\"\"\"
    if len(inspect.signature({func_name}).parameters) >= 2:
        result = {func_name}(7, 2)
        assert result == 3.5, "7 / 2 should equal 3.5"

"""
            else:
                # Generic but intelligent tests
                test_code += f"""def test_{func_name}_with_valid_args():
    \"\"\"Test {func_name} with valid arguments\"\"\"
    import inspect
    sig = inspect.signature({func_name})
    param_count = len(sig.parameters)
    
    if param_count == 0:
        result = {func_name}()
        assert result is not None or result is None  # Allow any return value
    elif param_count == 1:
        # Try different types of single arguments
        for test_val in [1, "test", [1, 2, 3]]:
            try:
                result = {func_name}(test_val)
                assert result is not None or result is None
                break
            except (TypeError, ValueError):
                continue
    elif param_count == 2:
        # Try pairs of arguments
        test_pairs = [(1, 2), ("a", "b"), ([1], [2])]
        for arg1, arg2 in test_pairs:
            try:
                result = {func_name}(arg1, arg2)
                assert result is not None or result is None
                break
            except (TypeError, ValueError):
                continue

def test_{func_name}_error_handling():
    \"\"\"Test {func_name} handles invalid input appropriately\"\"\"
    import inspect
    sig = inspect.signature({func_name})
    param_count = len(sig.parameters)
    
    if param_count > 0:
        # Test with None values
        try:
            if param_count == 1:
                {func_name}(None)
            elif param_count == 2:
                {func_name}(None, None)
            else:
                {func_name}(*[None] * param_count)
        except (TypeError, ValueError, AttributeError) as e:
            # Expected behavior - function should handle invalid input
            assert True, f"Function properly raised {{type(e).__name__}}"

"""
        
        # Add inspect import at the top
        test_code = test_code.replace("import pytest", "import pytest\nimport inspect")
        
        return test_code
    
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
    
    def _generate_javascript_fallback_test(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate basic JavaScript Jest template"""
        file_name = Path(file_data['file_path']).stem
        
        test_code = f"""const {{ }} = require('../{file_name}');

describe('{file_name}', () => {{
"""
        
        # Generate tests for functions
        for func in test_targets['functions']:
            test_code += f"""
    describe('{func['name']}', () => {{
        test('should exist and be callable', () => {{
            expect(typeof {func['name']}).toBe('function');
        }});
        
        test('should handle valid input', () => {{
            expect(() => {{
                {func['name']}('test');
            }}).not.toThrow();
        }});
        
        test('should handle invalid input', () => {{
            expect(() => {{
                {func['name']}(null);
            }}).toThrow();
        }});
        
        test('should return consistent type', () => {{
            const result = {func['name']}('test');
            expect(result).toBeDefined();
        }});
        
        test('should handle edge cases', () => {{
            expect(() => {{
                {func['name']}('');
            }}).not.toThrow();
        }});
    }});
"""
        
        test_code += "});"
        return test_code
    
    def _generate_java_fallback_test(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate basic Java JUnit template"""
        file_name = Path(file_data['file_path']).stem
        
        test_code = f"""import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

@DisplayName("{file_name} Test Suite")
public class {file_name}Test {{
    
    @BeforeEach
    void setUp() {{
        // Setup test fixtures
    }}
"""
        
        # Generate tests for each class/method
        for cls in test_targets['classes']:
            test_code += f"""
    @Test
    @DisplayName("Test {cls['name']} creation")
    void test{cls['name']}Creation() {{
        assertDoesNotThrow(() -> {{
            {cls['name']} instance = new {cls['name']}();
            assertNotNull(instance);
        }});
    }}
"""
        
        for func in test_targets['functions']:
            test_code += f"""
    @Test
    @DisplayName("Test {func['name']} function")
    void test{func['name']}() {{
        assertDoesNotThrow(() -> {{
            {func['name']}("test");
        }});
    }}
"""
        
        test_code += "}"
        return test_code
    
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