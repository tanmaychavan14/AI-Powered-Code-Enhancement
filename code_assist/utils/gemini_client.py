# import os
# from typing import Optional, Any
# from rich.console import Console
# from dotenv import load_dotenv

# console = Console()

# # Load environment variables from .env file
# load_dotenv()

# class GeminiClient:
#     """Client for interacting with Gemini AI"""
    
#     def __init__(self):
#         self.model = None
#         self._initialize()
    
#     def _initialize(self):
#         """Initialize Gemini client"""
#         try:
#             # Import API key from .env file
#             api_key = os.getenv('GEMINI_API_KEY')
#             if not api_key:
#                 console.print("[yellow]Warning: GEMINI_API_KEY not set in .env file[/yellow]")
#                 return
            
#             import google.generativeai as genai
#             genai.configure(api_key=api_key)
#             self.model = genai.GenerativeModel('gemini-1.5-flash-001')
            
#             console.print("[green]✅ Gemini AI initialized from .env file[/green]")
            
#         except Exception as e:
#             console.print(f"[red]Failed to initialize Gemini: {e}[/red]")
    
#     def generate_content(self, prompt: str) -> Optional[Any]:
#         """Generate content using Gemini"""
#         if not self.model:
#             return None
        
#         try:
#             response = self.model.generate_content(prompt)
#             return response
#         except Exception as e:
#             console.print(f"[red]Gemini generation failed: {e}[/red]")
#             return None

import os
from dotenv import load_dotenv
from rich.console import Console
import google.generativeai as genai

load_dotenv()
console = Console()

class LLMResponse:
    def __init__(self, text: str):
        self.text = text

class GeminiClient:
    def __init__(self):
        self.client = None
        self.model = None
        self._initialize()

    def _initialize(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            console.print("[yellow]⚠️ GEMINI_API_KEY not set in .env file[/yellow]")
            return

        try:
            # ✅ FIX: Use google.generativeai instead of google.genai
            genai.configure(api_key=api_key)
            
            # ✅ Use the correct SDK and model initialization
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.client = True  # Mark as initialized
            
            console.print(f"[green]✅ Gemini AI initialized with model: gemini-1.5-flash[/green]")
        except Exception as e:
            console.print(f"[red]❌ Gemini initialization failed: {e}[/red]")
            self.client = None
            self.model = None

    def generate_content(self, prompt: str):
        """Generate content using Gemini API"""
        if not self.client or not self.model:
            console.print("[yellow]⚠️ Gemini client not initialized[/yellow]")
            return None

        try:
            # ✅ Use the correct method for content generation
            response = self.model.generate_content(prompt)
            
            # Check if response has text
            if hasattr(response, 'text') and response.text:
                return LLMResponse(response.text)
            else:
                console.print("[yellow]⚠️ Empty response from Gemini[/yellow]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Gemini generation failed: {e}[/red]")
            
            # Provide helpful error message
            if "404" in str(e):
                console.print("[yellow]💡 Tip: Model not found. Make sure you're using the correct SDK[/yellow]")
                console.print("   Install: pip install google-generativeai")
            elif "quota" in str(e).lower() or "limit" in str(e).lower():
                console.print("[yellow]💡 Tip: API quota exceeded. Check your Gemini API usage[/yellow]")
            elif "api key" in str(e).lower() or "401" in str(e) or "403" in str(e):
                console.print("[yellow]💡 Tip: Invalid API key. Check GEMINI_API_KEY in .env[/yellow]")
            elif "safety" in str(e).lower():
                console.print("[yellow]💡 Tip: Content blocked by safety filters[/yellow]")
            
            return None
    
    def list_available_models(self):
        """List available Gemini models (for debugging)"""
        if not self.client:
            console.print("[yellow]Client not initialized[/yellow]")
            return []
        
        try:
            models = genai.list_models()
            console.print("[cyan]Available Gemini models:[/cyan]")
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    console.print(f"  - {model.name}")
            return models
        except Exception as e:
            console.print(f"[red]Failed to list models: {e}[/red]")
            return []