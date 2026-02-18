# octo_cl/tools.py

import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Callable

class ToolRegistry:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.tools: Dict[str, Callable] = {
            "read_file": self.read_file,
            "write_file": self.write_file,
            "run_shell": self.run_shell,
            "list_files": self.list_files
        }

    def execute(self, tool_name: str, **kwargs) -> str:
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        try:
            return self.tools[tool_name](**kwargs)
        except Exception as e:
            return f"Error executing '{tool_name}': {str(e)}"

    def _is_safe_path(self, path: str) -> bool:
        full_path = (self.root_dir / path).resolve()
        return str(full_path).startswith(str(self.root_dir))

    def read_file(self, path: str) -> str:
        if not self._is_safe_path(path):
            return f"Error: Access denied to {path}"
        try:
            with open(self.root_dir / path, "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading {path}: {str(e)}"

    def write_file(self, path: str, content: str) -> str:
        if not self._is_safe_path(path):
            return f"Error: Access denied to {path}"
        try:
            (self.root_dir / path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.root_dir / path, "w") as f:
                f.write(content)
            return f"Successfully wrote to {path}."
        except Exception as e:
            return f"Error writing to {path}: {str(e)}"

    def run_shell(self, command: str) -> str:
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=self.root_dir
            )
            output = result.stdout + result.stderr
            return f"Command: {command}\nExit Code: {result.returncode}\nOutput:\n{output}"
        except Exception as e:
            return f"Error running command '{command}': {str(e)}"

    def list_files(self, path: str = ".") -> str:
        if not self._is_safe_path(path):
            return f"Error: Access denied to {path}"
        try:
            files = os.listdir(self.root_dir / path)
            return "\n".join(files)
        except Exception as e:
            return f"Error listing {path}: {str(e)}"
