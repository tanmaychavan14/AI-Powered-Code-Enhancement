
class JestRunner:
    """Executes JavaScript tests using Jest"""
    
    def __init__(self):
        self.console = Console()
    
    def run_tests(self, test_file_path: str) -> Dict[str, Any]:
        """Run Jest on the generated test file"""
        try:
            # Check if Jest is available
            cmd_check = ['npx', 'jest', '--version']
            check_result = subprocess.run(cmd_check, capture_output=True, text=True)
            
            if check_result.returncode != 0:
                return {
                    'success': False,
                    'error': 'Jest not installed. Install with: npm install -g jest'
                }
            
            # Run Jest
            cmd = [
                'npx', 'jest',
                test_file_path,
                '--json',
                '--outputFile=tests/results/jest_report.json'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            return self._parse_jest_results(result, test_file_path)
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Jest execution failed: {str(e)}'
            }
    
    def _parse_jest_results(self, result: subprocess.CompletedProcess, test_file: str) -> Dict[str, Any]:
        """Parse Jest execution results"""
        try:
            # Try to parse JSON output
            if result.stdout:
                import json
                data = json.loads(result.stdout)
                
                return {
                    'success': data.get('success', False),
                    'passed': data.get('numPassedTests', 0),
                    'failed': data.get('numFailedTests', 0),
                    'total': data.get('numTotalTests', 0),
                    'test_file': test_file,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            
            return {
                'success': result.returncode == 0,
                'passed': 0,
                'failed': 0,
                'total': 0,
                'test_file': test_file,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse Jest results: {str(e)}'
            }

