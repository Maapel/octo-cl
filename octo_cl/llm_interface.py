# octo_cl/llm_interface.py

import json
import httpx
from typing import Generator, List, Dict, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:7b"):
        self.base_url = base_url
        self.model = model

    def check_connection(self) -> bool:
        """Checks if the Ollama server is reachable."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            return response.status_code == 200
        except Exception:
            return False

    def is_model_available(self) -> bool:
        """Checks if the specified model is pulled and available."""
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=2.0)
            if response.status_code == 200:
                models = response.json().get("models", [])
                # Check for exact match or name-only match (without tag)
                available_names = [m["name"] for m in models]
                return self.model in available_names or any(m.startswith(f"{self.model}:") for m in available_names)
            return False
        except Exception:
            return False

    def chat(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Sends a chat request to Ollama and yields the response chunks.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }

        try:
            with httpx.stream("POST", url, json=payload, timeout=None) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            yield chunk["message"]["content"]
                        if chunk.get("done"):
                            break
        except httpx.ConnectError:
            yield f"\n[bold red]Error:[/bold red] Could not connect to Ollama at {self.base_url}. Is it running?"
        except Exception as e:
            yield f"\n[bold red]Error:[/bold red] {str(e)}"
