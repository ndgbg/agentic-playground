# LangGraph Multi-Agent System

Build collaborative agent workflows with state management and conditional routing. Agents work together, passing state and making decisions based on context.

## Overview

LangGraph enables complex multi-agent workflows where agents collaborate, share state, and make routing decisions. Perfect for tasks requiring multiple specialized agents working in sequence or parallel.

## Quick Start

```bash
cd agent-framework-demos/langgraph-multi-agent
pip install -r requirements.txt
python multi_agent.py
```

**Output:**
```
LangGraph Multi-Agent System
============================================================

Query: Write a blog post about artificial intelligence

[RESEARCHER] Gathering information...
Found 5 key points about AI:
- Definition and history
- Machine learning fundamentals
- Current applications
- Future trends
- Ethical considerations

[WRITER] Creating draft...
Draft complete (500 words)
Title: "The Rise of Artificial Intelligence"

[REVIEWER] Reviewing content...
Feedback: Good structure, but needs more examples in section 2.
Requesting revision...

[WRITER] Revising based on feedback...
Revision complete. Added 3 concrete examples.

[REVIEWER] Final review...
✅ Approved! Content is ready for publication.

============================================================
Final Output:

# The Rise of Artificial Intelligence

Artificial intelligence has transformed from a theoretical concept...
[Full blog post content]
============================================================
```

## Architecture

### Agent Roles

**Researcher Agent**
- Gathers information
- Finds relevant sources
- Extracts key points
- Provides context

**Writer Agent**
- Creates content
- Structures information
- Maintains tone and style
- Incorporates feedback

**Reviewer Agent**
- Evaluates quality
- Provides feedback
- Requests revisions
- Approves final output

### State Management

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    query: str
    research: list
    draft: str
    feedback: str
    revision_count: int
    approved: bool
```

### Workflow Graph

```
START
  ↓
RESEARCHER (gather info)
  ↓
WRITER (create draft)
  ↓
REVIEWER (evaluate)
  ↓
  ├─→ APPROVED? → END
  └─→ NEEDS REVISION? → WRITER (revise)
```

## How It Works

### 1. Define State

```python
class ContentState(TypedDict):
    topic: str
    research_data: list
    draft_content: str
    feedback: str
    iterations: int
    final_approved: bool
```

### 2. Create Agent Nodes

```python
def researcher_node(state: ContentState) -> ContentState:
    """Research agent gathers information"""
    research = search_web(state["topic"])
    return {**state, "research_data": research}

def writer_node(state: ContentState) -> ContentState:
    """Writer agent creates content"""
    draft = generate_content(state["topic"], state["research_data"])
    return {**state, "draft_content": draft}

def reviewer_node(state: ContentState) -> ContentState:
    """Reviewer agent evaluates quality"""
    feedback = review_content(state["draft_content"])
    return {**state, "feedback": feedback}
```

### 3. Define Routing Logic

```python
def should_continue(state: ContentState) -> str:
    """Decide next step based on state"""
    if state["final_approved"]:
        return "end"
    elif state["iterations"] >= 3:
        return "end"  # Max revisions reached
    else:
        return "revise"
```

### 4. Build Graph

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(ContentState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("writer", writer_node)
workflow.add_node("reviewer", reviewer_node)

# Add edges
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "reviewer")

# Conditional routing
workflow.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        "revise": "writer",
        "end": END
    }
)

# Set entry point
workflow.set_entry_point("researcher")

# Compile
app = workflow.compile()
```

### 5. Execute Workflow

```python
result = app.invoke({
    "topic": "artificial intelligence",
    "research_data": [],
    "draft_content": "",
    "feedback": "",
    "iterations": 0,
    "final_approved": False
})

print(result["draft_content"])
```

## Features

### State Persistence

```python
from langgraph.checkpoint import MemorySaver

# Add checkpointing
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# Resume from checkpoint
result = app.invoke(state, config={"configurable": {"thread_id": "123"}})
```

### Human-in-the-Loop

```python
from langgraph.checkpoint import interrupt

def reviewer_node(state: ContentState) -> ContentState:
    feedback = review_content(state["draft_content"])
    
    # Pause for human review
    if feedback["score"] < 0.8:
        interrupt("Human review required")
    
    return {**state, "feedback": feedback}
```

### Parallel Execution

```python
# Execute multiple agents in parallel
workflow.add_node("researcher1", research_tech)
workflow.add_node("researcher2", research_business)

# Both run in parallel
workflow.add_edge(START, "researcher1")
workflow.add_edge(START, "researcher2")

# Merge results
workflow.add_edge(["researcher1", "researcher2"], "writer")
```

## Customization

### Add More Agents

```python
def fact_checker_node(state: ContentState) -> ContentState:
    """Verify facts in content"""
    verified = check_facts(state["draft_content"])
    return {**state, "fact_checked": verified}

workflow.add_node("fact_checker", fact_checker_node)
workflow.add_edge("writer", "fact_checker")
workflow.add_edge("fact_checker", "reviewer")
```

### Add Conditional Logic

```python
def route_by_quality(state: ContentState) -> str:
    """Route based on content quality"""
    score = evaluate_quality(state["draft_content"])
    
    if score > 0.9:
        return "publish"
    elif score > 0.7:
        return "minor_edits"
    else:
        return "major_revision"

workflow.add_conditional_edges(
    "reviewer",
    route_by_quality,
    {
        "publish": END,
        "minor_edits": "editor",
        "major_revision": "writer"
    }
)
```

### Add Memory

```python
from langgraph.prebuilt import MemorySaver

memory = MemorySaver()

def writer_node(state: ContentState) -> ContentState:
    # Access previous iterations
    history = memory.get(state["thread_id"])
    
    # Learn from past feedback
    draft = generate_with_history(state["topic"], history)
    
    return {**state, "draft_content": draft}
```

## Use Cases

### Content Creation Pipeline
Research → Write → Review → Edit → Publish

### Code Generation Workflow
Plan → Implement → Test → Review → Deploy

### Data Analysis Pipeline
Collect → Clean → Analyze → Visualize → Report

### Customer Support Escalation
Classify → Respond → Escalate if needed → Resolve

## Best Practices

### Clear State Structure
```python
# ✅ Well-defined state
class State(TypedDict):
    input: str
    intermediate_results: list
    final_output: str
    metadata: dict

# ❌ Unclear state
class State(TypedDict):
    data: dict  # What's in here?
```

### Limit Iterations
```python
def should_continue(state: State) -> str:
    if state["iterations"] >= MAX_ITERATIONS:
        return "end"  # Prevent infinite loops
    return "continue"
```

### Handle Errors
```python
def safe_node(state: State) -> State:
    try:
        result = process(state)
        return {**state, "result": result}
    except Exception as e:
        return {**state, "error": str(e), "failed": True}
```

## Troubleshooting

**Infinite Loops**
- Add iteration counters
- Set max iterations
- Add timeout logic

**State Not Updating**
- Return new state dict
- Don't mutate state in-place
- Check conditional logic

**Slow Execution**
- Use parallel nodes where possible
- Cache expensive operations
- Optimize agent prompts

## Next Steps

1. Design your workflow graph
2. Define state structure
3. Implement agent nodes
4. Add conditional routing
5. Test and iterate
