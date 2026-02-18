# octo_cl/main.py

import typer
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from octo_cl.llm_interface import OllamaClient
from octo_cl.context_builder import ContextBuilder
from octo_cl.tools import ToolRegistry
import os
import re
import sys
import subprocess
import time
import shutil
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()
console = Console()

# Configuration
DEFAULT_MODEL = os.getenv("OCTO_MODEL", "qwen2.5-coder:7b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def parse_tool_calls(text: str):
    """Parses tool calls from LLM response."""
    # Pattern for <tool_call:name param="val" />
    single_pattern = r'<tool_call:(\w+)\s+([^>]*)\s*/>'
    # Pattern for <tool_call:name param="val">content</tool_call:name>
    content_pattern = r'<tool_call:(\w+)\s+([^>]*)>(.*?)</tool_call:\1>'
    
    calls = []
    
    # Find calls with content (like write_file)
    for match in re.finditer(content_pattern, text, re.DOTALL):
        name = match.group(1)
        params_str = match.group(2)
        content = match.group(3)
        
        params = {}
        for p_match in re.finditer(r'(\w+)="([^"]*)"', params_str):
            params[p_match.group(1)] = p_match.group(2)
        params['content'] = content
        calls.append({"name": name, "params": params, "full_match": match.group(0)})
        
    # Find single-line calls
    for match in re.finditer(single_pattern, text):
        name = match.group(1)
        params_str = match.group(2)
        
        params = {}
        for p_match in re.finditer(r'(\w+)="([^"]*)"', params_str):
            params[p_match.group(1)] = p_match.group(2)
        calls.append({"name": name, "params": params, "full_match": match.group(0)})
        
    return calls

def try_start_ollama():
    """Attempts to start the Ollama server if it's installed."""
    ollama_path = shutil.which("ollama")
    if not ollama_path:
        console.print(Panel(
            "[bold yellow]Ollama is not installed or not in PATH.[/bold yellow]\n\n"
            "To install it:\n"
            " - [bold cyan]Linux/macOS:[/bold cyan] curl -fsSL https://ollama.com/install.sh | sh\n"
            " - [bold cyan]Termux:[/bold cyan] Requires proot-distro (e.g., Ubuntu) to run Ollama.\n"
            " - [bold cyan]Windows:[/bold cyan] Download from ollama.com",
            title="Ollama Not Found", border_style="yellow"
        ))
        return False

    if typer.confirm("Ollama is not running. Would you like to try starting it?"):
        console.print("[bold blue]Starting Ollama server...[/bold blue]")
        # Start ollama serve in the background
        subprocess.Popen([ollama_path, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for it to spin up
        with console.status("[bold green]Waiting for Ollama to respond...[/bold green]"):
            for _ in range(10):
                time.sleep(1)
                if OllamaClient(base_url=OLLAMA_URL).check_connection():
                    console.print("[bold green]Ollama is now running![/bold green]")
                    return True
        
        console.print("[bold red]Ollama started but is not responding. Check logs.[/bold red]")
    return False

@app.command()
def chat(
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="The Ollama model to use."),
):
    """
    Start an interactive chat session with octo-cl.
    """
    client = OllamaClient(base_url=OLLAMA_URL, model=model)
    
    # --- Pre-flight Checks ---
    if not client.check_connection():
        if not try_start_ollama():
            sys.exit(1)

    if not client.is_model_available():
        console.print(Panel(
            f"[bold red]Error:[/bold red] Model [bold cyan]{model}[/bold cyan] not found in Ollama.\n\n"
            f"Run [bold green]ollama pull {model}[/bold green] to download it first.",
            title="Model Missing", border_style="red"
        ))
        sys.exit(1)
    # -------------------------

    cb = ContextBuilder()
    tools = ToolRegistry()
    
    system_prompt = cb.build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]
    
    console.print(f"[bold blue]octo-cl[/bold blue] (model: {model}) is ready. Type 'exit' or '/help'.")
    
    while True:
        try:
            user_input = console.input("[bold green]>>> [/bold green]")
            
            if not user_input.strip():
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
            if user_input == "/help":
                console.print("[bold cyan]Commands:[/bold cyan]\n  /add <file> - Add file to context\n  exit, quit  - End session")
                continue
            if user_input.startswith("/add "):
                file_path = user_input.split(" ", 1)[1]
                content = cb.get_file_content(file_path)
                messages.append({"role": "user", "content": f"Content of {file_path}:\n{content}"})
                console.print(f"[bold yellow]Added {file_path} to context.[/bold yellow]")
                continue

            messages.append({"role": "user", "content": user_input})
            
            process_ai_response(client, messages, tools)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Session interrupted.[/yellow]")
            continue

def process_ai_response(client, messages, tools):
    while True:
        full_response = ""
        console.print("[bold blue]octo-cl:[/bold blue] ", end="")
        
        with Live("", console=console, refresh_per_second=10) as live:
            for chunk in client.chat(messages):
                full_response += chunk
                live.update(Markdown(full_response))
        
        messages.append({"role": "assistant", "content": full_response})
        print()
        
        tool_calls = parse_tool_calls(full_response)
        if not tool_calls:
            break
            
        for call in tool_calls:
            name = call['name']
            params = call['params']
            
            # Security Confirmation
            if name in ["write_file", "run_shell"]:
                console.print(Panel(f"[bold red]Security Check:[/bold red] Agent wants to call [bold cyan]{name}[/bold cyan]\nArgs: {params}", expand=False))
                confirm = typer.confirm("Allow this action?")
                if not confirm:
                    messages.append({"role": "user", "content": f"Tool '{name}' execution was denied by the user."})
                    continue

            observation = tools.execute(name, **params)
            console.print(f"[bold magenta]Tool Result ({name}):[/bold magenta] {observation[:100]}...")
            messages.append({"role": "user", "content": f"Tool Result ({name}):\n{observation}"})
        
        console.print("[dim italic]Agent is thinking based on tool results...[/dim italic]")

if __name__ == "__main__":
    app()
