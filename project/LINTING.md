# Code Linting and Formatting

This document describes how to set up and use the linting and formatting tools for the Wordlas project.

## Setup

### Prerequisites

- Python 3.10+
- Node.js and npm

### Installation

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install JavaScript dependencies:

```bash
cd project
npm install
```

3. Install pre-commit hooks:

```bash
cd project
python -m pre_commit install
```

## Usage

### Pre-commit Hooks

Pre-commit hooks will automatically run when you commit changes. To run them manually on all files:

```bash
cd project
python -m pre_commit run --all-files
```

### Python Tools

- Run pylint:

```bash
pylint project
```

- Format Python code with Black:

```bash
black project
```

- Sort imports with isort:

```bash
isort project
```

### JavaScript Tools

- Lint JavaScript files:

```bash
cd project
npm run lint:js
```

- Format JavaScript files:

```bash
cd project
npm run format:js
```

## Configuration Files

- `.pylintrc`: Pylint configuration
- `.jslintrc`: JSLint configuration
- `.prettierrc`: Prettier configuration for JavaScript formatting
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `pyproject.toml`: Black and isort configuration

## Automated Setup

You can run the setup script to install everything at once:

```bash
cd project
python setup_hooks.py
``` 