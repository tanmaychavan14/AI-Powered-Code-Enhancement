"""
Interactive CLI mode for guided workflows
"""
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.table import Table
from rich.text import Text

console = Console()


class InteractiveMode:
    """Interactive mode handler for guided workflows"""
    
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.current_path = Path.cwd()
    
    def run(self):
        """Main interactive loop"""
        console.clear()
        self._display_welcome()
        
        while True:
            try:
                choice = self._show_main_menu()
                
                if choice == 'quit':
                    console.print("\n👋 [bold blue]Thanks for using Code Assist![/bold blue]")
                    break
                elif choice == 'test':
                    self._test_workflow()
                elif choice == 'debug':
                    self._debug_workflow()
                elif choice == 'refactor':
                    self._refactor_workflow()
                elif choice == 'project':
                    self._project_overview()
                elif choice == 'settings':
                    self._settings_menu()
                    
            except KeyboardInterrupt:
                if Confirm.ask("\nAre you sure you want to exit?"):
                    break
                continue
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]")
                Prompt.ask("Press Enter to continue")
    
    def _display_welcome(self):
        """Display welcome message"""
        welcome_text = Text()
        welcome_text.append("🚀 Code Assist Interactive Mode\n", style="bold blue")
        welcome_text.append("Let's improve your code together!\n\n", style="dim")
        welcome_text.append(f"📂 Working Directory: ", style="dim")
        welcome_text.append(f"{self.current_path}", style="bold")
        
        console.print(Panel(welcome_text, title="Welcome", border_style="blue"))
    
    def _show_main_menu(self):
        """Display main menu and get user choice"""
        console.print("\n" + "="*50)
        console.print("🎯 [bold blue]What would you like to do?[/bold blue]")
        
        options = [
            ("1", "test", "🧪 Test Code", "Run and analyze tests"),
            ("2", "debug", "🐛 Debug Issues", "Debug failed tests"),
            ("3", "refactor", "🔧 Refactor Code", "Improve code quality"),
            ("4", "project", "📊 Project Overview", "View project status"),
            ("5", "settings", "⚙️ Settings", "Configure Code Assist"),
            ("6", "quit", "👋 Exit", "Exit interactive mode")
        ]
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="bold blue", width=3)
        table.add_column("", style="bold", width=20)
        table.add_column("", style="dim", width=30)
        
        for num, key, title, desc in options:
            table.add_row(num, title, desc)
        
        console.print(table)
        
        while True:
            choice = Prompt.ask("\nEnter your choice", choices=['1', '2', '3', '4', '5', '6'])
            choice_map = {opt[0]: opt[1] for opt in options}
            return choice_map[choice]
    
    def _test_workflow(self):
        """Interactive test workflow"""
        console.print("\n🧪 [bold blue]Test Workflow[/bold blue]")
        
        # Get test path
        test_path = Prompt.ask(
            "Test path", 
            default=str(self.current_path),
            show_default=True
        )
        
        # Get test pattern
        test_pattern = Prompt.ask(
            "Test pattern",
            default="test_*.py",
            show_default=True
        )
        
        # Get framework
        framework = Prompt.ask(
            "Test framework",
            choices=['pytest', 'unittest'],
            default='pytest'
        )
        
        # Coverage option
        coverage = Confirm.ask("Generate coverage report?", default=False)
        
        console.print(f"\n📋 [bold]Test Configuration:[/bold]")
        console.print(f"• Path: {test_path}")
        console.print(f"• Pattern: {test_pattern}")
        console.print(f"• Framework: {framework}")
        console.print(f"• Coverage: {coverage}")
        
        if Confirm.ask("\nRun tests with these settings?"):
            console.print("\n🚀 Running tests...")
            # Here you would call the actual test command
            # For now, show a placeholder
            console.print("✅ [green]Tests completed! (This is a placeholder)[/green]")
        
        Prompt.ask("\nPress Enter to continue")
    
    def _debug_workflow(self):
        """Interactive debug workflow"""
        console.print("\n🐛 [bold blue]Debug Workflow[/bold blue]")
        
        # Find test files
        test_files = list(self.current_path.rglob("test_*.py"))
        test_files.extend(list(self.current_path.rglob("*_test.py")))
        
        if not test_files:
            console.print("[yellow]No test files found in current directory[/yellow]")
            Prompt.ask("Press Enter to continue")
            return
        
        # Show available test files
        console.print("\n📁 [bold]Available test files:[/bold]")
        for i, file in enumerate(test_files[:10], 1):  # Show max 10 files
            console.print(f"{i}. {file.relative_to(self.current_path)}")
        
        if len(test_files) > 10:
            console.print(f"... and {len(test_files) - 10} more")
        
        # Let user choose or enter custom path
        choice = Prompt.ask(
            "\nEnter file number or custom path",
            default="1"
        )
        
        try:
            file_index = int(choice) - 1
            if 0 <= file_index < len(test_files):
                selected_file = test_files[file_index]
            else:
                selected_file = Path(choice)
        except ValueError:
            selected_file = Path(choice)
        
        # Get specific test function (optional)
        target_function = Prompt.ask(
            "Specific test function to debug (optional)",
            default=""
        )
        
        # Verbose logs option
        verbose = Confirm.ask("Show verbose logs?", default=True)
        
        console.print(f"\n📋 [bold]Debug Configuration:[/bold]")
        console.print(f"• File: {selected_file}")
        if target_function:
            console.print(f"• Function: {target_function}")
        console.print(f"• Verbose: {verbose}")
        
        if Confirm.ask("\nStart debugging?"):
            console.print("\n🔍 Analyzing test failures...")
            # Here you would call the actual debug command
            console.print("✅ [green]Debug analysis completed! (This is a placeholder)[/green]")
        
        Prompt.ask("\nPress Enter to continue")
    
    def _refactor_workflow(self):
        """Interactive refactor workflow"""
        console.print("\n🔧 [bold blue]Refactor Workflow[/bold blue]")
        
        # Get file to refactor
        file_path = Prompt.ask(
            "File to refactor",
            default="."
        )
        
        # Get refactor type
        refactor_type = Prompt.ask(
            "Refactoring type",
            choices=['optimize', 'clean', 'modernize'],
            default='optimize'
        )
        
        # Options
        backup = Confirm.ask("Create backup before refactoring?", default=True)
        dry_run = Confirm.ask("Preview changes only (dry run)?", default=True)
        
        console.print(f"\n📋 [bold]Refactor Configuration:[/bold]")
        console.print(f"• File: {file_path}")
        console.print(f"• Type: {refactor_type}")
        console.print(f"• Backup: {backup}")
        console.print(f"• Dry Run: {dry_run}")
        
        if Confirm.ask("\nStart refactoring analysis?"):
            console.print("\n🔍 Analyzing code for improvements...")
            # Here you would call the actual refactor command
            console.print("✅ [green]Refactoring analysis completed! (This is a placeholder)[/green]")
        
        Prompt.ask("\nPress Enter to continue")
    
    def _project_overview(self):
        """Show project overview"""
        console.print("\n📊 [bold blue]Project Overview[/bold blue]")
        
        # Project stats
        python_files = list(self.current_path.rglob("*.py"))
        test_files = [f for f in python_files if 'test' in f.name]
        
        stats_table = Table(title="Project Statistics", show_header=True, header_style="bold blue")
        stats_table.add_column("Metric", style="white")
        stats_table.add_column("Count", justify="right", style="green")
        
        stats_table.add_row("Python Files", str(len(python_files)))
        stats_table.add_row("Test Files", str(len(test_files)))
        stats_table.add_row("Directories", str(len([d for d in self.current_path.rglob("*") if d.is_dir()])))
        
        console.print(stats_table)
        
        # Recent files
        if python_files:
            console.print("\n📄 [bold]Recent Python Files:[/bold]")
            for file in sorted(python_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]:
                rel_path = file.relative_to(self.current_path)
                console.print(f"• {rel_path}")
        
        Prompt.ask("\nPress Enter to continue")
    
    def _settings_menu(self):
        """Settings configuration menu"""
        console.print("\n⚙️ [bold blue]Settings[/bold blue]")
        
        settings_options = [
            ("1", "ai", "🤖 AI Provider Settings"),
            ("2", "test", "🧪 Test Configuration"),
            ("3", "paths", "📁 Path Settings"),
            ("4", "back", "← Back to Main Menu")
        ]
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("", style="bold blue", width=3)
        table.add_column("", style="bold", width=25)
        
        for num, key, title in settings_options:
            table.add_row(num, title)
        
        console.print(table)
        
        choice = Prompt.ask("\nEnter your choice", choices=['1', '2', '3', '4'])
        
        if choice == '1':
            self._ai_settings()
        elif choice == '2':
            self._test_settings()
        elif choice == '3':
            self._path_settings()
        # choice == '4' returns to main menu
    
    def _ai_settings(self):
        """AI provider settings"""
        console.print("\n🤖 [bold blue]AI Provider Settings[/bold blue]")
        
        current_provider = getattr(self.config, 'ai_provider', 'gemini')
        current_model = getattr(self.config, 'ai_model', 'gemini-pro')
        
        console.print(f"Current Provider: [bold]{current_provider}[/bold]")
        console.print(f"Current Model: [bold]{current_model}[/bold]")
        
        if Confirm.ask("\nChange AI settings?"):
            # Provider selection
            provider = Prompt.ask(
                "AI Provider",
                choices=['gemini', 'openai', 'claude'],
                default=current_provider
            )
            
            # Model selection based on provider
            if provider == 'gemini':
                model = Prompt.ask(
                    "Gemini Model",
                    choices=['gemini-pro', 'gemini-pro-vision'],
                    default='gemini-pro'
                )
            elif provider == 'openai':
                model = Prompt.ask(
                    "OpenAI Model",
                    choices=['gpt-4', 'gpt-3.5-turbo'],
                    default='gpt-4'
                )
            else:  # claude
                model = Prompt.ask(
                    "Claude Model",
                    choices=['claude-3-opus', 'claude-3-sonnet'],
                    default='claude-3-sonnet'
                )
            
            # API Key check
            api_key_var = f"{provider.upper()}_API_KEY"
            if not os.getenv(api_key_var):
                console.print(f"[yellow]Warning: {api_key_var} environment variable not found[/yellow]")
                if Confirm.ask("Set it now?"):
                    api_key = Prompt.ask(f"Enter {provider} API key", password=True)
                    # In a real implementation, you'd save this securely
                    console.print("[green]API key would be saved securely[/green]")
            
            console.print(f"\n✅ AI settings updated:")
            console.print(f"• Provider: {provider}")
            console.print(f"• Model: {model}")
        
        Prompt.ask("\nPress Enter to continue")
    
    def _test_settings(self):
        """Test configuration settings"""
        console.print("\n🧪 [bold blue]Test Configuration[/bold blue]")
        
        current_framework = getattr(self.config, 'test_framework', 'pytest')
        current_patterns = getattr(self.config, 'test_patterns', ['test_*.py'])
        
        console.print(f"Current Framework: [bold]{current_framework}[/bold]")
        console.print(f"Current Patterns: [bold]{', '.join(current_patterns)}[/bold]")
        
        if Confirm.ask("\nChange test settings?"):
            # Framework
            framework = Prompt.ask(
                "Test Framework",
                choices=['pytest', 'unittest'],
                default=current_framework
            )
            
            # Test patterns
            console.print("\n📋 Configure test file patterns:")
            patterns = []
            while True:
                pattern = Prompt.ask(
                    f"Test pattern {len(patterns) + 1} (or press Enter to finish)",
                    default=""
                )
                if not pattern:
                    break
                patterns.append(pattern)
            
            if not patterns:
                patterns = current_patterns
            
            # Coverage settings
            coverage_enabled = Confirm.ask("Enable coverage by default?", default=True)
            coverage_threshold = None
            if coverage_enabled:
                coverage_threshold = IntPrompt.ask(
                    "Coverage threshold (%)",
                    default=80,
                    show_default=True
                )
            
            console.print(f"\n✅ Test settings updated:")
            console.print(f"• Framework: {framework}")
            console.print(f"• Patterns: {', '.join(patterns)}")
            console.print(f"• Coverage: {coverage_enabled}")
            if coverage_threshold:
                console.print(f"• Coverage Threshold: {coverage_threshold}%")
        
        Prompt.ask("\nPress Enter to continue")
    
    def _path_settings(self):
        """Path and exclusion settings"""
        console.print("\n📁 [bold blue]Path Settings[/bold blue]")
        
        current_excludes = getattr(self.config, 'exclude_patterns', ['__pycache__', '*.pyc', '.git'])
        
        console.print("Current exclusion patterns:")
        for pattern in current_excludes:
            console.print(f"• {pattern}")
        
        if Confirm.ask("\nChange path settings?"):
            # Working directory
            if Confirm.ask("Change working directory?"):
                new_path = Prompt.ask(
                    "New working directory",
                    default=str(self.current_path)
                )
                self.current_path = Path(new_path).resolve()
                console.print(f"Working directory changed to: {self.current_path}")
            
            # Exclusion patterns
            if Confirm.ask("Modify exclusion patterns?"):
                console.print("\n📋 Configure exclusion patterns:")
                excludes = []
                
                # Add existing patterns with option to keep
                for pattern in current_excludes:
                    if Confirm.ask(f"Keep pattern '{pattern}'?", default=True):
                        excludes.append(pattern)
                
                # Add new patterns
                while True:
                    pattern = Prompt.ask(
                        f"New exclusion pattern {len(excludes) - len([p for p in current_excludes if p in excludes]) + 1} (or press Enter to finish)",
                        default=""
                    )
                    if not pattern:
                        break
                    excludes.append(pattern)
                
                console.print(f"\n✅ Exclusion patterns updated:")
                for pattern in excludes:
                    console.print(f"• {pattern}")
        
        Prompt.ask("\nPress Enter to continue")