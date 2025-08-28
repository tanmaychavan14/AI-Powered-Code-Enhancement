from .base_agent import BaseAgent
class RefactorAgent(BaseAgent):
    """Agent for code refactoring tasks"""
    
    def __init__(self):
        super().__init__()
        self.name = "Refactor Agent"
        self.capabilities = ['code_optimization', 'structure_improvement', 'naming_conventions']
    
    def process(self, parsed_data, project_path):
        """Analyze code and suggest refactoring improvements"""
        results = super().process(parsed_data, project_path)
        
        refactoring_suggestions = []
        code_smells = []
        
        for file_path, data in parsed_data.items():
            file_data = data['data']
            
            # Check for long functions
            if 'functions' in file_data:
                for func in file_data['functions']:
                    # Simplified check - in real implementation, you'd count lines
                    if len(func['definition']) > 100:
                        code_smells.append({
                            'type': 'long_function',
                            'location': f"{file_path}:{func['line']}",
                            'description': f"Function '{func['name']}' might be too long"
                        })
                        
                        refactoring_suggestions.append({
                            'type': 'extract_method',
                            'target': func['name'],
                            'suggestion': 'Consider breaking this function into smaller methods'
                        })
            
            # Check for too many imports
            if 'imports' in file_data and len(file_data['imports']) > 20:
                code_smells.append({
                    'type': 'too_many_imports',
                    'location': file_path,
                    'description': 'File has many imports, consider organizing'
                })
        
        results.update({
            'code_smells': code_smells,
            'refactoring_suggestions': refactoring_suggestions,
            'total_issues_found': len(code_smells),
            'recommended_actions': [
                'Review and refactor long functions',
                'Organize imports and dependencies',
                'Apply consistent naming conventions'
            ]
        })
        
        return results
