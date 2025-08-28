#!/usr/bin/env python3
"""
Base Agent Class
Foundation for all AI agents in the Code Assist system
"""

class BaseAgent:
    """Base agent class that all agents should inherit from"""
    
    def __init__(self):
        self.name = "Base Agent"
        self.capabilities = ["basic_processing"]
        self.version = "1.0.0"
    
    def process(self, parsed_data, project_path):
        """Process the parsed data and return results"""
        files_info = []
        
        for file_path, data in parsed_data.items():
            file_info = {
                'file': file_path,
                'language': data.get('type', 'unknown'),
                'lines': data['data'].get('lines', 0),
                'chars': data['data'].get('chars', 0)
            }
            files_info.append(file_info)
        
        return {
            'status': 'completed',
            'agent': self.name,
            'version': self.version,
            'files_processed': len(parsed_data),
            'project_path': project_path,
            'files_info': files_info,
            'capabilities': self.capabilities,
            'message': f"Processed {len(parsed_data)} files successfully"
        }
    
    def can_handle(self, file_type):
        """Check if this agent can handle the file type"""
        return True  # Base agent handles all types
    
    def get_capabilities(self):
        """Return list of agent capabilities"""
        return self.capabilities
    
    def get_info(self):
        """Return agent information"""
        return {
            'name': self.name,
            'version': self.version,
            'capabilities': self.capabilities
        }