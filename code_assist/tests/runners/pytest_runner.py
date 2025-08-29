class PytestRunner:
    """Executes Python tests using pytest"""
    
    def __init__(self):
        self.console = Console()
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """Run pytest on the generated test file"""
        try:
            # Check if pytest is installed
            try:
                import pytest
            except ImportError:
                return {
                    'success': False,
                    'error': 'pytest not installed. Install with: pip install pytest'
                }
            
            # Run pytest with JSON output
            cmd = [
                'python', '-m', 'pytest', 
                test_file_path,
                '-v',
                '--tb=short',
                '--json-report',
                f'--json-report-file=tests/results/pytest_report.json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Parse results
            return self._parse_pytest_results(result, test_file_path)
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Test execution timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Pytest execution failed: {str(e)}'
            }
    
    def _parse_pytest_results(self, result: subprocess.CompletedProcess, test_file: str) -> Dict[str, Any]:
        """Parse pytest execution results"""
        try:
            # Try to read JSON report if available
            json_file = Path('tests/results/pytest_report.json')
            if json_file.exists():
                with open(json_file, 'r') as f:
                    json_data = json.load(f)
                
                return {
                    'success': True,
                    'passed': json_data.get('summary', {}).get('passed', 0),
                    'failed': json_data.get('summary', {}).get('failed', 0),
                    'total': json_data.get('summary', {}).get('total', 0),
                    'duration': json_data.get('duration', 0),
                    'test_file': test_file,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            
            # Fallback to parsing stdout
            lines = result.stdout.split('\n')
            passed = failed = 0
            
            for line in lines:
                if 'passed' in line and 'failed' in line:
                    # Parse line like "2 passed, 1 failed"
                    import re
                    pass_match = re.search(r'(\d+)\s+passed', line)
                    fail_match = re.search(r'(\d+)\s+failed', line)
                    
                    if pass_match:
                        passed = int(pass_match.group(1))
                    if fail_match:
                        failed = int(fail_match.group(1))
            
            return {
                'success': result.returncode == 0,
                'passed': passed,
                'failed': failed,
                'total': passed + failed,
                'test_file': test_file,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse results: {str(e)}',
                'stdout': result.stdout,
                'stderr': result.stderr
            }
