#!/usr/bin/env python3
"""
Output Agent - Handles all result display and formatting
Displays results from all service agents in a beautiful, organized format
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.tree import Tree
from rich.syntax import Syntax
from rich.layout import Layout
from rich.align import Align
from rich.text import Text
from core.service_config import SERVICE_MAP, normalize_service_name
console = Console()

class OutputAgent:
    """Agent responsible for displaying all service results"""
    
    def __init__(self):
        self.console = Console()
        
    def display_results(self, results: Dict[str, Any], service_type: str) -> None:
        """Main method to display results based on service type"""
        try:
            self.console.clear()
            self._display_header(service_type)
            
            if 'error' in results:
                self._display_error(results['error'], service_type)
                return
            service_name = normalize_service_name(service_type)
            # Route to appropriate display method
            service_lower = service_type.lower()
            if service_name == service_type.lower():  # Normalization didn't change it
                if 'service' in results:
                    result_service = results['service'].lower()
                    # Try to extract service name from results
                    for canonical_name in ['testing', 'refactoring', 'debugging', 
                                          'documentation', 'analysis', 'planning']:
                        if canonical_name in result_service:
                            service_name = canonical_name
                            break
            
            # if service_lower in ['test', 'testing']:
            #     self._display_testing_results(results)
            # elif service_lower in ['refactor', 'refactoring']:
            #     self._display_refactoring_results(results)
            # elif service_lower in ['debug', 'debugging']:
            #     self._display_debugging_results(results)
            # elif service_lower in ['docs', 'documentation']:
            #     self._display_documentation_results(results)
            # elif service_lower in ['analyze', 'analysis']:
            #     self._display_analysis_results(results)
            # elif service_lower in ['plan', 'planning']:
            #     self._display_planning_results(results)
            # else:
            #     self._display_generic_results(results, service_type)
            if service_name == 'testing':
                self._display_testing_results(results)
            elif service_name == 'refactoring':
                self._display_refactoring_results(results)
            elif service_name == 'debugging':
                self._display_debugging_results(results)
            elif service_name == 'documentation':
                self._display_documentation_results(results)
            elif service_name == 'analysis':
                self._display_analysis_results(results)
            elif service_name == 'planning':
                self._display_planning_results(results)
            else:
                self._display_generic_results(results, service_type)
                
        except Exception as e:
            self._display_error(f"Output display failed: {str(e)}", service_type)
    
    def _display_header(self, service_type: str) -> None:
        """Display service header with beautiful formatting"""
        service_icons = {
            'testing': '🧪',
            'refactoring': '🔧', 
            'debugging': '🐛',
            'documentation': '📚',
            'analysis': '📊',
            'planning': '📋'
        }
        service_name = normalize_service_name(service_type)
        icon = service_icons.get(service_name, '⚙️')
        # icon = service_icons.get(service_type.lower(), '⚙️')
        
        # header_text = Text()
        # header_text.append("AI-Powered Code Assistant\n", style="bold blue")
        # header_text.append(f"{icon} {service_type.title()} Service", style="bold white")
        
        # panel = Panel(
        #     Align.center(header_text),
        #     border_style="blue",
        #     padding=(1, 2)
        # )
        
        # self.console.print(panel)
        # self.console.print()
        header_text = Text()
        header_text.append("AI-Powered Code Assistant\n", style="bold blue")
        header_text.append(f"{icon} {service_name.title()} Service", style="bold white")
        
        panel = Panel(
            Align.center(header_text),
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def _display_error(self, error_msg: str, service_type: str) -> None:
        """Display error message with proper formatting"""
        error_panel = Panel(
            f"[red]❌ Error in {service_type} Service[/red]\n\n{error_msg}",
            title="[red]Error[/red]",
            border_style="red"
        )
        self.console.print(error_panel)
    
    def _display_testing_results(self, results: Dict[str, Any]) -> None:
        """Display comprehensive testing results"""
        # Project Summary Panel
        self._display_project_summary(results)
        
        # Test Statistics
        self._display_test_statistics(results)
        
        # Test Files Generated
        self._display_test_files(results)
        
        # Detailed Execution Results
        self._display_execution_details(results)
        
        # Errors and Warnings
        self._display_errors_and_warnings(results)
        
        # Recommendations
        self._display_testing_recommendations(results)
    
    def _display_project_summary(self, results: Dict[str, Any]) -> None:
        """Display project overview"""
        summary_table = Table(title="📋 Project Summary", border_style="cyan")
        summary_table.add_column("Metric", style="cyan", width=20)
        summary_table.add_column("Value", style="green", width=30)
        
        summary_table.add_row("Project Path", str(results.get('project_path', 'N/A')))
        summary_table.add_row("Files Analyzed", str(results.get('files_analyzed', 0)))
        summary_table.add_row("Files Processed", str(results.get('files_processed', 0)))
        summary_table.add_row("Status", results.get('status', 'Unknown'))
        
        self.console.print(summary_table)
        self.console.print()
    
#     def _display_test_statistics(self, results: Dict[str, Any]) -> None:
#         """Display test execution statistics"""
#         passed = results.get('tests_passed', 0)
#         failed = results.get('tests_failed', 0)
#         generated = results.get('tests_generated', 0)
#         functions_tested = results.get('functions_tested', 0)  # ✅ New
#         classes_tested = results.get('classes_tested', 0)      # ✅ New
#         total_executed = passed + failed
        
#         # Create statistics table
#         stats_table = Table(title="📊 Test Statistics", border_style="green")
#         stats_table.add_column("Metric", style="cyan", width=30)
#         stats_table.add_column("Count", style="white", width=10, justify="right")
#         stats_table.add_column("Details", style="dim", width=25)
        
#         # ✅ Show source code metrics
#         stats_table.add_row(
#             "Functions Analyzed", 
#             str(functions_tested), 
#             "in source code"
#         )
#         stats_table.add_row(
#             "Classes Analyzed", 
#             str(classes_tested), 
#             "in source code"
#         )
        
#         # Separator
#         stats_table.add_row("", "", "")
        
#         # ✅ Show generated test metrics
#         stats_table.add_row(
#             "Test Cases Generated", 
#             str(generated), 
#             f"~{generated // max(functions_tested + classes_tested, 1)} per function" if functions_tested + classes_tested > 0 else ""
#         )
#         stats_table.add_row(
#             "Test Cases Executed", 
#             str(total_executed), 
#             "✅ Complete"
#         )
        
#         # Separator
#         stats_table.add_row("", "", "")
        
#         # ✅ Show execution results
#         stats_table.add_row(
#             "Tests Passed", 
#             str(passed), 
#             "✅ Success" if passed > 0 else "⚠️  None"
#         )
#         stats_table.add_row(
#             "Tests Failed", 
#             str(failed), 
#             "❌ Failed" if failed > 0 else "✅ None"
#         )
        
#         # Calculate success rate
#         if total_executed > 0:
#             success_rate = (passed / total_executed) * 100
#             status = "🎉 Excellent" if success_rate >= 80 else "⚠️  Needs Work"
#             stats_table.add_row("Success Rate", f"{success_rate:.1f}%", status)
        
#         self.console.print(stats_table)
#         self.console.print()
        
#         # ✅ Add visual summary panel
#         if functions_tested > 0 or classes_tested > 0:
#             summary_text = f"""
# [bold cyan]📈 Coverage Summary[/bold cyan]

# • Analyzed [yellow]{functions_tested} function(s)[/yellow] + [yellow]{classes_tested} class(es)[/yellow]
# • Generated [green]{generated} test case(s)[/green]
# • Average: [blue]~{generated // max(functions_tested + classes_tested, 1)} tests per component[/blue]
# • Success Rate: [{"green" if (passed / max(total_executed, 1) * 100) >= 80 else "yellow"}]{(passed / max(total_executed, 1) * 100):.1f}%[/]
#             """
            
#             summary_panel = Panel(
#                 summary_text.strip(),
#                 title="[bold blue]Test Coverage Overview[/bold blue]",
#                 border_style="blue",
#                 padding=(1, 2)
#             )
#             self.console.print(summary_panel)
#             self.console.print() ds

    def _display_test_statistics(self, results: Dict[str, Any]) -> None:
        """Display test execution statistics"""
        passed = results.get('tests_passed', 0)
        failed = results.get('tests_failed', 0)
        generated = results.get('tests_generated', 0)
        functions_tested = results.get('functions_analyzed', 0)  # ✅ Changed key
        classes_tested = results.get('classes_analyzed', 0)      # ✅ Changed key
        total_executed = passed + failed
        
        # Create statistics table
        stats_table = Table(title="📊 Test Statistics", border_style="green")
        stats_table.add_column("Metric", style="cyan", width=30)
        stats_table.add_column("Count", style="white", width=10, justify="right")
        stats_table.add_column("Details", style="dim", width=25)
        
        # ✅ Show source code metrics
        stats_table.add_row(
            "Functions Analyzed", 
            str(functions_tested), 
            "in source code"
        )
        stats_table.add_row(
            "Classes Analyzed", 
            str(classes_tested), 
            "in source code"
        )
        
        # Separator
        stats_table.add_row("", "", "")
        
        # ✅ Show generated test metrics
        total_components = functions_tested + classes_tested
        avg_tests = generated // total_components if total_components > 0 else 0
        
        stats_table.add_row(
            "Test Cases Generated", 
            str(generated), 
            f"~{avg_tests} per component" if total_components > 0 else ""
        )
        stats_table.add_row(
            "Test Cases Executed", 
            str(total_executed), 
            "✅ Complete" if total_executed > 0 else "⚠️  None"
        )
        
        # Separator
        stats_table.add_row("", "", "")
        
        # ✅ Show execution results
        stats_table.add_row(
            "Tests Passed", 
            str(passed), 
            "✅ Success" if passed > 0 else "⚠️  None"
        )
        stats_table.add_row(
            "Tests Failed", 
            str(failed), 
            "❌ Failed" if failed > 0 else "✅ None"
        )
        
        # Calculate success rate
        if total_executed > 0:
            success_rate = (passed / total_executed) * 100
            status = "🎉 Excellent" if success_rate >= 80 else "⚠️  Needs Work"
            stats_table.add_row("Success Rate", f"{success_rate:.1f}%", status)
        
        self.console.print(stats_table)
        self.console.print()
        
        # ✅ Add visual summary panel
        if total_components > 0:
            success_rate = (passed / max(total_executed, 1) * 100)
            success_color = "green" if success_rate >= 80 else "yellow"
            
            summary_text = f"""
[bold cyan]📈 Coverage Summary[/bold cyan]

• Analyzed [yellow]{functions_tested} function(s)[/yellow] + [yellow]{classes_tested} class(es)[/yellow]
• Generated [green]{generated} test case(s)[/green]
• Average: [blue]~{avg_tests} tests per component[/blue]
• Executed: [cyan]{total_executed} test(s)[/cyan]
• Success Rate: [{success_color}]{success_rate:.1f}%[/{success_color}]
            """
            
            summary_panel = Panel(
                summary_text.strip(),
                title="[bold blue]Test Coverage Overview[/bold blue]",
                border_style="blue",
                padding=(1, 2)
            )
            self.console.print(summary_panel)
            self.console.print()
    
    def _display_test_files(self, results: Dict[str, Any]) -> None:
        """Display generated test files"""
        test_files = results.get('test_files', [])
        
        if test_files:
            files_table = Table(title="📁 Generated Test Files", border_style="yellow")
            files_table.add_column("File Name", style="yellow", width=40)
            files_table.add_column("Language", style="cyan", width=15)
            files_table.add_column("Size", style="green", width=10)
            
            for test_file in test_files:
                file_path = Path(test_file)
                file_size = "N/A"
                
                try:
                    if file_path.exists():
                        size_bytes = file_path.stat().st_size
                        file_size = f"{size_bytes} bytes"
                except:
                    pass
                
                # Detect language from path
                language = "Unknown"
                if "python" in str(file_path):
                    language = "Python"
                elif "javascript" in str(file_path):
                    language = "JavaScript"
                elif "java" in str(file_path):
                    language = "Java"
                
                files_table.add_row(file_path.name, language, file_size)
            
            self.console.print(files_table)
            self.console.print()
    
    def _display_execution_details(self, results: Dict[str, Any]) -> None:
        """Display detailed execution results for each file"""
        execution_results = results.get('execution_results', {})
        
        if execution_results:
            self.console.print("[bold blue]🔍 Detailed Execution Results[/bold blue]")
            
            for file_path, exec_result in execution_results.items():
                file_name = Path(file_path).name
                
                # Create panel for each file
                if exec_result.get('success', False):
                    status_color = "green"
                    status_icon = "✅"
                else:
                    status_color = "red"
                    status_icon = "❌"
                
                # File execution summary
                summary_text = f"[{status_color}]{status_icon} {file_name}[/{status_color}]\n"
                summary_text += f"Passed: {exec_result.get('passed', 0)} | "
                summary_text += f"Failed: {exec_result.get('failed', 0)} | "
                summary_text += f"Total: {exec_result.get('total', 0)}\n"
                
                if exec_result.get('duration'):
                    summary_text += f"Duration: {exec_result['duration']:.2f}s"
                
                # Show errors if any
                if exec_result.get('stderr'):
                    summary_text += f"\n[red]Errors:[/red]\n{exec_result['stderr'][:200]}..."
                
                file_panel = Panel(
                    summary_text,
                    title=f"[{status_color}]{file_name}[/{status_color}]",
                    border_style=status_color,
                    padding=(0, 1)
                )
                
                self.console.print(file_panel)
            
            self.console.print()
    
    def _display_errors_and_warnings(self, results: Dict[str, Any]) -> None:
        """Display errors and warnings"""
        errors = results.get('errors', [])
        
        if errors:
            error_table = Table(title="⚠️  Errors and Warnings", border_style="red")
            error_table.add_column("File/Component", style="yellow", width=30)
            error_table.add_column("Error Message", style="red", width=50)
            
            for error in errors:
                if ':' in error:
                    file_part, error_part = error.split(':', 1)
                    error_table.add_row(file_part.strip(), error_part.strip())
                else:
                    error_table.add_row("General", error)
            
            self.console.print(error_table)
            self.console.print()
    
    def _display_testing_recommendations(self, results: Dict[str, Any]) -> None:
        """Display testing recommendations and next steps"""
        passed = results.get('tests_passed', 0)
        failed = results.get('tests_failed', 0)
        total = passed + failed
        
        recommendations = []
        
        if total == 0:
            recommendations.append("• Generate more comprehensive test cases")
            recommendations.append("• Check if test frameworks are properly installed")
        elif failed > 0:
            recommendations.append("• Review and fix failing test cases")
            recommendations.append("• Check for missing dependencies or imports")
        
        if passed > 0:
            recommendations.append("• Consider adding edge case tests")
            recommendations.append("• Add performance and integration tests")
        
        recommendations.append("• Set up continuous integration for automated testing")
        
        if recommendations:
            recommendations_text = "\n".join(recommendations)
            recommendations_panel = Panel(
                recommendations_text,
                title="[blue]💡 Recommendations[/blue]",
                border_style="blue"
            )
            self.console.print(recommendations_panel)
    
    def _display_refactoring_results(self, results: Dict[str, Any]) -> None:
        """Display refactoring service results"""
        self.console.print("[bold green]🔧 Refactoring Results[/bold green]")
        
        refactor_table = Table(title="Refactoring Summary", border_style="green")
        refactor_table.add_column("Metric", style="cyan")
        refactor_table.add_column("Value", style="green")
        
        refactor_table.add_row("Files Refactored", str(results.get('files_refactored', 0)))
        refactor_table.add_row("Issues Fixed", str(results.get('issues_fixed', 0)))
        refactor_table.add_row("Code Quality Score", f"{results.get('quality_score', 0)}/100")
        
        self.console.print(refactor_table)
        
        # Display refactoring suggestions
        suggestions = results.get('suggestions', [])
        if suggestions:
            self.console.print("\n[bold blue]💡 Refactoring Suggestions:[/bold blue]")
            for i, suggestion in enumerate(suggestions, 1):
                self.console.print(f"  {i}. {suggestion}")
    
    def _display_debugging_results(self, results: Dict[str, Any]) -> None:
        """Display debugging service results"""
        self.console.print("[bold red]🐛 Debugging Results[/bold red]")
        
        debug_table = Table(title="Debug Analysis", border_style="red")
        debug_table.add_column("Component", style="cyan")
        debug_table.add_column("Status", style="white")
        debug_table.add_column("Issues Found", style="red")
        
        bugs_found = results.get('bugs_found', [])
        files_analyzed = results.get('files_analyzed', 0)
        
        debug_table.add_row("Files Analyzed", str(files_analyzed), "")
        debug_table.add_row("Bugs Detected", str(len(bugs_found)), "🐛")
        debug_table.add_row("Critical Issues", str(results.get('critical_issues', 0)), "🚨")
        
        self.console.print(debug_table)
        
        # Display detailed bug reports
        if bugs_found:
            self.console.print("\n[bold red]🐛 Detected Issues:[/bold red]")
            for i, bug in enumerate(bugs_found, 1):
                bug_panel = Panel(
                    f"[yellow]File:[/yellow] {bug.get('file', 'N/A')}\n"
                    f"[yellow]Line:[/yellow] {bug.get('line', 'N/A')}\n"
                    f"[yellow]Severity:[/yellow] {bug.get('severity', 'Unknown')}\n"
                    f"[yellow]Description:[/yellow] {bug.get('description', 'No description')}",
                    title=f"[red]Issue #{i}[/red]",
                    border_style="red"
                )
                self.console.print(bug_panel)
    
    def _display_documentation_results(self, results: Dict[str, Any]) -> None:
        """Display documentation service results"""
        self.console.print("[bold blue]📚 Documentation Results[/bold blue]")
        
        docs_table = Table(title="Documentation Summary", border_style="blue")
        docs_table.add_column("Metric", style="cyan")
        docs_table.add_column("Value", style="green")
        
        docs_table.add_row("Files Documented", str(results.get('files_documented', 0)))
        docs_table.add_row("Documentation Coverage", f"{results.get('coverage', 0)}%")
        docs_table.add_row("Generated Docs", str(results.get('docs_generated', 0)))
        
        self.console.print(docs_table)
        
        # Display generated documentation files
        doc_files = results.get('documentation_files', [])
        if doc_files:
            self.console.print("\n[bold blue]📄 Generated Documentation:[/bold blue]")
            
            docs_tree = Tree("📁 Documentation Files")
            for doc_file in doc_files:
                file_path = Path(doc_file)
                docs_tree.add(f"📄 {file_path.name}")
            
            self.console.print(docs_tree)
    
    def _display_analysis_results(self, results: Dict[str, Any]) -> None:
        """Display code analysis results"""
        self.console.print("[bold green]📊 Code Analysis Results[/bold green]")
        
        summary = results.get('summary', {})
        
        # Project Overview Table
        overview_table = Table(title="Project Overview", border_style="green")
        overview_table.add_column("Metric", style="cyan", width=25)
        overview_table.add_column("Value", style="green", width=15)
        overview_table.add_column("Details", style="white", width=30)
        
        overview_table.add_row("Total Files", str(summary.get('total_files', 0)), "Code files analyzed")
        overview_table.add_row("Total Lines", str(summary.get('total_lines', 0)), "Lines of code")
        overview_table.add_row("Total Classes", str(summary.get('total_classes', 0)), "Class definitions")
        overview_table.add_row("Total Functions", str(summary.get('total_functions', 0)), "Function definitions")
        
        self.console.print(overview_table)
        self.console.print()
        
        # Language Distribution
        languages = summary.get('languages', {})
        if languages:
            lang_table = Table(title="🌐 Language Distribution", border_style="blue")
            lang_table.add_column("Language", style="yellow")
            lang_table.add_column("Files", style="green", justify="right")
            lang_table.add_column("Percentage", style="cyan", justify="right")
            
            total_files = sum(languages.values())
            for language, count in languages.items():
                percentage = (count / total_files * 100) if total_files > 0 else 0
                lang_table.add_row(
                    language.title(),
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            self.console.print(lang_table)
            self.console.print()
        
        # Code Quality Metrics (if available)
        self._display_code_quality_metrics(results)
    
    def _display_code_quality_metrics(self, results: Dict[str, Any]) -> None:
        """Display code quality and complexity metrics"""
        metrics = results.get('quality_metrics', {})
        
        if metrics:
            quality_table = Table(title="⚡ Code Quality Metrics", border_style="yellow")
            quality_table.add_column("Metric", style="cyan")
            quality_table.add_column("Score", style="green", justify="right")
            quality_table.add_column("Status", style="white")
            
            # Add various quality metrics
            complexity = metrics.get('complexity', 0)
            maintainability = metrics.get('maintainability', 0)
            readability = metrics.get('readability', 0)
            
            quality_table.add_row("Complexity", str(complexity), self._get_quality_status(complexity, reverse=True))
            quality_table.add_row("Maintainability", f"{maintainability}/100", self._get_quality_status(maintainability))
            quality_table.add_row("Readability", f"{readability}/100", self._get_quality_status(readability))
            
            self.console.print(quality_table)
            self.console.print()
    
    def _display_planning_results(self, results: Dict[str, Any]) -> None:
        """Display planning service results"""
        self.console.print("[bold purple]📋 Planning Results[/bold purple]")
        
        # Display project roadmap
        roadmap = results.get('roadmap', [])
        if roadmap:
            self.console.print("\n[bold blue]🗺️  Project Roadmap:[/bold blue]")
            
            roadmap_tree = Tree("📋 Development Plan")
            for phase in roadmap:
                phase_node = roadmap_tree.add(f"📅 {phase.get('name', 'Phase')}")
                for task in phase.get('tasks', []):
                    phase_node.add(f"• {task}")
            
            self.console.print(roadmap_tree)
        
        # Display recommendations
        recommendations = results.get('recommendations', [])
        if recommendations:
            self.console.print("\n[bold green]💡 Recommendations:[/bold green]")
            for i, rec in enumerate(recommendations, 1):
                self.console.print(f"  {i}. {rec}")
    
    def _display_generic_results(self, results: Dict[str, Any], service_type: str) -> None:
        """Display generic results for any service"""
        generic_table = Table(title=f"{service_type} Results", border_style="white")
        generic_table.add_column("Key", style="cyan")
        generic_table.add_column("Value", style="white")
        
        for key, value in results.items():
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, indent=2)[:100] + "..." if len(str(value)) > 100 else json.dumps(value, indent=2)
            else:
                value_str = str(value)
            
            generic_table.add_row(str(key), value_str)
        
        self.console.print(generic_table)
    
    def _get_quality_status(self, score: float, reverse: bool = False) -> str:
        """Get quality status based on score"""
        if reverse:  # For metrics where lower is better (like complexity)
            if score <= 5:
                return "🟢 Excellent"
            elif score <= 10:
                return "🟡 Good"
            else:
                return "🔴 Needs Work"
        else:  # For metrics where higher is better
            if score >= 80:
                return "🟢 Excellent"
            elif score >= 60:
                return "🟡 Good"
            else:
                return "🔴 Needs Work"
    
    def display_live_progress(self, stage: str, current: int, total: int) -> None:
        """Display live progress for long-running operations"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            task = progress.add_task(f"[cyan]{stage}...", total=total)
            progress.update(task, completed=current)
    
    def display_file_tree(self, parsed_data: Dict[str, Any], title: str = "Project Structure") -> None:
        """Display project file structure as a tree"""
        tree = Tree(f"📁 {title}")
        
        # Group files by language
        files_by_lang = {}
        for file_path, file_data in parsed_data.items():
            if file_data.get('parsed', False):
                language = file_data.get('language', 'unknown')
                if language not in files_by_lang:
                    files_by_lang[language] = []
                files_by_lang[language].append(file_path)
        
        # Add language branches
        for language, files in files_by_lang.items():
            lang_node = tree.add(f"🔧 {language.title()}")
            for file_path in files:
                file_name = Path(file_path).name
                file_node = lang_node.add(f"📄 {file_name}")
                
                # Add file details
                file_data = parsed_data[file_path]
                classes = file_data.get('classes', [])
                functions = file_data.get('functions', [])
                
                if classes:
                    class_node = file_node.add("🏗️  Classes")
                    for cls in classes:
                        class_node.add(f"• {cls['name']}")
                
                if functions:
                    func_node = file_node.add("⚙️  Functions")
                    for func in functions:
                        func_node.add(f"• {func['name']}")
        
        self.console.print(tree)
        self.console.print()
    
    def display_success_message(self, service_type: str, summary: Dict[str, Any]) -> None:
        """Display final success message with summary"""
        success_text = Text()
        success_text.append("🎉 ", style="bold green")
        success_text.append(f"{service_type.title()} Service Completed Successfully!", style="bold green")
        
        # Add key metrics
        if summary:
            success_text.append("\n\n📈 Key Metrics:\n", style="bold blue")
            for key, value in summary.items():
                success_text.append(f"• {key}: {value}\n", style="white")
        
        success_panel = Panel(
            Align.center(success_text),
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(success_panel)
    
    def display_code_preview(self, file_path: str, language: str, lines_to_show: int = 10) -> None:
        """Display code preview with syntax highlighting"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Show first N lines
            lines = content.split('\n')[:lines_to_show]
            preview_content = '\n'.join(lines)
            
            syntax = Syntax(preview_content, language, theme="monokai", line_numbers=True)
            
            preview_panel = Panel(
                syntax,
                title=f"[green]📄 {Path(file_path).name}[/green]",
                border_style="green"
            )
            
            self.console.print(preview_panel)
            
        except Exception as e:
            self.console.print(f"[red]Could not display preview: {e}[/red]")
    
    def save_results_to_file(self, results: Dict[str, Any], service_type: str) -> None:
        """Save results to JSON file for later reference"""
        try:
            results_dir = Path("tests/results")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = Path().cwd().name
            results_file = results_dir / f"{service_type.lower()}_results.json"
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.console.print(f"[dim]💾 Results saved to: {results_file}[/dim]")
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save results - {e}[/yellow]")
    
    def display_interactive_menu(self, options: List[str]) -> None:
        """Display interactive menu for user choices"""
        menu_table = Table(title="🎯 Available Actions", border_style="cyan")
        menu_table.add_column("Option", style="cyan", width=10)
        menu_table.add_column("Action", style="white", width=40)
        
        for i, option in enumerate(options, 1):
            menu_table.add_row(str(i), option)
        
        self.console.print(menu_table)
        self.console.print("\n[bold yellow]Enter your choice (number):[/bold yellow] ", end="")


    def _display_refactoring_results(self, results: Dict[str, Any]) -> None:
     """Display comprehensive refactoring results"""
    
    # 1. Project Summary
     self._display_refactor_project_summary(results)
    
    # 2. Refactoring Statistics
     self._display_refactor_statistics(results)
    
    # 3. Refactored Files
     self._display_refactored_files(results)
    
    # 4. Improvements Made
     self._display_improvements(results)
    
    # 5. Code Smells Fixed
     self._display_code_smells_fixed(results)
    
    # 6. Recommendations
     self._display_refactoring_recommendations(results)

    def _display_refactor_project_summary(self, results: Dict[str, Any]) -> None:
     """Display refactoring project overview"""
     summary_table = Table(title="📋 Refactoring Overview", border_style="cyan")
     summary_table.add_column("Metric", style="cyan", width=20)
     summary_table.add_column("Value", style="green", width=30)
    
     summary_table.add_row("Project Path", str(results.get('project_path', 'N/A')))
     summary_table.add_row("Files Analyzed", str(results.get('files_analyzed', 0)))
     summary_table.add_row("Files Refactored", str(results.get('files_refactored', 0)))
     summary_table.add_row("Status", results.get('status', 'Unknown'))
    
     self.console.print(summary_table)
     self.console.print()

    def _display_refactor_statistics(self, results: Dict[str, Any]) -> None:
     """Display refactoring execution statistics"""
     files_analyzed = results.get('files_analyzed', 0)
     files_refactored = results.get('files_refactored', 0)
     improvements = results.get('improvements', [])
     total_improvements = len(improvements)
    
    # Create statistics table
     stats_table = Table(title="📊 Refactoring Statistics", border_style="green")
     stats_table.add_column("Metric", style="cyan", width=30)
     stats_table.add_column("Count", style="white", width=10, justify="right")
     stats_table.add_column("Details", style="dim", width=25)
    
    # Analysis metrics
     stats_table.add_row(
        "Files Analyzed", 
        str(files_analyzed), 
        "source code files"
     )
     stats_table.add_row(
        "Files Refactored", 
        str(files_refactored), 
        "✅ Successfully refactored" if files_refactored > 0 else "⚠️  None"
     )
    
    # Separator
     stats_table.add_row("", "", "")
    
    # Improvement metrics
     stats_table.add_row(
        "Total Improvements", 
        str(total_improvements), 
        "code quality enhancements"
     )
    
    # Calculate success rate
     if files_analyzed > 0:
        refactor_rate = (files_refactored / files_analyzed) * 100
        status = "🎉 Excellent" if refactor_rate >= 80 else "✅ Good" if refactor_rate >= 50 else "⚠️  Needs Review"
        stats_table.add_row("Refactoring Rate", f"{refactor_rate:.1f}%", status)
    
    # Average improvements per file
     if files_refactored > 0:
        avg_improvements = total_improvements / files_refactored
        stats_table.add_row(
            "Avg Improvements/File", 
            f"{avg_improvements:.1f}", 
            "per refactored file"
        )
    
     self.console.print(stats_table)
     self.console.print()
    
    # Add visual summary panel
     if files_refactored > 0:
        refactor_rate = (files_refactored / files_analyzed * 100) if files_analyzed > 0 else 0
        rate_color = "green" if refactor_rate >= 80 else "yellow"
        
        summary_text = f"""
[bold cyan]🔧 Refactoring Summary[/bold cyan]

• Analyzed [yellow]{files_analyzed} file(s)[/yellow]
• Refactored [green]{files_refactored} file(s)[/green]
• Applied [blue]{total_improvements} improvement(s)[/blue]
• Success Rate: [{rate_color}]{refactor_rate:.1f}%[/{rate_color}]
• Quality Impact: [green]Positive[/green]
        """
        
        summary_panel = Panel(
            summary_text.strip(),
            title="[bold blue]Refactoring Impact[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(summary_panel)
        self.console.print()

    def _display_refactored_files(self, results: Dict[str, Any]) -> None:
     """Display refactored files with details"""
     refactored_files = results.get('refactored_files', [])
     refactoring_details = results.get('refactoring_details', [])
    
     if refactored_files:
        files_table = Table(title="📁 Refactored Files", border_style="yellow")
        files_table.add_column("Original File", style="cyan", width=30)
        files_table.add_column("Refactored File", style="yellow", width=30)
        files_table.add_column("Improvements", style="green", width=15, justify="center")
        files_table.add_column("Status", style="white", width=10)
        
        for refactor_file in refactored_files:
            file_path = Path(refactor_file)
            
            # Find matching detail
            detail = None
            for d in refactoring_details:
                if d.get('refactored_file') == refactor_file:
                    detail = d
                    break
            
            original_name = detail.get('file_name', 'N/A') if detail else Path(refactor_file).stem.replace('_refactored', '')
            improvement_count = len(detail.get('improvements', [])) if detail else 0
            
            files_table.add_row(
                original_name,
                file_path.name,
                str(improvement_count),
                "✅"
            )
        
        self.console.print(files_table)
        self.console.print()
        
        # Show detailed file information
        if refactoring_details:
            self.console.print("[bold blue]📄 Detailed File Analysis[/bold blue]\n")
            
            for detail in refactoring_details[:3]:  # Show top 3 detailed
                file_name = detail.get('file_name', 'Unknown')
                lines_before = detail.get('lines_before', 0)
                lines_after = detail.get('lines_after', 0)
                code_smells = detail.get('code_smells', [])
                
                # Calculate reduction
                line_diff = lines_before - lines_after
                reduction_pct = (line_diff / lines_before * 100) if lines_before > 0 else 0
                
                detail_text = f"""
[bold cyan]{file_name}[/bold cyan]

[yellow]Before:[/yellow] {lines_before} lines
[green]After:[/green] {lines_after} lines
[blue]Reduction:[/blue] {line_diff} lines ({reduction_pct:.1f}%)

[yellow]Issues Fixed:[/yellow] {len(code_smells)}
                """
                
                detail_panel = Panel(
                    detail_text.strip(),
                    title=f"[green]✅ {file_name}[/green]",
                    border_style="green",
                    padding=(1, 2)
                )
                self.console.print(detail_panel)
            
            if len(refactoring_details) > 3:
                self.console.print(f"[dim]...and {len(refactoring_details) - 3} more file(s)[/dim]\n")

    def _display_improvements(self, results: Dict[str, Any]) -> None:
     """Display all improvements made during refactoring"""
     improvements = results.get('improvements', [])
    
     if improvements:
        improvements_table = Table(
            title="✨ Improvements Applied", 
            border_style="green",
            show_lines=True
        )
        improvements_table.add_column("#", style="cyan", width=5, justify="center")
        improvements_table.add_column("Improvement", style="white", width=60)
        improvements_table.add_column("Impact", style="green", width=15)
        
        # Categorize improvements by impact
        for i, improvement in enumerate(improvements[:15], 1):  # Show top 15
            # Determine impact based on keywords
            impact = "🟢 High"
            if any(word in improvement.lower() for word in ['minor', 'small', 'slight']):
                impact = "🟡 Medium"
            elif any(word in improvement.lower() for word in ['major', 'significant', 'critical']):
                impact = "🔴 Critical"
            
            improvements_table.add_row(str(i), improvement, impact)
        
        self.console.print(improvements_table)
        
        if len(improvements) > 15:
            self.console.print(f"[dim]...and {len(improvements) - 15} more improvement(s)[/dim]")
        
        self.console.print()

    def _display_code_smells_fixed(self, results: Dict[str, Any]) -> None:
     """Display code smells that were identified and fixed"""
     refactoring_details = results.get('refactoring_details', [])
    
    # Collect all code smells - ✅ PROPERLY HANDLE DICT FORMAT
     all_smells = []
     for detail in refactoring_details:
        smells = detail.get('code_smells', [])
        file_name = detail.get('file_name', 'Unknown')
        for smell in smells:
            # ✅ FIX: Extract description from dict
            if isinstance(smell, dict):
                smell_desc = smell.get('description', 'No description')
                severity = smell.get('severity', 'medium')
            elif isinstance(smell, str):
                smell_desc = smell
                severity = 'medium'
            else:
                smell_desc = str(smell)
                severity = 'medium'
            
            all_smells.append({
                'file': file_name,
                'description': smell_desc,  # ✅ NOW IT'S A STRING
                'severity': severity
            })
    
     if all_smells:
        smells_table = Table(
            title="🔍 Code Smells Fixed", 
            border_style="red",
            show_lines=True
        )
        smells_table.add_column("File", style="yellow", width=20)
        smells_table.add_column("Issue", style="red", width=40)
        smells_table.add_column("Severity", style="cyan", width=12)
        smells_table.add_column("Status", style="green", width=10)
        
        for smell_data in all_smells[:10]:  # Show top 10
            # Add severity indicator
            severity = smell_data.get('severity', 'medium').upper()
            severity_icon = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢'
            }.get(severity, '⚪')
            
            smells_table.add_row(
                smell_data['file'],
                smell_data['description'],  # ✅ NOW RENDERS AS STRING
                f"{severity_icon} {severity}",
                "✅ Fixed"
            )
        
        self.console.print(smells_table)
        
        if len(all_smells) > 10:
            self.console.print(f"[dim]...and {len(all_smells) - 10} more issue(s) fixed[/dim]")
        
        self.console.print()

    def _display_refactoring_recommendations(self, results: Dict[str, Any]) -> None:
     """Display refactoring recommendations and next steps"""
     files_refactored = results.get('files_refactored', 0)
     refactored_files = results.get('refactored_files', [])
    
     recommendations = []
    
     if files_refactored > 0:
        recommendations.append("✅ Review the refactored code in the generated files")
        recommendations.append("🧪 Run comprehensive tests on refactored code")
        recommendations.append("📝 Compare original vs refactored code side-by-side")
        recommendations.append("🔄 Apply refactored code to your project")
        recommendations.append("📊 Monitor performance impact after refactoring")
     else:
        recommendations.append("✨ Your code is already well-structured!")
        recommendations.append("📚 Consider adding more comprehensive documentation")
        recommendations.append("🧪 Increase test coverage for better code quality")
    
     recommendations.append("🔍 Schedule regular code quality reviews")
     recommendations.append("📈 Track code quality metrics over time")
    
     if recommendations:
        recommendations_text = "\n".join(f"  {rec}" for rec in recommendations)
        
        # Add file locations
        if refactored_files:
            recommendations_text += f"\n\n[bold blue]📁 Refactored Files Location:[/bold blue]\n"
            recommendations_text += f"  [dim]{Path(refactored_files[0]).parent}/[/dim]\n"
        
        recommendations_panel = Panel(
            recommendations_text,
            title="[blue]💡 Next Steps & Recommendations[/blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(recommendations_panel)
    
    # Display message if available
     message = results.get('message')
     if message:
        self.console.print(f"\n[bold green]✅ {message}[/bold green]\n")