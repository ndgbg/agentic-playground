# LangGraph Multi-Agent System

A demonstration of multiple specialized agents collaborating using LangGraph state management.

## Overview

This demo shows three agents working together:
- **Researcher**: Gathers information and facts
- **Writer**: Creates content based on research
- **Reviewer**: Reviews and provides feedback

## Architecture

```
User Query → Researcher → Writer → Reviewer → Final Output
              ↓           ↓         ↓
           [State]    [State]   [State]
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```python
python multi_agent.py
```

## Features

- State management across agents
- Agent handoffs with context
- Conditional routing based on agent output
- Deploy to AgentCore Runtime

## Files

- `multi_agent.py` - Main agent implementation
- `deploy.py` - AgentCore deployment script
- `requirements.txt` - Dependencies
