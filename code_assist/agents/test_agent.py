#!/usr/bin/env python3
"""
Test Agent
AI agent specialized in testing tasks and test generation
"""

from .base_agent import BaseAgent

class TestAgent(BaseAgent):
    """Agent for handling testing tasks"""
    
    def __init__(self):
        super().__init__()
        self.name = "Test Agent"
        self.capabilities = [
            'test_generation', 
            'test_execution', 
            'coverage_analysis',
            'test_suggestions',
            'mock_generation'
        ]
    
    def process(self, parsed_data, project_path):
        """Generate tests and analyze testing needs"""
        results = super().process(parsed_data, project_path)
        
        test_suggestions = []
        functions_found = 0
        classes_found = 0
        testable_items = []
        
        for file_path, data in parsed_data.items():
            file_data = data['data']
            
            # Process Python files
            if data['type'] == 'python' and 'functions' in file_data:
                functions = file_data['functions']
                functions_found += len(functions)
                
                for func in functions:
                    if not func['name'].startswith('_'):  # Skip private functions
                        testable_items.append({
                            'type': 'function',
                            'name': func['name'],
                            'file': file_path,
                            'line': func['line'],
                            'signature': func.get('signature', ''),
                            'has_docstring': bool(func.get('docstring'))
                        })
                        
                        test_suggestions.append({
                            'function': func['name'],
                            'file': file_path,
                            'test_file': self._suggest_test_file(file_path),
                            'test_methods': [
                                f"test_{func['name']}_valid_input",
                                f"test_{func['name']}_edge_cases", 
                                f"test_{func['name']}_error_handling"
                            ],
                            'priority': self._calculate_test_priority(func)
                        })
            
            # Process classes
            if data['type'] == 'python' and 'classes' in file_data:
                classes = file_data['classes']
                classes_found += len(classes)
                
                for cls in classes:
                    if not cls['name'].startswith('_'):
                        testable_items.append({
                            'type': 'class',
                            'name': cls['name'],
                            'file': file_path,
                            'line': cls['line'],
                            'inheritance': cls.get('inheritance', []),
                            'has_docstring': bool(cls.get('docstring'))
                        })
        
        # Generate test recommendations
        recommendations = self._generate_recommendations(testable_items, project_path)
        
        # Calculate test coverage estimate
        coverage_estimate = self._estimate_test_coverage(project_path, testable_items)
        
        results.update({
            'test_suggestions': test_suggestions,
            'testable_items': testable_items,
            'functions_found': functions_found,
            'classes_found': classes_found,
            'recommendations': recommendations,
            'coverage_estimate': coverage_estimate,
            'test_framework_suggestions': ['pytest', 'unittest', 'nose2'],
            'mock_suggestions': self._suggest_mocking_needs(testable_items)
        })
        
        return results
    
    def _suggest_test_file(self, source_file):
        """Suggest test file name for source file"""
        from pathlib import Path
        
        path = Path(source_file)
        if path.name.startswith('test_'):
            return str(path)
        
        # Standard test file naming conventions
        return str(path.parent / f"test_{path.stem}.py")
    
    def _calculate_test_priority(self, func):
        """Calculate priority for testing a function"""
        priority = 'medium'
        
        if func['name'] in ['main', 'init', 'setup']:
            priority = 'high'
        elif func['name'].startswith('_'):
            priority = 'low'
        elif func.get('docstring'):
            priority = 'high'  # Well-documented functions are important
        
        return priority
    
    def _generate_recommendations(self, testable_items, project_path):
        """Generate testing recommendations"""
        recommendations = []
        
        total_items = len(testable_items)
        functions = [item for item in testable_items if item['type'] == 'function']
        classes = [item for item in testable_items if item['type'] == 'class']
        
        if total_items > 0:
            recommendations.append(f"Found {len(functions)} functions and {len(classes)} classes to test")
            
        if not any('test_' in str(item['file']) for item in testable_items):
            recommendations.append("No existing test files detected - consider setting up a test suite")
            
        if len(functions) > 10:
            recommendations.append("Large codebase detected - prioritize testing critical functions first")
            
        high_priority = [item for item in testable_items 
                        if self._calculate_test_priority({'name': item['name']}) == 'high']
        if high_priority:
            recommendations.append(f"Focus on {len(high_priority)} high-priority items first")
        
        recommendations.extend([
            "Set up continuous integration for automated testing",
            "Aim for at least 80% code coverage",
            "Consider property-based testing for complex functions"
        ])
        
        return recommendations
    
    def _estimate_test_coverage(self, project_path, testable_items):
        """Estimate current test coverage"""
        # This is a simplified estimation
        # In a real implementation, you'd analyze existing test files
        
        return {
            'estimated_coverage': '0%',
            'testable_functions': len([item for item in testable_items if item['type'] == 'function']),
            'testable_classes': len([item for item in testable_items if item['type'] == 'class']),
            'total_testable': len(testable_items),
            'recommendation': 'Start with unit tests for core functions'
        }
    
    def _suggest_mocking_needs(self, testable_items):
        """Suggest where mocking might be needed"""
        mock_suggestions = []
        
        # Look for functions that might need mocking
        for item in testable_items:
            if item['type'] == 'function':
                name = item['name'].lower()
                if any(keyword in name for keyword in ['api', 'request', 'database', 'file', 'network']):
                    mock_suggestions.append({
                        'item': item['name'],
                        'file': item['file'],
                        'reason': 'Function name suggests external dependency',
                        'mock_type': 'external_service'
                    })
        
        return mock_suggestions