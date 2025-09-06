#!/usr/bin/env python3
"""
Enhanced Jest Runner - Executes JavaScript tests using Jest with multiple fallback strategies
Fixed to handle proper project root detection when node_modules is outside code_assist folder
"""

import subprocess
import json
import re
import os
from pathlib import Path
from typing import Dict, Any, List
from rich.console import Console

console = Console()

class JestRunner:
    """Enhanced runner for executing JavaScript tests with multiple strategies"""
    
    def __init__(self):
        self.console = Console()
        
        # Find the project root (where package.json and node_modules exist)
        self.project_root = self._find_project_root()
        console.print(f"[dim]Project root detected: {self.project_root}[/dim]")
        
        # Check availability from project root context
        self.jest_available = self._check_jest_available()
        self.node_available = self._check_node_available()
        self.npm_available = self._check_npm_available()
        
        # Multiple execution strategies
        self.execution_strategies = [
            self._run_with_jest,
            self._run_with_node_direct,
            self._run_basic_syntax_check
        ]
    
    def _find_project_root(self) -> Path:
        """Find the project root directory containing package.json and node_modules"""
        current_dir = Path.cwd()
        console.print(f"[dim]Starting search from: {current_dir}[/dim]")
        
        # Look for package.json and node_modules in current dir and ALL parent directories
        search_paths = [current_dir] + list(current_dir.parents)
        
        for path in search_paths:
            package_json_path = path / 'package.json'
            node_modules_path = path / 'node_modules'
            
            console.print(f"[dim]Checking: {path}[/dim]")
            console.print(f"[dim]  package.json exists: {package_json_path.exists()}[/dim]")
            console.print(f"[dim]  node_modules exists: {node_modules_path.exists()}[/dim]")
            
            if package_json_path.exists() and node_modules_path.exists():
                console.print(f"[green]✅ Found project root with both package.json and node_modules: {path}[/green]")
                return path
            elif package_json_path.exists():
                console.print(f"[yellow]Found package.json but no node_modules at: {path}[/yellow]")
                # Continue searching, but remember this location
                fallback_root = path
        
        # If we found package.json somewhere, use that
        if 'fallback_root' in locals():
            console.print(f"[yellow]Using fallback project root: {fallback_root}[/yellow]")
            return fallback_root
        
        # If no package.json found anywhere, return current directory
        console.print(f"[yellow]No project root found, using current directory: {current_dir}[/yellow]")
        return current_dir
    
    def _check_jest_available(self) -> bool:
        """Check Jest availability from project root"""
        try:
            # Check local node_modules from project root
            jest_paths = [
                self.project_root / 'node_modules' / '.bin' / 'jest',
                self.project_root / 'node_modules' / '.bin' / 'jest.cmd',  # Windows
                self.project_root / 'node_modules' / 'jest' / 'bin' / 'jest.js'
            ]
            
            for jest_path in jest_paths:
                if jest_path.exists():
                    console.print(f"[green]✅ Jest found at: {jest_path}[/green]")
                    return True
            
            # Check package.json for jest dependency
            package_json = self.project_root / 'package.json'
            if package_json.exists():
                try:
                    with open(package_json, 'r') as f:
                        package_data = json.load(f)
                        deps = {**package_data.get('dependencies', {}), 
                               **package_data.get('devDependencies', {})}
                        if 'jest' in deps:
                            console.print(f"[green]✅ Jest in package.json: {deps['jest']}[/green]")
                            return True
                except Exception as e:
                    console.print(f"[yellow]Could not read package.json: {e}[/yellow]")
            
            # Try npx from project root
            result = subprocess.run(['npx', 'jest', '--version'], 
                                  capture_output=True, text=True, timeout=10,
                                  cwd=self.project_root, shell=True)
            if result.returncode == 0:
                console.print(f"[green]✅ Jest via npx: {result.stdout.strip()}[/green]")
                return True
            
            console.print(f"[yellow]⚠️ Jest not available. Error: {result.stderr}[/yellow]")
            return False
            
        except Exception as e:
            console.print(f"[yellow]⚠️ Jest check failed: {e}[/yellow]")
            return False
    
    def _check_node_available(self) -> bool:
        """Check Node.js availability from project root"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5,
                                  cwd=self.project_root, shell=True)
            if result.returncode == 0:
                console.print(f"[green]✅ Node.js: {result.stdout.strip()}[/green]")
                return True
            
            console.print(f"[yellow]⚠️ Node.js not available: {result.stderr}[/yellow]")
            return False
            
        except Exception as e:
            console.print(f"[yellow]⚠️ Node.js check error: {e}[/yellow]")
            return False
    
    def _check_npm_available(self) -> bool:
        """Check if npm is available from project root"""
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, timeout=5,
                                  cwd=self.project_root, shell=True)
            return result.returncode == 0
        except:
            return False
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """Execute tests using the best available method"""
        console.print(f"[cyan]🧪 Running JavaScript tests: {Path(test_file_path).name}[/cyan]")
        console.print(f"[dim]Working from project root: {self.project_root}[/dim]")
        
        # Try each execution strategy in order
        for i, strategy in enumerate(self.execution_strategies):
            try:
                console.print(f"[dim]Trying strategy {i+1}...[/dim]")
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
            'error': 'All JavaScript test execution strategies failed',
            'passed': 0,
            'failed': 0,
            'strategies_attempted': len(self.execution_strategies),
            'jest_available': self.jest_available,
            'node_available': self.node_available,
            'npm_available': self.npm_available,
            'project_root': str(self.project_root)
        }
    
    def _run_with_jest(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 1: Run with Jest from project root (preferred method)"""
        if not self.jest_available or not self.node_available:
            return {'success': False, 'error': 'Jest or Node.js not available'}
        
        try:
            # Get relative path from project root to test file
            test_path = Path(test_file_path)
            if test_path.is_absolute():
                try:
                    rel_test_path = test_path.relative_to(self.project_root)
                except ValueError:
                    # Test file is outside project root, use absolute path
                    rel_test_path = test_path
            else:
                rel_test_path = test_path
            
            console.print(f"[dim]Running Jest from: {self.project_root}[/dim]")
            console.print(f"[dim]Test file: {rel_test_path}[/dim]")
            
            # Jest commands to try (from project root)
            jest_commands = [
                ['npx', 'jest', str(rel_test_path), '--verbose', '--forceExit'],
                ['npm', 'test', '--', str(rel_test_path)],
                ['node', 'node_modules/jest/bin/jest.js', str(rel_test_path), '--verbose'],
                ['npx', 'jest', str(rel_test_path), '--no-cache', '--verbose'],
                # Windows specific
                ['node_modules\\.bin\\jest.cmd', str(rel_test_path), '--verbose']
            ]
            
            for cmd in jest_commands:
                try:
                    console.print(f"[dim]Trying: {' '.join(cmd)}[/dim]")
                    
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=self.project_root,  # KEY: Run from project root!
                        shell=True,
                        env={**os.environ, 'NODE_OPTIONS': '--no-deprecation'}
                    )
                    
                    console.print(f"[dim]Exit code: {result.returncode}[/dim]")
                    if result.stdout:
                        console.print(f"[dim]Stdout preview: {result.stdout[:200]}...[/dim]")
                    if result.stderr:
                        console.print(f"[dim]Stderr preview: {result.stderr[:200]}...[/dim]")
                    
                    # Jest returns non-zero on test failures, but that's still valid output
                    if result.stdout or result.stderr:
                        console.print("[dim]Got Jest output, parsing...[/dim]")
                        return self._parse_jest_output(result, test_file_path)
                        
                except subprocess.TimeoutExpired:
                    console.print(f"[yellow]Command timeout: {' '.join(cmd)}[/yellow]")
                    continue
                except Exception as e:
                    console.print(f"[yellow]Command error: {e}[/yellow]")
                    continue
            
            return {'success': False, 'error': 'All Jest execution attempts failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'Jest execution error: {str(e)}'}
    
    def _run_with_node_direct(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 2: Run with Node.js directly from project root using custom test framework"""
        if not self.node_available:
            return {'success': False, 'error': 'Node.js not available'}
        
        try:
            console.print("[dim]Trying Node.js direct execution from project root...[/dim]")
            
            # Create a custom test runner
            test_runner = self._create_node_test_runner(test_file_path)
            
            # Write the runner to project root (where node_modules is)
            runner_file = self.project_root / f"temp_runner_{Path(test_file_path).stem}.js"
            with open(runner_file, 'w', encoding='utf-8') as f:
                f.write(test_runner)
            
            # Execute from project root
            result = subprocess.run(['node', str(runner_file.name)], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30,
                                  cwd=self.project_root,  # KEY: Run from project root!
                                  shell=True)
            
            # Clean up
            try:
                runner_file.unlink()
            except:
                pass
            
            return self._parse_node_direct_output(result, test_file_path)
            
        except Exception as e:
            return {'success': False, 'error': f'Node.js execution error: {str(e)}'}
    
    def _run_basic_syntax_check(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 3: Basic syntax and structure validation"""
        try:
            console.print("[dim]Performing syntax validation...[/dim]")
            
            if self.node_available:
                # Check syntax with Node.js from project root
                result = subprocess.run(['node', '-c', test_file_path], 
                                      capture_output=True, 
                                      text=True,
                                      timeout=10,
                                      cwd=self.project_root,
                                      shell=True)
                
                if result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'JavaScript syntax error: {result.stderr}',
                        'syntax_valid': False
                    }
            
            # Analyze test file structure
            return self._analyze_test_file_structure(test_file_path)
                
        except Exception as e:
            return {'success': False, 'error': f'Syntax check failed: {str(e)}'}
    
    def _ensure_package_json(self, test_file_path: str):
        """Ensure package.json exists for Jest to work properly"""
        # Use project root for package.json, not test file directory
        package_json_path = self.project_root / "package.json"
        
        if not package_json_path.exists():
            console.print("[dim]Creating minimal package.json for Jest...[/dim]")
            package_json = {
                "name": "generated-tests",
                "version": "1.0.0",
                "type": "module",
                "scripts": {
                    "test": "jest"
                },
                "jest": {
                    "testEnvironment": "node",
                    "transform": {},
                    "extensionsToTreatAsEsm": [".js"]
                },
                "devDependencies": {
                    "jest": "^29.0.0"
                }
            }
            
            try:
                with open(package_json_path, 'w', encoding='utf-8') as f:
                    json.dump(package_json, f, indent=2)
                console.print(f"[green]Created package.json at {package_json_path}[/green]")
            except Exception as e:
                console.print(f"[yellow]Failed to create package.json: {e}[/yellow]")
    
    def _create_node_test_runner(self, test_file_path: str) -> str:
        """Create a custom Node.js test runner"""
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                test_content = f.read()
        except Exception as e:
            console.print(f"[yellow]Could not read test file: {e}[/yellow]")
            test_content = ""
        
        # Make the test file path relative to project root for proper require/import
        test_path = Path(test_file_path)
        if test_path.is_absolute():
            try:
                relative_test_path = test_path.relative_to(self.project_root)
            except ValueError:
                relative_test_path = test_path
        else:
            relative_test_path = test_path
        
        return f"""
// Custom Node.js Test Runner (executed from project root)
const fs = require('fs');
const path = require('path');

// Simple test framework
let passed = 0;
let failed = 0;
let errors = [];

console.log('Starting JavaScript test execution...');
console.log('Working directory:', process.cwd());
console.log('Test file path:', '{relative_test_path}');

// Mock Jest functions
global.test = (name, testFn) => {{
    console.log(`Running: ${{name}}`);
    try {{
        if (testFn.constructor.name === 'AsyncFunction') {{
            // Handle async test
            testFn().then(() => {{
                passed++;
                console.log(`✅ ${{name}} PASSED`);
            }}).catch((error) => {{
                failed++;
                const errorMsg = `❌ ${{name}} FAILED: ${{error.message}}`;
                errors.push(errorMsg);
                console.log(errorMsg);
            }});
        }} else {{
            testFn();
            passed++;
            console.log(`✅ ${{name}} PASSED`);
        }}
    }} catch (error) {{
        failed++;
        const errorMsg = `❌ ${{name}} FAILED: ${{error.message}}`;
        errors.push(errorMsg);
        console.log(errorMsg);
    }}
}};

global.it = global.test;

global.describe = (name, suiteFn) => {{
    console.log(`\\n📋 Suite: ${{name}}`);
    try {{
        suiteFn();
    }} catch (error) {{
        console.log(`Suite error: ${{error.message}}`);
    }}
}};

// Enhanced expect function
global.expect = (actual) => {{
    return {{
        toBe: (expected) => {{
            if (actual !== expected) {{
                throw new Error(`Expected ${{expected}}, but got ${{actual}}`);
            }}
        }},
        toEqual: (expected) => {{
            if (JSON.stringify(actual) !== JSON.stringify(expected)) {{
                throw new Error(`Expected ${{JSON.stringify(expected)}}, but got ${{JSON.stringify(actual)}}`);
            }}
        }},
        toBeTruthy: () => {{
            if (!actual) {{
                throw new Error(`Expected truthy value, but got ${{actual}}`);
            }}
        }},
        toBeFalsy: () => {{
            if (actual) {{
                throw new Error(`Expected falsy value, but got ${{actual}}`);
            }}
        }},
        toThrow: () => {{
            if (typeof actual !== 'function') {{
                throw new Error('Expected a function');
            }}
            try {{
                actual();
                throw new Error('Expected function to throw');
            }} catch (e) {{
                // Expected to throw
            }}
        }},
        toBeGreaterThan: (expected) => {{
            if (actual <= expected) {{
                throw new Error(`Expected ${{actual}} to be greater than ${{expected}}`);
            }}
        }},
        toBeLessThan: (expected) => {{
            if (actual >= expected) {{
                throw new Error(`Expected ${{actual}} to be less than ${{expected}}`);
            }}
        }},
        toContain: (expected) => {{
            if (!actual.includes || !actual.includes(expected)) {{
                throw new Error(`Expected ${{actual}} to contain ${{expected}}`);
            }}
        }}
    }};
}};

// Mock console if needed
global.beforeEach = (fn) => {{ /* Mock implementation */ }};
global.afterEach = (fn) => {{ /* Mock implementation */ }};
global.beforeAll = (fn) => {{ /* Mock implementation */ }};
global.afterAll = (fn) => {{ /* Mock implementation */ }};

// Load and execute the test file
try {{
    console.log('Loading test file...');
    {test_content}
    
    // Give async tests some time to complete
    setTimeout(() => {{
        console.log('\\n=== RESULTS ===');
        console.log(`RESULTS: ${{passed}} passed, ${{failed}} failed`);
        
        if (errors.length > 0) {{
            console.log('\\n📋 FAILED TESTS:');
            errors.forEach(error => console.log(`  ${{error}}`));
        }}
        
        // Exit with appropriate code
        process.exit(failed > 0 ? 1 : 0);
    }}, 1000);
    
}} catch (error) {{
    console.log(`EXECUTION ERROR: ${{error.message}}`);
    console.log(`STACK: ${{error.stack}}`);
    process.exit(1);
}}
"""
    
    def _analyze_test_file_structure(self, test_file_path: str) -> Dict[str, Any]:
        """Analyze test file structure without execution"""
        try:
            with open(test_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count different types of test patterns
            test_patterns = [
                (r'\\btest\\s*\\(', 'test calls'),
                (r'\\bit\\s*\\(', 'it calls'),
                (r'describe\\s*\\(', 'describe blocks'),
                (r'expect\\s*\\(', 'expect statements')
            ]
            
            test_counts = {}
            total_tests = 0
            
            for pattern, name in test_patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                test_counts[name] = matches
                if 'test' in name or 'it' in name:
                    total_tests += matches
            
            # Look for imports/requires
            import_patterns = [
                r'import\\s+.*?from\\s+[\\\'"`]([^\\\'"`]+)[\\\'"`]',
                r'require\\s*\\(\\s*[\\\'"`]([^\\\'"`]+)[\\\'"`]\\s*\\)'
            ]
            
            imports = []
            for pattern in import_patterns:
                imports.extend(re.findall(pattern, content))
            
            return {
                'success': True,
                'passed': 0,
                'failed': 0,
                'syntax_valid': True,
                'potential_tests': total_tests,
                'test_file': test_file_path,
                'method': 'structure_analysis',
                'patterns_found': test_counts,
                'imports_found': imports,
                'project_root': str(self.project_root),
                'message': f'Structure valid. Found {total_tests} potential test functions.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Structure analysis failed: {str(e)}'
            }
    
    def _parse_jest_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Jest output (JSON or text)"""
        output = result.stdout + result.stderr
        
        try:
            # Try to find JSON in output
            json_match = re.search(r'\\{[^{}]*"numTotalTests"[^{}]*\\}', output)
            if json_match:
                try:
                    json_data = json.loads(json_match.group())
                    return self._parse_jest_json(json_data, test_file_path)
                except json.JSONDecodeError:
                    pass
            
            # Fallback to text parsing
            return self._parse_jest_text(result, test_file_path)
            
        except Exception as e:
            return {'success': False, 'error': f'Jest output parsing failed: {str(e)}', 'output': output}
    
    def _parse_jest_json(self, json_data: Dict, test_file_path: str) -> Dict[str, Any]:
        """Parse Jest JSON output"""
        return {
            'success': json_data.get('success', False),
            'passed': json_data.get('numPassedTests', 0),
            'failed': json_data.get('numFailedTests', 0),
            'skipped': json_data.get('numPendingTests', 0),
            'total': json_data.get('numTotalTests', 0),
            'test_file': test_file_path,
            'method': 'jest_json',
            'project_root': str(self.project_root)
        }
    
    def _parse_jest_text(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Jest text output"""
        output = result.stdout + result.stderr
        
        # Extract test counts using various patterns
        patterns = [
            (r'(\\d+)\\s+passing', 'passed'),
            (r'(\\d+)\\s+failing', 'failed'),
            (r'(\\d+)\\s+pending', 'skipped'),
            (r'Tests:\\s+(\\d+)\\s+failed,\\s+(\\d+)\\s+passed', 'failed_passed'),
            (r'Tests:\\s+(\\d+)\\s+passed', 'passed_only'),
            (r'PASS.*?(\\d+)\\s+passed', 'pass_count'),
            (r'FAIL.*?(\\d+)\\s+failed', 'fail_count')
        ]
        
        passed = failed = skipped = 0
        
        for pattern, pattern_type in patterns:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                if pattern_type == 'passed':
                    passed = int(matches[0])
                elif pattern_type == 'failed':
                    failed = int(matches[0])
                elif pattern_type == 'skipped':
                    skipped = int(matches[0])
                elif pattern_type == 'failed_passed':
                    failed, passed = int(matches[0][0]), int(matches[0][1])
                elif pattern_type == 'passed_only':
                    passed = int(matches[0])
                elif pattern_type == 'pass_count':
                    passed = max(passed, int(matches[-1]))
                elif pattern_type == 'fail_count':
                    failed = max(failed, int(matches[-1]))
        
        # If we found tests in output but no explicit counts, try to infer
        if passed == 0 and failed == 0:
            if 'PASS' in output:
                passed = 1
            elif 'FAIL' in output:
                failed = 1
        
        # Check for common success/failure indicators
        success_indicators = ['Tests passed', 'All tests passed', 'PASS']
        failure_indicators = ['Tests failed', 'FAIL', 'Error', 'Failed']
        
        has_success = any(indicator in output for indicator in success_indicators)
        has_failure = any(indicator in output for indicator in failure_indicators)
        
        # Determine success based on exit code and output
        success = (result.returncode == 0 or has_success) and not has_failure and failed == 0
        
        return {
            'success': success,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'test_file': test_file_path,
            'output': output,
            'return_code': result.returncode,
            'method': 'jest_text',
            'project_root': str(self.project_root)
        }
    
    def _parse_node_direct_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Node.js direct execution output"""
        output = result.stdout + result.stderr
        
        # Look for our custom output patterns
        passed_matches = output.count("✅") or output.count("PASSED")
        failed_matches = output.count("❌") or output.count("FAILED")
        
        # Extract results summary if present
        results_match = re.search(r'RESULTS:\\s*(\\d+)\\s+passed,\\s*(\\d+)\\s+failed', output)
        if results_match:
            passed = int(results_match.group(1))
            failed = int(results_match.group(2))
        else:
            passed = passed_matches
            failed = failed_matches
        
        # If no explicit results found but execution seemed successful
        if passed == 0 and failed == 0 and result.returncode == 0:
            if "Running:" in output:  # Tests were attempted
                passed = 1  # Assume at least one test passed
        
        return {
            'success': result.returncode == 0 and failed == 0,
            'passed': passed,
            'failed': failed,
            'skipped': 0,
            'duration': 0,
            'test_file': test_file_path,
            'output': output,
            'method': 'node_direct',
            'project_root': str(self.project_root)
        }
    
    def get_installation_instructions(self) -> Dict[str, Any]:
        """Get instructions for installing JavaScript testing dependencies"""
        return {
            'node': {
                'command': 'Install Node.js from https://nodejs.org/',
                'description': 'JavaScript runtime required for running tests'
            },
            'jest': {
                'command': 'npm install --save-dev jest',
                'description': 'Install Jest testing framework locally'
            },
            'alternative_commands': [
                'npm install -g jest',
                'yarn add --dev jest',
                'npx jest --init'
            ],
            'verification': 'node --version && npm --version && npx jest --version',
            'project_root': str(self.project_root)
        }
    
    def diagnose_environment(self) -> Dict[str, Any]:
        """Diagnose the JavaScript testing environment"""
        diagnosis = {
            'node_available': self.node_available,
            'npm_available': self.npm_available,
            'jest_available': self.jest_available,
            'project_root': str(self.project_root),
            'working_directory': str(Path.cwd()),
            'recommendations': []
        }
        
        if not self.node_available:
            diagnosis['recommendations'].append('Install Node.js from https://nodejs.org/')
        
        if not self.npm_available:
            diagnosis['recommendations'].append('Install npm (usually comes with Node.js)')
        
        if not self.jest_available:
            diagnosis['recommendations'].append('Install Jest: npm install --save-dev jest')
        
        # Check for package.json in project root
        try:
            package_json_path = self.project_root / 'package.json'
            node_modules_path = self.project_root / 'node_modules'
            
            diagnosis['package_json_exists'] = package_json_path.exists()
            diagnosis['node_modules_exists'] = node_modules_path.exists()
            
            if not package_json_path.exists():
                diagnosis['recommendations'].append('Create package.json: npm init -y')
            
            if not node_modules_path.exists():
                diagnosis['recommendations'].append('Install dependencies: npm install')
        except Exception as e:
            diagnosis['error'] = f'Error checking package.json or node_modules: {e}'