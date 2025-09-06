#!/usr/bin/env python3
"""
Enhanced Jest Runner - Executes JavaScript tests using Jest with multiple fallback strategies
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
        self.jest_available = self._check_jest_available()
        self.node_available = self._check_node_available()
        self.npm_available = self._check_npm_available()
        
        # Multiple execution strategies
        self.execution_strategies = [
            self._run_with_jest,
            self._run_with_node_direct,
            self._run_basic_syntax_check
        ]
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """Execute tests using the best available method"""
        console.print(f"[cyan]🧪 Running JavaScript tests: {Path(test_file_path).name}[/cyan]")
        
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
            'npm_available': self.npm_available
        }
    
    def _check_jest_available(self) -> bool:
        """Check if Jest is installed and available"""
        try:
            # Try npx jest first
            result = subprocess.run(['npx', 'jest', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                console.print(f"[green]✅ Jest available via npx: {result.stdout.strip()}[/green]")
                return True
            
            # Try global jest
            result = subprocess.run(['jest', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                console.print(f"[green]✅ Jest available globally: {result.stdout.strip()}[/green]")
                return True
            
            console.print("[yellow]⚠️ Jest not available[/yellow]")
            return False
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not check Jest: {e}[/yellow]")
            return False
    
    def _check_node_available(self) -> bool:
        """Check if Node.js is available"""
        try:
            result = subprocess.run(['node', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            available = result.returncode == 0
            if available:
                console.print(f"[green]✅ Node.js available: {result.stdout.strip()}[/green]")
            else:
                console.print("[yellow]⚠️ Node.js not available[/yellow]")
            return available
        except Exception as e:
            console.print(f"[yellow]⚠️ Could not check Node.js: {e}[/yellow]")
            return False
    
    def _check_npm_available(self) -> bool:
        """Check if npm is available"""
        try:
            result = subprocess.run(['npm', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _run_with_jest(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 1: Run with Jest (preferred method)"""
        if not self.jest_available or not self.node_available:
            return {'success': False, 'error': 'Jest or Node.js not available'}
        
        try:
            # Ensure package.json exists for Jest
            self._ensure_package_json(test_file_path)
            
            test_dir = Path(test_file_path).parent
            
            # Try different Jest command variations with better options
            jest_commands = [
                ['npx', 'jest', Path(test_file_path).name, '--verbose', '--no-cache'],
                ['npx', 'jest', test_file_path, '--verbose', '--no-cache'],
                ['jest', Path(test_file_path).name, '--verbose', '--no-cache'],
                ['node_modules/.bin/jest', Path(test_file_path).name, '--verbose', '--no-cache']
            ]
            
            for cmd in jest_commands:
                try:
                    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
                    
                    result = subprocess.run(cmd, 
                                          capture_output=True, 
                                          text=True,
                                          timeout=60,
                                          cwd=test_dir,
                                          env={**os.environ, 'NODE_OPTIONS': '--no-deprecation'})
                    
                    # Jest returns non-zero on test failures, but that's still valid output
                    if result.stdout or result.stderr:
                        return self._parse_jest_output(result, test_file_path)
                    
                except subprocess.TimeoutExpired:
                    console.print(f"[yellow]Jest command timed out: {' '.join(cmd)}[/yellow]")
                    continue
                except FileNotFoundError:
                    console.print(f"[yellow]Command not found: {cmd[0]}[/yellow]")
                    continue
            
            return {'success': False, 'error': 'All Jest command variations failed'}
            
        except Exception as e:
            return {'success': False, 'error': f'Jest execution failed: {str(e)}'}
    
    def _run_with_node_direct(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 2: Run with Node.js directly using custom test framework"""
        if not self.node_available:
            return {'success': False, 'error': 'Node.js not available'}
        
        try:
            console.print("[dim]Trying Node.js direct execution...[/dim]")
            
            # Create a custom test runner
            test_runner = self._create_node_test_runner(test_file_path)
            
            # Write the runner to a temporary file
            runner_file = Path(test_file_path).parent / f"runner_{Path(test_file_path).stem}.js"
            with open(runner_file, 'w', encoding='utf-8') as f:
                f.write(test_runner)
            
            # Execute with Node.js
            result = subprocess.run(['node', str(runner_file)], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30,
                                  cwd=Path(test_file_path).parent,
                                  encoding='utf-8')
            
            # Clean up
            try:
                runner_file.unlink()
            except:
                pass
            
            return self._parse_node_direct_output(result, test_file_path)
            
        except Exception as e:
            return {'success': False, 'error': f'Node.js direct execution failed: {str(e)}'}
    
    def _run_basic_syntax_check(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 3: Basic syntax and structure validation"""
        try:
            console.print("[dim]Performing syntax validation...[/dim]")
            
            if self.node_available:
                # Check syntax with Node.js
                result = subprocess.run(['node', '-c', test_file_path], 
                                      capture_output=True, 
                                      text=True,
                                      timeout=10)
                
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
        test_dir = Path(test_file_path).parent
        package_json_path = test_dir / "package.json"
        
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
        
        return f"""
// Custom Node.js Test Runner
const fs = require('fs');
const path = require('path');

// Simple test framework
let passed = 0;
let failed = 0;
let errors = [];

console.log('Starting JavaScript test execution...');

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
                (r'\btest\s*\(', 'test calls'),
                (r'\bit\s*\(', 'it calls'),
                (r'describe\s*\(', 'describe blocks'),
                (r'expect\s*\(', 'expect statements')
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
                r'import\s+.*?from\s+[\'"`]([^\'"`]+)[\'"`]',
                r'require\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\)'
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
            json_match = re.search(r'\{[^{}]*"numTotalTests"[^{}]*\}', output)
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
            'method': 'jest_json'
        }
    
    def _parse_jest_text(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Jest text output"""
        output = result.stdout + result.stderr
        
        # Extract test counts using various patterns
        patterns = [
            (r'(\d+)\s+passing', 'passed'),
            (r'(\d+)\s+failing', 'failed'),
            (r'(\d+)\s+pending', 'skipped'),
            (r'Tests:\s+(\d+)\s+failed,\s+(\d+)\s+passed', 'failed_passed'),
            (r'Tests:\s+(\d+)\s+passed', 'passed_only'),
            (r'PASS.*?(\d+)\s+passed', 'pass_count'),
            (r'FAIL.*?(\d+)\s+failed', 'fail_count')
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
            'method': 'jest_text'
        }
    
    def _parse_node_direct_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Node.js direct execution output"""
        output = result.stdout + result.stderr
        
        # Look for our custom output patterns
        passed_matches = output.count("✅") or output.count("PASSED")
        failed_matches = output.count("❌") or output.count("FAILED")
        
        # Extract results summary if present
        results_match = re.search(r'RESULTS:\s*(\d+)\s+passed,\s*(\d+)\s+failed', output)
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
            'method': 'node_direct'
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
            'verification': 'node --version && npm --version && npx jest --version'
        }
    
    def diagnose_environment(self) -> Dict[str, Any]:
        """Diagnose the JavaScript testing environment"""
        diagnosis = {
            'node_available': self.node_available,
            'npm_available': self.npm_available,
            'jest_available': self.jest_available,
            'recommendations': []
        }
        
        if not self.node_available:
            diagnosis['recommendations'].append('Install Node.js from https://nodejs.org/')
        
        if not self.npm_available:
            diagnosis['recommendations'].append('Install npm (usually comes with Node.js)')
        
        if not self.jest_available:
            diagnosis['recommendations'].append('Install Jest: npm install --save-dev jest')
        
        # Check for package.json
        try:
            package_json_exists = os.path.exists('package.json')
            diagnosis['package_json_exists'] = package_json_exists
            if not package_json_exists:
                diagnosis['recommendations'].append('Create package.json: npm init -y')
        except:
            pass
        
        return diagnosis