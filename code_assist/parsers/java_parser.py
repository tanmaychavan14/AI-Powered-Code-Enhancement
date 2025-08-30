#!/usr/bin/env python3
"""
Java Parser
Specialized parser for Java files
"""

from .base_parser import BaseParser
import re

class JavaParser(BaseParser):
    """Java-specific parser"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.java']
        self.language = "java"
    
    def parse(self, content, file_path):
        """Parse Java file and extract classes, methods, imports, etc."""
        base_data = super().parse(content, file_path)
        
        # Add Java-specific parsing
        java_data = {
            'package': self._extract_package(content),
            'imports': self._extract_imports(content),
            'classes': self._extract_classes(content),
            'interfaces': self._extract_interfaces(content),
            'enums': self._extract_enums(content),
            'methods': self._extract_methods(content),
            'fields': self._extract_fields(content),
            'annotations': self._extract_annotations(content),
            'complexity': self._analyze_complexity(content)
        }
        
        base_data.update(java_data)
        return base_data
    
    def _extract_package(self, content):
        """Extract package declaration"""
        lines = content.split('\n')
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('package ') and stripped.endswith(';'):
                return stripped[8:-1].strip()  # Remove 'package ' and ';'
        return None
    
    def _extract_imports(self, content):
        """Extract import statements"""
        imports = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('import ') and stripped.endswith(';'):
                import_path = stripped[7:-1].strip()  # Remove 'import ' and ';'
                is_static = stripped.startswith('import static')
                
                imports.append({
                    'path': import_path,
                    'line': i + 1,
                    'is_static': is_static,
                    'is_wildcard': import_path.endswith('.*'),
                    'statement': stripped
                })
        
        return imports
    
    def _extract_classes(self, content):
        """Extract class definitions"""
        classes = []
        lines = content.split('\n')
        
        # Pattern for class declaration
        class_pattern = r'^\s*(?:@\w+\s+)*(?:(public|private|protected)\s+)?(?:(abstract|final)\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?'
        
        for i, line in enumerate(lines):
            match = re.search(class_pattern, line)
            if match:
                visibility = match.group(1)
                modifier = match.group(2)
                class_name = match.group(3)
                extends_class = match.group(4)
                implements_interfaces = []
                
                if match.group(5):
                    implements_interfaces = [iface.strip() for iface in match.group(5).split(',')]
                
                classes.append({
                    'name': class_name,
                    'line': i + 1,
                    'visibility': visibility or 'package-private',
                    'modifier': modifier,
                    'extends': extends_class,
                    'implements': implements_interfaces,
                    'is_abstract': modifier == 'abstract',
                    'is_final': modifier == 'final',
                    'javadoc': self._get_javadoc(lines, i),
                    'annotations': self._get_annotations_before_line(lines, i),
                    'methods': self._extract_class_methods(lines, i, class_name),
                    'fields': self._extract_class_fields(lines, i, class_name)
                })
        
        return classes
    
    def _extract_interfaces(self, content):
        """Extract interface definitions"""
        interfaces = []
        lines = content.split('\n')
        
        interface_pattern = r'^\s*(?:@\w+\s+)*(?:(public|private|protected)\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?'
        
        for i, line in enumerate(lines):
            match = re.search(interface_pattern, line)
            if match:
                visibility = match.group(1)
                interface_name = match.group(2)
                extends_interfaces = []
                
                if match.group(3):
                    extends_interfaces = [iface.strip() for iface in match.group(3).split(',')]
                
                interfaces.append({
                    'name': interface_name,
                    'line': i + 1,
                    'visibility': visibility or 'package-private',
                    'extends': extends_interfaces,
                    'javadoc': self._get_javadoc(lines, i),
                    'annotations': self._get_annotations_before_line(lines, i),
                    'methods': self._extract_interface_methods(lines, i)
                })
        
        return interfaces
    
    def _extract_enums(self, content):
        """Extract enum definitions"""
        enums = []
        lines = content.split('\n')
        
        enum_pattern = r'^\s*(?:@\w+\s+)*(?:(public|private|protected)\s+)?enum\s+(\w+)(?:\s+implements\s+([^{]+))?'
        
        for i, line in enumerate(lines):
            match = re.search(enum_pattern, line)
            if match:
                visibility = match.group(1)
                enum_name = match.group(2)
                implements_interfaces = []
                
                if match.group(3):
                    implements_interfaces = [iface.strip() for iface in match.group(3).split(',')]
                
                enums.append({
                    'name': enum_name,
                    'line': i + 1,
                    'visibility': visibility or 'package-private',
                    'implements': implements_interfaces,
                    'javadoc': self._get_javadoc(lines, i),
                    'annotations': self._get_annotations_before_line(lines, i),
                    'values': self._extract_enum_values(lines, i)
                })
        
        return enums
    
    def _extract_methods(self, content):
        """Extract all method definitions"""
        methods = []
        lines = content.split('\n')
        
        # Method pattern - handles generics, arrays, etc.
        method_pattern = r'^\s*(?:@\w+\s+)*(?:(public|private|protected)\s+)?(?:(static|final|abstract|synchronized|native)\s+)*(?:<[^>]+>\s+)?(\w+(?:\[\])*|\w+<[^>]+>(?:\[\])*|void)\s+(\w+)\s*\([^)]*\)(?:\s+throws\s+[^{]+)?'
        
        for i, line in enumerate(lines):
            # Skip lines that are clearly not methods
            if any(keyword in line for keyword in ['class ', 'interface ', 'enum ', 'import ', 'package ']):
                continue
                
            match = re.search(method_pattern, line)
            if match and '{' in line or (i + 1 < len(lines) and '{' in lines[i + 1]):
                visibility = match.group(1)
                modifier = match.group(2)
                return_type = match.group(3)
                method_name = match.group(4)
                
                # Skip constructors (they'll be handled separately)
                if return_type == method_name:
                    continue
                
                methods.append({
                    'name': method_name,
                    'line': i + 1,
                    'visibility': visibility or 'package-private',
                    'modifier': modifier,
                    'return_type': return_type,
                    'is_static': 'static' in (modifier or ''),
                    'is_abstract': 'abstract' in (modifier or ''),
                    'is_final': 'final' in (modifier or ''),
                    'is_synchronized': 'synchronized' in (modifier or ''),
                    'javadoc': self._get_javadoc(lines, i),
                    'annotations': self._get_annotations_before_line(lines, i),
                    'signature': line.strip()
                })
        
        return methods
    
    def _extract_class_methods(self, lines, class_start_line, class_name):
        """Extract methods within a specific class"""
        methods = []
        brace_count = 0
        in_class = False
        
        for i in range(class_start_line, len(lines)):
            line = lines[i]
            
            # Track braces to stay within class boundaries
            brace_count += line.count('{') - line.count('}')
            
            if i == class_start_line and '{' in line:
                in_class = True
            elif in_class and brace_count <= 0:
                break
            
            if in_class and i > class_start_line:
                # Method or constructor pattern
                method_match = re.search(r'^\s*(?:@\w+\s+)*(?:(public|private|protected)\s+)?(?:(static|final|abstract)\s+)*(?:(\w+(?:\[\])*|\w+<[^>]+>(?:\[\])*|void)\s+)?(\w+)\s*\([^)]*\)', line)
                if method_match and ('{' in line or (i + 1 < len(lines) and '{' in lines[i + 1])):
                    visibility = method_match.group(1)
                    modifier = method_match.group(2)
                    return_type = method_match.group(3)
                    method_name = method_match.group(4)
                    
                    is_constructor = method_name == class_name or return_type is None
                    
                    methods.append({
                        'name': method_name,
                        'line': i + 1,
                        'visibility': visibility or 'package-private',
                        'modifier': modifier,
                        'return_type': return_type,
                        'is_constructor': is_constructor,
                        'is_static': 'static' in (modifier or ''),
                        'is_abstract': 'abstract' in (modifier or ''),
                        'javadoc': self._get_javadoc(lines, i)
                    })
        
        return methods
    
    def _extract_interface_methods(self, lines, interface_start_line):
        """Extract methods within an interface"""
        methods = []
        brace_count = 0
        in_interface = False
        
        for i in range(interface_start_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            
            if i == interface_start_line and '{' in line:
                in_interface = True
            elif in_interface and brace_count <= 0:
                break
            
            if in_interface and i > interface_start_line:
                # Interface method pattern (abstract by default)
                method_match = re.search(r'^\s*(?:@\w+\s+)*(?:(default|static)\s+)?(\w+(?:\[\])*|\w+<[^>]+>(?:\[\])*|void)\s+(\w+)\s*\([^)]*\)', line)
                if method_match and (';' in line or '{' in line):
                    modifier = method_match.group(1)
                    return_type = method_match.group(2)
                    method_name = method_match.group(3)
                    
                    methods.append({
                        'name': method_name,
                        'line': i + 1,
                        'return_type': return_type,
                        'is_default': modifier == 'default',
                        'is_static': modifier == 'static',
                        'is_abstract': modifier != 'default' and modifier != 'static',
                        'javadoc': self._get_javadoc(lines, i)
                    })
        
        return methods
    
    def _extract_fields(self, content):
        """Extract field declarations"""
        fields = []
        lines = content.split('\n')
        
        # Field pattern - excludes methods and local variables
        field_pattern = r'^\s*(?:@\w+\s+)*(?:(public|private|protected)\s+)?(?:(static|final|volatile|transient)\s+)*(\w+(?:\[\])*|\w+<[^>]+>(?:\[\])*)\s+(\w+)(?:\s*=\s*[^;]+)?;'
        
        for i, line in enumerate(lines):
            # Skip method signatures
            if '(' in line and ')' in line:
                continue
                
            match = re.search(field_pattern, line)
            if match:
                visibility = match.group(1)
                modifier = match.group(2)
                field_type = match.group(3)
                field_name = match.group(4)
                
                fields.append({
                    'name': field_name,
                    'line': i + 1,
                    'type': field_type,
                    'visibility': visibility or 'package-private',
                    'modifier': modifier,
                    'is_static': 'static' in (modifier or ''),
                    'is_final': 'final' in (modifier or ''),
                    'is_volatile': 'volatile' in (modifier or ''),
                    'is_transient': 'transient' in (modifier or ''),
                    'javadoc': self._get_javadoc(lines, i),
                    'annotations': self._get_annotations_before_line(lines, i)
                })
        
        return fields
    
    def _extract_class_fields(self, lines, class_start_line, class_name):
        """Extract fields within a specific class"""
        fields = []
        brace_count = 0
        in_class = False
        
        for i in range(class_start_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            
            if i == class_start_line and '{' in line:
                in_class = True
            elif in_class and brace_count <= 0:
                break
            
            if in_class and i > class_start_line:
                # Field pattern within class
                if '(' not in line or ')' not in line:  # Exclude methods
                    field_match = re.search(r'^\s*(?:@\w+\s+)*(?:(public|private|protected)\s+)?(?:(static|final|volatile)\s+)*(\w+(?:\[\])*)\s+(\w+)', line)
                    if field_match and ';' in line:
                        visibility = field_match.group(1)
                        modifier = field_match.group(2)
                        field_type = field_match.group(3)
                        field_name = field_match.group(4)
                        
                        fields.append({
                            'name': field_name,
                            'line': i + 1,
                            'type': field_type,
                            'visibility': visibility or 'package-private',
                            'modifier': modifier,
                            'is_static': 'static' in (modifier or ''),
                            'is_final': 'final' in (modifier or ''),
                            'javadoc': self._get_javadoc(lines, i)
                        })
        
        return fields
    
    def _extract_enum_values(self, lines, enum_start_line):
        """Extract enum constant values"""
        values = []
        brace_count = 0
        in_enum = False
        
        for i in range(enum_start_line, len(lines)):
            line = lines[i]
            brace_count += line.count('{') - line.count('}')
            
            if i == enum_start_line and '{' in line:
                in_enum = True
            elif in_enum and brace_count <= 0:
                break
            
            if in_enum and i > enum_start_line:
                # Look for enum constants (usually uppercase identifiers)
                enum_value_match = re.search(r'^\s*([A-Z][A-Z0-9_]*)\s*(?:\([^)]*\))?\s*[,;]?', line)
                if enum_value_match:
                    value_name = enum_value_match.group(1)
                    values.append({
                        'name': value_name,
                        'line': i + 1,
                        'has_constructor_args': '(' in line and ')' in line
                    })
        
        return values
    
    def _extract_annotations(self, content):
        """Extract annotation definitions and usages"""
        annotations = []
        lines = content.split('\n')
        
        # Annotation definitions
        annotation_pattern = r'^\s*(?:(public|private|protected)\s+)?@interface\s+(\w+)'
        
        # Annotation usages
        usage_pattern = r'^\s*@(\w+)(?:\([^)]*\))?'
        
        for i, line in enumerate(lines):
            # Annotation definitions
            def_match = re.search(annotation_pattern, line)
            if def_match:
                visibility = def_match.group(1)
                annotation_name = def_match.group(2)
                annotations.append({
                    'name': annotation_name,
                    'line': i + 1,
                    'type': 'definition',
                    'visibility': visibility or 'package-private',
                    'javadoc': self._get_javadoc(lines, i)
                })
            
            # Annotation usages
            usage_match = re.search(usage_pattern, line)
            if usage_match:
                annotation_name = usage_match.group(1)
                annotations.append({
                    'name': annotation_name,
                    'line': i + 1,
                    'type': 'usage',
                    'statement': line.strip()
                })
        
        return annotations
    
    def _get_annotations_before_line(self, lines, line_index):
        """Get annotations that appear before a declaration"""
        annotations = []
        
        # Look backwards for annotations
        for i in range(line_index - 1, max(0, line_index - 10), -1):
            stripped = lines[i].strip()
            if stripped.startswith('@'):
                annotation_match = re.search(r'@(\w+)(?:\([^)]*\))?', stripped)
                if annotation_match:
                    annotations.insert(0, {
                        'name': annotation_match.group(1),
                        'line': i + 1,
                        'statement': stripped
                    })
            elif stripped and not stripped.startswith('//') and not stripped.startswith('/*'):
                break
        
        return annotations
    
    def _get_javadoc(self, lines, line_index):
        """Extract Javadoc comment before a declaration"""
        if line_index == 0:
            return None
        
        # Look backwards for Javadoc comment
        for i in range(line_index - 1, max(0, line_index - 20), -1):
            stripped = lines[i].strip()
            if stripped.endswith('*/'):
                # Found end of Javadoc, now find the start
                javadoc_lines = []
                for j in range(i, max(0, i - 50), -1):
                    javadoc_lines.insert(0, lines[j])
                    if lines[j].strip().startswith('/**'):
                        return '\n'.join(javadoc_lines)
                break
            elif stripped and not stripped.startswith('*') and not stripped.startswith('//'):
                break
        
        return None
    
    def _analyze_complexity(self, content):
        """Analyze code complexity indicators"""
        lines = content.split('\n')
        complexity = {
            'if_statements': 0,
            'loops': 0,
            'try_blocks': 0,
            'switch_statements': 0,
            'nested_classes': 0,
            'method_calls': 0,
            'inheritance_depth': 0,
            'exception_handling': 0
        }
        
        for line in lines:
            stripped = line.strip()
            
            # Control structures
            if re.search(r'\bif\s*\(', stripped):
                complexity['if_statements'] += 1
            if re.search(r'\b(for|while|do)\s*[\(\s]', stripped):
                complexity['loops'] += 1
            if stripped.startswith('try'):
                complexity['try_blocks'] += 1
            if re.search(r'\bswitch\s*\(', stripped):
                complexity['switch_statements'] += 1
            
            # Exception handling
            if 'catch' in stripped or 'throws' in stripped or 'throw ' in stripped:
                complexity['exception_handling'] += 1
            
            # Nested classes (inner classes)
            if re.search(r'^\s+(public|private|protected)?\s*(static\s+)?class\s+', stripped):
                complexity['nested_classes'] += 1
            
            # Method calls (rough estimate)
            if '.' in stripped and '(' in stripped:
                complexity['method_calls'] += stripped.count('.')
        
        return complexity