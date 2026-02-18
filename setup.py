from setuptools import setup, find_packages

setup(
    name="octo-cl",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer",
        "httpx",
        "python-dotenv",
        "rich",
        "pathspec",
    ],
    entry_points={
        "console_scripts": [
            "octo=octo_cl.main:app",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="An Ollama-powered AI coding assistant for the terminal.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/octo-cl",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
