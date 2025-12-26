#!/usr/bin/env python3
"""
Documentation Agent - AI-powered code documentation generator
Generates comprehensive documentation using Gemini AI
Results are returned for display by OutputAgent
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from rich.console import Console

from utils.gemini_client import GeminiClient

console = Console()


@dataclass
class DocumentationResult:
    """Structured documentation result"""
    success: bool
    file_name: str
    file_path: str
    documentation: str = ""
    doc_file_path: str = ""
    sections: Dict[str, str] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for output agent"""
        return {
            'success': self.success,
            'file_name': self.file_name,
            'file_path': self.file_path,
            'documentation': self.documentation,
            'doc_file_path': self.doc_file_path,
            'sections': self.sections,
            'error': self.error
        }


class DocumentationAgent:
    """Agent responsible for generating code documentation"""
    
    MIN_FILE_LINES = 5
    
    def __init__(self):
        """Initialize the documentation agent"""
        self.console = Console()
        self.gemini_client: Optional[GeminiClient] = None
        self.llm_available = False
        self.docs_dir = Path("documentation/generated_docs")
        
        self._initialize_directories()
        self._initialize_llm_client()
    
    def _initialize_directories(self) -> None:
        """Create output directories"""
        try:
            self.docs_dir.mkdir(parents=True, exist_ok=True)
            console.print(f"[dim]📁 Documentation directory: {self.docs_dir}[/dim]")
        except OSError as e:
            console.print(f"[yellow]⚠️  Directory creation warning: {e}[/yellow]")
            self.docs_dir = Path.cwd() / "generated_documentation"
            self.docs_dir.mkdir(parents=True, exist_ok=True)
    
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
            console.print("[green]✅ Documentation Agent LLM initialized successfully[/green]")
            
        except Exception as e:
            console.print(f"[red]❌ LLM initialization error: {e}[/red]")
            self.llm_available = False
    
    def generate_documentation(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main documentation generation entry point
        Returns results for OutputAgent to display
        
        Args:
            parsed_data: Dictionary of parsed code files
        
        Returns:
            Documentation results dictionary for OutputAgent
        """
        console.print("\n[bold cyan]📚 Starting Documentation Generation...[/bold cyan]\n")
        
        if not parsed_data:
            return self._create_empty_result("No data provided")
        
        if not self.llm_available:
            console.print("[red]❌ Gemini LLM unavailable - Cannot generate documentation[/red]")
            return {
                'success': False,
                'status': 'failed',
                'files_analyzed': 0,
                'files_documented': 0,
                'documentation_files': [],
                'documentation_details': [],
                'errors': ['Gemini LLM is required for documentation generation'],
                'message': 'Gemini LLM unavailable. Please check API configuration.'
            }
        
        doc_results = {
            'success': True,
            'files_analyzed': 0,
            'files_documented': 0,
            'documentation_files': [],
            'documentation_details': [],
            'status': 'completed',
            'errors': [],
            'total_sections': 0
        }
        
        valid_files = self._filter_valid_files(parsed_data)
        console.print(f"[yellow]📊 Generating documentation for {len(valid_files)} file(s)...[/yellow]\n")
        
        for file_path, file_data in valid_files.items():
            try:
                console.print(f"[cyan]📝 Documenting: {Path(file_path).name}[/cyan]")
                
                result = self._process_single_file(file_path, file_data)
                
                if result.success:
                    doc_results['files_documented'] += 1
                    doc_results['documentation_files'].append(result.doc_file_path)
                    doc_results['documentation_details'].append(result.to_dict())
                    doc_results['total_sections'] += len(result.sections)
                    
                    console.print(f"[green]✅ Documentation generated: {result.file_name}[/green]")
                elif result.error:
                    error_msg = f"{file_path}: {result.error}"
                    doc_results['errors'].append(error_msg)
                    console.print(f"[red]❌ Failed: {result.error}[/red]")
                
                doc_results['files_analyzed'] += 1
                
            except Exception as e:
                error_msg = f"Error documenting {file_path}: {str(e)}"
                console.print(f"[red]❌ {error_msg}[/red]")
                doc_results['errors'].append(error_msg)
        
        # Generate summary
        doc_results['message'] = (
            f"Generated documentation for {doc_results['files_documented']} out of "
            f"{doc_results['files_analyzed']} files using Gemini AI"
        )
        
        # Calculate coverage
        if doc_results['files_analyzed'] > 0:
            coverage = (doc_results['files_documented'] / doc_results['files_analyzed']) * 100
            doc_results['coverage'] = round(coverage, 1)
        else:
            doc_results['coverage'] = 0.0
        
        # Add project path
        if parsed_data:
            first_file = next(iter(parsed_data.keys()))
            doc_results['project_path'] = str(Path(first_file).parent)
        
        console.print(f"\n[bold green]✅ Documentation generation complete![/bold green]")
        
        return doc_results
    
    def _create_empty_result(self, message: str) -> Dict[str, Any]:
        """Create empty result structure"""
        return {
            'success': False,
            'status': 'failed',
            'files_analyzed': 0,
            'files_documented': 0,
            'documentation_files': [],
            'documentation_details': [],
            'errors': [message],
            'message': message,
            'coverage': 0.0
        }
    
    def _filter_valid_files(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter valid files for documentation"""
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
    
    def _process_single_file(self, file_path: str, file_data: Dict[str, Any]) -> DocumentationResult:
        """Process a single file for documentation"""
        file_name = Path(file_path).name
        
        try:
            source_code = file_data.get('content', '')
            language = file_data.get('language', 'unknown')
            
            if not source_code:
                return DocumentationResult(
                    success=False,
                    file_name=file_name,
                    file_path=file_path,
                    error="Empty source code"
                )
            
            # Generate documentation using Gemini
            return self._generate_documentation(
                file_name, file_path, source_code, language, file_data
            )
            
        except Exception as e:
            console.print(f"[red]❌ Processing error: {e}[/red]")
            return DocumentationResult(
                success=False,
                file_name=file_name,
                file_path=file_path,
                error=str(e)
            )
    
    def _generate_documentation(
        self,
        file_name: str,
        file_path: str,
        source_code: str,
        language: str,
        file_data: Dict[str, Any]
    ) -> DocumentationResult:
        """Generate documentation using Gemini"""
        
        try:
            prompt = self._create_documentation_prompt(
                file_name, source_code, language, file_data
            )
            
            console.print(f"[cyan]🤖 Requesting documentation from Gemini...[/cyan]")
            
            # Call Gemini
            response = self.gemini_client.generate_content(prompt)
            
            if not response or not hasattr(response, 'text'):
                return DocumentationResult(
                    success=False,
                    file_name=file_name,
                    file_path=file_path,
                    error="No response from Gemini"
                )
            
            documentation = response.text
            
            if not documentation:
                return DocumentationResult(
                    success=False,
                    file_name=file_name,
                    file_path=file_path,
                    error="Empty response from Gemini"
                )
            
            console.print(f"[green]✅ Documentation received from Gemini[/green]")
            
            # Extract sections from documentation
            sections = self._extract_sections(documentation)
            
            # Save documentation
            try:
                doc_file = self._save_documentation(
                    file_name, documentation, file_path, language
                )
            except Exception as e:
                console.print(f"[yellow]⚠️  Save error: {e}[/yellow]")
                doc_file = Path("unsaved")
            
            return DocumentationResult(
                success=True,
                file_name=file_name,
                file_path=file_path,
                documentation=documentation,
                doc_file_path=str(doc_file),
                sections=sections
            )
            
        except Exception as e:
            console.print(f"[red]❌ Gemini API error: {e}[/red]")
            return DocumentationResult(
                success=False,
                file_name=file_name,
                file_path=file_path,
                error=f"Gemini API error: {str(e)}"
            )
    
    def _create_documentation_prompt(
        self,
        file_name: str,
        source_code: str,
        language: str,
        file_data: Dict[str, Any]
    ) -> str:
        """Create documentation prompt for Gemini"""
        
        # Extract metadata
        functions = file_data.get('functions', [])
        classes = file_data.get('classes', [])
        imports = file_data.get('imports', [])
        
        metadata_text = f"""
**File Metadata:**
- Functions: {len(functions)}
- Classes: {len(classes)}
- Imports: {len(imports)}
"""
        
        return f"""You are a senior software engineer writing clear developer documentation.

**TASK:**
Explain the following {language} code in a clear and structured way.

**FILE:** {file_name}
**LANGUAGE:** {language}

{metadata_text}

**CODE:**
```{language}
{source_code}
```

**RULES:**
- DO NOT refactor the code
- DO NOT change functionality
- DO NOT add new code
- Explain in simple, developer-friendly language
- Keep it concise but complete
- Focus on WHAT the code does and WHY
- Include usage examples where relevant

**OUTPUT FORMAT (Markdown):**

# {file_name} - Documentation

## File Overview
- What this file does
- Main responsibility
- Purpose in the larger system

## Key Components

### Functions
[For each major function:]
- **Function Name**: Purpose and functionality
- **Parameters**: What they accept
- **Returns**: What they return
- **Usage Example**: How to use it

### Classes
[For each class:]
- **Class Name**: Purpose and responsibility
- **Key Methods**: Important methods and their roles
- **Attributes**: Important attributes

## Execution Flow
- How the code runs step by step
- Entry points (if any)
- Key operations performed

## Dependencies
- What external libraries or modules are used
- Why they're needed

## Important Notes
- Any important assumptions or edge cases
- Potential gotchas or limitations
- Best practices for using this code

## Usage Example
```{language}
# Practical example of how to use this code
```

---
*Documentation generated by AI Documentation Agent*

Provide clear, developer-friendly documentation following this structure."""
    
    def _extract_sections(self, documentation: str) -> Dict[str, str]:
        """Extract sections from generated documentation"""
        sections = {}
        
        try:
            current_section = None
            current_content = []
            
            for line in documentation.split('\n'):
                # Check for main headers (##)
                if line.startswith('## '):
                    # Save previous section
                    if current_section:
                        sections[current_section] = '\n'.join(current_content).strip()
                    
                    # Start new section
                    current_section = line.replace('## ', '').strip()
                    current_content = []
                elif current_section:
                    current_content.append(line)
            
            # Save last section
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
        
        except Exception as e:
            console.print(f"[yellow]⚠️  Section extraction error: {e}[/yellow]")
        
        return sections
    
    def _save_documentation(
        self,
        file_name: str,
        documentation: str,
        original_path: str,
        language: str
    ) -> Path:
        """Save documentation to markdown file"""
        
        try:
            # Create documentation filename
            stem = Path(file_name).stem
            doc_file = self.docs_dir / f"{stem}_README.md"
            
            # Create full documentation with metadata
            full_content = f"""<!-- 
Documentation for: {original_path}
Generated by: Documentation Agent using Gemini AI
Language: {language}
Generated on: {Path().cwd().name}
-->

{documentation}

---

## Original File Information
- **File Path**: `{original_path}`
- **Language**: {language}
- **Documentation Generated**: Automatically by Gemini AI

## How to Use This Documentation
1. Read the File Overview to understand the purpose
2. Check Key Components for detailed function/class information
3. Review Execution Flow to understand how the code works
4. Refer to Usage Examples for practical implementation

## Need Updates?
If this code changes, regenerate documentation by running the Documentation Agent again.
"""
            
            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            console.print(f"[dim]💾 Saved: {doc_file.name}[/dim]")
            
            return doc_file
            
        except Exception as e:
            console.print(f"[red]❌ Save error: {e}[/red]")
            raise


# For backward compatibility
def generate_documentation(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Standalone function for documentation generation"""
    agent = DocumentationAgent()
    return agent.generate_documentation(parsed_data)