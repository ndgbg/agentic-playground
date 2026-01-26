"""
LangGraph Multi-Agent System

Three specialized agents collaborating:
- Researcher: Gathers information
- Writer: Creates content
- Reviewer: Provides feedback
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
import operator

# Define shared state
class AgentState(TypedDict):
    query: str
    research: Annotated[list, operator.add]
    draft: str
    feedback: str
    final_output: str
    iterations: int

# Initialize Claude model
llm = ChatBedrock(
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    region_name="us-west-2"
)

def researcher_agent(state: AgentState) -> AgentState:
    """Research agent gathers information"""
    query = state["query"]
    
    prompt = f"""You are a research agent. Gather key facts and information about: {query}
    
    Provide 3-5 key points."""
    
    response = llm.invoke(prompt)
    
    return {
        **state,
        "research": [response.content],
        "iterations": state.get("iterations", 0) + 1
    }

def writer_agent(state: AgentState) -> AgentState:
    """Writer agent creates content"""
    research = "\n".join(state["research"])
    
    prompt = f"""You are a writer agent. Based on this research:
    
{research}

Write a clear, concise summary (2-3 paragraphs)."""
    
    response = llm.invoke(prompt)
    
    return {
        **state,
        "draft": response.content
    }

def reviewer_agent(state: AgentState) -> AgentState:
    """Reviewer agent provides feedback"""
    draft = state["draft"]
    
    prompt = f"""You are a reviewer agent. Review this draft:
    
{draft}

Provide feedback: Is it clear, accurate, and complete? 
If good, say "APPROVED". If needs work, provide specific feedback."""
    
    response = llm.invoke(prompt)
    feedback = response.content
    
    # If approved, set final output
    if "APPROVED" in feedback.upper():
        return {
            **state,
            "feedback": feedback,
            "final_output": draft
        }
    else:
        return {
            **state,
            "feedback": feedback
        }

def should_continue(state: AgentState) -> str:
    """Decide whether to continue or end"""
    if state.get("final_output"):
        return "end"
    elif state.get("iterations", 0) >= 2:
        # Max 2 iterations, then end
        return "end"
    else:
        return "continue"

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("researcher", researcher_agent)
workflow.add_node("writer", writer_agent)
workflow.add_node("reviewer", reviewer_agent)

# Add edges
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "writer")
workflow.add_edge("writer", "reviewer")

# Conditional edge from reviewer
workflow.add_conditional_edges(
    "reviewer",
    should_continue,
    {
        "continue": "researcher",  # Go back for more research
        "end": END
    }
)

# Compile the graph
app = workflow.compile()

def run_multi_agent(query: str) -> str:
    """Run the multi-agent system"""
    initial_state = {
        "query": query,
        "research": [],
        "draft": "",
        "feedback": "",
        "final_output": "",
        "iterations": 0
    }
    
    result = app.invoke(initial_state)
    return result["final_output"] or result["draft"]

if __name__ == "__main__":
    query = "What is AWS Bedrock AgentCore?"
    print(f"Query: {query}\n")
    
    output = run_multi_agent(query)
    print(f"Final Output:\n{output}")
