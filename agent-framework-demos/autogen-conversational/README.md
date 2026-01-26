# AutoGen Conversational Agents

Multi-agent conversations with code generation and execution capabilities.

## Overview

Demonstrates AutoGen's conversational agents:
- **Assistant**: AI agent that writes code
- **Executor**: Executes and validates code
- **User Proxy**: Represents human input

## Features

- Multi-turn conversations
- Code generation and execution
- Human-in-the-loop workflows
- Automatic error handling and retry

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```python
python code_assistant.py
```

## Example

User: "Create a function to calculate fibonacci numbers"
Assistant: Generates Python code
Executor: Runs and validates the code
Output: Working fibonacci function
