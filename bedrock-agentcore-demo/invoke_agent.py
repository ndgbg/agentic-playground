"""
Invoke AgentCore Runtime agent programmatically using boto3.

This script demonstrates how to call a deployed AgentCore agent
using the AWS SDK (boto3).

Prerequisites:
- Agent deployed to AgentCore Runtime
- Agent ARN from deployment
- AWS credentials configured
- bedrock-agentcore:InvokeAgentRuntime permissions
"""

import json
import uuid
import boto3

# Replace with your agent ARN from deployment
AGENT_ARN = "<YOUR_AGENT_ARN_HERE>"

# Your prompt
PROMPT = "Explain what AWS Bedrock AgentCore is in simple terms"

def invoke_agent(agent_arn: str, prompt: str):
    """
    Invoke an AgentCore Runtime agent.
    
    Args:
        agent_arn: ARN of the deployed agent
        prompt: User message to send to the agent
        
    Returns:
        Agent response as a dictionary
    """
    # Initialize the AgentCore client
    client = boto3.client('bedrock-agentcore')
    
    # Prepare the payload
    payload = json.dumps({"prompt": prompt}).encode()
    
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    
    print(f"Invoking agent: {agent_arn}")
    print(f"Session ID: {session_id}")
    print(f"Prompt: {prompt}\n")
    
    # Invoke the agent
    response = client.invoke_agent_runtime(
        agentRuntimeArn=agent_arn,
        runtimeSessionId=session_id,
        payload=payload,
        qualifier="DEFAULT"
    )
    
    # Process the streaming response
    content = []
    for chunk in response.get("response", []):
        content.append(chunk.decode('utf-8'))
    
    # Parse and return the result
    result = json.loads(''.join(content))
    return result

if __name__ == "__main__":
    if AGENT_ARN == "<YOUR_AGENT_ARN_HERE>":
        print("❌ Error: Please set your AGENT_ARN in the script")
        print("Get it from: agentcore deploy output or .bedrock_agentcore.yaml")
        exit(1)
    
    try:
        result = invoke_agent(AGENT_ARN, PROMPT)
        print("✅ Agent Response:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Error invoking agent: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Verify agent ARN is correct")
        print("2. Check AWS credentials: aws sts get-caller-identity")
        print("3. Ensure you have bedrock-agentcore:InvokeAgentRuntime permissions")
        print("4. Verify agent is deployed: agentcore status")
