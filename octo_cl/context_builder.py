# octo_cl/context_builder.py

import os
from pathlib import Path
from typing import List, Set
import pathspec

class ContextBuilder:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.gitignore_spec = self._load_gitignore()

    def _load_gitignore(self):
        """Loads .gitignore patterns and returns a PathSpec object."""
        gitignore_path = self.root_dir / ".gitignore"
        patterns = []
        if gitignore_path.exists():
            with open(gitignore_path, "r") as f:
                patterns = f.read().splitlines()
        
        # Add common ignore patterns even if .gitignore is missing
        patterns.extend([".git/", "__pycache__/", "venv/", ".env"])
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    def get_directory_tree(self) -> str:
        """Returns a string representation of the directory tree, respecting .gitignore."""
        tree = []
        for root, dirs, files in os.walk(self.root_dir):
            level = Path(root).relative_to(self.root_dir).parts
            indent = "  " * len(level)
            
            # Filter directories
            dirs[:] = [d for d in dirs if not self.gitignore_spec.match_file(str(Path(root) / d / ""))]
            
            if root != str(self.root_dir):
                tree.append(f"{indent}{os.path.basename(root)}/")
            
            sub_indent = "  " * (len(level) + 1)
            for f in files:
                if not self.gitignore_spec.match_file(str(Path(root) / f)):
                    tree.append(f"{sub_indent}{f}")
                    
        return "\n".join(tree)

    def get_file_content(self, file_path: str) -> str:
        """Reads the content of a file if it's not ignored."""
        full_path = (self.root_dir / file_path).resolve()
        
        # Safety check: ensure file is within root_dir
        if not str(full_path).startswith(str(self.root_dir)):
            return f"Error: Access denied to {file_path}"

        if not full_path.exists():
            return f"Error: File {file_path} not found."

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
                return f"--- FILE: {file_path} ---\n{content}\n--- END FILE ---"
        except Exception as e:
            return f"Error reading {file_path}: {str(e)}"

    def build_system_prompt(self) -> str:
        """Constructs the initial system prompt with project context and tool usage instructions."""
        tree = self.get_directory_tree()
        prompt = (
            "You are octo-cl, an advanced AI coding assistant powered by local LLMs via Ollama.\n"
            "You have access to the user's project files and can help with coding tasks, "
            "refactoring, debugging, and explaining code.\n\n"
            "Current Directory Structure:\n"
            f"```\n{tree}\n```\n\n"
            "--- TOOL USAGE ---\n"
            "You can execute tools by outputting specific XML-like tags. "
            "The tool will execute, and the result will be provided to you in the next message.\n\n"
            "Available Tools:\n"
            "1. <tool_call:read_file path=\"relative/path/to/file\" /> - Read file content.\n"
            "2. <tool_call:write_file path=\"relative/path/to/file\">FILE_CONTENT</tool_call:write_file> - Write file content.\n"
            "3. <tool_call:run_shell command=\"shell command\" /> - Run a shell command in the project root.\n"
            "4. <tool_call:list_files path=\"relative/path/to/dir\" /> - List files in a directory.\n\n"
            "Guidelines:\n"
            "1. Be concise and professional.\n"
            "2. When suggesting code changes, use the `write_file` tool directly instead of just printing it.\n"
            "3. Always explain your thought process before calling a tool.\n"
            "4. Wait for the tool result before proceeding with your next step."
        )
        return prompt
