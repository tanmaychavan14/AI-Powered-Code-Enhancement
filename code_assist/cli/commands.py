#!/usr/bin/env python3
"""
Code Assist CLI - Simplified version that routes everything through Control Agent
AI-powered development companion with parser and agent integration
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich.align import Align
import time
import sys
import os
from pathlib import Path

# Initialize console
console = Console()

# Import control agent with fallback
CONTROL_AGENT_AVAILABLE = True

try:
    from agents.control_agent import ControlAgent
except ImportError:
    CONTROL_AGENT_AVAILABLE = False
    console.print(f"[yellow]Info: Control agent not available, using fallback mode[/yellow]")

class FallbackControlAgent:
    """Fallback control agent when actual control agent is not available"""
    
    def process_request(self, service_type, target_path):
        return {
            'status': 'completed',
            'service': service_type,
            'files_processed': 1,
            'results': {
                'message': f'Basic {service_type} processing completed for {target_path}',
                'note': 'Install proper control agent for enhanced functionality'
            }
        }

class SimplifiedCLI:
    """Simplified CLI that routes everything through Control Agent"""
    
    def __init__(self):
        # Initialize control agent
        if CONTROL_AGENT_AVAILABLE:
            self.control_agent = ControlAgent()
        else:
            self.control_agent = FallbackControlAgent()
        
        self.services = {
            '1': {'name': 'Testing Services', 'emoji': '🧪', 'desc': 'Run tests, generate test cases'},
            '2': {'name': 'Code Refactoring', 'emoji': '🔧', 'desc': 'Improve and optimize code structure'},
            '3': {'name': 'Debug Assistant', 'emoji': '🐛', 'desc': 'Find and fix bugs in your code'},
            '4': {'name': 'Documentation', 'emoji': '📚', 'desc': 'Generate docs and comments'},
            '5': {'name': 'Code Analysis', 'emoji': '🔍', 'desc': 'Analyze and parse code structure'},
            
        }
    
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
                f"🤖 via_control"
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
            
            console.print(f"[green]✅ Path selected: {path}[/green]")
            return str(path)
    
    def execute_service(self, service_key):
        """Execute the selected service by routing through Control Agent"""
        service = self.services[service_key]
        service_name = service['name']
        
        console.print(f"\n[bold blue]🚀 Starting {service_name}[/bold blue]")
        
        # Step 1: Get file/folder path from user
        target_path = self.get_file_or_folder_path()
        if not target_path:
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
        
        # Step 2: Route everything through Control Agent
        console.print(f"\n[bold green]🤖 Initializing Control Agent[/bold green]")
        
        try:
            # Let control agent handle everything: parsing, agent routing, and results
            result = self.control_agent.process_request(service_key, target_path)
            
            if result['status'] == 'error':
                console.print(f"[red]❌ Service failed: {result['error']}[/red]")
            else:
                console.print(f"[bold green]✅ {service_name} completed successfully![/bold green]")
                
        except Exception as e:
            console.print(f"[red]❌ Unexpected error: {e}[/red]")
    
    def continue_prompt(self):
        """Ask user if they want to continue"""
        console.print()
        return Confirm.ask(
            "[bold yellow]Would you like to use another service?[/bold yellow]",
            default=True
        )
    
    def run_interactive_mode(self):
        """Run the interactive CLI mode"""
        self.show_banner()
        
        while True:
            try:
                self.show_main_menu()
                choice = self.get_user_choice()
                
                if choice in ['q', 'quit', 'exit']:
                    console.print("\n[bold green]👋 Thank you for using Code Assist![/bold green]")
                    console.print("[dim]Goodbye![/dim]\n")
                    break
                
                # Execute the selected service via Control Agent
                self.execute_service(choice)
                
                # Ask if user wants to continue
                if not self.continue_prompt():
                    console.print("\n[bold green]👋 Thank you for using Code Assist![/bold green]")
                    break
                    
            except KeyboardInterrupt:
                console.print("\n\n[yellow]Operation cancelled by user[/yellow]")
                console.print("[bold green]👋 Thank you for using Code Assist![/bold green]")
                break
            except Exception as e:
                console.print(f"\n[bold red]❌ Error: {e}[/bold red]")
                if not self.continue_prompt():
                    break


# Initialize CLI handler
cli_handler = SimplifiedCLI()


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """🚀 Code Assist - AI-powered development companion with parser & agent integration"""
    if ctx.invoked_subcommand is None:
        # Interactive mode
        cli_handler.run_interactive_mode()


# Individual command functions (can be called directly with path)
@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def test(path):
    """🧪 Run testing services on specified path"""
    if path:
        result = cli_handler.control_agent.process_request('test', str(Path(path).resolve()))
        if result['status'] == 'error':
            console.print(f"[red]❌ Testing failed: {result['error']}[/red]")
        else:
            console.print(f"[green]✅ Testing completed for {path}[/green]")
    else:
        cli_handler.execute_service('1')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def refactor(path):
    """🔧 Run refactoring services on specified path"""
    if path:
        result = cli_handler.control_agent.process_request('refactor', str(Path(path).resolve()))
        if result['status'] == 'error':
            console.print(f"[red]❌ Refactoring failed: {result['error']}[/red]")
        else:
            console.print(f"[green]✅ Refactoring completed for {path}[/green]")
    else:
        cli_handler.execute_service('2')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def debug(path):
    """🐛 Run debugging services on specified path"""
    if path:
        result = cli_handler.control_agent.process_request('debug', str(Path(path).resolve()))
        if result['status'] == 'error':
            console.print(f"[red]❌ Debugging failed: {result['error']}[/red]")
        else:
            console.print(f"[green]✅ Debugging completed for {path}[/green]")
    else:
        cli_handler.execute_service('3')


@cli.command(name="docs")
@click.argument('path', type=click.Path(exists=True), required=False)
def documentation(path):
    """📚 Generate documentation for specified path"""
    if path:
        result = cli_handler.control_agent.process_request('docs', str(Path(path).resolve()))
        if result['status'] == 'error':
            console.print(f"[red]❌ Documentation failed: {result['error']}[/red]")
        else:
            console.print(f"[green]✅ Documentation completed for {path}[/green]")
    else:
        cli_handler.execute_service('4')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def analyze(path):
    """🔍 Analyze code structure for specified path"""
    if path:
        result = cli_handler.control_agent.process_request('analyze', str(Path(path).resolve()))
        if result['status'] == 'error':
            console.print(f"[red]❌ Analysis failed: {result['error']}[/red]")
        else:
            console.print(f"[green]✅ Analysis completed for {path}[/green]")
    else:
        cli_handler.execute_service('5')


@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
def plan(path):
    """📋 Plan development tasks for specified path"""
    if path:
        result = cli_handler.control_agent.process_request('plan', str(Path(path).resolve()))
        if result['status'] == 'error':
            console.print(f"[red]❌ Planning failed: {result['error']}[/red]")
        else:
            console.print(f"[green]✅ Planning completed for {path}[/green]")
    else:
        cli_handler.execute_service('6')


@cli.command(name="interactive")
def interactive_mode():
    """🎯 Run interactive mode"""
    cli_handler.run_interactive_mode()


if __name__ == "__main__":
    cli()