#!/usr/bin/env python3
"""
Control Agent - Orchestrates the entire workflow
Routes user requests to appropriate agents and coordinates processing
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel

console = Console()

class ControlAgent:
    """Main control agent that orchestrates all operations"""
    
    def __init__(self):
        self.parser_agent = None
        self.output_agent = None
        self.test_agent = None
        self.refactor_agent = None
        self.debug_agent = None
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all required agents with fallback handling"""
        try:
            from agents.parser_agent import ParserAgent
            self.parser_agent = ParserAgent()
        except ImportError:
            console.print("[yellow]Warning: Using fallback parser agent[/yellow]")
            self.parser_agent = self._create_fallback_parser_agent()
        
        try:
            from agents.output_agent import OutputAgent
            self.output_agent = OutputAgent()
        except ImportError:
            console.print("[yellow]Warning: Using fallback output agent[/yellow]")
            self.output_agent = self._create_fallback_output_agent()
        
        try:
            from agents.test_agent import TestAgent
            self.test_agent = TestAgent()
        except ImportError:
            console.print("[yellow]Warning: Using fallback test agent[/yellow]")
            self.test_agent = self._create_fallback_test_agent()
    
    def _create_fallback_parser_agent(self):
        """Create fallback parser agent"""
        class FallbackParserAgent:
            def detect_language(self, file_path):
                ext_map = {'.py': 'python', '.js': 'javascript', '.jsx': 'javascript', 
                          '.ts': 'javascript', '.tsx': 'javascript', '.java': 'java'}
                return ext_map.get(Path(file_path).suffix.lower(), 'unknown')
            
            def parse_file(self, file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return {
                        'file_path': file_path,
                        'language': self.detect_language(file_path),
                        'content': content,
                        'classes': [],
                        'functions': [],
                        'imports': [],
                        'lines': len(content.split('\n')),
                        'parsed': True
                    }
                except Exception as e:
                    return {'error': str(e), 'parsed': False}
        
        return FallbackParserAgent()
    
    def _create_fallback_output_agent(self):
        """Create fallback output agent"""
        class FallbackOutputAgent:
            def display_results(self, results, service_type):
                console.print(f"\n[bold green]✅ {service_type.title()} Results:[/bold green]")
                if isinstance(results, dict):
                    for key, value in results.items():
                        console.print(f"[cyan]{key}:[/cyan] {value}")
                else:
                    console.print(results)
        
        return FallbackOutputAgent()
    
    def _create_fallback_test_agent(self):
        """Create fallback test agent"""
        class FallbackTestAgent:
            def generate_tests(self, parsed_data):
                results = {
                    'tests_generated': 0,
                    'files_processed': len(parsed_data),
                    'status': 'completed',
                    'message': 'Basic test analysis completed'
                }
                
                for file_path, data in parsed_data.items():
                    if data.get('parsed', False):
                        results['tests_generated'] += len(data.get('classes', [])) + len(data.get('functions', []))
                
                return results
        
        return FallbackTestAgent()
    
    def process_request(self, service_type: str, target_path: str) -> Dict[str, Any]:
        """Main processing method that orchestrates the entire workflow"""
        try:
            console.print(f"[bold blue]🎯 Processing {service_type} request for: {target_path}[/bold blue]")
            
            # Step 1: Validate path
            path = Path(target_path).resolve()
            if not path.exists():
                raise FileNotFoundError(f"Path does not exist: {target_path}")
            
            # Step 2: Get files to process
            files_to_process = self._get_files_to_process(path)
            if not files_to_process:
                raise ValueError("No supported code files found")
            
            console.print(f"[green]Found {len(files_to_process)} files to process[/green]")
            
            # Step 3: Parse all files
            parsed_data = self._parse_all_files(files_to_process)
            
            # Step 4: Route to appropriate service agent
            results = self._route_to_service_agent(service_type, parsed_data, str(path))
            
            # Step 5: Display results via output agent
            self.output_agent.display_results(results, service_type)
            
            return {
                'status': 'success',
                'service': service_type,
                'files_processed': len(files_to_process),
                'results': results
            }
            
        except Exception as e:
            error_msg = f"Control Agent Error: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]")
            return {
                'status': 'error',
                'error': error_msg,
                'service': service_type
            }
    
    def _get_files_to_process(self, path: Path) -> List[Path]:
        """Get list of files to process"""
        supported_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java']
        files = []
        
        try:
            if path.is_file():
                if path.suffix.lower() in supported_extensions:
                    files.append(path)
            else:
                # Recursively find all supported files
                for ext in supported_extensions:
                    files.extend(path.rglob(f"*{ext}"))
            
            # Limit to reasonable number for processing
            return files[:20]  # Process max 20 files
            
        except Exception as e:
            console.print(f"[yellow]Warning: Error scanning files - {e}[/yellow]")
            return []
    
    def _parse_all_files(self, files: List[Path]) -> Dict[str, Any]:
        """Parse all files using parser agent"""
        parsed_data = {}
        
        console.print("[bold cyan]🔍 Parsing files...[/bold cyan]")
        
        for file_path in files:
            try:
                console.print(f"[dim]Parsing: {file_path.name}[/dim]")
                
                # Use parser agent to parse the file
                parsed_result = self.parser_agent.parse_file(str(file_path))
                
                if parsed_result.get('parsed', False):
                    parsed_data[str(file_path)] = parsed_result
                    console.print(f"[green]✅ {file_path.name}[/green]")
                else:
                    console.print(f"[yellow]⚠️  {file_path.name} - {parsed_result.get('error', 'Unknown error')}[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]❌ {file_path.name} - {str(e)}[/red]")
                continue
        
        console.print(f"[bold green]📊 Successfully parsed {len(parsed_data)} files[/bold green]")
        return parsed_data
    
    def _route_to_service_agent(self, service_type: str, parsed_data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Route to appropriate service agent based on user request"""
        try:
            console.print(f"[bold blue]🤖 Routing to {service_type} agent...[/bold blue]")
            
            if service_type.lower() in ['test', 'testing', '1']:
                return self._handle_testing_request(parsed_data, project_path)
            elif service_type.lower() in ['refactor', 'refactoring', '2']:
                return self._handle_refactoring_request(parsed_data, project_path)
            elif service_type.lower() in ['debug', 'debugging', '3']:
                return self._handle_debugging_request(parsed_data, project_path)
            elif service_type.lower() in ['docs', 'documentation', '4']:
                return self._handle_documentation_request(parsed_data, project_path)
            elif service_type.lower() in ['analyze', 'analysis', '5']:
                return self._handle_analysis_request(parsed_data, project_path)
            elif service_type.lower() in ['plan', 'planning', '6']:
                return self._handle_planning_request(parsed_data, project_path)
            else:
                raise ValueError(f"Unknown service type: {service_type}")
                
        except Exception as e:
            console.print(f"[red]Service routing error: {e}[/red]")
            return {'error': f"Service routing failed: {str(e)}"}
    
    
def _handle_testing_request(self, parsed_data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
    """Handle testing service request - Updated with better output formatting"""
    try:
        console.print("[bold cyan]🧪 Generating and executing tests...[/bold cyan]")
        
        # Show project structure first
        self.output_agent.display_file_tree(parsed_data, "Files to Test")
        
        # Generate tests using test agent
        test_results = self.test_agent.generate_tests(parsed_data)
        
        if 'error' in test_results:
            return test_results
        
        # Create comprehensive results for output agent
        results = {
            'service': 'Testing',
            'project_path': project_path,
            'files_analyzed': len(parsed_data),
            'files_processed': test_results['files_processed'],
            'tests_generated': test_results['tests_generated'],
            'tests_passed': test_results['tests_passed'],
            'tests_failed': test_results['tests_failed'],
            'test_files': test_results['test_files'],
            'execution_results': test_results['execution_results'],
            'errors': test_results['errors'],
            'status': 'completed'
        }
        
        # Save results for later reference
        self.output_agent.save_results_to_file(results, 'testing')
        
        # Display success message
        summary = {
            'Tests Generated': test_results['tests_generated'],
            'Tests Passed': test_results['tests_passed'],
            'Success Rate': f"{(test_results['tests_passed']/(test_results['tests_passed']+test_results['tests_failed'])*100):.1f}%" if (test_results['tests_passed']+test_results['tests_failed']) > 0 else "N/A"
        }
        
        self.output_agent.display_success_message('Testing', summary)
        
        return results
        
    except Exception as e:
        return {'error': f"Testing service failed: {str(e)}"}
    def _handle_refactoring_request(self, parsed_data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Handle refactoring service request"""
        return {
            'service': 'Refactoring',
            'status': 'Not implemented yet',
            'message': 'Refactoring agent integration pending'
        }
    
    def _handle_debugging_request(self, parsed_data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Handle debugging service request"""
        return {
            'service': 'Debugging', 
            'status': 'Not implemented yet',
            'message': 'Debug agent integration pending'
        }
    
    def _handle_documentation_request(self, parsed_data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Handle documentation service request"""
        return {
            'service': 'Documentation',
            'status': 'Not implemented yet', 
            'message': 'Documentation agent integration pending'
        }
    
    def _handle_analysis_request(self, parsed_data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Handle code analysis service request"""
        try:
            analysis_results = {
                'service': 'Code Analysis',
                'project_path': project_path,
                'summary': self._generate_project_summary(parsed_data)
            }
            return analysis_results
            
        except Exception as e:
            return {'error': f"Analysis service failed: {str(e)}"}
    
    def _handle_planning_request(self, parsed_data: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Handle planning service request"""
        return {
            'service': 'Planning',
            'status': 'Not implemented yet',
            'message': 'Planning agent integration pending'
        }
    
    def _extract_test_targets(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract classes and functions that need testing"""
        test_targets = {
            'files': {},
            'total_classes': 0,
            'total_functions': 0
        }
        
        for file_path, file_data in parsed_data.items():
            if file_data.get('parsed', False):
                classes = file_data.get('classes', [])
                functions = file_data.get('functions', [])
                
                test_targets['files'][file_path] = {
                    'language': file_data.get('language', 'unknown'),
                    'classes': classes,
                    'functions': functions
                }
                
                test_targets['total_classes'] += len(classes)
                test_targets['total_functions'] += len(functions)
        
        return test_targets
    
    def _generate_project_summary(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project summary from parsed data"""
        summary = {
            'total_files': len(parsed_data),
            'languages': {},
            'total_lines': 0,
            'total_classes': 0,
            'total_functions': 0
        }
        
        for file_path, file_data in parsed_data.items():
            if file_data.get('parsed', False):
                language = file_data.get('language', 'unknown')
                summary['languages'][language] = summary['languages'].get(language, 0) + 1
                summary['total_lines'] += file_data.get('lines', 0)
                summary['total_classes'] += len(file_data.get('classes', []))
                summary['total_functions'] += len(file_data.get('functions', []))
        
        return summary