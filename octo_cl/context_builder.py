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
                    
        return "
".join(tree)

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
                return f"--- FILE: {file_path} ---
{content}
--- END FILE ---"
        except Exception as e:
            return f"Error reading {file_path}: {str(e)}"

    def build_system_prompt(self) -> str:
        """Constructs the initial system prompt with project context."""
        tree = self.get_directory_tree()
        prompt = (
            "You are octo-cl, an advanced AI coding assistant powered by local LLMs via Ollama.
"
            "You have access to the user's project files and can help with coding tasks, "
            "refactoring, debugging, and explaining code.

"
            "Current Directory Structure:
"
            f"```
{tree}
```

"
            "Guidelines:
"
            "1. Be concise and professional.
"
            "2. When suggesting code changes, provide the full file content or clear diffs.
"
            "3. If you need to see a specific file's content, ask the user to provide it or use your tools (if enabled)."
        )
        return prompt
