# Contributing to octo-cl

First off, thank you for considering contributing to `octo-cl`! Your help is essential for making this tool great.

## How to Contribute

We encourage contributions in the form of bug reports, feature requests, and pull requests.

### 🐛 Reporting Bugs

If you find a bug, please create an issue using the "Bug Report" template. Provide as much detail as possible, including:
- Your operating system.
- Python version.
- The `octo-cl` version you're using.
- Steps to reproduce the bug.
- Any relevant error messages or logs.

### ✨ Requesting Features

If you have an idea for a new feature, please create an issue using the "Feature Request" template. Describe the feature and why you think it would be a valuable addition.

###  Pull Requests

We welcome pull requests for bug fixes and new features. Please follow this process:

1.  **Fork the repository:** Create your own fork of the `octo-cl` repository.
2.  **Create a branch:** Create a new branch for your changes (e.g., `git checkout -b feature/amazing-new-feature`).
3.  **Set up the development environment:** (See below)
4.  **Make your changes:** Implement your changes and ensure you adhere to the coding standards.
5.  **Add tests:** All new features or bug fixes should be accompanied by tests.
6.  **Ensure tests pass:** Run the test suite to make sure your changes haven't introduced any regressions.
7.  **Submit a pull request:** Push your branch to your fork and submit a pull request to the `main` branch of the `octo-cl` repository. Use the pull request template provided.

## 🛠️ Setting up the Development Environment

1.  **Clone your fork:**
    ```bash
    git clone https://github.com/your-username/octo-cl.git
    cd octo-cl
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt # For testing and linting
    ```

## Coding Standards

- **Formatting:** We use [**Black**](https://github.com/psf/black) for code formatting. Please run `black .` before committing your changes.
- **Linting:** We use [**Ruff**](https://github.com/astral-sh/ruff) for linting. Please run `ruff check .` to check for issues.
- **Type Hinting:** All new functions and methods should include type hints.
- **Commit Messages:** Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. For example: `feat: add support for reading files`.

## Submitting a Pull Request

When you're ready to submit a PR, please:
- Fill out the pull request template.
- Ensure your PR is focused on a single change.
- Rebase your branch on the latest `main` to resolve any conflicts.

Thank you for your contributions!
