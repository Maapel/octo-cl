# octo-cl 🐙

[![CI](https://github.com/your-username/octo-cl/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/octo-cl/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/octo-cl.svg)](https://badge.fury.io/py/octo-cl)

**Ollama Coding Tool - Command Line (`octo-cl`)**

`octo-cl` is a CLI-native AI coding assistant designed to work seamlessly with local LLMs through Ollama. It acts as your coding co-pilot, providing codebase context, executing commands, and helping you write and refactor code, all within your terminal. It's inspired by tools like Claude Code and Aider but is built from the ground up for the local-first, privacy-conscious developer.

## ✨ Vision

To provide a powerful, extensible, and open-source AI coding experience that runs entirely on your local machine. `octo-cl` aims to be the go-to tool for developers who want the power of agentic coding without relying on cloud-based services.

## 的核心功能 (Core Features)

*   **Chat with your Code:** Start an interactive session to discuss your codebase.
*   **Context-Aware:** Automatically reads your directory structure, respects `.gitignore`, and intelligently includes relevant file context in prompts.
*   **File Modifications:** Grant the agent permission to read and write files to apply fixes or add features.
*   **Shell Command Execution:** Allow the agent to run shell commands (with your approval) to verify changes, run tests, or install dependencies.
*   **Extensible Tool System:** Designed to be extended with new tools and capabilities.
*   **Ollama Native:** Optimized for use with a wide range of Ollama models.

## 🗺️ Project Roadmap & Milestones

This project is planned in several phases, moving from a simple proof-of-concept to a full-featured coding assistant.

### ✅ **Phase 1: Project Scaffolding & Foundation**
- [X] Define project vision and scope.
- [X] Create directory structure.
- [X] Set up `README.md`, `CONTRIBUTING.md`, and issue/PR templates.
- [X] Establish initial dependencies (`typer`, `httpx`, `python-dotenv`).

### ➡️ **Phase 2: The "Mini" Core Engine (Proof of Concept)**
- [ ] **Goal:** Create a basic interactive CLI loop that can talk to Ollama.
- [ ] Implement `llm_interface` to send a prompt and get a response from an Ollama model.
- [ ] Create a simple `main` CLI entry point.
- [ ] Basic, non-interactive "one-shot" prompt mode (e.g., `octo "how do I add a file?"`).
- [ ] Interactive chat loop (`octo --chat`).

### **Phase 3: Context-Awareness**
- [ ] **Goal:** Enable the agent to understand the project's file structure.
- [ ] Implement `context_builder` to read the directory tree and file contents.
- [ ] Inject context automatically into the LLM prompt.
- [ ] Add commands to manually add files to the context (`/add <file_path>`).

### **Phase 4: Agentic Capabilities (Tool Use)**
- [ ] **Goal:** Allow the agent to perform actions.
- [ ] Define a tool-use schema (e.g., XML or JSON) for the LLM to request actions.
- [ ] Implement core tools: `read_file`, `write_file`, `run_shell`.
- [ ] Create a robust confirmation system to ensure the user approves all actions.
- [ ] Implement the main agent loop: `User Prompt -> Thought -> Action -> Observation -> ... -> Final Answer`.

### **Phase 5: Polish & Extensibility**
- [ ] **Goal:** Make the tool robust, user-friendly, and extensible.
- [ ] Improve logging and error handling.
- [ ] Add configuration file support (`~/.config/octo-cl/config.yaml`).
- [ ] Develop a system for users to add custom tools.
- [ ] Publish to PyPI.

## 🚀 Getting Started

> **Note:** These instructions are for the future. The project is currently in development.

1.  **Install Ollama:** Follow the instructions at [ollama.com](https://ollama.com).
2.  **Pull a Model:** `ollama pull qwen2.5-coder:7b`
3.  **Install `octo-cl`:**
    ```bash
    pip install octo-cl
    ```
4.  **Run:**
    ```bash
    octo "Explain the purpose of this project."
    ```

## 🤝 Contributing

Contributions are welcome! Please read the [`CONTRIBUTING.md`](./CONTRIBUTING.md) file for guidelines on how to set up your development environment, our coding standards, and how to submit a pull request.
