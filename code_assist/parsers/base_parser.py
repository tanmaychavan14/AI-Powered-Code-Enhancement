#!/usr/bin/env python3
"""
just checking git working or not
Base Parser Class
Foundation for all file parsers in the Code Assist system
"""

class BaseParser:
    """Base parser class that all parsers should inherit from"""
    
    def __init__(self):
        self.supported_extensions = []
        self.language = "unknown"
    
    def parse(self, content, file_path):
        """Parse the file content and return structured data"""
        return {
            'file_path': file_path,
            'content': content,
            'lines': len(content.split('\n')),
            'chars': len(content),
            'language': self.language,
            'parsed': True,
            'basic_info': {
                'empty_lines': self._count_empty_lines(content),
                'comment_lines': self._count_comment_lines(content),
                'code_lines': self._count_code_lines(content)
            }
        }
    
    def can_parse(self, file_extension):
        """Check if this parser can handle the file extension"""
        return file_extension.lower() in self.supported_extensions
    
    def _count_empty_lines(self, content):
        """Count empty lines in content"""
        return sum(1 for line in content.split('\n') if line.strip() == '')
    
    def _count_comment_lines(self, content):
        """Count comment lines (basic implementation)"""
        comment_chars = ['#', '//', '/*', '*', '<!--']
        lines = content.split('\n')
        count = 0
        for line in lines:
            stripped = line.strip()
            if any(stripped.startswith(char) for char in comment_chars):
                count += 1
        return count
    
    def _count_code_lines(self, content):
        """Count non-empty, non-comment lines"""
        total_lines = len(content.split('\n'))
        empty_lines = self._count_empty_lines(content)
        comment_lines = self._count_comment_lines(content)
        return total_lines - empty_lines - comment_lines