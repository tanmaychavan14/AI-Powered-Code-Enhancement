import os
from typing import Optional, Any
from rich.console import Console
from dotenv import load_dotenv

console = Console()

# Load environment variables from .env file
load_dotenv()

class GeminiClient:
    """Client for interacting with Gemini AI"""
    
    def __init__(self):
        self.model = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Gemini client"""
        try:
            # Import API key from .env file
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                console.print("[yellow]Warning: GEMINI_API_KEY not set in .env file[/yellow]")
                return
            
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            
            console.print("[green]✅ Gemini AI initialized from .env file[/green]")
            
        except Exception as e:
            console.print(f"[red]Failed to initialize Gemini: {e}[/red]")
    
    def generate_content(self, prompt: str) -> Optional[Any]:
        """Generate content using Gemini"""
        if not self.model:
            return None
        
        try:
            response = self.model.generate_content(prompt)
            return response
        except Exception as e:
            console.print(f"[red]Gemini generation failed: {e}[/red]")
            return None