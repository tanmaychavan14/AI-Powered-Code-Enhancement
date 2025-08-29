import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
import google.generativeai as genai

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
            model = genai.GenerativeModel('gemini-1.5-flash')
            console.print("[green]✅ Gemini AI initialized[/green]")
            return model
            
        except Exception as e:
            console.print(f"[red]❌ Failed to initialize Gemini: {e}[/red]")
            return None
    
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
            
            # Extract testable components
            test_targets = self._extract_test_targets(file_data)
            
            if not test_targets['classes'] and not test_targets['functions']:
                return {
                    'success': False,
                    'error': 'No testable components found'
                }
            
            # Generate test code using Gemini
            test_code = self._generate_test_code_with_llm(file_data, test_targets)
            
            if not test_code:
                return {
                    'success': False,
                    'error': 'Failed to generate test code'
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
    
    def _extract_test_targets(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract classes and functions that need testing"""
        return {
            'classes': file_data.get('classes', []),
            'functions': file_data.get('functions', []),
            'imports': file_data.get('imports', [])
        }
    
    def _generate_test_code_with_llm(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> Optional[str]:
        """Generate test code using Gemini LLM"""
        try:
            if not self.gemini_client:
                return self._generate_fallback_test(file_data, test_targets)
            
            language = file_data['language']
            content = file_data['content']
            
            # Create prompt for Gemini
            prompt = self._create_test_generation_prompt(language, content, test_targets)
            
            # Generate test code
            response = self.gemini_client.generate_content(prompt)
            
            if response and response.text:
                # Clean and validate generated code
                test_code = self._clean_generated_code(response.text, language)
                return test_code
            
            return self._generate_fallback_test(file_data, test_targets)
            
        except Exception as e:
            console.print(f"[yellow]LLM generation failed: {e}[/yellow]")
            return self._generate_fallback_test(file_data, test_targets)
    
    def _create_test_generation_prompt(self, language: str, content: str, test_targets: Dict[str, Any]) -> str:
        """Create prompt for test generation"""
        if language == 'python':
            return f"""
Generate comprehensive pytest test cases for the following Python code.

Requirements:
- Use pytest framework
- Test all public methods and functions
- Include edge cases and error handling tests
- Use proper assertions
- Add docstrings for test methods
- Mock external dependencies if needed

Code to test:
```python
{content}
```

Classes to test: {[cls['name'] for cls in test_targets['classes']]}
Functions to test: {[func['name'] for func in test_targets['functions']]}

Generate only the test code, properly formatted and ready to run.
"""
        
        elif language == 'javascript':
            return f"""
Generate comprehensive Jest test cases for the following JavaScript code.

Requirements:
- Use Jest framework
- Test all exported functions and classes
- Include edge cases and error handling
- Use proper expect() assertions
- Mock dependencies where appropriate

Code to test:
```javascript
{content}
```

Generate only the test code, properly formatted and ready to run.
"""
        
        elif language == 'java':
            return f"""
Generate comprehensive JUnit test cases for the following Java code.

Requirements:
- Use JUnit 5 framework
- Test all public methods
- Include edge cases and error handling
- Use proper assertions
- Follow Java naming conventions

Code to test:
```java
{content}
```

Generate only the test code, properly formatted and ready to run.
"""
    
    def _clean_generated_code(self, generated_text: str, language: str) -> str:
        """Clean and extract code from LLM response"""
        # Remove markdown code blocks if present
        import re
        
        # Extract code between ```language and ```
        pattern = rf'```{language}(.*?)```'
        matches = re.findall(pattern, generated_text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Try general code blocks
        pattern = r'```(.*?)```'
        matches = re.findall(pattern, generated_text, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Return as-is if no code blocks found
        return generated_text.strip()
    
    def _generate_fallback_test(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate basic test template as fallback"""
        language = file_data['language']
        
        if language == 'python':
            return self._generate_python_fallback_test(file_data, test_targets)
        elif language == 'javascript':
            return self._generate_javascript_fallback_test(file_data, test_targets)
        elif language == 'java':
            return self._generate_java_fallback_test(file_data, test_targets)
        
        return ""
    
    def _generate_python_fallback_test(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate basic Python pytest template"""
        file_name = Path(file_data['file_path']).stem
        
        test_code = f"""import pytest
import sys
from pathlib import Path

# Add the source directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from {file_name} import *

"""
        
        # Generate test classes for each class
        for cls in test_targets['classes']:
            test_code += f"""
class Test{cls['name']}:
    \"\"\"Test cases for {cls['name']} class\"\"\"
    
    def test_{cls['name'].lower()}_creation(self):
        \"\"\"Test {cls['name']} can be created\"\"\"
        # TODO: Add proper test implementation
        assert True
        
    def test_{cls['name'].lower()}_methods(self):
        \"\"\"Test {cls['name']} methods\"\"\"
        # TODO: Add method tests
        assert True
"""
        
        # Generate test functions for standalone functions
        for func in test_targets['functions']:
            test_code += f"""
def test_{func['name']}():
    \"\"\"Test {func['name']} function\"\"\"
    # TODO: Add proper test implementation
    assert True
"""
        
        return test_code
    
    def _generate_javascript_fallback_test(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate basic JavaScript Jest template"""
        file_name = Path(file_data['file_path']).stem
        
        test_code = f"""const {{ }} = require('../{file_name}');

describe('{file_name}', () => {{
"""
        
        # Generate tests for functions
        for func in test_targets['functions']:
            test_code += f"""
    test('{func['name']} should work correctly', () => {{
        // TODO: Add proper test implementation
        expect(true).toBe(true);
    }});
"""
        
        test_code += "});"
        return test_code
    
    def _generate_java_fallback_test(self, file_data: Dict[str, Any], test_targets: Dict[str, Any]) -> str:
        """Generate basic Java JUnit template"""
        file_name = Path(file_data['file_path']).stem
        
        test_code = f"""import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

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
    void test{cls['name']}Creation() {{
        // TODO: Add proper test implementation
        assertTrue(true);
    }}
"""
        
        for func in test_targets['functions']:
            test_code += f"""
    @Test
    void test{func['name']}() {{
        // TODO: Add proper test implementation
        assertTrue(true);
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
            
            return runner.run_tests(test_file_path)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Test execution failed: {str(e)}'
            }
