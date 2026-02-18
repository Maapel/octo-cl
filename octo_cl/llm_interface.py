# octo_cl/llm_interface.py

import json
import httpx
from typing import Generator, List, Dict

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:7b"):
        self.base_url = base_url
        self.model = model

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
            yield f"
[bold red]Error:[/bold red] Could not connect to Ollama at {self.base_url}. Is it running?"
        except Exception as e:
            yield f"
[bold red]Error:[/bold red] {str(e)}"
