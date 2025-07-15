# SK Process Framework Example (Python)

[![CI](https://github.com/${{ github.repository }}/actions/workflows/ci.yml/badge.svg)](https://github.com/${{ github.repository }}/actions/workflows/ci.yml)

Hey there! 👋

This repo is a hands-on example of using the [Semantic Kernel Process Framework](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/examples/example-first-process?pivots=programming-language-python) for orchestrating multi-step AI workflows in Python. The code here is based on (and adapted from) the official Microsoft tutorials:

- [Create your first Process](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/examples/example-first-process?pivots=programming-language-python)
- [Using Cycles (Proofreading/Feedback Loop)](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/process/examples/example-cycles?pivots=programming-language-python)

A few fixes and extra comments/annotations have been added to make things a bit clearer and easier to follow.

## What is this?

This project shows how to build a simple AI-powered process for generating product documentation, then extends it with a proofreading step that loops until the docs are good enough to publish. It's a practical demo of how to chain together steps ("processes") using Semantic Kernel's experimental process framework.

- **part1.py**: The basic process — gather product info, generate docs, publish.
- **part2.py**: Adds a proofreader step and a feedback loop (cycle) so the docs get reviewed and improved before publishing.

## Running the code

You can use either [uv](https://github.com/astral-sh/uv) (a fast Python package manager) or a regular Python virtual environment. Both work fine!

### Option 1: Using uv (recommended for speed)

```sh
uv venv .venv
.venv\Scripts\activate  # On Windows
uv pip install -r requirements.txt  # or just: uv pip install semantic-kernel
```

### Option 2: Using regular venv

```sh
python -m venv .venv
.venv\Scripts\activate  # On Windows
pip install semantic-kernel
```

> **Note:** The project expects `semantic-kernel` as a dependency. You can also use the version specified in `pyproject.toml`.

## Environment setup

You'll need an `.env` file with your Azure OpenAI deployment details. See the provided `.env` for the required variables:

```properties
API_KEY=...
ENDPOINT=...
DEPLOYMENT_NAME=...
```

## How it works

- **part1.py**: Sets up a process with three steps: gather info, generate docs, publish.
- **part2.py**: Adds a proofreader step. If the docs don't pass, suggestions are sent back to the generator for revision, and the cycle repeats until approval.

The code is pretty well commented, so you can follow along and tweak as you like.

## Credits

Big thanks to the [Semantic Kernel team](https://github.com/microsoft/semantic-kernel) and the authors of the official tutorials. This repo is just a slightly annotated and fixed-up version of their great examples.

---

Feel free to fork, play around, and experiment. If you spot any issues or want to suggest improvements, PRs are welcome!
