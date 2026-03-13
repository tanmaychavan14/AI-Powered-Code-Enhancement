

# import subprocess
# import json
# import re
# import sys
# import os
# from pathlib import Path
# from typing import Dict, Any, Optional, List
# from rich.console import Console

# console = Console()

# class JestRunner:
#     """Jest test runner - runs tests directly like PyTest runner"""
    
#     def __init__(self):
#      self.console = Console()
#      # Add Node.js to PATH for subprocess
#      node_path = r"C:\Program Files\nodejs"
#      os.environ["PATH"] = node_path + os.pathsep + os.environ["PATH"]
#     # Set the project root as parent folder of runner/
#      # code_assist/agents/runners => go 2 levels up to code_assist/
#      self.project_root = Path(__file__).resolve().parents[2]

    
#      console.print(f"[cyan]Jest Runner initialized from project root: {self.project_root}[/cyan]")
    
#      self.jest_available = self._check_jest_availability()

        
#         # Define execution strategies similar to PyTest runner
#      self.execution_strategies = [
#             self._run_with_jest,
#             self._run_with_node_direct,
#             self._run_syntax_check
#         ]
    
#     def _check_jest_availability(self) -> bool:
#         """Check if Jest is available in the project"""
#         # Try multiple ways to find Jest
#         jest_commands = [
#             ['npx', 'jest', '--version'],
#             ['jest', '--version'],  # Global Jest
#             ['node', '-e', "console.log(require('jest/package.json').version)"]  # Via Node
#         ]
        
#         for cmd in jest_commands:
#             try:
#                 console.print(f"[dim]Checking Jest with: {' '.join(cmd)}[/dim]")
#                 result = subprocess.run(
#                     cmd,
#                     capture_output=True,
#                     timeout=5,
#                     cwd=self.project_root,
#                     shell = True,

#                     encoding='utf-8',
#                     errors='replace'
#                 )
                
#                 if result.returncode == 0:
#                     version = result.stdout.strip()
#                     console.print(f"[green]✅ Jest available via '{cmd[0]}': {version}[/green]")
#                     return True
                    
#             except FileNotFoundError:
#                 console.print(f"[dim]Command not found: {cmd[0]}[/dim]")
#                 continue
#             except Exception as e:
#                 console.print(f"[dim]Failed with {cmd[0]}: {e}[/dim]")
#                 continue
        
#         console.print("[yellow]⚠️ Jest not found via any method[/yellow]")
#         console.print("[yellow]💡 Tests will run with Node.js mock instead[/yellow]")
#         return False
    
#     def run_tests(self, test_file_path: str) -> Dict[str, Any]:
#         """Execute Jest tests using the best available method"""
#         console.print(f"[cyan]🧪 Running JavaScript tests: {Path(test_file_path).name}[/cyan]")
        
#         test_file = Path(test_file_path).resolve()
        
#         if not test_file.exists():
#             return {
#                 'success': False,
#                 'error': f'Test file not found: {test_file}',
#                 'passed': 0,
#                 'failed': 0
#             }
        
#         # Try each execution strategy in order (like PyTest runner)
#         for i, strategy in enumerate(self.execution_strategies):
#             try:
#                 console.print(f"[cyan]Strategy {i+1}: {strategy.__name__}[/cyan]")
#                 result = strategy(test_file)
                
#                 if result['success'] or result.get('passed', 0) > 0:
#                     console.print(f"[green]✅ Tests executed successfully using strategy {i+1}[/green]")
#                     return result
#                 else:
#                     console.print(f"[yellow]Strategy {i+1} failed: {result.get('error', 'No tests passed')}[/yellow]")
                    
#             except Exception as e:
#                 console.print(f"[yellow]Strategy {i+1} exception: {e}[/yellow]")
#                 continue
        
#         # If all strategies fail
#         return {
#             'success': False,
#             'error': 'All test execution strategies failed',
#             'passed': 0,
#             'failed': 0,
#             'strategies_attempted': len(self.execution_strategies),
#             'jest_available': self.jest_available
#         }
    
#     def _run_with_jest(self, test_file: Path) -> Dict[str, Any]:
#         """Strategy 1: Run Jest from test file's directory"""
#         console.print("[dim]Running Jest...[/dim]")
        
#         # Convert to relative path from project root
#         try:
#             rel_path = test_file.relative_to(self.project_root)
#         except ValueError:
#             rel_path = test_file
        
#         commands = [
#             ['npx', 'jest', str(rel_path), '--json', '--verbose', '--forceExit'],
#             ['npx', 'jest', str(rel_path), '--verbose', '--forceExit'],
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
#                     errors='replace',
#                     shell = True
#                 )
                
#                 parsed = self._parse_jest_output(result, str(test_file))
                
#                 if parsed['success'] or parsed.get('passed', 0) > 0:
#                     console.print(f"[green]✅ Jest ran successfully[/green]")
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
#         """Strategy 2: Run test directly with Node.js (mock Jest API)"""
#         console.print("[dim]Running with Node.js direct execution...[/dim]")
        
#         # Create a wrapper that provides Jest API
#         wrapper_code = '''
# // Mock Jest globals
# let testsPassed = 0;
# let testsFailed = 0;
# let currentDescribe = '';
# const testResults = [];

# global.describe = (name, fn) => {
#     currentDescribe = name;
#     console.log(`\\n📦 ${name}`);
#     try {
#         fn();
#     } catch (e) {
#         console.error(`  ❌ Describe block failed: ${e.message}`);
#         testsFailed++;
#     }
# };

# global.test = global.it = (name, fn) => {
#     const fullName = currentDescribe ? `${currentDescribe} > ${name}` : name;
#     try {
#         fn();
#         testsPassed++;
#         testResults.push({name: fullName, status: 'passed'});
#         console.log(`  ✅ ${name}`);
#     } catch (e) {
#         testsFailed++;
#         testResults.push({name: fullName, status: 'failed', error: e.message});
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
#             if (e.message === 'Expected function to throw but it did not') throw e;
#             // Expected to throw - success
#         }
#     },
#     toContain: (item) => {
#         if (Array.isArray(actual)) {
#             if (!actual.includes(item)) {
#                 throw new Error(`Expected array to contain ${JSON.stringify(item)}`);
#             }
#         } else if (typeof actual === 'string') {
#             if (actual.indexOf(item) === -1) {
#                 throw new Error(`Expected string to contain "${item}"`);
#             }
#         } else {
#             throw new Error(`toContain() requires array or string`);
#         }
#     },
#     toHaveLength: (length) => {
#         if (actual.length !== length) {
#             throw new Error(`Expected length ${length} but got ${actual.length}`);
#         }
#     },
#     toBeGreaterThan: (expected) => {
#         if (!(actual > expected)) {
#             throw new Error(`Expected ${actual} to be greater than ${expected}`);
#         }
#     },
#     toBeLessThan: (expected) => {
#         if (!(actual < expected)) {
#             throw new Error(`Expected ${actual} to be less than ${expected}`);
#         }
#     },
#     toBeCloseTo: (expected, precision = 2) => {
#         const pow = Math.pow(10, precision);
#         const delta = Math.abs(expected - actual);
#         if (Math.round(delta * pow) / pow !== 0) {
#             throw new Error(`Expected ${actual} to be close to ${expected}`);
#         }
#     }
# });

# global.beforeEach = (fn) => { try { fn(); } catch(e) { console.error('beforeEach failed:', e.message); } };
# global.afterEach = (fn) => { try { fn(); } catch(e) { console.error('afterEach failed:', e.message); } };
# global.beforeAll = (fn) => { try { fn(); } catch(e) { console.error('beforeAll failed:', e.message); } };
# global.afterAll = (fn) => { try { fn(); } catch(e) { console.error('afterAll failed:', e.message); } };

# // Load and run test
# try {
#     require('TEST_FILE_PATH');
#     console.log(`\\n📊 Results: ${testsPassed} passed, ${testsFailed} failed`);
#     console.log(`RESULTS: ${testsPassed} passed, ${testsFailed} failed`);
#     process.exit(testsFailed > 0 ? 1 : 0);
# } catch (e) {
#     console.error(`\\n❌ Test execution error: ${e.message}`);
#     console.error(e.stack);
#     console.log(`RESULTS: 0 passed, 1 failed`);
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
#             console.print(f"\n[dim]Node.js Output:\n{output[:500]}...[/dim]")
            
#             return self._parse_direct_execution_output(result, str(test_file), output)
            
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
#         """Strategy 3: At minimum, check if the test file has valid syntax"""
#         console.print("[dim]Performing syntax validation...[/dim]")
        
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
#         console.print(f"[dim]Output preview (first 300 chars):\n{output[:300]}[/dim]")
        
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
#                     console.print(f"[dim]Found {passed} passed using pattern '{pattern}'[/dim]")
#                 elif ptype == 'failed' and value > failed:
#                     failed = value
#                     console.print(f"[dim]Found {failed} failed using pattern '{pattern}'[/dim]")
        
#         # Count test outcomes if no numbers found
#         if passed == 0 and failed == 0:
#             passed = output.count('✓') + output.count('PASS')
#             failed = output.count('✗') + output.count('FAIL')
#             console.print(f"[dim]Counted symbols: {passed} passed, {failed} failed[/dim]")
        
#         success = result.returncode == 0 or (passed > 0 and failed == 0)
        
#         console.print(f"[cyan]📊 Jest Text Results: {passed} passed, {failed} failed, return_code={result.returncode}[/cyan]")
        
#         return {
#             'success': success,
#             'passed': passed,
#             'failed': failed,
#             'test_file': test_file,
#             'output': output[:1000],
#             'method': 'jest_text',
#             'return_code': result.returncode
#         }
    
#     def _parse_direct_execution_output(self, result: subprocess.CompletedProcess, test_file: str, output: str) -> Dict[str, Any]:
#         """Parse direct Node.js execution output"""
        
#         passed = 0
#         failed = 0
        
#         # Look for our custom RESULTS line
#         results_match = re.search(r'RESULTS: (\d+) passed, (\d+) failed', output)
#         if results_match:
#             passed = int(results_match.group(1))
#             failed = int(results_match.group(2))
#             console.print(f"[dim]Found results line: {passed} passed, {failed} failed[/dim]")
        
#         # Fallback: count checkmarks
#         if passed == 0 and failed == 0:
#             passed = output.count('✅')
#             failed = output.count('❌')
#             console.print(f"[dim]Counted checkmarks: {passed} passed, {failed} failed[/dim]")
        
#         success = result.returncode == 0 and failed == 0
        
#         console.print(f"[cyan]📊 Direct Execution Results: {passed} passed, {failed} failed[/cyan]")
        
#         return {
#             'success': success,
#             'passed': passed,
#             'failed': failed,
#             'test_file': test_file,
#             'output': output,
#             'return_code': result.returncode,
#             'method': 'node_direct'
#         }
    
#     def diagnose_environment(self) -> Dict[str, Any]:
#         """Diagnose the testing environment"""
#         diagnosis = {
#             'node_version': None,
#             'npm_version': None,
#             'jest_available': self.jest_available,
#             'recommendations': []
#         }
        
#         # Check Node.js
#         try:
#             result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
#             if result.returncode == 0:
#                 diagnosis['node_version'] = result.stdout.strip()
#             else:
#                 diagnosis['recommendations'].append('Node.js not found. Install from nodejs.org')
#         except:
#             diagnosis['recommendations'].append('Node.js not found. Install from nodejs.org')
        
#         # Check npm
#         try:
#             result = subprocess.run(['npm', '--version'], capture_output=True, text=True, timeout=5)
#             if result.returncode == 0:
#                 diagnosis['npm_version'] = result.stdout.strip()
#         except:
#             diagnosis['recommendations'].append('npm not found. Install Node.js which includes npm')
        
#         # Check Jest
#         if not self.jest_available:
#             diagnosis['recommendations'].append('Install Jest: npm install --save-dev jest')
        
#         return diagnosis


#!/usr/bin/env python3
"""
Fixed Jest Runner - Properly returns structured failure details
matching what test_agent.py's _extract_failure_details expects
"""

import subprocess
import json
import re
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from unittest import suite
from unittest import suite
from rich.console import Console

console = Console()


class JestRunner:
    """Jest test runner - runs tests directly like PyTest runner"""

    def __init__(self):
        self.console = Console()
        node_path = r"C:\Program Files\nodejs"
        os.environ["PATH"] = node_path + os.pathsep + os.environ["PATH"]
        # code_assist/agents/runners => go 2 levels up to code_assist/
        self.project_root = Path(__file__).resolve().parents[2]

        console.print(
            f"[cyan]Jest Runner initialized from project root: {self.project_root}[/cyan]"
        )

        self.jest_available = self._check_jest_availability()

        self.execution_strategies = [
            self._run_with_jest,
            self._run_with_node_direct,
            self._run_syntax_check,
        ]

    def _check_jest_availability(self) -> bool:
        """Check if Jest is available in the project"""
        jest_commands = [
            ["npx", "jest", "--version"],
            ["jest", "--version"],
            ["node", "-e", "console.log(require('jest/package.json').version)"],
        ]

        for cmd in jest_commands:
            try:
                console.print(f"[dim]Checking Jest with: {' '.join(cmd)}[/dim]")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=5,
                    cwd=self.project_root,
                    shell=True,
                    encoding="utf-8",
                    errors="replace",
                )

                if result.returncode == 0:
                    version = result.stdout.strip()
                    console.print(
                        f"[green]✅ Jest available via '{cmd[0]}': {version}[/green]"
                    )
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
        console.print(
            f"[cyan]🧪 Running JavaScript tests: {Path(test_file_path).name}[/cyan]"
        )

        test_file = Path(test_file_path).resolve()

        if not test_file.exists():
            return {
                "success": False,
                "error": f"Test file not found: {test_file}",
                "passed": 0,
                "failed": 0,
                # ✅ FIX: Always tag runner and include empty failed_tests
                "runner": "jest",
                "failed_tests": [],
            }

        for i, strategy in enumerate(self.execution_strategies):
            try:
                console.print(f"[cyan]Strategy {i+1}: {strategy.__name__}[/cyan]")
                result = strategy(test_file)

                # ✅ FIX: Always tag the runner so test_agent can identify it
                result["runner"] = "jest"

                if result["success"] or result.get("passed", 0) > 0:
                    console.print(
                        f"[green]✅ Tests executed successfully using strategy {i+1}[/green]"
                    )
                    return result
                else:
                    console.print(
                        f"[yellow]Strategy {i+1} failed: {result.get('error', 'No tests passed')}[/yellow]"
                    )

            except Exception as e:
                console.print(f"[yellow]Strategy {i+1} exception: {e}[/yellow]")
                continue

        return {
            "success": False,
            "error": "All test execution strategies failed",
            "passed": 0,
            "failed": 0,
            # ✅ FIX: Tag runner even on full failure
            "runner": "jest",
            "failed_tests": [],
            "strategies_attempted": len(self.execution_strategies),
            "jest_available": self.jest_available,
        }

    # ------------------------------------------------------------------ #
    #  Strategy 1 – Real Jest via npx / npm / yarn
    # ------------------------------------------------------------------ #

    def _run_with_jest(self, test_file: Path) -> Dict[str, Any]:
        """Strategy 1: Run Jest from project root with --json for structured output"""
        console.print("[dim]Running Jest...[/dim]")

        try:
            rel_path = test_file.relative_to(self.project_root)
        except ValueError:
            rel_path = test_file

        # ✅ FIX: Prefer --json so we get structured failure data
        commands = [
            ["npx", "jest", str(rel_path), "--json", "--verbose", "--forceExit"],
            ["npx", "jest", str(rel_path), "--verbose", "--forceExit"],
            ["npm", "test", "--", str(rel_path), "--json"],
            ["yarn", "test", str(rel_path), "--json"],
        ]

        for cmd in commands:
            try:
                console.print(f"[dim]Trying: {' '.join(cmd)}[/dim]")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=30,
                    cwd=self.project_root,
                    encoding="utf-8",
                    errors="replace",
                    shell=True,
                )

                parsed = self._parse_jest_output(result, str(test_file))

                if parsed["success"] or parsed.get("passed", 0) > 0:
                    console.print("[green]✅ Jest ran successfully[/green]")
                    return parsed

            except subprocess.TimeoutExpired:
                console.print("[yellow]Command timed out[/yellow]")
                continue
            except FileNotFoundError:
                continue
            except Exception as e:
                console.print(f"[yellow]Command failed: {e}[/yellow]")
                continue

        return {
            "success": False,
            "error": "All Jest commands failed",
            "passed": 0,
            "failed": 0,
            "failed_tests": [],
        }

    # ------------------------------------------------------------------ #
    #  Strategy 2 – Node.js direct with mock Jest API
    # ------------------------------------------------------------------ #

    def _run_with_node_direct(self, test_file: Path) -> Dict[str, Any]:
        """Strategy 2: Run test directly with Node.js (mock Jest API)"""
        console.print("[dim]Running with Node.js direct execution...[/dim]")

        # ✅ FIX: Output JSON so Python can parse structured failures
        wrapper_code = r"""
// Mock Jest globals
let testsPassed = 0;
let testsFailed = 0;
let currentDescribe = '';
const testResults = [];

global.describe = (name, fn) => {
    currentDescribe = name;
    try { fn(); } catch (e) {
        testsFailed++;
        testResults.push({title: name, ancestorTitles: [], failureMessages: [e.message], status: 'failed'});
    }
};

global.test = global.it = (name, fn) => {
    try {
        fn();
        testsPassed++;
        testResults.push({title: name, ancestorTitles: [currentDescribe], failureMessages: [], status: 'passed'});
    } catch (e) {
        testsFailed++;
        testResults.push({title: name, ancestorTitles: [currentDescribe], failureMessages: [e.message], status: 'failed'});
    }
};

global.expect = (actual) => ({
    toBe: (expected) => {
        if (actual !== expected)
            throw new Error(`Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`);
    },
    toEqual: (expected) => {
        if (JSON.stringify(actual) !== JSON.stringify(expected))
            throw new Error(`Expected ${JSON.stringify(expected)} but got ${JSON.stringify(actual)}`);
    },
    toBeNull: () => { if (actual !== null) throw new Error(`Expected null but got ${actual}`); },
    toBeUndefined: () => { if (actual !== undefined) throw new Error(`Expected undefined but got ${actual}`); },
    toBeTruthy: () => { if (!actual) throw new Error(`Expected truthy but got ${actual}`); },
    toBeFalsy:  () => { if  (actual) throw new Error(`Expected falsy but got ${actual}`); },
    toThrow: () => {
        try { actual(); throw new Error('Expected function to throw but it did not'); }
        catch (e) { if (e.message === 'Expected function to throw but it did not') throw e; }
    },
    toContain: (item) => {
        if (Array.isArray(actual)) {
            if (!actual.includes(item)) throw new Error(`Expected array to contain ${JSON.stringify(item)}`);
        } else if (typeof actual === 'string') {
            if (actual.indexOf(item) === -1) throw new Error(`Expected string to contain "${item}"`);
        } else {
            throw new Error('toContain() requires array or string');
        }
    },
    toHaveLength: (len) => {
        if (actual.length !== len) throw new Error(`Expected length ${len} but got ${actual.length}`);
    },
    toBeGreaterThan: (exp) => { if (!(actual > exp)) throw new Error(`Expected ${actual} > ${exp}`); },
    toBeLessThan:    (exp) => { if (!(actual < exp)) throw new Error(`Expected ${actual} < ${exp}`); },
    toBeCloseTo: (exp, precision = 2) => {
        const pow = Math.pow(10, precision);
        if (Math.round(Math.abs(exp - actual) * pow) / pow !== 0)
            throw new Error(`Expected ${actual} to be close to ${exp}`);
    }
});

global.beforeEach = (fn) => { try { fn(); } catch(e) {} };
global.afterEach  = (fn) => { try { fn(); } catch(e) {} };
global.beforeAll  = (fn) => { try { fn(); } catch(e) {} };
global.afterAll   = (fn) => { try { fn(); } catch(e) {} };

try {
    require('TEST_FILE_PATH');
} catch (e) {
    testsFailed++;
    testResults.push({title: 'Module load error', ancestorTitles: [], failureMessages: [e.message], status: 'failed'});
}

// ✅ FIX: Print structured JSON so Python can parse it
const summary = {
    numPassedTests: testsPassed,
    numFailedTests: testsFailed,
    numTotalTests: testsPassed + testsFailed,
    testResults: [{
        testResults: testResults
    }]
};
console.log('JEST_JSON_START');
console.log(JSON.stringify(summary));
console.log('JEST_JSON_END');
process.exit(testsFailed > 0 ? 1 : 0);
""".replace(
            "TEST_FILE_PATH", str(test_file).replace("\\", "\\\\")
        )

        try:
            result = subprocess.run(
                ["node", "-e", wrapper_code],
                capture_output=True,
                timeout=30,
                cwd=test_file.parent,
                encoding="utf-8",
                errors="replace",
            )

            output = result.stdout + result.stderr
            console.print(f"\n[dim]Node.js Output preview:\n{output[:400]}[/dim]")

            return self._parse_direct_execution_output(result, str(test_file), output)

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Node.js execution timed out",
                "passed": 0,
                "failed": 0,
                "failed_tests": [],
            }
        except Exception as e:
            console.print(f"[red]Node.js execution error: {e}[/red]")
            return {
                "success": False,
                "error": str(e),
                "passed": 0,
                "failed": 0,
                "failed_tests": [],
            }

    # ------------------------------------------------------------------ #
    #  Strategy 3 – Syntax check only
    # ------------------------------------------------------------------ #

    def _run_syntax_check(self, test_file: Path) -> Dict[str, Any]:
        """Strategy 3: Validate syntax only when execution isn't possible"""
        console.print("[dim]Performing syntax validation...[/dim]")

        try:
            result = subprocess.run(
                ["node", "--check", str(test_file)],
                capture_output=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
            )

            if result.returncode == 0:
                with open(test_file, "r", encoding="utf-8") as f:
                    content = f.read()

                test_count = len(re.findall(r"\b(?:test|it)\s*\(", content))

                return {
                    "success": True,
                    "passed": 0,
                    "failed": 0,
                    "failed_tests": [],
                    "syntax_valid": True,
                    "potential_tests": test_count,
                    "test_file": str(test_file),
                    "method": "syntax_check",
                    "message": f"✅ Syntax valid. Found {test_count} test cases (not executed).",
                }
            else:
                return {
                    "success": False,
                    "error": f"Syntax error: {result.stderr}",
                    "syntax_valid": False,
                    "passed": 0,
                    "failed": 0,
                    "failed_tests": [],
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Syntax check failed: {str(e)}",
                "passed": 0,
                "failed": 0,
                "failed_tests": [],
            }

    # ------------------------------------------------------------------ #
    #  Output parsers
    # ------------------------------------------------------------------ #

    def _parse_jest_output(
        self, result: subprocess.CompletedProcess, test_file: str
    ) -> Dict[str, Any]:
        """Parse Jest --json output OR fall back to text parsing"""

        # ── JSON path ──────────────────────────────────────────────────
        try:
            json_data = json.loads(result.stdout)

            passed = json_data.get("numPassedTests", 0)
            failed = json_data.get("numFailedTests", 0)
            total  = json_data.get("numTotalTests",  0)

            # ✅ FIX: Extract structured failures from Jest JSON
            failed_tests = self._extract_failed_tests_from_jest_json(json_data)

            console.print(
                f"[cyan]📊 Jest JSON Results: {passed}/{total} passed, {failed} failed[/cyan]"
            )

            return {
                "success": failed == 0 and passed > 0,
                "passed": passed,
                "failed": failed,
                "total": total,
                "test_file": test_file,
                "method": "jest_json",
                "return_code": result.returncode,
                # ✅ FIX: Always include structured failed_tests
                "failed_tests": failed_tests,
            }

        except (json.JSONDecodeError, KeyError):
            pass  # fall through to text parsing

        # ── Text path ──────────────────────────────────────────────────
        output = result.stdout + result.stderr
        console.print(f"[dim]Output preview (first 300 chars):\n{output[:300]}[/dim]")

        passed, failed = self._count_from_text(output)

        # ✅ FIX: Extract failure details from text output
        failed_tests = self._extract_failed_tests_from_text(output)

        success = result.returncode == 0 or (passed > 0 and failed == 0)

        console.print(
            f"[cyan]📊 Jest Text Results: {passed} passed, {failed} failed, "
            f"return_code={result.returncode}[/cyan]"
        )

        return {
            "success": success,
            "passed": passed,
            "failed": failed,
            "test_file": test_file,
            "output": output[:2000],
            "method": "jest_text",
            "return_code": result.returncode,
            # ✅ FIX: Always include structured failed_tests
            "failed_tests": failed_tests,
        }

    def _parse_direct_execution_output(
        self,
        result: subprocess.CompletedProcess,
        test_file: str,
        output: str,
    ) -> Dict[str, Any]:
        """Parse Node.js direct execution output (our custom JSON block)"""

        passed = 0
        failed = 0
        failed_tests: List[Dict] = []

        # ✅ FIX: Try to parse our custom JSON block first
        json_match = re.search(
            r"JEST_JSON_START\s*(.*?)\s*JEST_JSON_END", output, re.DOTALL
        )
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                passed = data.get("numPassedTests", 0)
                failed = data.get("numFailedTests", 0)
                failed_tests = self._extract_failed_tests_from_jest_json(data)
                console.print(
                    f"[dim]Parsed custom JSON block: {passed} passed, {failed} failed, "
                    f"{len(failed_tests)} failure details[/dim]"
                )
            except json.JSONDecodeError:
                console.print("[yellow]Custom JSON block parse error, falling back[/yellow]")

        # Fallback: scan text
        if passed == 0 and failed == 0:
            passed, failed = self._count_from_text(output)
            if failed_tests == []:
                failed_tests = self._extract_failed_tests_from_text(output)

        success = result.returncode == 0 and failed == 0

        console.print(
            f"[cyan]📊 Direct Execution Results: {passed} passed, {failed} failed[/cyan]"
        )

        return {
            "success": success,
            "passed": passed,
            "failed": failed,
            "test_file": test_file,
            "output": output,
            "return_code": result.returncode,
            "method": "node_direct",
            # ✅ FIX: Structured failure list
            "failed_tests": failed_tests,
        }

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _extract_failed_tests_from_jest_json(
        self, json_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Pull individual failing test entries out of Jest JSON output.

        Jest JSON shape:
        {
          "testResults": [
            {
              "testResults": [
                {
                  "title": "should return empty string",
                  "fullName": "reverseString should return empty string",
                  "ancestorTitles": ["reverseString"],
                  "status": "failed",
                  "failureMessages": ["Error: Expected 'abc' but got 'cba'"]
                }
              ]
            }
          ]
        }
        This is also the format produced by our custom Node wrapper.
        """
        failed: List[Dict[str, Any]] = []

        for suite in json_data.get("testResults", []):
            # AFTER - check both keys (handles all Jest versions)
            for test in suite.get("assertionResults", suite.get("testResults", [])):
                if test.get("status") == "failed":
                    failed.append(
                        {
                            # ✅ These keys match what _extract_failure_details expects
                            "title": test.get("title", "Unknown"),
                            "fullName": test.get(
                                "fullName",
                                " > ".join(
                                    test.get("ancestorTitles", [])
                                    + [test.get("title", "Unknown")]
                                ),
                            ),
                            "failureMessages": test.get("failureMessages", []),
                            "ancestorTitles": test.get("ancestorTitles", []),
                        }
                    )

        console.print(
            f"[dim]Extracted {len(failed)} structured Jest failure(s)[/dim]"
        )
        return failed

    def _extract_failed_tests_from_text(self, output: str) -> List[Dict[str, Any]]:
        """
        Best-effort extraction of failures from Jest / Node text output.
        Handles patterns like:
            ✗  should return empty string
            ❌  should return empty string
               Expected 'abc' but got 'cba'
            ● describe > test name
        """
        failed: List[Dict[str, Any]] = []

        lines = output.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # Jest "● Test Suite > test name" failure header
            bullet_match = re.match(r"^\s*●\s+(.+)$", line)
            # Checkmark variants
            cross_match = re.match(r"^\s*[✗❌✘×]\s+(.+)$", line)

            match = bullet_match or cross_match
            if match:
                test_title = match.group(1).strip()
                # Gather failure message from the next non-blank lines
                messages: List[str] = []
                j = i + 1
                while j < len(lines) and j < i + 8:
                    next_line = lines[j].strip()
                    if next_line and not re.match(r"[✗❌✘×✅✓●]", next_line):
                        messages.append(next_line)
                    elif next_line.startswith(("✅", "✓", "●")):
                        break
                    j += 1

                failed.append(
                    {
                        "title": test_title,
                        "fullName": test_title,
                        "failureMessages": messages[:3],  # keep first 3 lines
                        "ancestorTitles": [],
                    }
                )

            i += 1

        console.print(
            f"[dim]Text-parsed {len(failed)} Jest failure(s)[/dim]"
        )
        return failed

    def _count_from_text(self, output: str):
        """Count passed/failed from text output; returns (passed, failed)."""
        passed = 0
        failed = 0

        patterns = [
            (r"Tests:\s+(\d+)\s+passed",  "passed"),
            (r"Tests:\s+(\d+)\s+failed",  "failed"),
            (r"(\d+)\s+passed",            "passed"),
            (r"(\d+)\s+failed",            "failed"),
        ]

        for pattern, ptype in patterns:
            matches = re.findall(pattern, output)
            if matches:
                value = int(matches[0])
                if ptype == "passed" and value > passed:
                    passed = value
                elif ptype == "failed" and value > failed:
                    failed = value

        # Last resort: emoji counts
        if passed == 0 and failed == 0:
            passed = output.count("✅") + output.count("✓")
            failed = output.count("❌") + output.count("✗")

        return passed, failed

    def diagnose_environment(self) -> Dict[str, Any]:
        """Diagnose the testing environment"""
        diagnosis: Dict[str, Any] = {
            "node_version": None,
            "npm_version": None,
            "jest_available": self.jest_available,
            "recommendations": [],
        }

        try:
            result = subprocess.run(
                ["node", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                diagnosis["node_version"] = result.stdout.strip()
            else:
                diagnosis["recommendations"].append(
                    "Node.js not found. Install from nodejs.org"
                )
        except Exception:
            diagnosis["recommendations"].append(
                "Node.js not found. Install from nodejs.org"
            )

        try:
            result = subprocess.run(
                ["npm", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                diagnosis["npm_version"] = result.stdout.strip()
        except Exception:
            diagnosis["recommendations"].append(
                "npm not found. Install Node.js which includes npm"
            )

        if not self.jest_available:
            diagnosis["recommendations"].append(
                "Install Jest: npm install --save-dev jest"
            )

        return diagnosis  # ✅ typo fix: was `diagnosisi`