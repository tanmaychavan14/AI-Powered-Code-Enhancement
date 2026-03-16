# #!/usr/bin/env python3
# """
# Debug Agent - AI-powered debugging and code fixing
# Analyzes test failures and generates corrected code using Gemini
# """

# import os
# import json
# from pathlib import Path
# from typing import Dict, List, Any, Optional
# from rich.console import Console
# from rich.panel import Panel
# from rich.table import Table
# from rich.syntax import Syntax

# from utils.gemini_client import GeminiClient

# console = Console()

# class DebugAgent:
#     """Agent responsible for analyzing bugs and suggesting fixes"""
    
#     def __init__(self):
#         self.console = Console()
#         self.gemini_client = self._initialize_llm()
#         self.llm_available = self.gemini_client is not None
#         self.fixes_dir = Path("debug/fixes")
#         self.fixes_dir.mkdir(parents=True, exist_ok=True)
    
#     def _initialize_llm(self) -> Optional[GeminiClient]:
#         """Initialize LLM client"""
#         try:
#             gemini_client = GeminiClient()
            
#             if gemini_client.model is None:
#                 console.print("[red]❌ LLM initialization failed[/red]")
#                 return None
            
#             console.print("[green]✅ Debug Agent LLM initialized[/green]")
#             return gemini_client
            
#         except Exception as e:
#             console.print(f"[red]❌ LLM initialization error: {e}[/red]")
#             return None
    
#     def analyze_and_fix(self, test_results: Dict[str, Any], parsed_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Main method to analyze test failures and generate fixes
        
#         Args:
#             test_results: Results from test execution with failure details
#             parsed_data: Original parsed source code data
        
#         Returns:
#             Dictionary with fixes and debugging information
#         """
#         console.print("\n[bold cyan]🔍 Starting Debug Analysis...[/bold cyan]\n")
        
#         if not self.llm_available:
#             console.print("[red]❌ LLM unavailable - cannot generate fixes[/red]")
#             return {
#                 'success': False,
#                 'error': 'LLM not available for debugging'
#             }
        
#         debug_results = {
#             'success': True,
#             'files_analyzed': 0,
#             'bugs_found': 0,
#             'fixes_generated': 0,
#             'fixed_functions': [],
#             'fix_files': [],
#             'analysis_details': []
#         }
        
#         # Extract failed tests
#         failed_tests = test_results.get('failed_tests', [])
        
#         if not failed_tests:
#             console.print("[green]✅ No test failures to debug![/green]")
#             return debug_results
        
#         console.print(f"[yellow]Analyzing {len(failed_tests)} failed test(s)...[/yellow]\n")
        
#         # Group failures by file
#         failures_by_file = self._group_failures_by_file(failed_tests)
        
#         # Process each file
#         for file_path, failures in failures_by_file.items():
#             console.print(f"\n[bold blue]📁 Processing: {Path(file_path).name}[/bold blue]")
            
#             # Get original source code
#             file_data = parsed_data.get(file_path)
#             if not file_data:
#                 console.print(f"[red]⚠️  Could not find source: {file_path}[/red]")
#                 continue
            
#             source_code = file_data.get('content', '')
#             language = file_data.get('language', 'unknown')
            
#             # Analyze and fix each failed function
#             for failure in failures:
#                 fix_result = self._analyze_and_fix_function(
#                     failure,
#                     source_code,
#                     language,
#                     file_path
#                 )
                
#                 if fix_result['success']:
#                     debug_results['fixes_generated'] += 1
#                     debug_results['fixed_functions'].append(fix_result['function_name'])
#                     debug_results['fix_files'].append(fix_result['fix_file'])
#                     debug_results['analysis_details'].append(fix_result)
                    
#                     self._display_fix(fix_result)
                
#                 debug_results['bugs_found'] += 1
            
#             debug_results['files_analyzed'] += 1
        
#         # Display summary
#         self._display_debug_summary(debug_results)
        
#         return debug_results
    
#     def _group_failures_by_file(self, failed_tests: List[Dict]) -> Dict[str, List[Dict]]:
#         """Group test failures by source file"""
#         grouped = {}
        
#         for failure in failed_tests:
#             file_path = failure.get('file', 'unknown')
#             if file_path not in grouped:
#                 grouped[file_path] = []
#             grouped[file_path].append(failure)
        
#         return grouped
    
#     def _analyze_and_fix_function(self, failure: Dict, source_code: str, 
#                                   language: str, file_path: str) -> Dict[str, Any]:
#         """
#         Analyze a specific function failure and generate a fix
#         """
#         function_name = failure.get('original_function', 'Unknown')
#         test_name = failure.get('test_name', '')
#         error_info = failure.get('error_snippet', '')
        
#         console.print(f"\n[cyan]🔧 Analyzing: {function_name}[/cyan]")
        
#         # Extract the specific function code
#         function_code = self._extract_function_code(source_code, function_name, language)
        
#         if not function_code:
#             console.print(f"[yellow]⚠️  Could not extract function code[/yellow]")
#             return {'success': False}
        
#         # Generate fix using Gemini
#         fix_prompt = self._create_debug_prompt(
#             function_name,
#             function_code,
#             test_name,
#             error_info,
#             language
#         )
        
#         try:
#             console.print(f"[dim]Asking Gemini for fix...[/dim]")
            
#             response = self.gemini_client.generate_content(fix_prompt)
            
#             if not response or not hasattr(response, 'text'):
#                 return {'success': False, 'error': 'No response from LLM'}
            
#             fixed_code = self._extract_fixed_code(response.text, language)
            
#             if not fixed_code:
#                 return {'success': False, 'error': 'Could not extract fixed code'}
            
#             # Save the fix
#             fix_file = self._save_fix(
#                 function_name,
#                 fixed_code,
#                 file_path,
#                 language
#             )
            
#             # Extract explanation
#             explanation = self._extract_explanation(response.text)
            
#             return {
#                 'success': True,
#                 'function_name': function_name,
#                 'original_code': function_code,
#                 'fixed_code': fixed_code,
#                 'explanation': explanation,
#                 'fix_file': str(fix_file),
#                 'test_error': error_info
#             }
            
#         except Exception as e:
#             console.print(f"[red]Error generating fix: {e}[/red]")
#             return {'success': False, 'error': str(e)}
    
#     def _extract_function_code(self, source_code: str, function_name: str, language: str) -> str:
#         """Extract a specific function from source code"""
#         lines = source_code.split('\n')
        
#         if language == 'python':
#             pattern = f'def {function_name}'
#         elif language == 'javascript':
#             pattern = f'function {function_name}'
#         else:
#             pattern = function_name
        
#         # Find function start
#         start_idx = -1
#         for i, line in enumerate(lines):
#             if pattern in line:
#                 start_idx = i
#                 break
        
#         if start_idx == -1:
#             return ""
        
#         # Find function end (simple heuristic)
#         end_idx = start_idx + 1
#         indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())
        
#         for i in range(start_idx + 1, len(lines)):
#             line = lines[i]
#             if line.strip() == '':
#                 continue
#             current_indent = len(line) - len(line.lstrip())
#             if current_indent <= indent_level and line.strip():
#                 end_idx = i
#                 break
#             end_idx = i + 1
        
#         return '\n'.join(lines[start_idx:end_idx])
    
#     def _create_debug_prompt(self, function_name: str, function_code: str,
#                             test_name: str, error_info: str, language: str) -> str:
#         """Create prompt for Gemini to fix the code"""
        
#         return f"""You are an expert {language} debugger. A function has failing tests and needs to be fixed.

# **FUNCTION NAME:** {function_name}

# **ORIGINAL CODE:**
# ```{language}
# {function_code}
# ```

# **FAILING TEST:** {test_name}

# **ERROR INFORMATION:**
# {error_info}

# **YOUR TASK:**
# 1. Analyze why the test is failing
# 2. Identify the bug in the code
# 3. Provide a corrected version of the function
# 4. Explain what was wrong and how you fixed it

# **CRITICAL REQUIREMENTS:**
# - Fix ONLY the bug causing the test failure
# - Keep the function signature exactly the same
# - Maintain the same logic and behavior, just fix the bug
# - Don't add unnecessary features
# - Ensure the fix handles edge cases properly

# **FORMAT YOUR RESPONSE AS:**

# ### Analysis
# [Explain what the bug is]

# ### Fixed Code
# ```{language}
# [The complete corrected function]
# ```

# ### Explanation
# [Explain the specific changes you made and why]

# Only provide the corrected code, don't make unnecessary changes.
# """
    
#     def _extract_fixed_code(self, response_text: str, language: str) -> str:
#         """Extract the fixed code from Gemini's response"""
#         import re
        
#         # Look for code blocks
#         patterns = [
#             rf'```{language}\n(.*?)```',
#             r'```\n(.*?)```',
#             r'### Fixed Code\n```.*?\n(.*?)```'
#         ]
        
#         for pattern in patterns:
#             matches = re.findall(pattern, response_text, re.DOTALL)
#             if matches:
#                 code = matches[0].strip()
#                 # Remove any markdown formatting
#                 code = re.sub(r'^\s*```.*?\n', '', code)
#                 code = re.sub(r'```\s*$', '', code)
#                 return code.strip()
        
#         return ""
    
#     def _extract_explanation(self, response_text: str) -> str:
#         """Extract explanation from Gemini's response"""
#         lines = response_text.split('\n')
        
#         # Look for explanation section
#         in_explanation = False
#         explanation_lines = []
        
#         for line in lines:
#             if '### Explanation' in line or '## Explanation' in line:
#                 in_explanation = True
#                 continue
#             elif line.startswith('###') or line.startswith('##'):
#                 in_explanation = False
#             elif in_explanation and line.strip():
#                 explanation_lines.append(line)
        
#         return '\n'.join(explanation_lines).strip() if explanation_lines else "Fix applied"
    
#     def _save_fix(self, function_name: str, fixed_code: str, 
#                   original_file: str, language: str) -> Path:
#         """Save the fixed code to a file"""
        
#         # Create fix filename
#         original_name = Path(original_file).stem
#         ext = {
#             'python': '.py',
#             'javascript': '.js',
#             'java': '.java'
#         }.get(language, '.txt')
        
#         fix_file = self.fixes_dir / f"{original_name}_{function_name}_fixed{ext}"
        
#         # Create full file with fix
#         full_content = f"""# FIXED CODE for {function_name}
# # Original file: {original_file}
# # Generated by Debug Agent

# {fixed_code}

# # How to apply this fix:
# # 1. Copy the function above
# # 2. Replace the original function in {original_file}
# # 3. Re-run tests to verify the fix
# """
        
#         with open(fix_file, 'w', encoding='utf-8') as f:
#             f.write(full_content)
        
#         console.print(f"[green]💾 Fix saved to: {fix_file}[/green]")
        
#         return fix_file
    
#     def _display_fix(self, fix_result: Dict[str, Any]):
#         """Display the fix details"""
        
#         console.print(f"\n[bold green]✅ Fix Generated for: {fix_result['function_name']}[/bold green]\n")
        
#         # Show original vs fixed code
#         console.print("[yellow]📄 Original Code:[/yellow]")
#         original_syntax = Syntax(
#             fix_result['original_code'],
#             "python",
#             theme="monokai",
#             line_numbers=True
#         )
#         console.print(original_syntax)
        
#         console.print("\n[green]✨ Fixed Code:[/green]")
#         fixed_syntax = Syntax(
#             fix_result['fixed_code'],
#             "python",
#             theme="monokai",
#             line_numbers=True
#         )
#         console.print(fixed_syntax)
        
#         # Show explanation
#         if fix_result.get('explanation'):
#             explanation_panel = Panel(
#                 fix_result['explanation'],
#                 title="[bold cyan]💡 Explanation[/bold cyan]",
#                 border_style="cyan",
#                 padding=(1, 2)
#             )
#             console.print(explanation_panel)
        
#         console.print()
    
#     def _display_debug_summary(self, debug_results: Dict[str, Any]):
#         """Display debugging summary"""
#         console.print("\n" + "="*70)
#         console.print("[bold cyan]🔍 DEBUG SUMMARY[/bold cyan]")
#         console.print("="*70 + "\n")
        
#         summary_table = Table(title="Debugging Results", border_style="green")
#         summary_table.add_column("Metric", style="cyan", width=30)
#         summary_table.add_column("Value", style="white", width=15)
        
#         summary_table.add_row("Files Analyzed", str(debug_results['files_analyzed']))
#         summary_table.add_row("Bugs Found", str(debug_results['bugs_found']))
#         summary_table.add_row("Fixes Generated", str(debug_results['fixes_generated']))
#         summary_table.add_row("Success Rate", 
#                              f"{(debug_results['fixes_generated'] / max(debug_results['bugs_found'], 1) * 100):.1f}%")
        
#         console.print(summary_table)
#         console.print()
        
#         # List fixed functions
#         if debug_results['fixed_functions']:
#             console.print("[bold green]✅ Fixed Functions:[/bold green]")
#             for func in debug_results['fixed_functions']:
#                 console.print(f"   • {func}")
#             console.print()
        
#         # List fix files
#         if debug_results['fix_files']:
#             console.print("[bold blue]📁 Fix Files Generated:[/bold blue]")
#             for fix_file in debug_results['fix_files']:
#                 console.print(f"   • {fix_file}")
#             console.print()
        
#         # Final instructions
#         instructions_panel = Panel(
#             "[cyan]Next Steps:[/cyan]\n\n"
#             "1. Review the fixed code above\n"
#             "2. Copy fixes from the generated files\n"
#             "3. Replace original functions in your source code\n"
#             "4. Re-run tests to verify fixes\n\n"
#             "[dim]All fixes saved in: debug/fixes/[/dim]",
#             title="[bold yellow]📋 How to Apply Fixes[/bold yellow]",
#             border_style="yellow"
#         )
#         console.print(instructions_panel)
    
#     def analyze_bugs(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         General bug analysis (without test results)
#         Used when called directly from control agent
#         """
#         console.print("[bold cyan]🐛 Running General Bug Analysis...[/bold cyan]\n")
        
#         results = {
#             'status': 'completed',
#             'files_analyzed': len(parsed_data),
#             'potential_issues': 0,
#             'suggestions': []
#         }
        
#         for file_path, file_data in parsed_data.items():
#             if not file_data.get('parsed', False):
#                 continue
            
#             # Basic static analysis
#             content = file_data.get('content', '')
#             lines = file_data.get('lines', 0)
            
#             # Check for common issues
#             if lines > 200:
#                 results['potential_issues'] += 1
#                 results['suggestions'].append(
#                     f"Large file detected: {Path(file_path).name} ({lines} lines) - consider refactoring"
#                 )
            
#             if 'TODO' in content or 'FIXME' in content:
#                 results['potential_issues'] += 1
#                 results['suggestions'].append(
#                     f"TODO/FIXME comments found in {Path(file_path).name}"
#                 )
        
#         results['message'] = f'Analyzed {len(parsed_data)} files, found {results["potential_issues"]} potential issues'
        
#         return results

#!/usr/bin/env python3
"""
Debug Agent - AI-powered debugging and code fixing
Analyzes test failures and generates corrected code using Gemini
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from collections import defaultdict

from utils.gemini_client import GeminiClient

console = Console()

class DebugAgent:
    """Agent responsible for analyzing bugs and suggesting fixes"""

    def __init__(self):
        self.console = Console()
        self.gemini_client = self._initialize_llm()
        self.llm_available = self.gemini_client is not None
        self.fixes_dir = Path("debug/fixes")
        self.fixes_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_llm(self) -> Optional[GeminiClient]:
        """Initialize LLM client"""
        try:
            gemini_client = GeminiClient()
            if gemini_client.model is None:
                console.print("[red]❌ LLM initialization failed[/red]")
                return None
            console.print("[green]✅ Debug Agent LLM initialized[/green]")
            return gemini_client
        except Exception as e:
            console.print(f"[red]❌ LLM initialization error: {e}[/red]")
            return None

    def analyze_and_fix(self, test_results: Dict[str, Any],
                        parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method to analyze test failures and generate fixes.
        Calls LLM ONCE per unique function — not once per failed test.
        """
        console.print("\n[bold cyan]🔍 Starting Debug Analysis...[/bold cyan]\n")

        if not self.llm_available:
            console.print("[red]❌ LLM unavailable - cannot generate fixes[/red]")
            return {'success': False, 'error': 'LLM not available for debugging'}

        debug_results = {
            'success': True,
            'files_analyzed': 0,
            'bugs_found': 0,
            'fixes_generated': 0,
            'fixed_functions': [],
            'fix_files': [],
            'analysis_details': []
        }

        failed_tests = test_results.get('failed_tests', [])

        if not failed_tests:
            console.print("[green]✅ No test failures to debug![/green]")
            return debug_results

        console.print(f"[yellow]Analyzing {len(failed_tests)} failed test(s)...[/yellow]\n")

        # Group failures by file
        failures_by_file = self._group_failures_by_file(failed_tests)

        for file_path, failures in failures_by_file.items():
            console.print(f"\n[bold blue]📁 Processing: {Path(file_path).name}[/bold blue]")

            file_data = parsed_data.get(file_path)
            if not file_data:
                console.print(f"[red]⚠️  Could not find source: {file_path}[/red]")
                continue

            source_code = file_data.get('content', '')
            language    = file_data.get('language', 'unknown')

            # ✅ FIX: group by unique function — ONE LLM call per function
            failures_by_function = self._group_failures_by_function(failures)

            console.print(
                f"[dim]{len(failures)} failed test(s) → "
                f"{len(failures_by_function)} unique function(s) to fix[/dim]"
            )

            for func_name, func_failures in failures_by_function.items():
                console.print(
                    f"\n[cyan]🔧 Analyzing: {func_name} "
                    f"({len(func_failures)} failing test(s))[/cyan]"
                )

                # ✅ Pass ALL failures for this function in ONE call
                fix_result = self._analyze_and_fix_function(
                    func_name,
                    func_failures,     # list of all failures for this function
                    source_code,
                    language,
                    file_path
                )

                debug_results['bugs_found'] += 1

                if fix_result['success']:
                    debug_results['fixes_generated'] += 1
                    debug_results['fixed_functions'].append(fix_result['function_name'])
                    debug_results['fix_files'].append(fix_result['fix_file'])
                    debug_results['analysis_details'].append(fix_result)
                    self._display_fix(fix_result)

            debug_results['files_analyzed'] += 1

        self._display_debug_summary(debug_results)
        return debug_results

    # ------------------------------------------------------------------ #
    #  Grouping helpers
    # ------------------------------------------------------------------ #

    def _group_failures_by_file(self, failed_tests: List[Dict]) -> Dict[str, List[Dict]]:
        """Group test failures by source file"""
        grouped = defaultdict(list)
        for failure in failed_tests:
            grouped[failure.get('file', 'unknown')].append(failure)
        return dict(grouped)

    def _group_failures_by_function(self, failures: List[Dict]) -> Dict[str, List[Dict]]:
        """
        ✅ NEW — Group failures by unique function name.
        Prevents multiple LLM calls for the same function.

        Example:
          fetch_user × 6 failures  →  one entry  {'fetch_user': [f1,f2,f3,f4,f5,f6]}
          get_user_email × 1       →  one entry  {'get_user_email': [f1]}
        """
        grouped = defaultdict(list)
        for failure in failures:
            func_name = failure.get('original_function', 'Unknown')
            grouped[func_name].append(failure)
        return dict(grouped)

    # ------------------------------------------------------------------ #
    #  Core fix method — now receives ALL failures for one function
    # ------------------------------------------------------------------ #

    def _analyze_and_fix_function(
        self,
        function_name: str,
        func_failures: List[Dict],   # ✅ list, not single failure
        source_code: str,
        language: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Analyze ONE function with ALL its failing tests and generate ONE fix.
        """
        # Collect all test names + errors for this function
        test_names   = [f.get('test_name',     '') for f in func_failures]
        error_infos  = [f.get('error_snippet', '') for f in func_failures]

        function_code = self._extract_function_code(source_code, function_name, language)

        if not function_code:
            console.print(f"[yellow]⚠️  Could not extract function code for {function_name}[/yellow]")
            return {'success': False}

        # ✅ Build prompt with ALL failures listed
        fix_prompt = self._create_debug_prompt(
            function_name,
            function_code,
            test_names,    # list of test names
            error_infos,   # list of error snippets
            language
        )

        try:
            console.print(f"[dim]Asking Gemini for fix "
                          f"(covering {len(func_failures)} test(s))...[/dim]")

            response = self.gemini_client.generate_content(fix_prompt)

            if not response or not hasattr(response, 'text'):
                return {'success': False, 'error': 'No response from LLM'}

            fixed_code  = self._extract_fixed_code(response.text, language)
            explanation = self._extract_explanation(response.text)

            if not fixed_code:
                return {'success': False, 'error': 'Could not extract fixed code'}

            fix_file = self._save_fix(function_name, fixed_code, file_path, language)

            return {
                'success':       True,
                'function_name': function_name,
                'original_code': function_code,
                'fixed_code':    fixed_code,
                'explanation':   explanation,
                'fix_file':      str(fix_file),
                'tests_covered': len(func_failures),   # how many failures this fix addresses
                'test_names':    test_names,
            }

        except Exception as e:
            console.print(f"[red]Error generating fix: {e}[/red]")
            return {'success': False, 'error': str(e)}

    # ------------------------------------------------------------------ #
    #  Prompt builder — now lists ALL failing tests
    # ------------------------------------------------------------------ #

    def _create_debug_prompt(
        self,
        function_name: str,
        function_code: str,
        test_names: List[str],    # ✅ list
        error_infos: List[str],   # ✅ list
        language: str
    ) -> str:
        """
        Build a prompt that includes ALL failing tests for this function.
        LLM generates ONE fix that handles all cases.
        """
        # Format all failures into a numbered list
        failures_text = "\n".join([
            f"{i+1}. Test: {name}\n   Error: {error}"
            for i, (name, error) in enumerate(zip(test_names, error_infos))
        ])

        return f"""You are an expert {language} debugger. A function is failing multiple tests.

**FUNCTION NAME:** {function_name}

**ORIGINAL CODE:**
```{language}
{function_code}
```

**ALL FAILING TESTS ({len(test_names)} total):**
{failures_text}

**YOUR TASK:**
1. Analyze why ALL the tests above are failing
2. Identify the root cause(s)
3. Provide ONE corrected version that fixes ALL the failures above
4. Explain what was wrong and how you fixed it

**CRITICAL REQUIREMENTS:**
- ONE fix that handles ALL {len(test_names)} failing test(s)
- Keep the function signature exactly the same
- Fix only the bugs — don't add unnecessary features
- Handle all edge cases shown in the failing tests

**FORMAT YOUR RESPONSE AS:**

### Analysis
[Explain what the bug(s) are]

### Fixed Code
```{language}
[The complete corrected function]
```

### Explanation
[Explain the specific changes you made and why they fix all the failures]
"""

    # ------------------------------------------------------------------ #
    #  Unchanged helpers below
    # ------------------------------------------------------------------ #

    def _extract_function_code(self, source_code: str, function_name: str,
                               language: str) -> str:
        """Extract a specific function from source code"""
        lines = source_code.split('\n')

        if language == 'python':
            pattern = f'def {function_name}'
        elif language == 'javascript':
            pattern = f'function {function_name}'
        else:
            pattern = function_name

        start_idx = -1
        for i, line in enumerate(lines):
            if pattern in line:
                start_idx = i
                break

        if start_idx == -1:
            return ""

        end_idx     = start_idx + 1
        indent_level = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            if line.strip() == '':
                continue
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                end_idx = i
                break
            end_idx = i + 1

        return '\n'.join(lines[start_idx:end_idx])

    def _extract_fixed_code(self, response_text: str, language: str) -> str:
        """Extract the fixed code from Gemini's response"""
        import re

        patterns = [
            rf'```{language}\n(.*?)```',
            r'```\n(.*?)```',
            r'### Fixed Code\n```.*?\n(.*?)```'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL)
            if matches:
                code = matches[0].strip()
                code = re.sub(r'^\s*```.*?\n', '', code)
                code = re.sub(r'```\s*$', '', code)
                return code.strip()

        return ""

    def _extract_explanation(self, response_text: str) -> str:
        """Extract explanation from Gemini's response"""
        lines = response_text.split('\n')
        in_explanation  = False
        explanation_lines = []

        for line in lines:
            if '### Explanation' in line or '## Explanation' in line:
                in_explanation = True
                continue
            elif line.startswith('###') or line.startswith('##'):
                in_explanation = False
            elif in_explanation and line.strip():
                explanation_lines.append(line)

        return '\n'.join(explanation_lines).strip() if explanation_lines else "Fix applied"

    def _save_fix(self, function_name: str, fixed_code: str,
                  original_file: str, language: str) -> Path:
        """Save the fixed code to a file"""
        original_name = Path(original_file).stem
        ext = {'python': '.py', 'javascript': '.js', 'java': '.java'}.get(language, '.txt')
        fix_file = self.fixes_dir / f"{original_name}_{function_name}_fixed{ext}"

        full_content = (
            f"# FIXED CODE for {function_name}\n"
            f"# Original file: {original_file}\n"
            f"# Generated by Debug Agent\n\n"
            f"{fixed_code}\n\n"
            f"# How to apply this fix:\n"
            f"# 1. Copy the function above\n"
            f"# 2. Replace the original function in {original_file}\n"
            f"# 3. Re-run tests to verify the fix\n"
        )

        with open(fix_file, 'w', encoding='utf-8') as f:
            f.write(full_content)

        console.print(f"[green]💾 Fix saved to: {fix_file}[/green]")
        return fix_file

    def _display_fix(self, fix_result: Dict[str, Any]):
        """Display the fix details"""
        n = fix_result.get('tests_covered', 1)
        console.print(
            f"\n[bold green]✅ Fix Generated for: {fix_result['function_name']} "
            f"(covers {n} test(s))[/bold green]\n"
        )

        console.print("[yellow]📄 Original Code:[/yellow]")
        console.print(Syntax(fix_result['original_code'], "python",
                             theme="monokai", line_numbers=True))

        console.print("\n[green]✨ Fixed Code:[/green]")
        console.print(Syntax(fix_result['fixed_code'], "python",
                             theme="monokai", line_numbers=True))

        if fix_result.get('explanation'):
            console.print(Panel(
                fix_result['explanation'],
                title="[bold cyan]💡 Explanation[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            ))

        console.print()

    def _display_debug_summary(self, debug_results: Dict[str, Any]):
        """Display debugging summary"""
        console.print("\n" + "=" * 70)
        console.print("[bold cyan]🔍 DEBUG SUMMARY[/bold cyan]")
        console.print("=" * 70 + "\n")

        table = Table(title="Debugging Results", border_style="green")
        table.add_column("Metric",  style="cyan",  width=30)
        table.add_column("Value",   style="white", width=15)

        table.add_row("Files Analyzed",   str(debug_results['files_analyzed']))
        table.add_row("Bugs Found",       str(debug_results['bugs_found']))
        table.add_row("Fixes Generated",  str(debug_results['fixes_generated']))
        table.add_row(
            "Success Rate",
            f"{debug_results['fixes_generated'] / max(debug_results['bugs_found'], 1) * 100:.1f}%"
        )
        console.print(table)
        console.print()

        # ✅ deduplicated list — no more repeated function names
        unique_funcs = list(dict.fromkeys(debug_results['fixed_functions']))
        if unique_funcs:
            console.print("[bold green]✅ Fixed Functions:[/bold green]")
            for func in unique_funcs:
                console.print(f"   • {func}")
            console.print()

        unique_files = list(dict.fromkeys(debug_results['fix_files']))
        if unique_files:
            console.print("[bold blue]📁 Fix Files Generated:[/bold blue]")
            for fix_file in unique_files:
                console.print(f"   • {fix_file}")
            console.print()

        console.print(Panel(
            "[cyan]Next Steps:[/cyan]\n\n"
            "1. Review the fixed code above\n"
            "2. Copy fixes from the generated files\n"
            "3. Replace original functions in your source code\n"
            "4. Re-run tests to verify fixes\n\n"
            "[dim]All fixes saved in: debug/fixes/[/dim]",
            title="[bold yellow]📋 How to Apply Fixes[/bold yellow]",
            border_style="yellow"
        ))

    def analyze_bugs(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """General bug analysis without test results"""
        console.print("[bold cyan]🐛 Running General Bug Analysis...[/bold cyan]\n")

        results = {
            'status': 'completed',
            'files_analyzed': len(parsed_data),
            'potential_issues': 0,
            'suggestions': []
        }

        for file_path, file_data in parsed_data.items():
            if not file_data.get('parsed', False):
                continue
            content = file_data.get('content', '')
            lines   = file_data.get('lines', 0)

            if lines > 200:
                results['potential_issues'] += 1
                results['suggestions'].append(
                    f"Large file: {Path(file_path).name} ({lines} lines)"
                )
            if 'TODO' in content or 'FIXME' in content:
                results['potential_issues'] += 1
                results['suggestions'].append(
                    f"TODO/FIXME found in {Path(file_path).name}"
                )

        results['message'] = (
            f"Analyzed {len(parsed_data)} files, "
            f"found {results['potential_issues']} potential issues"
        )
        return results