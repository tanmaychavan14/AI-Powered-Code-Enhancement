from .base_agent import BaseAgent
class DebugAgent(BaseAgent):
    """Agent for debugging and error detection"""
    
    def __init__(self):
        super().__init__()
        self.name = "Debug Agent"
        self.capabilities = ['static_analysis', 'error_detection', 'code_review']
    
    def process(self, parsed_data, project_path):
        """Analyze code for potential bugs and issues"""
        results = super().process(parsed_data, project_path)
        
        potential_bugs = []
        warnings = []
        
        for file_path, data in parsed_data.items():
            content = data['data']['content']
            
            # Simple static analysis examples
            lines = content.split('\n')
            for i, line in enumerate(lines):
                # Check for common Python issues
                if 'print(' in line and data['type'] == 'python':
                    warnings.append({
                        'type': 'debug_print',
                        'location': f"{file_path}:{i+1}",
                        'message': 'Debug print statement found'
                    })
                
                if 'TODO' in line or 'FIXME' in line:
                    warnings.append({
                        'type': 'todo_comment',
                        'location': f"{file_path}:{i+1}",
                        'message': 'TODO/FIXME comment found'
                    })
        
        results.update({
            'potential_bugs': potential_bugs,
            'warnings': warnings,
            'total_issues': len(potential_bugs) + len(warnings),
            'recommended_actions': [
                'Review all TODO/FIXME comments',
                'Remove debug print statements',
                'Add proper error handling'
            ]
        })
        
        return results