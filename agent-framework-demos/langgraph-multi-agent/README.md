# LangGraph Multi-Agent System

Collaborative agents with state management.

## Quick Start
```bash
pip install -r requirements.txt
python multi_agent.py
```

## Agents
- **Researcher**: Gathers information
- **Writer**: Creates content
- **Reviewer**: Provides feedback

## Features
- State-based handoffs
- Conditional routing
- Iterative improvement
- Memory across agents

## Example
```
Query: "Write about AI"
→ Researcher gathers facts
→ Writer creates draft
→ Reviewer approves/requests changes
→ Final output
```

**Status:** ✅ Implemented | **Complexity:** Medium | **Time:** 1 hour
