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
            
            # Route to appropriate display method
            service_lower = service_type.lower()
            
            if service_lower in ['test', 'testing']:
                self._display_testing_results(results)
            elif service_lower in ['refactor', 'refactoring']:
                self._display_refactoring_results(results)
            elif service_lower in ['debug', 'debugging']:
                self._display_debugging_results(results)
            elif service_lower in ['docs', 'documentation']:
                self._display_documentation_results(results)
            elif service_lower in ['analyze', 'analysis']:
                self._display_analysis_results(results)
            elif service_lower in ['plan', 'planning']:
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
        
        icon = service_icons.get(service_type.lower(), '⚙️')
        
        header_text = Text()
        header_text.append("AI-Powered Code Assistant\n", style="bold blue")
        header_text.append(f"{icon} {service_type.title()} Service", style="bold white")
        
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
    
    def _display_test_statistics(self, results: Dict[str, Any]) -> None:
        """Display test execution statistics"""
        passed = results.get('tests_passed', 0)
        failed = results.get('tests_failed', 0)
        generated = results.get('tests_generated', 0)
        total_executed = passed + failed
        
        # Create statistics table
        stats_table = Table(title="📊 Test Statistics", border_style="green")
        stats_table.add_column("Metric", style="cyan", width=25)
        stats_table.add_column("Count", style="white", width=10, justify="right")
        stats_table.add_column("Status", style="green", width=15)
        
        stats_table.add_row("Tests Generated", str(generated), "✅ Complete")
        stats_table.add_row("Tests Executed", str(total_executed), "✅ Complete")
        stats_table.add_row("Tests Passed", str(passed), "✅ Success" if passed > 0 else "⚠️  None")
        stats_table.add_row("Tests Failed", str(failed), "❌ Failed" if failed > 0 else "✅ None")
        
        # Calculate success rate
        if total_executed > 0:
            success_rate = (passed / total_executed) * 100
            status = "🎉 Excellent" if success_rate >= 80 else "⚠️  Needs Work"
            stats_table.add_row("Success Rate", f"{success_rate:.1f}%", status)
        
        self.console.print(stats_table)
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


