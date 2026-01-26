# 🎯 Agent Framework Demos

Working demonstrations of popular AI agent frameworks with production-ready patterns.

## Overview

This section contains fully implemented demos showing how to build multi-agent systems using different frameworks. Each demo includes working code, test cases, and deployment instructions.

## Implemented Demos

### ✅ [LangGraph Multi-Agent](./langgraph-multi-agent/)
**Status:** Fully implemented  
**Complexity:** Medium  
**Time to Run:** 5 minutes

Collaborative agents with state management:
- **Researcher Agent**: Gathers information
- **Writer Agent**: Creates content
- **Reviewer Agent**: Provides feedback

**Key Features:**
- State-based handoffs between agents
- Conditional routing
- Iterative improvement loops
- Memory across agent interactions

**Run:**
```bash
cd langgraph-multi-agent
pip install -r requirements.txt
python multi_agent.py
```

**Use Cases:**
- Content creation pipelines
- Research and analysis
- Document review workflows

---

### ✅ [CrewAI Task Automation](./crewai-task-automation/)
**Status:** Fully implemented  
**Complexity:** Low-Medium  
**Time to Run:** 5 minutes

Role-based agents working in crews:
- **Research Specialist**: Finds information
- **Content Writer**: Creates articles
- **Editor**: Polishes content

**Key Features:**
- Sequential task execution
- Role-based specialization
- Automatic task delegation
- Context sharing between agents

**Run:**
```bash
cd crewai-task-automation
pip install -r requirements.txt
python content_crew.py
```

**Use Cases:**
- Blog post generation
- Report creation
- Marketing content
- Research summaries

---

### ✅ [AutoGen Conversational](./autogen-conversational/)
**Status:** Fully implemented  
**Complexity:** Medium  
**Time to Run:** 5 minutes

Multi-agent conversations with code generation:
- **Assistant Agent**: Writes code
- **Executor Agent**: Runs and validates code
- **User Proxy**: Represents human input

**Key Features:**
- Code generation and execution
- Multi-turn conversations
- Automatic error handling
- Human-in-the-loop workflows

**Run:**
```bash
cd autogen-conversational
pip install -r requirements.txt
python code_assistant.py
```

**Use Cases:**
- Code generation
- Data analysis
- Problem solving
- Automated testing

## Comparison

| Framework | Best For | Complexity | Learning Curve |
|-----------|----------|------------|----------------|
| **LangGraph** | Custom workflows, complex logic | Medium | Medium |
| **CrewAI** | Role-based teams, simple flows | Low | Low |
| **AutoGen** | Code generation, conversations | Medium | Medium |

## When to Use Each

### Use LangGraph When:
- ✅ Need complex state management
- ✅ Conditional routing required
- ✅ Custom workflow logic
- ✅ Iterative processes

### Use CrewAI When:
- ✅ Clear role definitions
- ✅ Sequential workflows
- ✅ Quick prototyping
- ✅ Team-based metaphor fits

### Use AutoGen When:
- ✅ Code generation focus
- ✅ Multi-turn conversations
- ✅ Human oversight needed
- ✅ Automated testing

## Getting Started

### 1. Choose Your Framework

Start with CrewAI if you're new to multi-agent systems. It has the gentlest learning curve.

### 2. Run the Demo

```bash
cd <framework-demo>
pip install -r requirements.txt
python <demo-file>.py
```

### 3. Customize

Modify the agents, tasks, or workflows to fit your use case.

### 4. Deploy

All demos can be deployed to AgentCore Runtime:

```bash
agentcore configure -e <demo-file>.py
agentcore deploy
```

## Common Patterns

### Sequential Pipeline

```
Agent A → Agent B → Agent C → Result
```

**Best Framework:** CrewAI  
**Use Case:** Content creation, data processing

### Conditional Routing

```
Input → Router → Agent A
              → Agent B
              → Agent C
```

**Best Framework:** LangGraph  
**Use Case:** Customer support, task classification

### Iterative Improvement

```
Agent A → Agent B → Review → (loop back if needed) → Done
```

**Best Framework:** LangGraph  
**Use Case:** Code review, content editing

### Conversational

```
User ↔ Assistant ↔ Executor
```

**Best Framework:** AutoGen  
**Use Case:** Code generation, problem solving

## Tips & Best Practices

### Start Simple
Begin with 2-3 agents. Add complexity as needed.

### Clear Roles
Define specific responsibilities for each agent.

### Test Individually
Test each agent separately before combining.

### Monitor Performance
Track execution time and token usage.

### Handle Errors
Implement fallbacks and error recovery.

## Troubleshooting

### Agents Not Communicating

**Issue:** Agents don't share information

**Solutions:**
- Check state management
- Verify context passing
- Review framework documentation

### Infinite Loops

**Issue:** Agents keep passing tasks back and forth

**Solutions:**
- Add max iterations limit
- Implement termination conditions
- Add timeout

### High Costs

**Issue:** Token usage too high

**Solutions:**
- Reduce context size
- Cache repeated queries
- Use smaller models for simple tasks

## Next Steps

1. **Run All Demos**: Try each framework
2. **Compare Results**: See which fits your use case
3. **Customize**: Adapt to your specific needs
4. **Deploy**: Move to production with AgentCore
5. **Monitor**: Track performance and costs

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Multi-Agent Patterns](../../agentic-ai-insights/patterns/multi-agent-orchestration.md)

## Contributing

Have improvements or new framework demos? Contributions welcome!

---

**All demos are production-ready and can be deployed to AgentCore Runtime.**
