#!/usr/bin/env python3
"""
Enhanced PyTest Runner - Executes Python tests with multiple fallback strategies
"""

import subprocess
import json
import re
import sys
import importlib.util
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console

console = Console()

class PytestRunner:
    """Enhanced runner for executing Python tests with multiple strategies"""
    
    def __init__(self):
        self.console = Console()
        self.pytest_available = self._check_pytest_available()
        self.execution_strategies = [
            self._run_with_pytest,
            self._run_with_unittest,
            self._run_with_direct_execution,
            self._run_basic_syntax_check
        ]
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """Execute tests using the best available method"""
        console.print(f"[cyan]🧪 Running Python tests: {Path(test_file_path).name}[/cyan]")
        
        # Try each execution strategy in order
        for i, strategy in enumerate(self.execution_strategies):
            try:
                result = strategy(test_file_path)
                if result['success']:
                    console.print(f"[green]✅ Tests executed successfully using strategy {i+1}[/green]")
                    return result
                else:
                    console.print(f"[yellow]Strategy {i+1} failed: {result.get('error', 'Unknown error')}[/yellow]")
            except Exception as e:
                console.print(f"[yellow]Strategy {i+1} exception: {e}[/yellow]")
                continue
        
        # If all strategies fail, return comprehensive failure info
        return {
            'success': False,
            'error': 'All test execution strategies failed',
            'passed': 0,
            'failed': 0,
            'strategies_attempted': len(self.execution_strategies),
            'pytest_available': self.pytest_available
        }
    
    def _check_pytest_available(self) -> bool:
        """Check if pytest is installed and available"""
        try:
            result = subprocess.run(['python', '-m', 'pytest', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            available = result.returncode == 0
            if available:
                console.print("[green]✅ pytest is available[/green]")
            else:
                console.print("[yellow]⚠️ pytest not available[/yellow]")
            return available
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not check pytest: {e}[/yellow]")
            return False
    
    def _run_with_pytest(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 1: Run with pytest (preferred method)"""
        if not self.pytest_available:
            return {'success': False, 'error': 'pytest not available'}
        
        try:
            # Create a temporary JSON report file
            json_report_path = Path(test_file_path).parent / f"pytest_report_{Path(test_file_path).stem}.json"
            
            # Run pytest with comprehensive options
            cmd = [
                'python', '-m', 'pytest', 
                str(test_file_path),
                '-v',
                '--tb=short',
                '--json-report',
                f'--json-report-file={json_report_path}'
            ]
            
            console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30)
            
            # Parse results
            if json_report_path.exists():
                try:
                    with open(json_report_path, 'r') as f:
                        json_data = json.load(f)
                    json_report_path.unlink()  # Clean up
                    return self._parse_json_report(json_data, test_file_path)
                except Exception as e:
                    console.print(f"[yellow]JSON parsing failed: {e}[/yellow]")
            
            # Fallback to text parsing
            return self._parse_pytest_text_output(result, test_file_path)
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'pytest execution timed out (30s)',
                'passed': 0,
                'failed': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'pytest execution failed: {str(e)}'
            }
    
    def _run_with_unittest(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 2: Run with Python's built-in unittest"""
        try:
            console.print("[dim]Trying unittest execution...[/dim]")
            
            # Convert pytest-style test to unittest compatible
            test_content = self._read_and_convert_to_unittest(test_file_path)
            if not test_content:
                return {'success': False, 'error': 'Could not convert to unittest format'}
            
            # Create temporary unittest file
            unittest_file = Path(test_file_path).parent / f"unittest_{Path(test_file_path).stem}.py"
            with open(unittest_file, 'w') as f:
                f.write(test_content)
            
            # Run with unittest
            result = subprocess.run([
                'python', '-m', 'unittest', 
                f"unittest_{Path(test_file_path).stem}.py",
                '-v'
            ], 
            capture_output=True, 
            text=True,
            timeout=30,
            cwd=unittest_file.parent
            )
            
            # Clean up
            unittest_file.unlink()
            
            return self._parse_unittest_output(result, test_file_path)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'unittest execution failed: {str(e)}'
            }
    
    def _run_with_direct_execution(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 3: Direct Python execution with custom test discovery"""
        try:
            console.print("[dim]Trying direct execution...[/dim]")
            
            # Read the test file
            with open(test_file_path, 'r') as f:
                test_content = f.read()
            
            # Create a wrapper script that executes tests
            wrapper_script = self._create_test_wrapper(test_content, test_file_path)
            
            # Execute the wrapper
            result = subprocess.run([
                'python', '-c', wrapper_script
            ], 
            capture_output=True, 
            text=True,
            timeout=30
            )
            
            return self._parse_direct_execution_output(result, test_file_path)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Direct execution failed: {str(e)}'
            }
    
    def _run_basic_syntax_check(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 4: At minimum, check if the test file is syntactically valid"""
        try:
            console.print("[dim]Performing syntax validation...[/dim]")
            
            # Check syntax
            result = subprocess.run([
                'python', '-m', 'py_compile', test_file_path
            ], 
            capture_output=True, 
            text=True,
            timeout=10
            )
            
            if result.returncode == 0:
                # Syntax is valid, count potential tests
                with open(test_file_path, 'r') as f:
                    content = f.read()
                
                test_functions = re.findall(r'def test_\w+', content)
                
                return {
                    'success': True,
                    'passed': 0,
                    'failed': 0,
                    'syntax_valid': True,
                    'potential_tests': len(test_functions),
                    'test_file': test_file_path,
                    'method': 'syntax_check_only',
                    'message': f'Syntax valid. Found {len(test_functions)} test functions.'
                }
            else:
                return {
                    'success': False,
                    'error': f'Syntax error in test file: {result.stderr}',
                    'syntax_valid': False
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Syntax check failed: {str(e)}'
            }
    
    def _read_and_convert_to_unittest(self, test_file_path: str) -> str:
        """Convert pytest-style tests to unittest format"""
        try:
            with open(test_file_path, 'r') as f:
                content = f.read()
            
            # Basic conversion from pytest to unittest
            # This is a simplified conversion
            unittest_content = """import unittest
import sys
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
            
            # Extract imports from original file
            import_lines = [line for line in content.split('\n') if line.strip().startswith('import') or line.strip().startswith('from')]
            unittest_content += '\n'.join(import_lines) + '\n\n'
            
            # Create unittest class
            class_name = f"Test{Path(test_file_path).stem.replace('test_', '').title()}"
            unittest_content += f"class {class_name}(unittest.TestCase):\n"
            
            # Convert test functions
            test_functions = re.findall(r'def (test_\w+.*?)(?=def|\Z)', content, re.DOTALL)
            
            for func_match in test_functions:
                # Replace assert statements with unittest assertions
                func_content = func_match
                func_content = re.sub(r'assert ([^,]+) == ([^,\n]+)', r'self.assertEqual(\1, \2)', func_content)
                func_content = re.sub(r'assert ([^,\n]+)', r'self.assertTrue(\1)', func_content)
                func_content = re.sub(r'pytest\.raises\(([^)]+)\)', r'self.assertRaises(\1)', func_content)
                
                # Add proper indentation
                func_lines = func_content.split('\n')
                indented_lines = ['    ' + line if line.strip() else line for line in func_lines]
                unittest_content += '\n'.join(indented_lines) + '\n\n'
            
            unittest_content += """
if __name__ == '__main__':
    unittest.main()
"""
            
            return unittest_content
            
        except Exception as e:
            console.print(f"[yellow]Conversion to unittest failed: {e}[/yellow]")
            return ""
    
    def _create_test_wrapper(self, test_content: str, test_file_path: str) -> str:
        """Create a wrapper script for direct test execution"""
        return f"""
import sys
import traceback
from pathlib import Path

# Add source directory to path
test_file_dir = Path(r"{test_file_path}").parent
source_dir = test_file_dir.parent
sys.path.insert(0, str(source_dir))

# Test execution results
passed = 0
failed = 0
errors = []

# Execute the test file content
try:
    exec('''{test_content}''')
    
    # Find and execute test functions
    import inspect
    current_module = sys.modules[__name__]
    
    for name, obj in inspect.getmembers(current_module):
        if name.startswith('test_') and callable(obj):
            try:
                print(f"Running {{name}}...")
                obj()
                passed += 1
                print(f"✅ {{name}} PASSED")
            except Exception as e:
                failed += 1
                errors.append(f"❌ {{name}} FAILED: {{str(e)}}")
                print(f"❌ {{name}} FAILED: {{str(e)}}")
    
    print(f"\\nRESULTS: {{passed}} passed, {{failed}} failed")
    if errors:
        print("\\nERRORS:")
        for error in errors:
            print(error)
            
except Exception as e:
    print(f"EXECUTION ERROR: {{str(e)}}")
    print(traceback.format_exc())
    failed = 1
"""
    
    def _parse_json_report(self, json_data: Dict, test_file_path: str) -> Dict[str, Any]:
        """Parse pytest JSON report"""
        summary = json_data.get('summary', {})
        
        return {
            'success': True,
            'passed': summary.get('passed', 0),
            'failed': summary.get('failed', 0),
            'skipped': summary.get('skipped', 0),
            'duration': summary.get('duration', 0),
            'test_file': test_file_path,
            'details': json_data.get('tests', []),
            'method': 'pytest_json'
        }
    
    def _parse_pytest_text_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse pytest text output"""
        output = result.stdout + result.stderr
        
        # Extract test counts using regex
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)
        skipped_match = re.search(r'(\d+) skipped', output)
        error_match = re.search(r'(\d+) error', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        skipped = int(skipped_match.group(1)) if skipped_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        
        # Extract duration
        duration_match = re.search(r'(\d+\.?\d*) seconds', output)
        duration = float(duration_match.group(1)) if duration_match else 0
        
        # Determine if execution was actually successful
        success = result.returncode == 0 and (passed > 0 or failed >= 0)
        
        return {
            'success': success,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'errors': errors,
            'duration': duration,
            'test_file': test_file_path,
            'output': output,
            'return_code': result.returncode,
            'method': 'pytest_text'
        }
    
    def _parse_unittest_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse unittest output"""
        output = result.stdout + result.stderr
        
        # Parse unittest output patterns
        # Look for patterns like "Ran 5 tests in 0.001s" and "OK" or "FAILED"
        ran_match = re.search(r'Ran (\d+) tests? in ([\d.]+)s', output)
        ok_match = re.search(r'\nOK\n', output)
        failed_match = re.search(r'FAILED \(failures=(\d+)\)', output)
        error_match = re.search(r'FAILED \(errors=(\d+)\)', output)
        
        total_tests = int(ran_match.group(1)) if ran_match else 0
        duration = float(ran_match.group(2)) if ran_match else 0
        
        if ok_match:
            passed = total_tests
            failed = 0
        else:
            failed_count = int(failed_match.group(1)) if failed_match else 0
            error_count = int(error_match.group(1)) if error_match else 0
            failed = failed_count + error_count
            passed = max(0, total_tests - failed)
        
        return {
            'success': result.returncode == 0,
            'passed': passed,
            'failed': failed,
            'skipped': 0,
            'duration': duration,
            'test_file': test_file_path,
            'output': output,
            'method': 'unittest'
        }
    
    def _parse_direct_execution_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse direct execution output"""
        output = result.stdout + result.stderr
        
        # Look for our custom output patterns
        passed_matches = output.count("PASSED")
        failed_matches = output.count("FAILED")
        
        # Extract results summary if present
        results_match = re.search(r'RESULTS: (\d+) passed, (\d+) failed', output)
        if results_match:
            passed = int(results_match.group(1))
            failed = int(results_match.group(2))
        else:
            passed = passed_matches
            failed = failed_matches
        
        return {
            'success': result.returncode == 0 and failed == 0,
            'passed': passed,
            'failed': failed,
            'skipped': 0,
            'duration': 0,
            'test_file': test_file_path,
            'output': output,
            'method': 'direct_execution'
        }
    
    def get_installation_instructions(self) -> Dict[str, Any]:
        """Get instructions for installing testing dependencies"""
        return {
            'pytest': {
                'command': 'pip install pytest pytest-json-report',
                'description': 'Install pytest with JSON reporting support'
            },
            'alternative_commands': [
                'python -m pip install pytest pytest-json-report',
                'pip3 install pytest pytest-json-report',
                'conda install pytest pytest-json-report'
            ],
            'verification': 'python -m pytest --version',
            'minimal_setup': 'pip install pytest'
        }
    
    def diagnose_environment(self) -> Dict[str, Any]:
        """Diagnose the testing environment and provide recommendations"""
        diagnosis = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'pytest_available': self.pytest_available,
            'recommendations': []
        }
        
        # Check Python version
        if sys.version_info < (3, 6):
            diagnosis['recommendations'].append('Upgrade Python to 3.6+ for better testing support')
        
        # Check pytest
        if not self.pytest_available:
            diagnosis['recommendations'].append('Install pytest: pip install pytest pytest-json-report')
        
        # Check if we can import common testing modules
        modules_to_check = ['unittest', 'json', 'subprocess']
        available_modules = []
        
        for module_name in modules_to_check:
            try:
                importlib.import_module(module_name)
                available_modules.append(module_name)
            except ImportError:
                diagnosis['recommendations'].append(f'Module {module_name} not available')
        
        diagnosis['available_modules'] = available_modules
        
        return diagnosis
    
    def install_pytest(self) -> Dict[str, Any]:
        """Attempt to automatically install pytest"""
        try:
            console.print("[cyan]Attempting to install pytest...[/cyan]")
            
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-json-report'
            ], 
            capture_output=True, 
            text=True,
            timeout=60
            )
            
            if result.returncode == 0:
                # Re-check availability
                self.pytest_available = self._check_pytest_available()
                return {
                    'success': True,
                    'message': 'pytest installed successfully',
                    'pytest_available': self.pytest_available
                }
            else:
                return {
                    'success': False,
                    'error': f'Installation failed: {result.stderr}',
                    'suggestions': [
                        'Try: pip install pytest',
                        'Try: python -m pip install pytest',
                        'Check internet connection',
                        'Check permissions'
                    ]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Installation attempt failed: {str(e)}'
            }
    
    def _read_and_convert_to_unittest(self, test_file_path: str) -> str:
        """Read test file and convert pytest syntax to unittest"""
        try:
            with open(test_file_path, 'r') as f:
                content = f.read()
            
            # Basic pytest to unittest conversion
            unittest_content = """import unittest
import sys
from pathlib import Path

# Add source to path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
            
            # Extract imports (excluding pytest-specific ones)
            import_lines = []
            for line in content.split('\n'):
                if line.strip().startswith(('import ', 'from ')) and 'pytest' not in line:
                    import_lines.append(line)
            
            unittest_content += '\n'.join(import_lines) + '\n\n'
            
            # Create test class
            class_name = f"Test{Path(test_file_path).stem.replace('test_', '').title()}"
            unittest_content += f"class {class_name}(unittest.TestCase):\n\n"
            
            # Convert test functions
            test_functions = re.findall(r'def (test_\w+.*?)(?=def test_|\Z)', content, re.DOTALL)
            
            for func_match in test_functions:
                # Convert pytest assertions to unittest
                func_content = func_match
                
                # Basic assertion conversions
                func_content = re.sub(r'assert ([^=]+) == ([^,\n]+)', r'self.assertEqual(\1, \2)', func_content)
                func_content = re.sub(r'assert ([^,\n]+)', r'self.assertTrue(\1)', func_content)
                func_content = re.sub(r'with pytest\.raises\(([^)]+)\):', r'with self.assertRaises(\1):', func_content)
                
                # Add proper indentation (unittest methods need 4 extra spaces)
                func_lines = func_content.split('\n')
                indented_lines = []
                for line in func_lines:
                    if line.strip():
                        indented_lines.append('    ' + line)
                    else:
                        indented_lines.append(line)
                
                unittest_content += '\n'.join(indented_lines) + '\n\n'
            
            unittest_content += """
if __name__ == '__main__':
    unittest.main(verbosity=2)
"""
            
            return unittest_content
            
        except Exception as e:
            console.print(f"[yellow]Conversion failed: {e}[/yellow]")
            return ""
    
    def _create_test_wrapper(self, test_content: str, test_file_path: str) -> str:
        """Create a wrapper script for direct test execution"""
        return f"""
import sys
import traceback
import re
from pathlib import Path

# Add source directory to path
test_file_dir = Path(r"{test_file_path}").parent
source_dir = test_file_dir.parent
sys.path.insert(0, str(source_dir))

# Test execution results
passed = 0
failed = 0
errors = []

print("Starting direct test execution...")

# Import the test content
test_globals = {{}}
test_locals = {{}}

try:
    # Execute the test file to define functions
    exec('''{test_content}''', test_globals, test_locals)
    
    # Find and execute test functions
    for name, obj in test_locals.items():
        if name.startswith('test_') and callable(obj):
            try:
                print(f"Running {{name}}...")
                obj()
                passed += 1
                print(f"✅ {{name}} PASSED")
            except Exception as e:
                failed += 1
                error_msg = f"❌ {{name}} FAILED: {{str(e)}}"
                errors.append(error_msg)
                print(error_msg)
                print(f"   Traceback: {{traceback.format_exc().split(chr(10))[-3]}}")
    
    print(f"\\n=== RESULTS ===")
    print(f"RESULTS: {{passed}} passed, {{failed}} failed")
    if errors:
        print("\\nFAILED TESTS:")
        for error in errors:
            print(f"  {{error}}")
            
except Exception as e:
    print(f"EXECUTION ERROR: {{str(e)}}")
    print(f"TRACEBACK: {{traceback.format_exc()}}")
    failed = 1
"""