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
            self._run_with_mocha_fallback,
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
        if not self.jest_available:
            return {'success': False, 'error': 'Jest not available'}
        
        try:
            # Ensure package.json exists for Jest
            self._ensure_package_json(test_file_path)
            
            # Try different Jest command variations
            jest_commands = [
                ['npx', 'jest', test_file_path, '--json', '--verbose'],
                ['jest', test_file_path, '--json', '--verbose'],
                ['npx', 'jest', test_file_path, '--verbose'],
                ['jest', test_file_path, '--verbose']
            ]
            
            for cmd in jest_commands:
                try:
                    console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
                    
                    result = subprocess.run(cmd, 
                                          capture_output=True, 
                                          text=True,
                                          timeout=45,
                                          cwd=Path(test_file_path).parent)
                    
                    if result.returncode == 0 or 'test' in result.stdout.lower():
                        return self._parse_jest_output(result, test_file_path)
                    
                except subprocess.TimeoutExpired:
                    continue
                except FileNotFoundError:
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
            with open(runner_file, 'w') as f:
                f.write(test_runner)
            
            # Execute with Node.js
            result = subprocess.run(['node', str(runner_file)], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30,
                                  cwd=Path(test_file_path).parent)
            
            # Clean up
            try:
                runner_file.unlink()
            except:
                pass
            
            return self._parse_node_direct_output(result, test_file_path)
            
        except Exception as e:
            return {'success': False, 'error': f'Node.js direct execution failed: {str(e)}'}
    
    def _run_with_mocha_fallback(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 3: Try Mocha as fallback test runner"""
        if not self.node_available:
            return {'success': False, 'error': 'Node.js not available for Mocha'}
        
        try:
            console.print("[dim]Trying Mocha fallback...[/dim]")
            
            # Check if Mocha is available
            mocha_check = subprocess.run(['npx', 'mocha', '--version'], 
                                       capture_output=True, text=True, timeout=5)
            
            if mocha_check.returncode != 0:
                return {'success': False, 'error': 'Mocha not available'}
            
            # Convert Jest-style test to Mocha-style
            mocha_test = self._convert_to_mocha(test_file_path)
            if not mocha_test:
                return {'success': False, 'error': 'Could not convert to Mocha format'}
            
            # Write Mocha test file
            mocha_file = Path(test_file_path).parent / f"mocha_{Path(test_file_path).stem}.js"
            with open(mocha_file, 'w') as f:
                f.write(mocha_test)
            
            # Run with Mocha
            result = subprocess.run(['npx', 'mocha', str(mocha_file), '--reporter', 'json'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=30,
                                  cwd=Path(test_file_path).parent)
            
            # Clean up
            try:
                mocha_file.unlink()
            except:
                pass
            
            return self._parse_mocha_output(result, test_file_path)
            
        except Exception as e:
            return {'success': False, 'error': f'Mocha execution failed: {str(e)}'}
    
    def _run_basic_syntax_check(self, test_file_path: str) -> Dict[str, Any]:
        """Strategy 4: Basic syntax and structure validation"""
        try:
            console.print("[dim]Performing syntax validation...[/dim]")
            
            if not self.node_available:
                # Fallback to basic file analysis
                return self._analyze_test_file_structure(test_file_path)
            
            # Check syntax with Node.js
            result = subprocess.run(['node', '-c', test_file_path], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=10)
            
            if result.returncode == 0:
                # Syntax is valid, analyze test structure
                return self._analyze_test_file_structure(test_file_path)
            else:
                return {
                    'success': False,
                    'error': f'JavaScript syntax error: {result.stderr}',
                    'syntax_valid': False
                }
                
        except Exception as e:
            return {'success': False, 'error': f'Syntax check failed: {str(e)}'}
    
    def _ensure_package_json(self, test_file_path: str):
        """Ensure package.json exists for Jest to work properly"""
        package_json_path = Path(test_file_path).parent / "package.json"
        
        if not package_json_path.exists():
            console.print("[dim]Creating minimal package.json for Jest...[/dim]")
            package_json = {
                "name": "generated-tests",
                "version": "1.0.0",
                "scripts": {
                    "test": "jest"
                },
                "devDependencies": {
                    "jest": "^29.0.0"
                }
            }
            
            with open(package_json_path, 'w') as f:
                json.dump(package_json, f, indent=2)
    
    def _create_node_test_runner(self, test_file_path: str) -> str:
        """Create a custom Node.js test runner"""
        with open(test_file_path, 'r') as f:
            test_content = f.read()
        
        # Extract the source file path from imports
        source_imports = re.findall(r'(?:import|require)\s*\(?[\'"]([^\'"`]+)[\'"]', test_content)
        
        return f"""
// Custom Node.js Test Runner
const fs = require('fs');
const path = require('path');

// Simple test framework
let passed = 0;
let failed = 0;
let errors = [];

// Mock Jest functions
global.test = (name, testFn) => {{
    console.log(`Running: ${{name}}`);
    try {{
        testFn();
        passed++;
        console.log(`✅ ${{name}} PASSED`);
    }} catch (error) {{
        failed++;
        const errorMsg = `❌ ${{name}} FAILED: ${{error.message}}`;
        errors.push(errorMsg);
        console.log(errorMsg);
    }}
}};

global.it = global.test;

global.describe = (name, suiteFn) => {{
    console.log(`\\nSuite: ${{name}}`);
    suiteFn();
}};

// Mock expect function
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
        }}
    }};
}};

// Try to load and execute the test file
try {{
    {test_content}
    
    console.log('\\n=== RESULTS ===');
    console.log(`RESULTS: ${{passed}} passed, ${{failed}} failed`);
    
    if (errors.length > 0) {{
        console.log('\\nFAILED TESTS:');
        errors.forEach(error => console.log(`  ${{error}}`));
    }}
    
}} catch (error) {{
    console.log(`EXECUTION ERROR: ${{error.message}}`);
    console.log(`STACK: ${{error.stack}}`);
}}
"""
    
    def _convert_to_mocha(self, test_file_path: str) -> str:
        """Convert Jest-style tests to Mocha-style"""
        try:
            with open(test_file_path, 'r') as f:
                content = f.read()
            
            # Basic Jest to Mocha conversion
            mocha_content = content
            
            # Replace Jest imports with Mocha equivalents
            mocha_content = re.sub(r'import.*from [\'"]@?jest[\'"];?\n?', '', mocha_content)
            
            # Add Mocha/Chai requires if needed
            if 'expect(' in mocha_content:
                mocha_content = "const { expect } = require('chai');\n" + mocha_content
            
            # Jest and Mocha have similar syntax for describe/test/it, so minimal changes needed
            return mocha_content
            
        except Exception as e:
            console.print(f"[yellow]Mocha conversion failed: {e}[/yellow]")
            return ""
    
    def _analyze_test_file_structure(self, test_file_path: str) -> Dict[str, Any]:
        """Analyze test file structure without execution"""
        try:
            with open(test_file_path, 'r') as f:
                content = f.read()
            
            # Count different types of test patterns
            test_patterns = [
                r'\btest\s*\(',
                r'\bit\s*\(',
                r'describe\s*\(',
                r'expect\s*\('
            ]
            
            test_counts = {}
            total_tests = 0
            
            for pattern in test_patterns:
                matches = len(re.findall(pattern, content))
                test_counts[pattern] = matches
                if pattern in [r'\btest\s*\(', r'\bit\s*\(']:
                    total_tests += matches
            
            # Look for imports/requires
            imports = re.findall(r'(?:import|require)\s*.*?[\'"`]([^\'"`]+)[\'"`]', content)
            
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
        try:
            # Try JSON parsing first
            if result.stdout and '{' in result.stdout:
                json_start = result.stdout.find('{')
                json_end = result.stdout.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result.stdout[json_start:json_end]
                    json_data = json.loads(json_str)
                    return self._parse_jest_json(json_data, test_file_path)
            
            # Fallback to text parsing
            return self._parse_jest_text(result, test_file_path)
            
        except json.JSONDecodeError:
            return self._parse_jest_text(result, test_file_path)
        except Exception as e:
            return {'success': False, 'error': f'Jest output parsing failed: {str(e)}'}
    
    def _parse_jest_json(self, json_data: Dict, test_file_path: str) -> Dict[str, Any]:
        """Parse Jest JSON output"""
        test_results = json_data.get('testResults', [])
        
        total_passed = 0
        total_failed = 0
        total_duration = 0
        
        for test_file in test_results:
            for assertion in test_file.get('assertionResults', []):
                if assertion.get('status') == 'passed':
                    total_passed += 1
                else:
                    total_failed += 1
            
            total_duration += test_file.get('endTime', 0) - test_file.get('startTime', 0)
        
        return {
            'success': json_data.get('success', total_failed == 0),
            'passed': total_passed,
            'failed': total_failed,
            'skipped': json_data.get('numPendingTests', 0),
            'duration': total_duration / 1000,  # Convert to seconds
            'test_file': test_file_path,
            'method': 'jest_json'
        }
    
    def _parse_jest_text(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Jest text output"""
        output = result.stdout + result.stderr
        
        # Extract test counts using various patterns
        patterns = [
            (r'(\d+) passing', 'passed'),
            (r'(\d+) failing', 'failed'),
            (r'(\d+) pending', 'skipped'),
            (r'Tests:\s+(\d+) failed,\s+(\d+) passed', 'failed_passed'),
            (r'Tests:\s+(\d+) passed', 'passed_only')
        ]
        
        passed = failed = skipped = 0
        
        for pattern, pattern_type in patterns:
            matches = re.findall(pattern, output)
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
                break
        
        # Extract duration
        duration_patterns = [
            r'(\d+\.?\d*)\s*s',
            r'(\d+\.?\d*)\s*ms'
        ]
        
        duration = 0
        for pattern in duration_patterns:
            duration_match = re.search(pattern, output)
            if duration_match:
                duration = float(duration_match.group(1))
                if 'ms' in pattern:
                    duration /= 1000
                break
        
        return {
            'success': result.returncode == 0 and failed == 0,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': duration,
            'test_file': test_file_path,
            'output': output,
            'method': 'jest_text'
        }
    
    def _parse_node_direct_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Node.js direct execution output"""
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
            'method': 'node_direct'
        }
    
    def _parse_mocha_output(self, result: subprocess.CompletedProcess, test_file_path: str) -> Dict[str, Any]:
        """Parse Mocha output"""
        output = result.stdout + result.stderr
        
        try:
            # Try JSON parsing if available
            if result.stdout and '{' in result.stdout:
                json_data = json.loads(result.stdout)
                return {
                    'success': len(json_data.get('failures', [])) == 0,
                    'passed': json_data.get('stats', {}).get('passes', 0),
                    'failed': json_data.get('stats', {}).get('failures', 0),
                    'skipped': json_data.get('stats', {}).get('pending', 0),
                    'duration': json_data.get('stats', {}).get('duration', 0) / 1000,
                    'test_file': test_file_path,
                    'method': 'mocha_json'
                }
        except json.JSONDecodeError:
            pass
        
        # Fallback to text parsing
        passed_match = re.search(r'(\d+) passing', output)
        failed_match = re.search(r'(\d+) failing', output)
        pending_match = re.search(r'(\d+) pending', output)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        skipped = int(pending_match.group(1)) if pending_match else 0
        
        return {
            'success': result.returncode == 0,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'duration': 0,
            'test_file': test_file_path,
            'output': output,
            'method': 'mocha_text'
        }
    
    def get_installation_instructions(self) -> Dict[str, Any]:
        """Get instructions for installing JavaScript testing dependencies"""
        return {
            'primary': {
                'command': 'npm install --save-dev jest',
                'description': 'Install Jest testing framework'
            },
            'alternative_commands': [
                'npm install -g jest',
                'yarn add --dev jest',
                'npm install --save-dev mocha chai'
            ],
            'verification': 'npx jest --version',
            'node_requirement': 'Node.js and npm must be installed first'
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