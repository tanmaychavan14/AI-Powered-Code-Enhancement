#!/usr/bin/env python3
"""
Code Assist CLI - Interactive Commands Module
AI-powered development companion with parser and agent integration
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import sys
import os
from pathlib import Path

# Initialize console first, before any error handling
console = Console()

# Import parsers with fallback
PARSERS_AVAILABLE = True
AGENTS_AVAILABLE = True

try:
    from parsers.base_parser import BaseParser
    from parsers.python_parser import PythonParser
    from parsers.javascript_parser import JavaScriptParser
    from parsers.java_parser import JavaParser
except ImportError as e:
    PARSERS_AVAILABLE = False
    console.print(f"[yellow]Info: Parsers not fully available, using fallback mode[/yellow]")

try:
    from agents.base_agent import BaseAgent
    from agents.test_agent import TestAgent
    from agents.refactor_agent import RefactorAgent
    from agents.debug_agent import DebugAgent
    from agents.output_agent import OutputAgent
    from agents.parser_agent import ParserAgent
    from agents.planner_agent import PlannerAgent
    from agents.control_agent import ControlAgent
except ImportError as e:
    AGENTS_AVAILABLE = False
    console.print(f"[yellow]Info: Agents not fully available, using fallback mode[/yellow]")


# Fallback classes for when parsers/agents are not available
class FallbackParser:
    """Fallback parser when actual parsers are not available"""
    def parse(self, content, file_path):
        return {
            'file_path': file_path,
            'content': content,
            'lines': len(content.split('\n')),
            'chars': len(content),
            'parsed': True,
            'type': 'fallback'
        }

class FallbackAgent:
    """Fallback agent when actual agents are not available"""
    def process(self, parsed_data, project_path):
        return {
            'status': 'completed',
            'agent': 'Fallback Agent',
            'files_processed': len(parsed_data),
            'project_path': project_path,
            'message': f"Basic processing completed for {len(parsed_data)} files",
            'note': 'Install proper agents for enhanced functionality'
        }

class CLIHandler:
    """Handles CLI interactions, file parsing, and agent coordination"""
    
    def __init__(self):
        self.services = {
            '1': {'name': 'Testing Services', 'emoji': '🧪', 'desc': 'Run tests, generate test cases', 'agent': 'test'},
            '2': {'name': 'Code Refactoring', 'emoji': '🔧', 'desc': 'Improve and optimize code structure', 'agent': 'refactor'},
            '3': {'name': 'Debug Assistant', 'emoji': '🐛', 'desc': 'Find and fix bugs in your code', 'agent': 'debug'},
            '4': {'name': 'Documentation', 'emoji': '📚', 'desc': 'Generate docs and comments', 'agent': 'output'},
            '5': {'name': 'Code Analysis', 'emoji': '🔍', 'desc': 'Analyze and parse code structure', 'agent': 'parser'},
            '6': {'name': 'Project Planning', 'emoji': '📋', 'desc': 'Plan development tasks', 'agent': 'planner'},
        }
        
        self.parsers = {
            '.py': 'python',
            '.js': 'javascript', 
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.java': 'java',
        }
        
        self.current_path = None
        self.parsed_data = None
    
    def show_banner(self):
        """Display welcome banner"""
        banner = Panel.fit(
            Text.assemble(
                ("🚀 ", "bold blue"),
                ("Code Assist", "bold blue"),
                ("\n"),
                ("AI-powered Development Companion", "dim cyan"),
                ("\n"),
                ("With Parser & Agent Integration", "dim yellow"),
                ("\n"),
                ("Version 1.0.0", "dim white")
            ),
            title="[bold green]Welcome[/bold green]",
            border_style="blue",
            padding=(1, 2)
        )
        console.print(Align.center(banner))
        console.print()
    
    def show_main_menu(self):
        """Display main service menu"""
        table = Table(
            title="[bold blue]🔧 Available Services[/bold blue]",
            show_header=True,
            header_style="bold magenta",
            border_style="blue"
        )
        
        table.add_column("Option", style="bold cyan", width=8)
        table.add_column("Service", style="bold white", width=25)
        table.add_column("Description", style="dim white")
        table.add_column("Agent", style="bold green", width=12)
        
        for key, service in self.services.items():
            table.add_row(
                f"[{key}]",
                f"{service['emoji']} {service['name']}",
                service['desc'],
                f"🤖 {service['agent']}_agent"
            )
        
        table.add_row("[q]", "🚪 Quit", "Exit the application", "")
        
        console.print(table)
        console.print()
    
    def get_user_choice(self):
        """Get user's service selection"""
        valid_choices = list(self.services.keys()) + ['q', 'quit', 'exit']
        
        choice = Prompt.ask(
            "[bold yellow]Select a service[/bold yellow]",
            choices=valid_choices,
            default="1"
        ).lower()
        
        return choice
    
    def get_file_or_folder_path(self):
        """Get file or folder path from user"""
        console.print("\n[bold cyan]📁 File/Folder Selection[/bold cyan]")
        
        while True:
            path_input = Prompt.ask(
                "[yellow]Enter the path to your file or folder[/yellow]",
                default="."
            )
            
            path = Path(path_input).resolve()
            
            if not path.exists():
                console.print(f"[red]❌ Path does not exist: {path}[/red]")
                if not Confirm.ask("[yellow]Try again?[/yellow]"):
                    return None
                continue
            
            self.current_path = path
            console.print(f"[green]✅ Path selected: {path}[/green]")
            return path
    
    def detect_file_type(self, file_path):
        """Detect file type based on extension"""
        suffix = file_path.suffix.lower()
        return self.parsers.get(suffix, 'unknown')
    
    def get_parser(self, file_type):
        """Get appropriate parser for file type"""
        if not PARSERS_AVAILABLE:
            return FallbackParser()
            
        try:
            if file_type == 'python':
                return PythonParser()
            elif file_type == 'javascript':
                return JavaScriptParser()
            elif file_type == 'java':
                return JavaParser()
            else:
                return BaseParser()
        except:
            console.print(f"[yellow]Warning: Using fallback parser for {file_type}[/yellow]")
            return FallbackParser()
    
    def parse_files(self, path):
        """Parse files in the given path"""
        console.print("\n[bold blue]🔍 Analyzing Files...[/bold blue]")
        
        files_to_parse = []
        
        if path.is_file():
            files_to_parse = [path]
        else:
            # Get all code files in directory
            for ext in self.parsers.keys():
                files_to_parse.extend(path.rglob(f"*{ext}"))
        
        if not files_to_parse:
            console.print("[yellow]No supported files found![/yellow]")
            return None
        
        parsed_results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            for file_path in files_to_parse[:10]:  # Limit to 10 files for demo
                task = progress.add_task(f"Parsing {file_path.name}...", total=1)
                
                try:
                    file_type = self.detect_file_type(file_path)
                    parser = self.get_parser(file_type)
                    
                    # Parse the file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    parsed_data = parser.parse(content, str(file_path))
                    parsed_results[str(file_path)] = {
                        'type': file_type,
                        'data': parsed_data,
                        'size': len(content)
                    }
                    
                except Exception as e:
                    console.print(f"[red]Error parsing {file_path}: {e}[/red]")
                
                progress.update(task, advance=1)
        
        self.parsed_data = parsed_results
        return parsed_results
    
    def show_parsing_results(self, parsed_results):
        """Display parsing results"""
        if not parsed_results:
            return
        
        console.print("\n[bold green]✅ Parsing Complete![/bold green]")
        
        table = Table(
            title="[bold blue]📊 Parsed Files Summary[/bold blue]",
            show_header=True,
            header_style="bold magenta",
            border_style="green"
        )
        
        table.add_column("File", style="bold white")
        table.add_column("Type", style="bold cyan")
        table.add_column("Size", style="bold yellow")
        table.add_column("Status", style="bold green")
        
        for file_path, data in parsed_results.items():
            file_name = Path(file_path).name
            table.add_row(
                file_name,
                data['type'].upper(),
                f"{data['size']} chars",
                "✅ Parsed"
            )
        
        console.print(table)
    
    def get_agent(self, agent_type):
        """Get appropriate agent for the service"""
        if not AGENTS_AVAILABLE:
            return FallbackAgent()
            
        try:
            if agent_type == 'test':
                return TestAgent()
            elif agent_type == 'refactor':
                return RefactorAgent()
            elif agent_type == 'debug':
                return DebugAgent()
            elif agent_type == 'output':
                return OutputAgent()
            elif agent_type == 'parser':
                return ParserAgent()
            elif agent_type == 'planner':
                return PlannerAgent()
            else:
                return BaseAgent()
        except Exception as e:
            console.print(f"[yellow]Warning: Using fallback agent - {e}[/yellow]")
            return FallbackAgent()
    
    def execute_service(self, service_key):
        """Execute the selected service with parsing and agent integration"""
        service = self.services[service_key]
        service_name = service['name']
        agent_type = service['agent']
        
        console.print(f"\n[bold blue]🚀 Starting {service_name}[/bold blue]")
        
        # Step 1: Get file/folder path
        path = self.get_file_or_folder_path()
        if not path:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
        
        # Step 2: Parse files
        parsed_results = self.parse_files(path)
        if not parsed_results:
            console.print("[yellow]No files to process.[/yellow]")
            return
        
        # Step 3: Show parsing results
        self.show_parsing_results(parsed_results)
        
        # Step 4: Initialize and run agent
        console.print(f"\n[bold green]🤖 Initializing {agent_type.title()} Agent[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"Running {service_name}...", total=1)
            
            try:
                agent = self.get_agent(agent_type)
                
                # Pass parsed data to agent
                result = agent.process(parsed_results, str(path))
                
                progress.update(task, advance=1)
                
                # Display results
                self.show_agent_results(service_name, result)
                
            except Exception as e:
                console.print(f"[red]❌ Agent error: {e}[/red]")
    
    def show_agent_results(self, service_name, result):
        """Display agent processing results"""
        console.print(f"\n[bold green]✅ {service_name} Complete![/bold green]")
        
        if isinstance(result, dict):
            panel_content = ""
            for key, value in result.items():
                panel_content += f"[bold cyan]{key}:[/bold cyan] {value}\n"
        else:
            panel_content = str(result)
        
        console.print(Panel(
            panel_content,
            title=f"[bold green]📋 {service_name} Results[/bold green]",
            border_style="green"
        ))
    
    def continue_prompt(self):
        """Ask user if they want to continue"""
        console.print()
        return Confirm.ask(
            "[bold yellow]Would you like to use another service?[/bold yellow]",
            default=True
        )


# Initialize CLI handler
cli_handler = CLIHandler()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """🚀 Code Assist - AI-powered development companion with parser & agent integration"""
    if ctx.invoked_subcommand is None:
        # Interactive mode
        run_interactive_mode()


def run_interactive_mode():
    """Run the interactive CLI mode"""
    cli_handler.show_banner()
    
    while True:
        try:
            cli_handler.show_main_menu()
            choice = cli_handler.get_user_choice()
            
            if choice in ['q', 'quit', 'exit']:
                console.print("\n[bold green]👋 Thank you for using Code Assist![/bold green]")
                console.print("[dim]Goodbye![/dim]\n")
                break
            
            # Execute the selected service
            cli_handler.execute_service(choice)
            
            # Ask if user wants to continue
            if not cli_handler.continue_prompt():
                console.print("\n[bold green]👋 Thank you for using Code Assist![/bold green]")
                break
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Operation cancelled by user[/yellow]")
            console.print("[bold green]👋 Thank you for using Code Assist![/bold green]")
            break
        except Exception as e:
            console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
            if not cli_handler.continue_prompt():
                break


# Individual command functions (can be called directly with path)
@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def test(path):
    """🧪 Run testing services on specified path"""
    if path:
        cli_handler.current_path = Path(path)
        cli_handler.execute_service('1')
    else:
        cli_handler.execute_service('1')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def refactor(path):
    """🔧 Run refactoring services on specified path"""
    if path:
        cli_handler.current_path = Path(path)
        cli_handler.execute_service('2')
    else:
        cli_handler.execute_service('2')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def debug(path):
    """🐛 Run debugging services on specified path"""
    if path:
        cli_handler.current_path = Path(path)
        cli_handler.execute_service('3')
    else:
        cli_handler.execute_service('3')


@cli.command(name="docs")
@click.argument('path', type=click.Path(exists=True), required=False)
def documentation(path):
    """📚 Generate documentation for specified path"""
    if path:
        cli_handler.current_path = Path(path)
        cli_handler.execute_service('4')
    else:
        cli_handler.execute_service('4')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def analyze(path):
    """🔍 Analyze code structure for specified path"""
    if path:
        cli_handler.current_path = Path(path)
        cli_handler.execute_service('5')
    else:
        cli_handler.execute_service('5')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def plan(path):
    """📋 Plan development tasks for specified path"""
    if path:
        cli_handler.current_path = Path(path)
        cli_handler.execute_service('6')
    else:
        cli_handler.execute_service('6')


@cli.command(name="interactive")
def interactive_mode():
    """🎯 Run interactive mode"""
    run_interactive_mode()


if __name__ == "__main__":
    cli()