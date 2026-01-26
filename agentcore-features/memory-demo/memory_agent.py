"""
AgentCore Memory Demo

Demonstrates STM and LTM usage in agents.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from bedrock_agentcore.memory import Memory
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    """
    Agent with memory capabilities.
    
    Memory is automatically managed by AgentCore:
    - STM: Available within session
    - LTM: Persists across sessions
    """
    user_message = payload.get("prompt")
    session_id = payload.get("session_id", "default")
    
    # Memory is automatically injected by AgentCore
    # The agent can reference previous conversations
    
    result = agent(user_message)
    
    return {
        "result": result.message,
        "session_id": session_id
    }

if __name__ == "__main__":
    app.run()
