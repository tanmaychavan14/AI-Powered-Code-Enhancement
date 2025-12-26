# #!/usr/bin/env python3
# """
# Refactor Agent - AI-powered code refactoring
# Analyzes code and generates refactored versions using Gemini
# Fixed to always call Gemini for comprehensive refactoring analysis
# Results are returned for display by OutputAgent
# """

# import os
# import json
# import re
# from pathlib import Path
# from typing import Dict, List, Any, Optional, Set, Tuple
# from dataclasses import dataclass, field, asdict
# from enum import Enum
# from rich.console import Console
# from rich.panel import Panel
# from rich.table import Table
# from rich.syntax import Syntax

# from utils.gemini_client import GeminiClient

# console = Console()


# class CodeSmellType(Enum):
#     """Enumeration of code smell types"""
#     LONG_FUNCTION = "long_function"
#     TOO_MANY_IMPORTS = "too_many_imports"
#     CODE_DUPLICATION = "code_duplication"
#     LONG_LINES = "long_lines"
#     DEEP_NESTING = "deep_nesting"
#     MAGIC_NUMBERS = "magic_numbers"
#     TECHNICAL_DEBT = "technical_debt"
#     GENERAL_IMPROVEMENT = "general_improvement"


# @dataclass
# class CodeSmell:
#     """Represents a detected code smell"""
#     smell_type: CodeSmellType
#     description: str
#     severity: str = "medium"
#     line_number: Optional[int] = None
    
#     def __str__(self) -> str:
#         location = f" (line {self.line_number})" if self.line_number else ""
#         return f"[{self.severity.upper()}] {self.description}{location}"
    
#     def to_dict(self) -> Dict[str, Any]:
#         """Convert to dictionary for serialization"""
#         return {
#             'smell_type': self.smell_type.value,
#             'description': self.description,
#             'severity': self.severity,
#             'line_number': self.line_number
#         }


# @dataclass
# class RefactorResult:
#     """Structured refactoring result"""
#     success: bool
#     file_name: str
#     file_path: str
#     original_code: str = ""
#     refactored_code: str = ""
#     improvements: List[str] = field(default_factory=list)
#     code_smells: List[CodeSmell] = field(default_factory=list)
#     refactored_file: str = ""
#     lines_before: int = 0
#     lines_after: int = 0
#     error: Optional[str] = None
    
#     def to_dict(self) -> Dict[str, Any]:
#         """Convert to dictionary for output agent"""
#         return {
#             'success': self.success,
#             'file_name': self.file_name,
#             'file_path': self.file_path,
#             'original_code': self.original_code,
#             'refactored_code': self.refactored_code,
#             'improvements': self.improvements,
#             'code_smells': [smell.to_dict() for smell in self.code_smells],
#             'refactored_file': self.refactored_file,
#             'lines_before': self.lines_before,
#             'lines_after': self.lines_after,
#             'error': self.error
#         }


# class RefactorAgent:
#     """Agent responsible for analyzing and refactoring code"""
    
#     # Configuration constants
#     MIN_FILE_LINES = 10
#     LONG_FUNCTION_THRESHOLD = 50
#     MAX_IMPORTS_THRESHOLD = 20
#     DUPLICATE_LINE_MIN_LENGTH = 20
#     DUPLICATE_OCCURRENCE_THRESHOLD = 2
#     LONG_LINE_THRESHOLD = 100
#     LONG_LINE_COUNT_THRESHOLD = 5
#     DEEP_NESTING_THRESHOLD = 20
#     MAGIC_NUMBER_THRESHOLD = 5
    
#     def __init__(self):
#         """Initialize the refactor agent"""
#         self.console = Console()
#         self.gemini_client: Optional[GeminiClient] = None
#         self.llm_available = False
#         self.refactor_dir = Path("refactor/refactored_code")
#         self._regex_cache: Dict[str, re.Pattern] = {}
        
#         self._initialize_directories()
#         self._initialize_llm_client()
    
#     def _initialize_directories(self) -> None:
#         """Create output directories"""
#         try:
#             self.refactor_dir.mkdir(parents=True, exist_ok=True)
#         except OSError as e:
#             console.print(f"[yellow]⚠️  Directory creation warning: {e}[/yellow]")
#             self.refactor_dir = Path.cwd() / "refactored_output"
#             self.refactor_dir.mkdir(parents=True, exist_ok=True)
    
#     def _initialize_llm_client(self) -> None:
#         """Initialize Gemini client with error handling"""
#         try:
#             self.gemini_client = GeminiClient()
            
#             if self.gemini_client is None:
#                 console.print("[red]❌ GeminiClient returned None[/red]")
#                 self.llm_available = False
#                 return
            
#             if not hasattr(self.gemini_client, 'model') or self.gemini_client.model is None:
#                 console.print("[red]❌ LLM model not initialized[/red]")
#                 self.llm_available = False
#                 return
            
#             self.llm_available = True
#             console.print("[green]✅ Refactor Agent LLM initialized successfully[/green]")
            
#         except Exception as e:
#             console.print(f"[red]❌ LLM initialization error: {e}[/red]")
#             self.llm_available = False
    
#     def _get_regex_pattern(self, pattern: str) -> re.Pattern:
#         """Get or compile regex pattern with caching"""
#         if pattern not in self._regex_cache:
#             try:
#                 self._regex_cache[pattern] = re.compile(pattern, re.DOTALL | re.MULTILINE)
#             except re.error as e:
#                 console.print(f"[red]Regex error for pattern {pattern}: {e}[/red]")
#                 self._regex_cache[pattern] = re.compile(r'(?!.*)')
#         return self._regex_cache[pattern]
    
#     def refactor_code(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
#         """
#         Main refactoring entry point - ALWAYS calls Gemini
#         Returns results for OutputAgent to display
        
#         Args:
#             parsed_data: Dictionary of parsed code files
        
#         Returns:
#             Refactoring results dictionary for OutputAgent
#         """
#         console.print("\n[bold cyan]🔧 Starting Code Refactoring...[/bold cyan]\n")
        
#         if not parsed_data:
#             return self._create_empty_result("No data provided")
        
#         if not self.llm_available:
#             console.print("[red]❌ Gemini LLM unavailable - Cannot proceed with refactoring[/red]")
#             return {
#                 'success': False,
#                 'status': 'failed',
#                 'files_analyzed': 0,
#                 'files_refactored': 0,
#                 'improvements': [],
#                 'refactored_files': [],
#                 'refactoring_details': [],
#                 'errors': ['Gemini LLM is required for refactoring'],
#                 'message': 'Gemini LLM unavailable. Please check API configuration.'
#             }
        
#         refactor_results = {
#             'success': True,
#             'files_analyzed': 0,
#             'files_refactored': 0,
#             'improvements': [],
#             'refactored_files': [],
#             'refactoring_details': [],
#             'status': 'completed',
#             'errors': []
#         }
        
#         valid_files = self._filter_valid_files(parsed_data)
#         console.print(f"[yellow]📊 Processing {len(valid_files)} file(s) with Gemini...[/yellow]\n")
        
#         for file_path, file_data in valid_files.items():
#             try:
#                 console.print(f"[cyan]🤖 Calling Gemini for: {Path(file_path).name}[/cyan]")
                
#                 result = self._process_single_file(file_path, file_data)
                
#                 if result.success:
#                     refactor_results['files_refactored'] += 1
#                     refactor_results['improvements'].extend(result.improvements)
#                     refactor_results['refactored_files'].append(result.refactored_file)
#                     refactor_results['refactoring_details'].append(result.to_dict())
                    
#                     console.print(f"[green]✅ Successfully refactored: {result.file_name}[/green]")
#                 elif result.error and result.error != "no_issues":
#                     error_msg = f"{file_path}: {result.error}"
#                     refactor_results['errors'].append(error_msg)
#                     console.print(f"[red]❌ Failed: {result.error}[/red]")
                
#                 refactor_results['files_analyzed'] += 1
                
#             except Exception as e:
#                 error_msg = f"Error processing {file_path}: {str(e)}"
#                 console.print(f"[red]❌ {error_msg}[/red]")
#                 refactor_results['errors'].append(error_msg)
        
#         # Generate summary message
#         refactor_results['message'] = (
#             f"Refactored {refactor_results['files_refactored']} out of "
#             f"{refactor_results['files_analyzed']} files using Gemini AI"
#         )
        
#         # Add project path if available
#         if parsed_data:
#             first_file = next(iter(parsed_data.keys()))
#             refactor_results['project_path'] = str(Path(first_file).parent)
        
#         console.print(f"\n[bold green]✅ Refactoring complete! Results ready for display.[/bold green]")
        
#         return refactor_results
    
#     def _create_empty_result(self, message: str) -> Dict[str, Any]:
#         """Create empty result structure"""
#         return {
#             'success': False,
#             'status': 'failed',
#             'files_analyzed': 0,
#             'files_refactored': 0,
#             'improvements': [],
#             'refactored_files': [],
#             'refactoring_details': [],
#             'errors': [message],
#             'message': message
#         }
    
#     def _filter_valid_files(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Filter valid files for refactoring"""
#         valid_files = {}
        
#         for file_path, file_data in parsed_data.items():
#             try:
#                 if not isinstance(file_data, dict):
#                     continue
                
#                 if not file_data.get('parsed', False):
#                     continue
                
#                 lines = file_data.get('lines', 0)
#                 if lines < self.MIN_FILE_LINES:
#                     console.print(f"[dim]⏭️  Skipping small file: {Path(file_path).name} ({lines} lines)[/dim]")
#                     continue
                
#                 content = file_data.get('content', '')
#                 if not content or not isinstance(content, str):
#                     continue
                
#                 valid_files[file_path] = file_data
                
#             except Exception as e:
#                 console.print(f"[yellow]⚠️  Validation error for {file_path}: {e}[/yellow]")
        
#         return valid_files
    
#     def _process_single_file(self, file_path: str, file_data: Dict[str, Any]) -> RefactorResult:
#         """
#         Process a single file for refactoring
#         ALWAYS calls Gemini regardless of detected code smells
#         """
#         file_name = Path(file_path).name
        
#         try:
#             source_code = file_data.get('content', '')
#             language = file_data.get('language', 'unknown')
            
#             if not source_code:
#                 return RefactorResult(
#                     success=False,
#                     file_name=file_name,
#                     file_path=file_path,
#                     error="Empty source code"
#                 )
            
#             # Detect code smells (for reporting, not for blocking)
#             code_smells = self._identify_code_smells(source_code, language, file_data)
            
#             # ALWAYS add a general improvement request if no specific smells found
#             if not code_smells:
#                 console.print(f"[green]✨ No critical issues - requesting quality improvements[/green]")
#                 code_smells = [
#                     CodeSmell(
#                         smell_type=CodeSmellType.GENERAL_IMPROVEMENT,
#                         description="Analyze and improve code quality, readability, and best practices",
#                         severity="low"
#                     )
#                 ]
#             else:
#                 console.print(f"[yellow]🔍 Found {len(code_smells)} improvement opportunities[/yellow]")
            
#             # ALWAYS call Gemini for refactoring
#             return self._generate_refactoring(
#                 file_name, file_path, source_code, language, code_smells
#             )
            
#         except Exception as e:
#             console.print(f"[red]❌ Processing error: {e}[/red]")
#             return RefactorResult(
#                 success=False,
#                 file_name=file_name,
#                 file_path=file_path,
#                 error=str(e)
#             )
    
#     def _identify_code_smells(
#         self,
#         source_code: str,
#         language: str,
#         file_data: Dict[str, Any]
#     ) -> List[CodeSmell]:
#         """
#         Identify code smells and issues
#         Returns empty list if no issues (will still trigger general improvement)
#         """
#         smells: List[CodeSmell] = []
        
#         try:
#             lines = source_code.split('\n')
#             total_lines = len(lines)
            
#             # Check long functions
#             smells.extend(self._check_long_functions(file_data))
            
#             # Check imports
#             smells.extend(self._check_imports(file_data))
            
#             # Check duplication
#             if total_lines > 100:
#                 smells.extend(self._check_duplication(lines))
            
#             # Check long lines
#             smells.extend(self._check_long_lines(lines))
            
#             # Check nesting
#             smells.extend(self._check_nesting_depth(lines))
            
#             # Check magic numbers
#             if language == 'python':
#                 smells.extend(self._check_magic_numbers(source_code))
            
#             # Check technical debt
#             smells.extend(self._check_technical_debt(lines))
            
#         except Exception as e:
#             console.print(f"[yellow]⚠️  Code smell detection error: {e}[/yellow]")
        
#         return smells
    
#     def _check_long_functions(self, file_data: Dict[str, Any]) -> List[CodeSmell]:
#         """Check for long functions"""
#         smells = []
#         functions = file_data.get('functions', [])
        
#         if not isinstance(functions, list):
#             return smells
        
#         for func in functions:
#             try:
#                 if not isinstance(func, dict):
#                     continue
                
#                 func_name = func.get('name', 'unknown')
#                 func_code = func.get('definition', '')
                
#                 if isinstance(func_code, str):
#                     func_lines = func_code.count('\n') + 1
                    
#                     if func_lines > self.LONG_FUNCTION_THRESHOLD:
#                         severity = "high" if func_lines > 100 else "medium"
#                         smells.append(CodeSmell(
#                             smell_type=CodeSmellType.LONG_FUNCTION,
#                             description=f"Long function '{func_name}' ({func_lines} lines)",
#                             severity=severity
#                         ))
#             except Exception:
#                 continue
        
#         return smells
    
#     def _check_imports(self, file_data: Dict[str, Any]) -> List[CodeSmell]:
#         """Check import count"""
#         smells = []
#         imports = file_data.get('imports', [])
        
#         if isinstance(imports, list) and len(imports) > self.MAX_IMPORTS_THRESHOLD:
#             severity = "high" if len(imports) > 30 else "medium"
#             smells.append(CodeSmell(
#                 smell_type=CodeSmellType.TOO_MANY_IMPORTS,
#                 description=f"Too many imports ({len(imports)})",
#                 severity=severity
#             ))
        
#         return smells
    
#     def _check_duplication(self, lines: List[str]) -> List[CodeSmell]:
#         """Check for duplicated lines"""
#         smells = []
#         line_counts: Dict[str, int] = {}
        
#         for line in lines:
#             stripped = line.strip()
#             if stripped and len(stripped) > self.DUPLICATE_LINE_MIN_LENGTH:
#                 line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
#         duplicates = sum(1 for count in line_counts.values() if count > self.DUPLICATE_OCCURRENCE_THRESHOLD)
        
#         if duplicates > 0:
#             severity = "high" if duplicates > 10 else "medium"
#             smells.append(CodeSmell(
#                 smell_type=CodeSmellType.CODE_DUPLICATION,
#                 description=f"Code duplication detected ({duplicates} repeated patterns)",
#                 severity=severity
#             ))
        
#         return smells
    
#     def _check_long_lines(self, lines: List[str]) -> List[CodeSmell]:
#         """Check for long lines"""
#         smells = []
#         long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > self.LONG_LINE_THRESHOLD]
        
#         if len(long_lines) > self.LONG_LINE_COUNT_THRESHOLD:
#             smells.append(CodeSmell(
#                 smell_type=CodeSmellType.LONG_LINES,
#                 description=f"Multiple long lines ({len(long_lines)} exceeding {self.LONG_LINE_THRESHOLD} chars)",
#                 severity="low",
#                 line_number=long_lines[0]
#             ))
        
#         return smells
    
#     def _check_nesting_depth(self, lines: List[str]) -> List[CodeSmell]:
#         """Check nesting depth"""
#         smells = []
#         max_indent = 0
#         max_indent_line = 0
        
#         for i, line in enumerate(lines, 1):
#             if line.strip():
#                 indent = len(line) - len(line.lstrip())
#                 if indent > max_indent:
#                     max_indent = indent
#                     max_indent_line = i
        
#         if max_indent > self.DEEP_NESTING_THRESHOLD:
#             smells.append(CodeSmell(
#                 smell_type=CodeSmellType.DEEP_NESTING,
#                 description=f"Deep nesting detected (indent level: {max_indent})",
#                 severity="medium",
#                 line_number=max_indent_line
#             ))
        
#         return smells
    
#     def _check_magic_numbers(self, source_code: str) -> List[CodeSmell]:
#         """Check for magic numbers"""
#         smells = []
        
#         try:
#             pattern = self._get_regex_pattern(r'\b\d{2,}\b')
#             magic_numbers = pattern.findall(source_code)
            
#             if len(magic_numbers) > self.MAGIC_NUMBER_THRESHOLD:
#                 smells.append(CodeSmell(
#                     smell_type=CodeSmellType.MAGIC_NUMBERS,
#                     description=f"Magic numbers found ({len(magic_numbers)} occurrences)",
#                     severity="low"
#                 ))
#         except Exception:
#             pass
        
#         return smells
    
#     def _check_technical_debt(self, lines: List[str]) -> List[CodeSmell]:
#         """Check for TODO/FIXME comments"""
#         smells = []
#         todo_lines = [i + 1 for i, line in enumerate(lines) if 'TODO' in line.upper() or 'FIXME' in line.upper()]
        
#         if todo_lines:
#             smells.append(CodeSmell(
#                 smell_type=CodeSmellType.TECHNICAL_DEBT,
#                 description=f"Technical debt markers ({len(todo_lines)} TODO/FIXME comments)",
#                 severity="low",
#                 line_number=todo_lines[0]
#             ))
        
#         return smells
    
#     def _generate_refactoring(
#         self,
#         file_name: str,
#         file_path: str,
#         source_code: str,
#         language: str,
#         code_smells: List[CodeSmell]
#     ) -> RefactorResult:
#         """Generate refactored code using Gemini - ALWAYS CALLED"""
        
#         try:
#             prompt = self._create_refactor_prompt(file_name, source_code, language, code_smells)
            
#             console.print(f"[cyan]🤖 Sending request to Gemini API...[/cyan]")
            
#             # Call Gemini - THIS IS THE CRITICAL CALL
#             response = self.gemini_client.generate_content(prompt)
            
#             if not response or not hasattr(response, 'text'):
#                 return RefactorResult(
#                     success=False,
#                     file_name=file_name,
#                     file_path=file_path,
#                     error="No response from Gemini"
#                 )
            
#             response_text = response.text
            
#             if not response_text:
#                 return RefactorResult(
#                     success=False,
#                     file_name=file_name,
#                     file_path=file_path,
#                     error="Empty response from Gemini"
#                 )
            
#             console.print(f"[green]✅ Received response from Gemini[/green]")
            
#             # Extract refactored code
#             refactored_code = self._extract_refactored_code(response_text, language)
            
#             if not refactored_code:
#                 return RefactorResult(
#                     success=False,
#                     file_name=file_name,
#                     file_path=file_path,
#                     error="Could not extract refactored code from response"
#                 )
            
#             # Extract improvements
#             improvements = self._extract_improvements(response_text)
            
#             # Save refactored code
#             try:
#                 refactored_file = self._save_refactored_code(
#                     file_name, refactored_code, file_path, language, improvements
#                 )
#             except Exception as e:
#                 console.print(f"[yellow]⚠️  Save error: {e}[/yellow]")
#                 refactored_file = Path("unsaved")
            
#             return RefactorResult(
#                 success=True,
#                 file_name=file_name,
#                 file_path=file_path,
#                 original_code=source_code,
#                 refactored_code=refactored_code,
#                 improvements=improvements,
#                 code_smells=code_smells,
#                 refactored_file=str(refactored_file),
#                 lines_before=source_code.count('\n') + 1,
#                 lines_after=refactored_code.count('\n') + 1
#             )
            
#         except Exception as e:
#             console.print(f"[red]❌ Gemini API error: {e}[/red]")
#             return RefactorResult(
#                 success=False,
#                 file_name=file_name,
#                 file_path=file_path,
#                 error=f"Gemini API error: {str(e)}"
#             )
    
#     def _create_refactor_prompt(
#         self,
#         file_name: str,
#         source_code: str,
#         language: str,
#         code_smells: List[CodeSmell]
#     ) -> str:
#         """Create comprehensive refactoring prompt for Gemini"""
        
#         # Format detected issues
#         if code_smells:
#             issues_text = '\n'.join(f"  {i+1}. {str(smell)}" for i, smell in enumerate(code_smells))
#         else:
#             issues_text = "  No critical issues detected - provide general improvements"
        
#         return f"""You are an expert {language} code refactoring specialist. Analyze and refactor the following code to improve quality, readability, maintainability, and performance.

# **FILE:** {file_name}
# **LANGUAGE:** {language}

# **ORIGINAL CODE:**
# ```{language}
# {source_code}
# ```

# **DETECTED ISSUES:**
# {issues_text}

# **REFACTORING OBJECTIVES:**
# 1. **Code Quality**: Improve overall code structure and organization
# 2. **Readability**: Make code self-documenting with clear naming
# 3. **DRY Principle**: Eliminate code duplication
# 4. **Performance**: Optimize time and space complexity
# 5. **Error Handling**: Add comprehensive exception handling
# 6. **Best Practices**: Apply {language} idioms and patterns
# 7. **Maintainability**: Ensure easy modification and testing
# 8. **Type Safety**: Add type hints (for Python) or proper typing

# **REQUIREMENTS:**
# ✓ Maintain exact same functionality
# ✓ Preserve all public APIs
# ✓ Add docstrings and comments where helpful
# ✓ Improve variable and function naming
# ✓ Add error handling for edge cases
# ✓ Optimize algorithm complexity where possible
# ✓ Follow {language} style conventions
# ✓ Keep code in {language}

# **RESPONSE FORMAT:*


# ### Refactored Code
# ```{language}
# [Complete refactored code - production ready]
# ```

# ### Improvements Made
# - [Specific improvement 1]
# - [Specific improvement 2]
# - [Specific improvement 3]
# ...

# Provide clean, optimized, production-ready code following best practices."""
    
#     def _extract_refactored_code(self, response_text: str, language: str) -> str:
#         """Extract the refactored code from Gemini's response"""
        
#         try:
#             # Look for code blocks with multiple patterns
#             patterns = [
#                 rf'```{language}\n(.*?)```',
#                 r'```\n(.*?)```',
#                 r'### Refactored Code\n```.*?\n(.*?)```',
#                 r'## Refactored Code\n```.*?\n(.*?)```'
#             ]
            
#             for pattern in patterns:
#                 matches = re.findall(pattern, response_text, re.DOTALL)
#                 if matches:
#                     # Get the longest match (most likely to be complete code)
#                     code = max(matches, key=len).strip()
                    
#                     # Clean up markdown artifacts
#                     code = re.sub(r'^\s*```.*?\n', '', code)
#                     code = re.sub(r'```\s*$', '', code)
                    
#                     return code.strip()
            
#             # Fallback: look for any code block
#             code_block_match = re.search(r'```(.*?)```', response_text, re.DOTALL)
#             if code_block_match:
#                 return code_block_match.group(1).strip()
            
#         except Exception as e:
#             console.print(f"[yellow]⚠️  Code extraction error: {e}[/yellow]")
        
#         return ""
    
#     def _extract_improvements(self, response_text: str) -> List[str]:
#         """Extract list of improvements from Gemini's response"""
#         improvements = []
        
#         try:
#             lines = response_text.split('\n')
            
#             # Look for improvements section
#             in_improvements = False
            
#             for line in lines:
#                 # Check for section headers
#                 if any(header in line for header in ['### Improvements', '## Improvements', '### Changes', '## Changes']):
#                     in_improvements = True
#                     continue
#                 elif line.startswith('###') or line.startswith('##'):
#                     in_improvements = False
#                 elif in_improvements:
#                     # Extract bullet points
#                     match = re.match(r'^\s*[-*•]\s*(.+)$', line)
#                     if match:
#                         improvements.append(match.group(1).strip())
#                     elif line.strip() and not line.strip().startswith('['):
#                         # Also capture non-bullet lines in improvements section
#                         improvements.append(line.strip())
            
#             # If no improvements found, add a default
#             if not improvements:
#                 improvements = ["Code refactored for improved quality using Gemini AI"]
            
#         except Exception as e:
#             console.print(f"[yellow]⚠️  Improvements extraction error: {e}[/yellow]")
#             improvements = ["Code refactored successfully"]
        
#         return improvements
    
#     def _save_refactored_code(
#         self,
#         file_name: str,
#         refactored_code: str,
#         original_path: str,
#         language: str,
#         improvements: List[str]
#     ) -> Path:
#         """Save the refactored code to a file"""
        
#         try:
#             # Create refactored filename
#             stem = Path(file_name).stem
#             ext = Path(file_name).suffix or {
#                 'python': '.py',
#                 'javascript': '.js',
#                 'java': '.java',
#                 'typescript': '.ts',
#                 'cpp': '.cpp',
#                 'c': '.c'
#             }.get(language, '.txt')
            
#             refactored_file = self.refactor_dir / f"{stem}_refactored{ext}"
            
#             # Create header comment with improvements
#             comment_char = '#' if language in ['python', 'ruby', 'shell'] else '//'
#             improvements_text = '\n'.join(f"{comment_char}   - {imp}" for imp in improvements)
            
#             full_content = f"""{comment_char} REFACTORED CODE (Generated by Gemini AI)
# {comment_char} Original file: {original_path}
# {comment_char} Generated by Refactor Agent using Gemini
# {comment_char}
# {comment_char} Improvements made:
# {improvements_text}
# {comment_char}
# {comment_char} ============================================

# {refactored_code}

# {comment_char} ============================================
# {comment_char} How to use this refactored code:
# {comment_char} 1. Review the changes above carefully
# {comment_char} 2. Test the refactored code thoroughly
# {comment_char} 3. Replace the original file: {original_path}
# {comment_char} 4. Update any imports or references if needed
# """
            
#             with open(refactored_file, 'w', encoding='utf-8') as f:
#                 f.write(full_content)
            
#             console.print(f"[dim]💾 Saved: {refactored_file.name}[/dim]")
            
#             return refactored_file
            
#         except Exception as e:
#             console.print(f"[red]❌ Save error: {e}[/red]")
#             raise
    
#     def _fallback_refactor(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
#         """Fallback refactoring when LLM is not available"""
#         console.print("[yellow]⚠️  Using basic analysis (LLM unavailable)[/yellow]\n")
        
#         improvements = []
#         files_analyzed = 0
        
#         for file_path, file_data in parsed_data.items():
#             if file_data.get('parsed', False):
#                 files_analyzed += 1
                
#                 # Basic suggestions
#                 if file_data.get('functions'):
#                     improvements.append(f"Review function complexity in {Path(file_path).name}")
#                 if file_data.get('classes'):
#                     improvements.append(f"Consider class responsibilities in {Path(file_path).name}")
#                 if file_data.get('lines', 0) > 200:
#                     improvements.append(f"Large file detected: {Path(file_path).name} - consider splitting")
        
#         return {
#             'status': 'completed',
#             'files_analyzed': files_analyzed,
#             'files_refactored': 0,
#             'improvements': improvements[:5],
#             'refactored_files': [],
#             'message': f'Basic analysis completed for {files_analyzed} files (LLM unavailable for full refactoring)'
#         }
#!/usr/bin/env python3
"""
Refactor Agent - AI-powered code refactoring
Analyzes code and generates refactored versions using Gemini
Fixed to always call Gemini for comprehensive refactoring analysis
Results are returned for display by OutputAgent
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from utils.gemini_client import GeminiClient

console = Console()


class CodeSmellType(Enum):
    """Enumeration of code smell types"""
    LONG_FUNCTION = "long_function"
    TOO_MANY_IMPORTS = "too_many_imports"
    CODE_DUPLICATION = "code_duplication"
    LONG_LINES = "long_lines"
    DEEP_NESTING = "deep_nesting"
    MAGIC_NUMBERS = "magic_numbers"
    TECHNICAL_DEBT = "technical_debt"
    GENERAL_IMPROVEMENT = "general_improvement"


@dataclass
class CodeSmell:
    """Represents a detected code smell"""
    smell_type: CodeSmellType
    description: str
    severity: str = "medium"
    line_number: Optional[int] = None
    
    def __str__(self) -> str:
        location = f" (line {self.line_number})" if self.line_number else ""
        return f"[{self.severity.upper()}] {self.description}{location}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'smell_type': self.smell_type.value,
            'description': self.description,
            'severity': self.severity,
            'line_number': self.line_number
        }


@dataclass
class RefactorResult:
    """Structured refactoring result"""
    success: bool
    file_name: str
    file_path: str
    original_code: str = ""
    refactored_code: str = ""
    improvements: List[str] = field(default_factory=list)
    code_smells: List[CodeSmell] = field(default_factory=list)
    refactored_file: str = ""
    lines_before: int = 0
    lines_after: int = 0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for output agent"""
        return {
            'success': self.success,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'original_code': self.original_code,
            'refactored_code': self.refactored_code,
            'improvements': self.improvements,
            'code_smells': [smell.to_dict() for smell in self.code_smells],
            'refactored_file': self.refactored_file,
            'lines_before': self.lines_before,
            'lines_after': self.lines_after,
            'error': self.error
        }


class RefactorAgent:
    """Agent responsible for analyzing and refactoring code"""
    
    # Configuration constants
    MIN_FILE_LINES = 10
    LONG_FUNCTION_THRESHOLD = 50
    MAX_IMPORTS_THRESHOLD = 20
    DUPLICATE_LINE_MIN_LENGTH = 20
    DUPLICATE_OCCURRENCE_THRESHOLD = 2
    LONG_LINE_THRESHOLD = 100
    LONG_LINE_COUNT_THRESHOLD = 5
    DEEP_NESTING_THRESHOLD = 20
    MAGIC_NUMBER_THRESHOLD = 5
    
    def __init__(self):
        """Initialize the refactor agent"""
        self.console = Console()
        self.gemini_client: Optional[GeminiClient] = None
        self.llm_available = False
        self.refactor_dir = Path("refactor/refactored_code")
        self._regex_cache: Dict[str, re.Pattern] = {}
        
        self._initialize_directories()
        self._initialize_llm_client()
    
    def _initialize_directories(self) -> None:
        """Create output directories"""
        try:
            self.refactor_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print(f"[yellow]⚠️  Directory creation warning: {e}[/yellow]")
            self.refactor_dir = Path.cwd() / "refactored_output"
            self.refactor_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_llm_client(self) -> None:
        """Initialize Gemini client with error handling"""
        try:
            self.gemini_client = GeminiClient()
            
            if self.gemini_client is None:
                console.print("[red]❌ GeminiClient returned None[/red]")
                self.llm_available = False
                return
            
            if not hasattr(self.gemini_client, 'model') or self.gemini_client.model is None:
                console.print("[red]❌ LLM model not initialized[/red]")
                self.llm_available = False
                return
            
            self.llm_available = True
            console.print("[green]✅ Refactor Agent LLM initialized successfully[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ LLM initialization error: {e}[/red]")
            self.llm_available = False
    
    def _get_regex_pattern(self, pattern: str) -> re.Pattern:
        """Get or compile regex pattern with caching"""
        if pattern not in self._regex_cache:
            try:
                self._regex_cache[pattern] = re.compile(pattern, re.DOTALL | re.MULTILINE)
            except re.error as e:
                console.print(f"[red]Regex error for pattern {pattern}: {e}[/red]")
                self._regex_cache[pattern] = re.compile(r'(?!.*)')
        return self._regex_cache[pattern]
    
    def refactor_code(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main refactoring entry point - ALWAYS calls Gemini
        Returns results for OutputAgent to display
        
        Args:
            parsed_data: Dictionary of parsed code files
        
        Returns:
            Refactoring results dictionary for OutputAgent
        """
        console.print("\n[bold cyan]🔧 Starting Code Refactoring...[/bold cyan]\n")
        
        if not parsed_data:
            return self._create_empty_result("No data provided")
        
        if not self.llm_available:
            console.print("[red]❌ Gemini LLM unavailable - Cannot proceed with refactoring[/red]")
            return {
                'success': False,
                'status': 'failed',
                'files_analyzed': 0,
                'files_refactored': 0,
                'improvements': [],
                'refactored_files': [],
                'refactoring_details': [],
                'errors': ['Gemini LLM is required for refactoring'],
                'message': 'Gemini LLM unavailable. Please check API configuration.'
            }
        
        refactor_results = {
            'success': True,
            'files_analyzed': 0,
            'files_refactored': 0,
            'improvements': [],
            'refactored_files': [],
            'refactoring_details': [],
            'status': 'completed',
            'errors': []
        }
        
        valid_files = self._filter_valid_files(parsed_data)
        console.print(f"[yellow]📊 Processing {len(valid_files)} file(s) with Gemini...[/yellow]\n")
        
        for file_path, file_data in valid_files.items():
            try:
                console.print(f"[cyan]🤖 Calling Gemini for: {Path(file_path).name}[/cyan]")
                
                result = self._process_single_file(file_path, file_data)
                
                if result.success:
                    refactor_results['files_refactored'] += 1
                    refactor_results['improvements'].extend(result.improvements)
                    refactor_results['refactored_files'].append(result.refactored_file)
                    refactor_results['refactoring_details'].append(result.to_dict())
                    
                    console.print(f"[green]✅ Successfully refactored: {result.file_name}[/green]")
                elif result.error and result.error != "no_issues":
                    error_msg = f"{file_path}: {result.error}"
                    refactor_results['errors'].append(error_msg)
                    console.print(f"[red]❌ Failed: {result.error}[/red]")
                
                refactor_results['files_analyzed'] += 1
                
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                console.print(f"[red]❌ {error_msg}[/red]")
                refactor_results['errors'].append(error_msg)
        
        # Generate summary message
        refactor_results['message'] = (
            f"Refactored {refactor_results['files_refactored']} out of "
            f"{refactor_results['files_analyzed']} files using Gemini AI"
        )
        
        # Add project path if available
        if parsed_data:
            first_file = next(iter(parsed_data.keys()))
            refactor_results['project_path'] = str(Path(first_file).parent)
        
        console.print(f"\n[bold green]✅ Refactoring complete! Results ready for display.[/bold green]")
        
        return refactor_results
    
    def _create_empty_result(self, message: str) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            'success': False,
            'status': 'failed',
            'files_analyzed': 0,
            'files_refactored': 0,
            'improvements': [],
            'refactored_files': [],
            'refactoring_details': [],
            'errors': [message],
            'message': message
        }
    
    def _filter_valid_files(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter valid files for refactoring"""
        valid_files = {}
        
        for file_path, file_data in parsed_data.items():
            try:
                if not isinstance(file_data, dict):
                    continue
                
                if not file_data.get('parsed', False):
                    continue
                
                lines = file_data.get('lines', 0)
                if lines < self.MIN_FILE_LINES:
                    console.print(f"[dim]⏭️  Skipping small file: {Path(file_path).name} ({lines} lines)[/dim]")
                    continue
                
                content = file_data.get('content', '')
                if not content or not isinstance(content, str):
                    continue
                
                valid_files[file_path] = file_data
                
            except Exception as e:
                console.print(f"[yellow]⚠️  Validation error for {file_path}: {e}[/yellow]")
        
        return valid_files
    
    def _process_single_file(self, file_path: str, file_data: Dict[str, Any]) -> RefactorResult:
        """
        Process a single file for refactoring
        ALWAYS calls Gemini regardless of detected code smells
        """
        file_name = Path(file_path).name
        
        try:
            source_code = file_data.get('content', '')
            language = file_data.get('language', 'unknown')
            
            if not source_code:
                return RefactorResult(
                    success=False,
                    file_name=file_name,
                    file_path=file_path,
                    error="Empty source code"
                )
            
            # Detect code smells (for reporting, not for blocking)
            code_smells = self._identify_code_smells(source_code, language, file_data)
            
            # ALWAYS add a general improvement request if no specific smells found
            if not code_smells:
                console.print(f"[green]✨ No critical issues - requesting quality improvements[/green]")
                code_smells = [
                    CodeSmell(
                        smell_type=CodeSmellType.GENERAL_IMPROVEMENT,
                        description="Analyze and improve code quality, readability, and best practices",
                        severity="low"
                    )
                ]
            else:
                console.print(f"[yellow]🔍 Found {len(code_smells)} improvement opportunities[/yellow]")
            
            # ALWAYS call Gemini for refactoring
            return self._generate_refactoring(
                file_name, file_path, source_code, language, code_smells
            )
            
        except Exception as e:
            console.print(f"[red]❌ Processing error: {e}[/red]")
            return RefactorResult(
                success=False,
                file_name=file_name,
                file_path=file_path,
                error=str(e)
            )
    
    def _identify_code_smells(
        self,
        source_code: str,
        language: str,
        file_data: Dict[str, Any]
    ) -> List[CodeSmell]:
        """
        Identify code smells and issues
        Returns empty list if no issues (will still trigger general improvement)
        """
        smells: List[CodeSmell] = []
        
        try:
            lines = source_code.split('\n')
            total_lines = len(lines)
            
            # Check long functions
            smells.extend(self._check_long_functions(file_data))
            
            # Check imports
            smells.extend(self._check_imports(file_data))
            
            # Check duplication
            if total_lines > 100:
                smells.extend(self._check_duplication(lines))
            
            # Check long lines
            smells.extend(self._check_long_lines(lines))
            
            # Check nesting
            smells.extend(self._check_nesting_depth(lines))
            
            # Check magic numbers
            if language == 'python':
                smells.extend(self._check_magic_numbers(source_code))
            
            # Check technical debt
            smells.extend(self._check_technical_debt(lines))
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Code smell detection error: {e}[/yellow]")
        
        return smells
    
    def _check_long_functions(self, file_data: Dict[str, Any]) -> List[CodeSmell]:
        """Check for long functions"""
        smells = []
        functions = file_data.get('functions', [])
        
        if not isinstance(functions, list):
            return smells
        
        for func in functions:
            try:
                if not isinstance(func, dict):
                    continue
                
                func_name = func.get('name', 'unknown')
                func_code = func.get('definition', '')
                
                if isinstance(func_code, str):
                    func_lines = func_code.count('\n') + 1
                    
                    if func_lines > self.LONG_FUNCTION_THRESHOLD:
                        severity = "high" if func_lines > 100 else "medium"
                        smells.append(CodeSmell(
                            smell_type=CodeSmellType.LONG_FUNCTION,
                            description=f"Long function '{func_name}' ({func_lines} lines)",
                            severity=severity
                        ))
            except Exception:
                continue
        
        return smells
    
    def _check_imports(self, file_data: Dict[str, Any]) -> List[CodeSmell]:
        """Check import count"""
        smells = []
        imports = file_data.get('imports', [])
        
        if isinstance(imports, list) and len(imports) > self.MAX_IMPORTS_THRESHOLD:
            severity = "high" if len(imports) > 30 else "medium"
            smells.append(CodeSmell(
                smell_type=CodeSmellType.TOO_MANY_IMPORTS,
                description=f"Too many imports ({len(imports)})",
                severity=severity
            ))
        
        return smells
    
    def _check_duplication(self, lines: List[str]) -> List[CodeSmell]:
        """Check for duplicated lines"""
        smells = []
        line_counts: Dict[str, int] = {}
        
        for line in lines:
            stripped = line.strip()
            if stripped and len(stripped) > self.DUPLICATE_LINE_MIN_LENGTH:
                line_counts[stripped] = line_counts.get(stripped, 0) + 1
        
        duplicates = sum(1 for count in line_counts.values() if count > self.DUPLICATE_OCCURRENCE_THRESHOLD)
        
        if duplicates > 0:
            severity = "high" if duplicates > 10 else "medium"
            smells.append(CodeSmell(
                smell_type=CodeSmellType.CODE_DUPLICATION,
                description=f"Code duplication detected ({duplicates} repeated patterns)",
                severity=severity
            ))
        
        return smells
    
    def _check_long_lines(self, lines: List[str]) -> List[CodeSmell]:
        """Check for long lines"""
        smells = []
        long_lines = [i + 1 for i, line in enumerate(lines) if len(line) > self.LONG_LINE_THRESHOLD]
        
        if len(long_lines) > self.LONG_LINE_COUNT_THRESHOLD:
            smells.append(CodeSmell(
                smell_type=CodeSmellType.LONG_LINES,
                description=f"Multiple long lines ({len(long_lines)} exceeding {self.LONG_LINE_THRESHOLD} chars)",
                severity="low",
                line_number=long_lines[0]
            ))
        
        return smells
    
    def _check_nesting_depth(self, lines: List[str]) -> List[CodeSmell]:
        """Check nesting depth"""
        smells = []
        max_indent = 0
        max_indent_line = 0
        
        for i, line in enumerate(lines, 1):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > max_indent:
                    max_indent = indent
                    max_indent_line = i
        
        if max_indent > self.DEEP_NESTING_THRESHOLD:
            smells.append(CodeSmell(
                smell_type=CodeSmellType.DEEP_NESTING,
                description=f"Deep nesting detected (indent level: {max_indent})",
                severity="medium",
                line_number=max_indent_line
            ))
        
        return smells
    
    def _check_magic_numbers(self, source_code: str) -> List[CodeSmell]:
        """Check for magic numbers"""
        smells = []
        
        try:
            pattern = self._get_regex_pattern(r'\b\d{2,}\b')
            magic_numbers = pattern.findall(source_code)
            
            if len(magic_numbers) > self.MAGIC_NUMBER_THRESHOLD:
                smells.append(CodeSmell(
                    smell_type=CodeSmellType.MAGIC_NUMBERS,
                    description=f"Magic numbers found ({len(magic_numbers)} occurrences)",
                    severity="low"
                ))
        except Exception:
            pass
        
        return smells
    
    def _check_technical_debt(self, lines: List[str]) -> List[CodeSmell]:
        """Check for TODO/FIXME comments"""
        smells = []
        todo_lines = [i + 1 for i, line in enumerate(lines) if 'TODO' in line.upper() or 'FIXME' in line.upper()]
        
        if todo_lines:
            smells.append(CodeSmell(
                smell_type=CodeSmellType.TECHNICAL_DEBT,
                description=f"Technical debt markers ({len(todo_lines)} TODO/FIXME comments)",
                severity="low",
                line_number=todo_lines[0]
            ))
        
        return smells
    
    def _generate_refactoring(
        self,
        file_name: str,
        file_path: str,
        source_code: str,
        language: str,
        code_smells: List[CodeSmell]
    ) -> RefactorResult:
        """Generate refactored code using Gemini - ALWAYS CALLED"""
        
        try:
            prompt = self._create_refactor_prompt(file_name, source_code, language, code_smells)
            
            console.print(f"[cyan]🤖 Sending request to Gemini API...[/cyan]")
            
            # Call Gemini - THIS IS THE CRITICAL CALL
            response = self.gemini_client.generate_content(prompt)
            
            if not response or not hasattr(response, 'text'):
                return RefactorResult(
                    success=False,
                    file_name=file_name,
                    file_path=file_path,
                    error="No response from Gemini"
                )
            
            response_text = response.text
            
            if not response_text:
                return RefactorResult(
                    success=False,
                    file_name=file_name,
                    file_path=file_path,
                    error="Empty response from Gemini"
                )
            
            console.print(f"[green]✅ Received response from Gemini[/green]")
            
            # Extract refactored code
            refactored_code = self._extract_refactored_code(response_text, language)
            
            if not refactored_code:
                return RefactorResult(
                    success=False,
                    file_name=file_name,
                    file_path=file_path,
                    error="Could not extract refactored code from response"
                )
            
            # Extract improvements
            improvements = self._extract_improvements(response_text)
            
            # Save refactored code
            try:
                refactored_file = self._save_refactored_code(
                    file_name, refactored_code, file_path, language, improvements
                )
            except Exception as e:
                console.print(f"[yellow]⚠️  Save error: {e}[/yellow]")
                refactored_file = Path("unsaved")
            
            return RefactorResult(
                success=True,
                file_name=file_name,
                file_path=file_path,
                original_code=source_code,
                refactored_code=refactored_code,
                improvements=improvements,
                code_smells=code_smells,
                refactored_file=str(refactored_file),
                lines_before=source_code.count('\n') + 1,
                lines_after=refactored_code.count('\n') + 1
            )
            
        except Exception as e:
            console.print(f"[red]❌ Gemini API error: {e}[/red]")
            return RefactorResult(
                success=False,
                file_name=file_name,
                file_path=file_path,
                error=f"Gemini API error: {str(e)}"
            )
    
    def _create_refactor_prompt(
        self,
        file_name: str,
        source_code: str,
        language: str,
        code_smells: List[CodeSmell]
    ) -> str:
        """Create comprehensive refactoring prompt for Gemini"""
        
        # Format detected issues
        if code_smells:
            issues_text = '\n'.join(f"  {i+1}. {str(smell)}" for i, smell in enumerate(code_smells))
        else:
            issues_text = "  No critical issues detected - provide general improvements"
        
        return f"""You are an expert {language} code refactoring specialist. Analyze and refactor the following code to improve quality, readability, maintainability, and performance.

**FILE:** {file_name}
**LANGUAGE:** {language}

**ORIGINAL CODE:**
```{language}
{source_code}
```

**DETECTED ISSUES:**
{issues_text}

**REFACTORING OBJECTIVES:**
1. **Code Quality**: Improve overall code structure and organization
2. **Readability**: Make code self-documenting with clear naming
3. **DRY Principle**: Eliminate code duplication
4. **Performance**: Optimize time and space complexity
5. **Error Handling**: Add comprehensive exception handling
6. **Best Practices**: Apply {language} idioms and patterns
7. **Maintainability**: Ensure easy modification and testing
8. **Type Safety**: Add type hints (for Python) or proper typing
9. **don't return to much text - keep it concise**
**REQUIREMENTS:**
✓ Maintain exact same functionality
✓ Preserve all public APIs


✓ Add error handling for edge cases
✓ Optimize algorithm complexity where possible
✓ Follow {language} style conventions
✓ Keep code in {language}

STRICT RULES (MANDATORY):
- Output ONLY valid {language} code
- DO NOT include docstrings
- DO NOT include comments
- DO NOT include explanations
- DO NOT include analysis
- DO NOT repeat the original code
- DO NOT add markdown outside the code block
- DO NOT add example usage or test code
- Keep output minimal and executable
**RESPONSE FORMAT:**



### Refactored Code
```{language}
[Complete refactored code - production ready]
```



Provide clean, optimized, production-ready code following best practices."""
    
    def _extract_refactored_code(self, response_text: str, language: str) -> str:
        """Extract the refactored code from Gemini's response"""
        
        try:
            # Look for code blocks with multiple patterns
            patterns = [
                rf'```{language}\n(.*?)```',
                r'```\n(.*?)```',
                r'### Refactored Code\n```.*?\n(.*?)```',
                r'## Refactored Code\n```.*?\n(.*?)```'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, response_text, re.DOTALL)
                if matches:
                    # Get the longest match (most likely to be complete code)
                    code = max(matches, key=len).strip()
                    
                    # Clean up markdown artifacts
                    code = re.sub(r'^\s*```.*?\n', '', code)
                    code = re.sub(r'```\s*$', '', code)
                    
                    return code.strip()
            
            # Fallback: look for any code block
            code_block_match = re.search(r'```(.*?)```', response_text, re.DOTALL)
            if code_block_match:
                return code_block_match.group(1).strip()
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Code extraction error: {e}[/yellow]")
        
        return ""
    
    def _extract_improvements(self, response_text: str) -> List[str]:
        """Extract list of improvements from Gemini's response"""
        improvements = []
        
        try:
            lines = response_text.split('\n')
            
            # Look for improvements section
            in_improvements = False
            
            for line in lines:
                # Check for section headers
                if any(header in line for header in ['### Improvements', '## Improvements', '### Changes', '## Changes']):
                    in_improvements = True
                    continue
                elif line.startswith('###') or line.startswith('##'):
                    in_improvements = False
                elif in_improvements:
                    # Extract bullet points
                    match = re.match(r'^\s*[-*•]\s*(.+)$', line)
                    if match:
                        improvements.append(match.group(1).strip())
                    elif line.strip() and not line.strip().startswith('['):
                        # Also capture non-bullet lines in improvements section
                        improvements.append(line.strip())
            
            # If no improvements found, add a default
            if not improvements:
                improvements = ["Code refactored for improved quality using Gemini AI"]
            
        except Exception as e:
            console.print(f"[yellow]⚠️  Improvements extraction error: {e}[/yellow]")
            improvements = ["Code refactored successfully"]
        
        return improvements
    
    def _save_refactored_code(
        self,
        file_name: str,
        refactored_code: str,
        original_path: str,
        language: str,
        improvements: List[str]
    ) -> Path:
        """Save the refactored code to a file"""
        
        try:
            # Create refactored filename
            stem = Path(file_name).stem
            ext = Path(file_name).suffix or {
                'python': '.py',
                'javascript': '.js',
                'java': '.java',
                'typescript': '.ts',
                'cpp': '.cpp',
                'c': '.c'
            }.get(language, '.txt')
            
            refactored_file = self.refactor_dir / f"{stem}_refactored{ext}"
            
            # Create header comment with improvements
            comment_char = '#' if language in ['python', 'ruby', 'shell'] else '//'
            improvements_text = '\n'.join(f"{comment_char}   - {imp}" for imp in improvements)
            
            full_content = f"""{comment_char} REFACTORED CODE (Generated by Gemini AI)
{comment_char} Original file: {original_path}
{comment_char} Generated by Refactor Agent using Gemini
{comment_char}
{comment_char} Improvements made:
{improvements_text}
{comment_char}
{comment_char} ============================================

{refactored_code}

{comment_char} ============================================
{comment_char} How to use this refactored code:
{comment_char} 1. Review the changes above carefully
{comment_char} 2. Test the refactored code thoroughly
{comment_char} 3. Replace the original file: {original_path}
{comment_char} 4. Update any imports or references if needed
"""
            
            with open(refactored_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            console.print(f"[dim]💾 Saved: {refactored_file.name}[/dim]")
            
            return refactored_file
            
        except Exception as e:
            console.print(f"[red]❌ Save error: {e}[/red]")
            raise
    
    def _fallback_refactor(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback refactoring when LLM is not available
        NOTE: This should rarely be used as Gemini is required
        """
        console.print("[yellow]⚠️  Using basic analysis (LLM unavailable)[/yellow]\n")
        
        improvements = []
        files_analyzed = 0
        
        for file_path, file_data in parsed_data.items():
            if file_data.get('parsed', False):
                files_analyzed += 1
                
                # Basic suggestions without Gemini
                if file_data.get('functions'):
                    improvements.append(f"Review function complexity in {Path(file_path).name}")
                if file_data.get('classes'):
                    improvements.append(f"Consider class responsibilities in {Path(file_path).name}")
                if file_data.get('lines', 0) > 200:
                    improvements.append(f"Large file detected: {Path(file_path).name} - consider splitting")
        
        return {
            'success': False,
            'status': 'failed',
            'files_analyzed': files_analyzed,
            'files_refactored': 0,
            'improvements': improvements[:5],
            'refactored_files': [],
            'refactoring_details': [],
            'errors': ['Gemini LLM is required for full refactoring'],
            'message': f'Basic analysis completed for {files_analyzed} files (Gemini unavailable)'
        }