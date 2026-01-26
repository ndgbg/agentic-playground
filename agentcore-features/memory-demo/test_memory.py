"""
Test memory capabilities across sessions.
"""

import json
import uuid
import boto3

AGENT_ARN = "<YOUR_AGENT_ARN>"

client = boto3.client('bedrock-agentcore')

def chat(message: str, session_id: str):
    """Send message to agent with session ID"""
    payload = json.dumps({
        "prompt": message,
        "session_id": session_id
    }).encode()
    
    response = client.invoke_agent_runtime(
        agentRuntimeArn=AGENT_ARN,
        runtimeSessionId=session_id,
        payload=payload
    )
    
    content = []
    for chunk in response.get("response", []):
        content.append(chunk.decode('utf-8'))
    
    result = json.loads(''.join(content))
    return result["result"]

if __name__ == "__main__":
    # Session 1: Teach the agent
    session1 = str(uuid.uuid4())
    print("Session 1:")
    print(f"User: My name is Alice and I love Python programming")
    response = chat("My name is Alice and I love Python programming", session1)
    print(f"Agent: {response}\n")
    
    # Session 2: Test memory recall
    session2 = str(uuid.uuid4())
    print("Session 2 (different session):")
    print(f"User: What's my name?")
    response = chat("What's my name?", session2)
    print(f"Agent: {response}\n")
    
    print(f"User: What programming language do I like?")
    response = chat("What programming language do I like?", session2)
    print(f"Agent: {response}")
