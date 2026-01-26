# AgentCore Memory Demo

Demonstrates short-term and long-term memory capabilities in AgentCore.

## Overview

Shows how agents use memory:
- **Short-term memory (STM)**: Conversation context within a session
- **Long-term memory (LTM)**: Persistent facts, preferences, and summaries

## Features

- Session-based conversations with context
- Fact extraction and storage
- Preference learning
- Memory retrieval patterns

## Setup

```bash
pip install -r requirements.txt
agentcore configure -e memory_agent.py
agentcore deploy
```

## Usage

```python
python test_memory.py
```

## Example

Session 1:
- User: "My name is Alice and I love Python"
- Agent: Stores name and preference

Session 2 (different session ID):
- User: "What's my name?"
- Agent: "Your name is Alice" (retrieved from LTM)
