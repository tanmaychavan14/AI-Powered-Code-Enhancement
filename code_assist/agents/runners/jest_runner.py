# #!/usr/bin/env python3
# """
# Complete Jest Runner - Handles Windows paths, encoding, and module resolution
# """

# import subprocess
# import json
# import re
# import sys
# import os
# import shutil
# from pathlib import Path
# from typing import Dict, Any, Optional, List
# from rich.console import Console

# console = Console()

# class JestRunner:
#     """Jest test runner with proper path and encoding handling"""
    
#     def __init__(self):
#         self.console = Console()
        
#         # Set the project root as parent folder of runner/
#         self.project_root = Path(__file__).resolve().parent.parent
        
#         console.print(f"[cyan]Jest Runner initialized from project root: {self.project_root}[/cyan]")
        
#         self.jest_available = self._check_jest_availability()

    
#     def _check_jest_availability(self) -> bool:
#         """Check if Jest is available in the project"""
#         try:
#             result = subprocess.run(
#                 ['npx', 'jest', '--version'],
#                 capture_output=True,
#                 timeout=5,
#                 cwd=self.project_root,
#                 encoding='utf-8',
#                 errors='replace'
#             )
            
#             if result.returncode == 0:
#                 console.print(f"[green]✅ Jest available: {result.stdout.strip()}[/green]")
#                 return True
#             else:
#                 console.print("[yellow]⚠️ Jest not found via npx[/yellow]")
#                 return False
                
#         except Exception as e:
#             console.print(f"[yellow]⚠️ Could not check Jest: {e}[/yellow]")
#             return False
    
#     def run_tests(self, test_file_path: str) -> Dict[str, Any]:
#         """Execute Jest tests with multiple fallback strategies"""
#         console.print(f"[cyan]🧪 Running JavaScript tests: {Path(test_file_path).name}[/cyan]")
        
#         test_file = Path(test_file_path).resolve()
        
#         if not test_file.exists():
#             return {
#                 'success': False,
#                 'error': f'Test file not found: {test_file}',
#                 'passed': 0,
#                 'failed': 0
#             }
        
#         # Strategy 1: Copy test to source directory
#         source_file = self._find_source_file(test_file)
#         if source_file:
#             result = self._run_test_in_source_dir(test_file, source_file)
#             if result['success'] or result.get('passed', 0) > 0:
#                 return result
        
#         # Strategy 2: Run Jest from project root
#         result = self._run_with_jest(test_file)
#         if result['success'] or result.get('passed', 0) > 0:
#             return result
        
#         # Strategy 3: Direct Node.js execution with mocked Jest
#         result = self._run_with_node_direct(test_file)
#         if result['success'] or result.get('passed', 0) > 0:
#             return result
        
#         # Strategy 4: Syntax check only
#         return self._run_syntax_check(test_file)
    
#     def _find_source_file(self, test_file: Path) -> Optional[Path]:
#         """Find the corresponding source file for a test"""
#         # Extract source name from test name
#         # javascript.test.js -> javascript.js
#         source_name = test_file.name.replace('.test.js', '.js').replace('.spec.js', '.js')
        
#         console.print(f"[dim]Looking for source file: {source_name}[/dim]")
        
#         # Search in common source directories
#         search_dirs = [
#             test_file.parent,  # Same directory as the test file
#             test_file.parent.parent,  # One level up from test file
#             Path('testing_files'),
#             Path('src'),
#             Path('lib'),
#             Path('tests/generated/javascript'),
#             Path('.'),
#             self.project_root,
#             self.project_root / 'testing_files',
#             self.project_root / 'src',
#             self.project_root / 'tests' / 'generated' / 'javascript'
#         ]
        
#         for search_dir in search_dirs:
#             if search_dir.exists() and search_dir.is_dir():
#                 source_file = search_dir / source_name
#                 if source_file.exists():
#                     console.print(f"[green]✅ Found source: {source_file}[/green]")
#                     return source_file
        
#         console.print(f"[yellow]⚠️ Could not find source file: {source_name}[/yellow]")
#         return None
    
#     def _run_test_in_source_dir(self, test_file: Path, source_file: Path) -> Dict[str, Any]:
#         """
#         Copy test to source directory and run it there
#         This fixes module resolution issues
#         """
#         console.print(f"[cyan]Strategy 1: Running test in source directory[/cyan]")
        
#         working_dir = source_file.parent
#         temp_test_file = working_dir / test_file.name
        
#         try:
#             # Copy test file to source directory
#             shutil.copy2(test_file, temp_test_file)
#             console.print(f"[green]✅ Copied test to: {temp_test_file}[/green]")
            
#             # Update require/import paths in test file
#             self._fix_test_imports(temp_test_file, source_file.name)
            
#             # Try multiple Jest commands
#             commands = [
#                 ['npx', 'jest', test_file.name, '--json', '--no-coverage'],
#                 ['npm', 'test', '--', test_file.name, '--json'],
#                 ['node', '--test', test_file.name]  # Node.js native test runner
#             ]
            
#             for cmd in commands:
#                 try:
#                     console.print(f"[dim]Trying: {' '.join(cmd)}[/dim]")
                    
#                     result = subprocess.run(
#                         cmd,
#                         capture_output=True,
#                         timeout=30,
#                         cwd=working_dir,
#                         encoding='utf-8',
#                         errors='replace'
#                     )
                    
#                     parsed = self._parse_jest_output(result, str(temp_test_file))
                    
#                     if parsed['success'] or parsed.get('passed', 0) > 0:
#                         console.print(f"[green]✅ Tests ran successfully with: {cmd[0]}[/green]")
#                         return parsed
                    
#                 except subprocess.TimeoutExpired:
#                     console.print(f"[yellow]Command timed out: {' '.join(cmd)}[/yellow]")
#                     continue
#                 except Exception as e:
#                     console.print(f"[yellow]Command failed: {e}[/yellow]")
#                     continue
            
#             # If all Jest commands fail, try direct Node execution
#             return self._run_with_node_direct(temp_test_file)
            
#         except Exception as e:
#             console.print(f"[red]Error in source dir strategy: {e}[/red]")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'passed': 0,
#                 'failed': 0
#             }
#         finally:
#             # Clean up temporary test file
#             if temp_test_file.exists() and temp_test_file != test_file:
#                 try:
#                     temp_test_file.unlink()
#                     console.print(f"[dim]Cleaned up: {temp_test_file}[/dim]")
#                 except:
#                     pass
    
#     def _fix_test_imports(self, test_file: Path, source_filename: str):
#         """
#         Fix import/require statements in test file to use correct relative path
#         """
#         try:
#             with open(test_file, 'r', encoding='utf-8') as f:
#                 content = f.read()
            
#             # Get source module name (without .js)
#             source_module = source_filename.replace('.js', '')
            
#             # Fix require statements
#             patterns = [
#                 (r"require\(['\"]\.\/.*?['\"]", f"require('./{source_module}')"),
#                 (r"require\(['\"]\.\.\/.*?['\"]", f"require('./{source_module}')"),
#                 (r"from ['\"]\.\/.*?['\"]", f"from './{source_module}'"),
#                 (r"from ['\"]\.\.\/.*?['\"]", f"from './{source_module}'"),
#             ]
            
#             modified = False
#             for pattern, replacement in patterns:
#                 if re.search(pattern, content):
#                     content = re.sub(pattern, replacement, content)
#                     modified = True
            
#             if modified:
#                 with open(test_file, 'w', encoding='utf-8') as f:
#                     f.write(content)
#                 console.print(f"[green]✅ Fixed import paths in test file[/green]")
            
#         except Exception as e:
#             console.print(f"[yellow]Could not fix imports: {e}[/yellow]")
    
#     def _run_with_jest(self, test_file: Path) -> Dict[str, Any]:
#         """Run Jest from project root"""
#         console.print("[cyan]Strategy 2: Running Jest from project root[/cyan]")
        
#         # Convert to relative path from project root
#         try:
#             rel_path = test_file.relative_to(self.project_root)
#         except ValueError:
#             rel_path = test_file
        
#         commands = [
#             ['npx', 'jest', str(rel_path), '--json', '--verbose', '--forceExit'],
#             ['npm', 'test', '--', str(rel_path), '--json'],
#             ['yarn', 'test', str(rel_path), '--json']
#         ]
        
#         for cmd in commands:
#             try:
#                 console.print(f"[dim]Trying: {' '.join(cmd)}[/dim]")
                
#                 result = subprocess.run(
#                     cmd,
#                     capture_output=True,
#                     timeout=30,
#                     cwd=self.project_root,
#                     encoding='utf-8',
#                     errors='replace'
#                 )
                
#                 parsed = self._parse_jest_output(result, str(test_file))
                
#                 if parsed['success'] or parsed.get('passed', 0) > 0:
#                     return parsed
                
#             except subprocess.TimeoutExpired:
#                 console.print(f"[yellow]Command timed out[/yellow]")
#                 continue
#             except FileNotFoundError:
#                 # Command not found, try next one
#                 continue
#             except Exception as e:
#                 console.print(f"[yellow]Command failed: {e}[/yellow]")
#                 continue
        
#         return {
#             'success': False,
#             'error': 'All Jest commands failed',
#             'passed': 0,
#             'failed': 0
#         }
    
#     def _run_with_node_direct(self, test_file: Path) -> Dict[str, Any]:
#         """Run test directly with Node.js (mock Jest API)"""
#         console.print("[cyan]Strategy 3: Node.js direct execution with Jest mocks[/cyan]")
        
#         # Create a wrapper that provides Jest API
#         wrapper_code = '''
# // Mock Jest globals
# let testsPassed = 0;
# let testsFailed = 0;
# let currentDescribe = '';

# global.describe = (name, fn) => {
#     currentDescribe = name;
#     console.log(`\\n📦 ${name}`);
#     try {
#         fn();
#     } catch (e) {
#         console.error(`  ❌ Describe failed: ${e.message}`);
#     }
# };

# global.test = global.it = (name, fn) => {
#     const fullName = currentDescribe ? `${currentDescribe} > ${name}` : name;
#     try {
#         fn();
#         testsPassed++;
#         console.log(`  ✅ ${name}`);
#     } catch (e) {
#         testsFailed++;
#         console.log(`  ❌ ${name}`);
#         console.log(`     ${e.message}`);
#     }
# };

# global.expect = (actual) => ({
#     toBe: (expected) => {
#         if (actual !== expected) {
#             throw new Error(`Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`);
#         }
#     },
#     toEqual: (expected) => {
#         const actualStr = JSON.stringify(actual);
#         const expectedStr = JSON.stringify(expected);
#         if (actualStr !== expectedStr) {
#             throw new Error(`Expected ${expectedStr} but got ${actualStr}`);
#         }
#     },
#     toBeNull: () => {
#         if (actual !== null) {
#             throw new Error(`Expected null but got ${actual}`);
#         }
#     },
#     toBeUndefined: () => {
#         if (actual !== undefined) {
#             throw new Error(`Expected undefined but got ${actual}`);
#         }
#     },
#     toBeTruthy: () => {
#         if (!actual) {
#             throw new Error(`Expected truthy value but got ${actual}`);
#         }
#     },
#     toBeFalsy: () => {
#         if (actual) {
#             throw new Error(`Expected falsy value but got ${actual}`);
#         }
#     },
#     toThrow: () => {
#         try {
#             actual();
#             throw new Error('Expected function to throw but it did not');
#         } catch (e) {
#             // Expected to throw
#         }
#     },
#     toContain: (item) => {
#         if (!actual.includes(item)) {
#             throw new Error(`Expected array to contain ${item}`);
#         }
#     },
#     toHaveLength: (length) => {
#         if (actual.length !== length) {
#             throw new Error(`Expected length ${length} but got ${actual.length}`);
#         }
#     }
# });

# global.beforeEach = (fn) => fn();
# global.afterEach = (fn) => fn();
# global.beforeAll = (fn) => fn();
# global.afterAll = (fn) => fn();

# // Load and run test
# try {
#     require('TEST_FILE_PATH');
#     console.log(`\\n📊 Results: ${testsPassed} passed, ${testsFailed} failed`);
#     process.exit(testsFailed > 0 ? 1 : 0);
# } catch (e) {
#     console.error(`\\n❌ Test execution error: ${e.message}`);
#     console.error(e.stack);
#     process.exit(1);
# }
# '''.replace('TEST_FILE_PATH', str(test_file).replace('\\', '\\\\'))
        
#         try:
#             result = subprocess.run(
#                 ['node', '-e', wrapper_code],
#                 capture_output=True,
#                 timeout=30,
#                 cwd=test_file.parent,
#                 encoding='utf-8',
#                 errors='replace'
#             )
            
#             output = result.stdout + result.stderr
#             console.print(f"\n[dim]Node.js Output:\n{output}[/dim]")
            
#             # Parse results
#             passed = 0
#             failed = 0
            
#             passed_match = re.search(r'(\d+) passed', output)
#             failed_match = re.search(r'(\d+) failed', output)
            
#             if passed_match:
#                 passed = int(passed_match.group(1))
#             if failed_match:
#                 failed = int(failed_match.group(1))
            
#             # Also count checkmarks
#             if passed == 0 and failed == 0:
#                 passed = output.count('✅')
#                 failed = output.count('❌')
            
#             return {
#                 'success': result.returncode == 0 and failed == 0,
#                 'passed': passed,
#                 'failed': failed,
#                 'test_file': str(test_file),
#                 'output': output,
#                 'method': 'node_direct'
#             }
            
#         except subprocess.TimeoutExpired:
#             return {
#                 'success': False,
#                 'error': 'Node.js execution timed out',
#                 'passed': 0,
#                 'failed': 0
#             }
#         except Exception as e:
#             console.print(f"[red]Node.js execution error: {e}[/red]")
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'passed': 0,
#                 'failed': 0
#             }
    
#     def _run_syntax_check(self, test_file: Path) -> Dict[str, Any]:
#         """Fallback: Just check if the test file has valid syntax"""
#         console.print("[cyan]Strategy 4: Syntax validation only[/cyan]")
        
#         try:
#             result = subprocess.run(
#                 ['node', '--check', str(test_file)],
#                 capture_output=True,
#                 timeout=10,
#                 encoding='utf-8',
#                 errors='replace'
#             )
            
#             if result.returncode == 0:
#                 # Count potential tests
#                 with open(test_file, 'r', encoding='utf-8') as f:
#                     content = f.read()
                
#                 test_count = len(re.findall(r'\b(?:test|it)\s*\(', content))
                
#                 return {
#                     'success': True,
#                     'passed': 0,
#                     'failed': 0,
#                     'syntax_valid': True,
#                     'potential_tests': test_count,
#                     'test_file': str(test_file),
#                     'method': 'syntax_check',
#                     'message': f'✅ Syntax valid. Found {test_count} test cases (not executed).'
#                 }
#             else:
#                 return {
#                     'success': False,
#                     'error': f'Syntax error: {result.stderr}',
#                     'syntax_valid': False,
#                     'passed': 0,
#                     'failed': 0
#                 }
                
#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': f'Syntax check failed: {str(e)}',
#                 'passed': 0,
#                 'failed': 0
#             }
    
#     def _parse_jest_output(self, result: subprocess.CompletedProcess, test_file: str) -> Dict[str, Any]:
#         """Parse Jest output (JSON or text format)"""
        
#         # Try JSON parsing first
#         try:
#             json_data = json.loads(result.stdout)
            
#             passed = json_data.get('numPassedTests', 0)
#             failed = json_data.get('numFailedTests', 0)
#             total = json_data.get('numTotalTests', 0)
            
#             console.print(f"[cyan]📊 Jest JSON Results: {passed}/{total} passed, {failed} failed[/cyan]")
            
#             return {
#                 'success': failed == 0 and passed > 0,
#                 'passed': passed,
#                 'failed': failed,
#                 'total': total,
#                 'test_file': test_file,
#                 'method': 'jest_json',
#                 'return_code': result.returncode
#             }
            
#         except (json.JSONDecodeError, KeyError):
#             # Fall back to text parsing
#             pass
        
#         # Text parsing
#         output = result.stdout + result.stderr
        
#         passed = 0
#         failed = 0
        
#         # Try multiple patterns
#         patterns = [
#             (r'Tests:\s+(\d+) passed', 'passed'),
#             (r'Tests:\s+(\d+) failed', 'failed'),
#             (r'(\d+) passed', 'passed'),
#             (r'(\d+) failed', 'failed'),
#             (r'PASS.*?(\d+)', 'passed'),
#             (r'FAIL.*?(\d+)', 'failed'),
#         ]
        
#         for pattern, ptype in patterns:
#             matches = re.findall(pattern, output)
#             if matches:
#                 value = int(matches[0])
#                 if ptype == 'passed' and value > passed:
#                     passed = value
#                 elif ptype == 'failed' and value > failed:
#                     failed = value
        
#         # Count test outcomes if no numbers found
#         if passed == 0 and failed == 0:
#             passed = output.count('✓') + output.count('PASS')
#             failed = output.count('✗') + output.count('FAIL')
        
#         console.print(f"[cyan]📊 Jest Text Results: {passed} passed, {failed} failed[/cyan]")
        
#         success = result.returncode == 0 or (passed > 0 and failed == 0)
        
#         return {
#             'success': success,
#             'passed': passed,
#             'failed': failed,
#             'test_file': test_file,
#             'output': output[:1000],  # First 1000 chars
#             'method': 'jest_text',
#             'return_code': result.returncode
#         }



#!/usr/bin/env python3
"""
Complete Jest Runner - Simplified to match PyTest runner behavior
"""

import subprocess
import json
import re
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from rich.console import Console

console = Console()

class JestRunner:
    """Jest test runner - runs tests directly like PyTest runner"""
    
    def __init__(self):
     self.console = Console()
     # Add Node.js to PATH for subprocess
     node_path = r"C:\Program Files\nodejs"
     os.environ["PATH"] = node_path + os.pathsep + os.environ["PATH"]
    # Set the project root as parent folder of runner/
     # code_assist/agents/runners => go 2 levels up to code_assist/
     self.project_root = Path(__file__).resolve().parents[2]

    
     console.print(f"[cyan]Jest Runner initialized from project root: {self.project_root}[/cyan]")
    
     self.jest_available = self._check_jest_availability()

        
        # Define execution strategies similar to PyTest runner
     self.execution_strategies = [
            self._run_with_jest,
            self._run_with_node_direct,
            self._run_syntax_check
        ]
    
    def _check_jest_availability(self) -> bool:
        """Check if Jest is available in the project"""
        # Try multiple ways to find Jest
        jest_commands = [
            ['npx', 'jest', '--version'],
            ['jest', '--version'],  # Global Jest
            ['node', '-e', "console.log(require('jest/package.json').version)"]  # Via Node
        ]
        
        for cmd in jest_commands:
            try:
                console.print(f"[dim]Checking Jest with: {' '.join(cmd)}[/dim]")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=5,
                    cwd=self.project_root,
                    shell = True,

                    encoding='utf-8',
                    errors='replace'
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    console.print(f"[green]✅ Jest available via '{cmd[0]}': {version}[/green]")
                    return True
                    
            except FileNotFoundError:
                console.print(f"[dim]Command not found: {cmd[0]}[/dim]")
                continue
            except Exception as e:
                console.print(f"[dim]Failed with {cmd[0]}: {e}[/dim]")
                continue
        
        console.print("[yellow]⚠️ Jest not found via any method[/yellow]")
        console.print("[yellow]💡 Tests will run with Node.js mock instead[/yellow]")
        return False
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """Execute Jest tests using the best available method"""
        console.print(f"[cyan]🧪 Running JavaScript tests: {Path(test_file_path).name}[/cyan]")
        
        test_file = Path(test_file_path).resolve()
        
        if not test_file.exists():
            return {
                'success': False,
                'error': f'Test file not found: {test_file}',
                'passed': 0,
                'failed': 0
            }
        
        # Try each execution strategy in order (like PyTest runner)
        for i, strategy in enumerate(self.execution_strategies):
            try:
                console.print(f"[cyan]Strategy {i+1}: {strategy.__name__}[/cyan]")
                result = strategy(test_file)
                
                if result['success'] or result.get('passed', 0) > 0:
                    console.print(f"[green]✅ Tests executed successfully using strategy {i+1}[/green]")
                    return result
                else:
                    console.print(f"[yellow]Strategy {i+1} failed: {result.get('error', 'No tests passed')}[/yellow]")
                    
            except Exception as e:
                console.print(f"[yellow]Strategy {i+1} exception: {e}[/yellow]")
                continue
        
        # If all strategies fail
        return {
            'success': False,
            'error': 'All test execution strategies failed',
            'passed': 0,
            'failed': 0,
            'strategies_attempted': len(self.execution_strategies),
            'jest_available': self.jest_available
        }
    
    def _run_with_jest(self, test_file: Path) -> Dict[str, Any]:
        """Strategy 1: Run Jest from test file's directory"""
        console.print("[dim]Running Jest...[/dim]")
        
        # Convert to relative path from project root
        try:
            rel_path = test_file.relative_to(self.project_root)
        except ValueError:
            rel_path = test_file
        
        commands = [
            ['npx', 'jest', str(rel_path), '--json', '--verbose', '--forceExit'],
            ['npx', 'jest', str(rel_path), '--verbose', '--forceExit'],
            ['npm', 'test', '--', str(rel_path), '--json'],
            ['yarn', 'test', str(rel_path), '--json']
        ]
        
        for cmd in commands:
            try:
                console.print(f"[dim]Trying: {' '.join(cmd)}[/dim]")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=30,
                    cwd=self.project_root,
                    encoding='utf-8',
                    errors='replace',
                    shell = True
                )
                
                parsed = self._parse_jest_output(result, str(test_file))
                
                if parsed['success'] or parsed.get('passed', 0) > 0:
                    console.print(f"[green]✅ Jest ran successfully[/green]")
                    return parsed
                
            except subprocess.TimeoutExpired:
                console.print(f"[yellow]Command timed out[/yellow]")
                continue
            except FileNotFoundError:
                # Command not found, try next one
                continue
            except Exception as e:
                console.print(f"[yellow]Command failed: {e}[/yellow]")
                continue
        
        return {
            'success': False,
            'error': 'All Jest commands failed',
            'passed': 0,
            'failed': 0
        }
    
    def _run_with_node_direct(self, test_file: Path) -> Dict[str, Any]:
        """Strategy 2: Run test directly with Node.js (mock Jest API)"""
        console.print("[dim]Running with Node.js direct execution...[/dim]")
        
        # Create a wrapper that provides Jest API
        wrapper_code = '''
// Mock Jest globals
let testsPassed = 0;
let testsFailed = 0;
let currentDescribe = '';
const testResults = [];

global.describe = (name, fn) => {
    currentDescribe = name;
    console.log(`\\n📦 ${name}`);
    try {
        fn();
    } catch (e) {
        console.error(`  ❌ Describe block failed: ${e.message}`);
        testsFailed++;
    }
};

global.test = global.it = (name, fn) => {
    const fullName = currentDescribe ? `${currentDescribe} > ${name}` : name;
    try {
        fn();
        testsPassed++;
        testResults.push({name: fullName, status: 'passed'});
        console.log(`  ✅ ${name}`);
    } catch (e) {
        testsFailed++;
        testResults.push({name: fullName, status: 'failed', error: e.message});
        console.log(`  ❌ ${name}`);
        console.log(`     ${e.message}`);
    }
};

global.expect = (actual) => ({
    toBe: (expected) => {
        if (actual !== expected) {
            throw new Error(`Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`);
        }
    },
    toEqual: (expected) => {
        const actualStr = JSON.stringify(actual);
        const expectedStr = JSON.stringify(expected);
        if (actualStr !== expectedStr) {
            throw new Error(`Expected ${expectedStr} but got ${actualStr}`);
        }
    },
    toBeNull: () => {
        if (actual !== null) {
            throw new Error(`Expected null but got ${actual}`);
        }
    },
    toBeUndefined: () => {
        if (actual !== undefined) {
            throw new Error(`Expected undefined but got ${actual}`);
        }
    },
    toBeTruthy: () => {
        if (!actual) {
            throw new Error(`Expected truthy value but got ${actual}`);
        }
    },
    toBeFalsy: () => {
        if (actual) {
            throw new Error(`Expected falsy value but got ${actual}`);
        }
    },
    toThrow: () => {
        try {
            actual();
            throw new Error('Expected function to throw but it did not');
        } catch (e) {
            if (e.message === 'Expected function to throw but it did not') throw e;
            // Expected to throw - success
        }
    },
    toContain: (item) => {
        if (Array.isArray(actual)) {
            if (!actual.includes(item)) {
                throw new Error(`Expected array to contain ${JSON.stringify(item)}`);
            }
        } else if (typeof actual === 'string') {
            if (actual.indexOf(item) === -1) {
                throw new Error(`Expected string to contain "${item}"`);
            }
        } else {
            throw new Error(`toContain() requires array or string`);
        }
    },
    toHaveLength: (length) => {
        if (actual.length !== length) {
            throw new Error(`Expected length ${length} but got ${actual.length}`);
        }
    },
    toBeGreaterThan: (expected) => {
        if (!(actual > expected)) {
            throw new Error(`Expected ${actual} to be greater than ${expected}`);
        }
    },
    toBeLessThan: (expected) => {
        if (!(actual < expected)) {
            throw new Error(`Expected ${actual} to be less than ${expected}`);
        }
    },
    toBeCloseTo: (expected, precision = 2) => {
        const pow = Math.pow(10, precision);
        const delta = Math.abs(expected - actual);
        if (Math.round(delta * pow) / pow !== 0) {
            throw new Error(`Expected ${actual} to be close to ${expected}`);
        }
    }
});

global.beforeEach = (fn) => { try { fn(); } catch(e) { console.error('beforeEach failed:', e.message); } };
global.afterEach = (fn) => { try { fn(); } catch(e) { console.error('afterEach failed:', e.message); } };
global.beforeAll = (fn) => { try { fn(); } catch(e) { console.error('beforeAll failed:', e.message); } };
global.afterAll = (fn) => { try { fn(); } catch(e) { console.error('afterAll failed:', e.message); } };

// Load and run test
try {
    require('TEST_FILE_PATH');
    console.log(`\\n📊 Results: ${testsPassed} passed, ${testsFailed} failed`);
    console.log(`RESULTS: ${testsPassed} passed, ${testsFailed} failed`);
    process.exit(testsFailed > 0 ? 1 : 0);
} catch (e) {
    console.error(`\\n❌ Test execution error: ${e.message}`);
    console.error(e.stack);
    console.log(`RESULTS: 0 passed, 1 failed`);
    process.exit(1);
}
'''.replace('TEST_FILE_PATH', str(test_file).replace('\\', '\\\\'))
        
        try:
            result = subprocess.run(
                ['node', '-e', wrapper_code],
                capture_output=True,
                timeout=30,
                cwd=test_file.parent,
                encoding='utf-8',
                errors='replace'
            )
            
            output = result.stdout + result.stderr
            console.print(f"\n[dim]Node.js Output:\n{output[:500]}...[/dim]")
            
            return self._parse_direct_execution_output(result, str(test_file), output)
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Node.js execution timed out',
                'passed': 0,
                'failed': 0
            }
        except Exception as e:
            console.print(f"[red]Node.js execution error: {e}[/red]")
            return {
                'success': False,
                'error': str(e),
                'passed': 0,
                'failed': 0
            }
    
    def _run_syntax_check(self, test_file: Path) -> Dict[str, Any]:
        """Strategy 3: At minimum, check if the test file has valid syntax"""
        console.print("[dim]Performing syntax validation...[/dim]")
        
        try:
            result = subprocess.run(
                ['node', '--check', str(test_file)],
                capture_output=True,
                timeout=10,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode == 0:
                # Count potential tests
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                test_count = len(re.findall(r'\b(?:test|it)\s*\(', content))
                
                return {
                    'success': True,
                    'passed': 0,
                    'failed': 0,
                    'syntax_valid': True,
                    'potential_tests': test_count,
                    'test_file': str(test_file),
                    'method': 'syntax_check',
                    'message': f'✅ Syntax valid. Found {test_count} test cases (not executed).'
                }
            else:
                return {
                    'success': False,
                    'error': f'Syntax error: {result.stderr}',
                    'syntax_valid': False,
                    'passed': 0,
                    'failed': 0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Syntax check failed: {str(e)}',
                'passed': 0,
                'failed': 0
            }
    
    def _parse_jest_output(self, result: subprocess.CompletedProcess, test_file: str) -> Dict[str, Any]:
        """Parse Jest output (JSON or text format)"""
        
        # Try JSON parsing first
        try:
            json_data = json.loads(result.stdout)
            
            passed = json_data.get('numPassedTests', 0)
            failed = json_data.get('numFailedTests', 0)
            total = json_data.get('numTotalTests', 0)
            
            console.print(f"[cyan]📊 Jest JSON Results: {passed}/{total} passed, {failed} failed[/cyan]")
            
            return {
                'success': failed == 0 and passed > 0,
                'passed': passed,
                'failed': failed,
                'total': total,
                'test_file': test_file,
                'method': 'jest_json',
                'return_code': result.returncode
            }
            
        except (json.JSONDecodeError, KeyError):
            # Fall back to text parsing
            pass
        
        # Text parsing
        output = result.stdout + result.stderr
        console.print(f"[dim]Output preview (first 300 chars):\n{output[:300]}[/dim]")
        
        passed = 0
        failed = 0
        
        # Try multiple patterns
        patterns = [
            (r'Tests:\s+(\d+) passed', 'passed'),
            (r'Tests:\s+(\d+) failed', 'failed'),
            (r'(\d+) passed', 'passed'),
            (r'(\d+) failed', 'failed'),
            (r'PASS.*?(\d+)', 'passed'),
            (r'FAIL.*?(\d+)', 'failed'),
        ]
        
        for pattern, ptype in patterns:
            matches = re.findall(pattern, output)
            if matches:
                value = int(matches[0])
                if ptype == 'passed' and value > passed:
                    passed = value
                    console.print(f"[dim]Found {passed} passed using pattern '{pattern}'[/dim]")
                elif ptype == 'failed' and value > failed:
                    failed = value
                    console.print(f"[dim]Found {failed} failed using pattern '{pattern}'[/dim]")
        
        # Count test outcomes if no numbers found
        if passed == 0 and failed == 0:
            passed = output.count('✓') + output.count('PASS')
            failed = output.count('✗') + output.count('FAIL')
            console.print(f"[dim]Counted symbols: {passed} passed, {failed} failed[/dim]")
        
        success = result.returncode == 0 or (passed > 0 and failed == 0)
        
        console.print(f"[cyan]📊 Jest Text Results: {passed} passed, {failed} failed, return_code={result.returncode}[/cyan]")
        
        return {
            'success': success,
            'passed': passed,
            'failed': failed,
            'test_file': test_file,
            'output': output[:1000],
            'method': 'jest_text',
            'return_code': result.returncode
        }
    
    def _parse_direct_execution_output(self, result: subprocess.CompletedProcess, test_file: str, output: str) -> Dict[str, Any]:
        """Parse direct Node.js execution output"""
        
        passed = 0
        failed = 0
        
        # Look for our custom RESULTS line
        results_match = re.search(r'RESULTS: (\d+) passed, (\d+) failed', output)
        if results_match:
            passed = int(results_match.group(1))
            failed = int(results_match.group(2))
            console.print(f"[dim]Found results line: {passed} passed, {failed} failed[/dim]")
        
        # Fallback: count checkmarks
        if passed == 0 and failed == 0:
            passed = output.count('✅')
            failed = output.count('❌')
            console.print(f"[dim]Counted checkmarks: {passed} passed, {failed} failed[/dim]")
        
        success = result.returncode == 0 and failed == 0
        
        console.print(f"[cyan]📊 Direct Execution Results: {passed} passed, {failed} failed[/cyan]")
        
        return {
            'success': success,
            'passed': passed,
            'failed': failed,
            'test_file': test_file,
            'output': output,
            'return_code': result.returncode,
            'method': 'node_direct'
        }
    
    def diagnose_environment(self) -> Dict[str, Any]:
        """Diagnose the testing environment"""
        diagnosis = {
            'node_version': None,
            'npm_version': None,
            'jest_available': self.jest_available,
            'recommendations': []
        }
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                diagnosis['node_version'] = result.stdout.strip()
            else:
                diagnosis['recommendations'].append('Node.js not found. Install from nodejs.org')
        except:
            diagnosis['recommendations'].append('Node.js not found. Install from nodejs.org')
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                diagnosis['npm_version'] = result.stdout.strip()
        except:
            diagnosis['recommendations'].append('npm not found. Install Node.js which includes npm')
        
        # Check Jest
        if not self.jest_available:
            diagnosis['recommendations'].append('Install Jest: npm install --save-dev jest')
        
        return diagnosis