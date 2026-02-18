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

@app.command()
def chat(
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="The Ollama model to use."),
):
    """
    Start an interactive chat session with octo-cl.
    """
    client = OllamaClient(base_url=OLLAMA_URL, model=model)
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
                    observation = "User denied the execution of this tool."
                    messages.append({"role": "user", "content": f"Tool '{name}' execution was denied by the user."})
                    continue

            observation = tools.execute(name, **params)
            console.print(f"[bold magenta]Tool Result ({name}):[/bold magenta] {observation[:100]}...")
            messages.append({"role": "user", "content": f"Tool Result ({name}):\n{observation}"})
        
        # After tool execution, the loop continues to let the AI process the observation
        console.print("[dim italic]Agent is thinking based on tool results...[/dim italic]")

if __name__ == "__main__":
    app()
