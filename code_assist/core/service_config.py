#!/usr/bin/env python3
"""
Service Configuration - Shared mappings for all agents
"""

# Service mapping - maps all possible inputs to canonical service names
SERVICE_MAP = {
    # Testing Service
    '1': 'testing',
    'test': 'testing',
    'testing': 'testing',
    't': 'testing',
    
    # Refactoring Service
    '2': 'refactoring',
    'refactor': 'refactoring',
    'refactoring': 'refactoring',
    'r': 'refactoring',
    
    # Debugging Service
    '3': 'debugging',
    'debug': 'debugging',
    'debugging': 'debugging',
    'd': 'debugging',
    
    # Documentation Service
    '4': 'documentation',
    'docs': 'documentation',
    'documentation': 'documentation',
    'doc': 'documentation',
    
    # Analysis Service
    '5': 'analysis',
    'analyze': 'analysis',
    'analysis': 'analysis',
    'a': 'analysis',
    
    # Planning Service
    '6': 'planning',
    'plan': 'planning',
    'planning': 'planning',
    'p': 'planning'
}

# Service display names
SERVICE_DISPLAY_NAMES = {
    'testing': '🧪 Testing',
    'refactoring': '🔧 Refactoring',
    'debugging': '🐛 Debugging',
    'documentation': '📚 Documentation',
    'analysis': '📊 Analysis',
    'planning': '📋 Planning'
}

# Service icons
SERVICE_ICONS = {
    'testing': '🧪',
    'refactoring': '🔧',
    'debugging': '🐛',
    'documentation': '📚',
    'analysis': '📊',
    'planning': '📋'
}

def normalize_service_name(service_input: str) -> str:
    """
    Normalize service input to canonical service name
    
    Args:
        service_input: User input ('1', 'test', 'testing', etc.)
    
    Returns:
        Canonical service name ('testing', 'debugging', etc.)
    """
    return SERVICE_MAP.get(service_input.lower(), service_input.lower())