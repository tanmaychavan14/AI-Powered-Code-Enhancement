#!/usr/bin/env python3
"""
Test-Debug Integration Module
Coordinates testing and debugging workflow
"""

from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

console = Console()

class TestDebugCoordinator:
    """Coordinates the test-debug workflow"""
    
    def __init__(self, test_agent, debug_agent, output_agent):
        self.test_agent = test_agent
        self.debug_agent = debug_agent
        self.output_agent = output_agent
        self.console = Console()
    
    # def run_test_and_debug_workflow(self, parsed_data: Dict[str, Any], 
    #                                 project_path: str) -> Dict[str, Any]:
    #     """
    #     Complete workflow: test generation → execution → debugging
    #     """
    #     console.print("\n[bold cyan]🚀 Starting Test-Debug Workflow[/bold cyan]\n")
        
    #     workflow_results = {
    #         'test_results': None,
    #         'debug_results': None,
    #         'workflow_completed': False
    #     }
        
    #     # Step 1: Generate and run tests
    #     console.print("[bold blue]Step 1: Test Generation & Execution[/bold blue]")
    #     test_results = self.test_agent.generate_tests(parsed_data)
    #     workflow_results['test_results'] = test_results
        
    #     if 'error' in test_results:
    #         console.print(f"[red]❌ Testing failed: {test_results['error']}[/red]")
    #         return workflow_results
        
    #     # Step 2: Check if debugging is needed
    #     tests_failed = test_results.get('tests_failed', 0)
        
    #     if tests_failed == 0:
    #         console.print("\n[bold green]🎉 All tests passed! No debugging needed.[/bold green]")
    #         workflow_results['workflow_completed'] = True
    #         return workflow_results
        
    #     # Step 3: Prompt for debugging
    #     console.print(f"\n[yellow]⚠️  Found {tests_failed} failing test(s)[/yellow]")
        
    #     # Show debugging prompt
    #     self._show_debugging_prompt(test_results)
        
    #     # Ask user if they want auto-debug
    #     should_debug = Confirm.ask(
    #         "\n[bold cyan]Would you like to auto-debug with AI?[/bold cyan]",
    #         default=True
    #     )
        
    #     if not should_debug:
    #         console.print("\n[dim]Skipping debug. You can run debug manually later.[/dim]")
    #         workflow_results['workflow_completed'] = True
    #         return workflow_results
        
    #     # Step 4: Run debugging
    #     console.print("\n[bold blue]Step 2: AI-Powered Debugging[/bold blue]")
    #     debug_results = self.debug_agent.analyze_and_fix(test_results, parsed_data)
    #     workflow_results['debug_results'] = debug_results
        
    #     # Step 5: Show final summary
    #     self._show_final_summary(test_results, debug_results)
        
    #     workflow_results['workflow_completed'] = True
    #     return workflow_results
    

    def run_test_and_debug_workflow(self, parsed_data: Dict[str, Any], 
                                project_path: str) -> Dict[str, Any]:
     """
     Complete workflow: test generation → execution → debugging
     """
     console.print("\n[bold cyan]🚀 Starting Test-Debug Workflow[/bold cyan]\n")
    
     workflow_results = {
        'test_results': None,
        'debug_results': None,
        'workflow_completed': False
     }
    
    # Step 1: Generate and run tests
     console.print("[bold blue]Step 1: Test Generation & Execution[/bold blue]")
     test_results = self.test_agent.generate_tests(parsed_data)
     workflow_results['test_results'] = test_results
    
    # ✅ Check if test generation failed
     if 'error' in test_results:
        console.print(f"[red]❌ Testing failed: {test_results['error']}[/red]")
        workflow_results['workflow_completed'] = False
        return workflow_results
    
    # Step 2: Check if debugging is needed
     tests_failed = test_results.get('tests_failed', 0)
    
    # ✅ Handle successful case (no failures)
     if tests_failed == 0:
        console.print("\n[bold green]🎉 All tests passed! No debugging needed.[/bold green]")
        workflow_results['workflow_completed'] = True
        return workflow_results
    
    # Step 3: Prompt for debugging (only if there are failures)
     console.print(f"\n[yellow]⚠️  Found {tests_failed} failing test(s)[/yellow]")
    
    # Show debugging prompt
     self._show_debugging_prompt(test_results)
    
    # Ask user if they want auto-debug
     should_debug = Confirm.ask(
        "\n[bold cyan]Would you like to auto-debug with AI?[/bold cyan]",
        default=True
     )
    
     if not should_debug:
        console.print("\n[dim]Skipping debug. You can run debug manually later.[/dim]")
        workflow_results['workflow_completed'] = True
        return workflow_results
    
    # Step 4: Run debugging
     console.print("\n[bold blue]Step 2: AI-Powered Debugging[/bold blue]")
     debug_results = self.debug_agent.analyze_and_fix(test_results, parsed_data)
     workflow_results['debug_results'] = debug_results
    
    # Step 5: Show final summary
     self._show_final_summary(test_results, debug_results)
    
     workflow_results['workflow_completed'] = True
     return workflow_results
    
    def _show_debugging_prompt(self, test_results: Dict[str, Any]):
        """Show detailed debugging prompt"""
        failed_tests = test_results.get('failed_tests', [])
        failed_functions = test_results.get('functions_with_failures', [])
        
        prompt_text = f"""[bold yellow]Debugging Available[/bold yellow]

[cyan]Failed Tests:[/cyan] {len(failed_tests)}
[cyan]Failed Functions:[/cyan] {', '.join(failed_functions[:5])}

[dim]The Debug Agent can:[/dim]
• Analyze each test failure
• Identify the root cause
• Generate corrected code
• Explain the fix

"""
        
        prompt_panel = Panel(
            prompt_text,
            title="[bold]🔧 Debug Assistant[/bold]",
            border_style="yellow",
            padding=(1, 2)
        )
        
        console.print(prompt_panel)
    
    def _show_final_summary(self, test_results: Dict[str, Any], 
                           debug_results: Dict[str, Any]):
        """Show final workflow summary"""
        console.print("\n" + "="*70)
        console.print("[bold green]✅ WORKFLOW COMPLETED[/bold green]")
        console.print("="*70 + "\n")
        
        # Test summary
        console.print("[bold cyan]📊 Test Results:[/bold cyan]")
        console.print(f"   • Tests Generated: {test_results.get('tests_generated', 0)}")
        console.print(f"   • Tests Passed: {test_results.get('tests_passed', 0)}")
        console.print(f"   • Tests Failed: {test_results.get('tests_failed', 0)}")
        
        # Debug summary
        if debug_results:
            console.print(f"\n[bold cyan]🔧 Debug Results:[/bold cyan]")
            console.print(f"   • Bugs Analyzed: {debug_results.get('bugs_found', 0)}")
            console.print(f"   • Fixes Generated: {debug_results.get('fixes_generated', 0)}")
            console.print(f"   • Fixed Functions: {', '.join(debug_results.get('fixed_functions', []))}")
        
        # Next steps
        next_steps = """
[bold yellow]📋 Next Steps:[/bold yellow]

1. Review generated fixes in [cyan]debug/fixes/[/cyan]
2. Apply fixes to your source code
3. Re-run tests to verify fixes
4. Iterate if needed

[dim]Tip: You can re-run the debug agent anytime with the 'debug' command[/dim]
"""
        
        next_steps_panel = Panel(
            next_steps,
            title="[bold]What's Next?[/bold]",
            border_style="green"
        )
        
        console.print(next_steps_panel)


# Integration into Control Agent
# Add this method to your ControlAgent class:

def _handle_testing_request_with_debug(self, parsed_data: Dict[str, Any], 
                                       project_path: str) -> Dict[str, Any]:
    """
    Enhanced testing handler with integrated debugging
    Replace the existing _handle_testing_request with this
    """
    try:
        console.print("[bold cyan]  Running Testing Services with Debug Integration...[/bold cyan]")
        
        # Show what files we're testing
        self.output_agent.display_file_tree(parsed_data, "Files to Test")
        
        # Create coordinator
        from agents.test_debug_integration import TestDebugCoordinator
        coordinator = TestDebugCoordinator(
            self.test_agent,
            self.debug_agent,
            self.output_agent
        )
        
        # Run complete workflow
        workflow_results = coordinator.run_test_and_debug_workflow(
            parsed_data,
            project_path
        )
        
        test_results = workflow_results['test_results']
        debug_results = workflow_results.get('debug_results')
        
        # Create comprehensive results
        results = {
            'service': 'Testing with Debug Integration',
            'project_path': project_path,
            'files_analyzed': len(parsed_data),
            'tests_generated': test_results.get('tests_generated', 0),
            'tests_passed': test_results.get('tests_passed', 0),
            'tests_failed': test_results.get('tests_failed', 0),
            'functions_analyzed': test_results.get('functions_analyzed', 0),
            'classes_analyzed': test_results.get('classes_analyzed', 0),
            'status': 'completed',
            'workflow_completed': workflow_results['workflow_completed']
        }
        
        # Add debug info if available
        if debug_results:
            results.update({
                'bugs_fixed': debug_results.get('fixes_generated', 0),
                'fix_files': debug_results.get('fix_files', []),
                'debug_status': 'completed'
            })
        
        return results
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        return {'error': f"Testing service failed: {str(e)}"}