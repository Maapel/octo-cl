# octo_cl/main.py

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from octo_cl.llm_interface import OllamaClient
from octo_cl.context_builder import ContextBuilder
import os
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()
console = Console()

# Configuration
DEFAULT_MODEL = os.getenv("OCTO_MODEL", "qwen2.5-coder:7b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

@app.command()
def chat(
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="The Ollama model to use."),
):
    """
    Start an interactive chat session with octo-cl.
    """
    client = OllamaClient(base_url=OLLAMA_URL, model=model)
    cb = ContextBuilder()
    
    # Initialize messages with a system prompt containing project context
    system_prompt = cb.build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]
    
    console.print(f"[bold blue]octo-cl[/bold blue] (model: {model}) is ready. Type 'exit' or '/help' for options.")
    
    while True:
        try:
            user_input = console.input("[bold green]>>> [/bold green]")
            
            if not user_input.strip():
                continue

            if user_input.lower() in ["exit", "quit"]:
                break
                
            if user_input.startswith("/add "):
                file_path = user_input.split(" ", 1)[1]
                content = cb.get_file_content(file_path)
                messages.append({"role": "user", "content": f"Here is the content of {file_path}:\n{content}"})
                console.print(f"[bold yellow]Added {file_path} to context.[/bold yellow]")
                continue

            if user_input == "/help":
                console.print("[bold cyan]Commands:[/bold cyan]")
                console.print("  /add <file> - Add file content to context")
                console.print("  exit, quit  - End session")
                continue

            messages.append({"role": "user", "content": user_input})
            
            full_response = ""
            console.print("[bold blue]octo-cl:[/bold blue] ", end="")
            
            with Live("", console=console, refresh_per_second=10) as live:
                for chunk in client.chat(messages):
                    full_response += chunk
                    live.update(Markdown(full_response))
            
            messages.append({"role": "assistant", "content": full_response})
            print() # New line after response
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted. Type 'exit' to quit.[/yellow]")
            continue

if __name__ == "__main__":
    app()
