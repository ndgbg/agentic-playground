"""
AWS Bedrock AgentCore - Simple Agent Example

This demonstrates how to create an AI agent using:
- AWS Bedrock AgentCore Runtime
- Strands Agents framework
- Claude foundation model

The agent can:
- Answer questions
- Have conversations
- Be deployed to AgentCore Runtime
- Scale automatically
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

# Initialize the AgentCore app
app = BedrockAgentCoreApp()

# Create a Strands agent
agent = Agent()

@app.entrypoint
def invoke(payload):
    """
    Main entry point for the agent.
    
    Args:
        payload: Dict with 'prompt' key containing user message
        
    Returns:
        Dict with 'result' key containing agent response
    """
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    
    # Process the message through the agent
    result = agent(user_message)
    
    return {"result": result.message}

if __name__ == "__main__":
    # Run locally on port 8080
    app.run()
