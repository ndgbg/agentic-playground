# 🤖 AWS Bedrock AgentCore Demo

A complete tutorial for building and deploying AI agents using AWS Bedrock AgentCore Runtime with the Strands Agents framework.

## What is AWS Bedrock AgentCore?

AWS Bedrock AgentCore is a comprehensive platform for building, deploying, and operating AI agents at scale. It provides:

- **Runtime**: Serverless execution environment for agents with any framework (Strands, LangGraph, CrewAI)
- **Memory**: Persistent short-term and long-term memory across sessions
- **Gateway**: MCP-compatible tool connections to enterprise APIs
- **Identity**: OAuth and enterprise authentication integration
- **Code Interpreter**: Safe Python/JavaScript/TypeScript execution sandbox
- **Browser**: Cloud-based browser for web interaction
- **Observability**: Tracing, debugging, and monitoring with CloudWatch
- **Policy**: Business rules and access control with Cedar

## This Demo

This tutorial shows you how to:
1. Create an AI agent using Strands Agents framework
2. Test it locally
3. Deploy to AgentCore Runtime
4. Invoke it programmatically with boto3
5. Add memory, tools, and observability

## Quick Start

### Prerequisites

- AWS account with credentials configured
- Python 3.10+
- boto3 installed
- Claude Sonnet 4.0 model access enabled in Bedrock console

### Step 1: Setup Environment

```bash
cd bedrock-agentcore-demo
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install --upgrade pip
pip install bedrock-agentcore strands-agents bedrock-agentcore-starter-toolkit
```

Verify installation:
```bash
agentcore --help
```

### Step 2: Create Your Agent

The `my_agent.py` file contains a simple conversational agent:

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    """Your AI agent function"""
    user_message = payload.get("prompt", "Hello! How can I help you today?")
    result = agent(user_message)
    return {"result": result.message}

if __name__ == "__main__":
    app.run()
```

### Step 3: Test Locally

Start the agent:
```bash
python my_agent.py
```

In another terminal, test it:
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Tell me a joke"}'
```

Stop the agent with `Ctrl+C`.

### Step 4: Configure for Deployment

```bash
agentcore configure -e my_agent.py
```

This creates `.bedrock_agentcore.yaml` with deployment configuration. Accept defaults or customize:
- Region (default: us-west-2)
- Memory options (STM only or STM + LTM)
- Deployment mode (direct_code_deploy or container)

### Step 5: Deploy to AgentCore Runtime

```bash
agentcore deploy
```

This command:
- Packages your agent code
- Creates IAM roles and S3 buckets
- Deploys to AgentCore Runtime
- Provisions memory resources (if configured)
- Sets up CloudWatch logging

**Save the Agent ARN** from the output - you'll need it to invoke the agent.

### Step 6: Test Deployed Agent

```bash
agentcore invoke '{"prompt": "What is quantum computing?"}'
```

### Step 7: Invoke Programmatically

Use the `invoke_agent.py` script:

```python
import json
import uuid
import boto3

agent_arn = "<YOUR_AGENT_ARN>"
prompt = "Explain AI agents in simple terms"

client = boto3.client('bedrock-agentcore')

payload = json.dumps({"prompt": prompt}).encode()

response = client.invoke_agent_runtime(
    agentRuntimeArn=agent_arn,
    runtimeSessionId=str(uuid.uuid4()),
    payload=payload,
    qualifier="DEFAULT"
)

content = []
for chunk in response.get("response", []):
    content.append(chunk.decode('utf-8'))
print(json.loads(''.join(content)))
```

Run it:
```bash
python invoke_agent.py
```

### Step 8: Clean Up

```bash
agentcore destroy
```

## Project Structure

```
bedrock-agentcore-demo/
├── my_agent.py                    # Agent implementation
├── invoke_agent.py                # Programmatic invocation example
├── requirements.txt               # Python dependencies
├── .bedrock_agentcore.yaml        # Deployment config (created by CLI)
└── README.md                      # This file
```

## Advanced Features

### Add Memory

During `agentcore configure`, choose memory options:
- **Short-term memory (STM)**: Conversation context within a session
- **Long-term memory (LTM)**: Persistent facts, preferences, and summaries across sessions

Memory is automatically available to your agent through the AgentCore SDK.

### Add Tools with Gateway

Connect your agent to external APIs and tools using AgentCore Gateway:

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool

app = BedrockAgentCoreApp()
agent = Agent()

@tool
def get_weather(location: str) -> str:
    """Get weather for a location"""
    # Your API call here
    return f"Weather in {location}: Sunny, 72°F"

agent.add_tool(get_weather)

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    result = agent(user_message)
    return {"result": result.message}
```

### Enable Observability

View traces and logs in CloudWatch:
1. Enable CloudWatch Transaction Search (see AWS docs)
2. Deploy your agent
3. View logs at: CloudWatch → Log groups → `/aws/bedrock-agentcore/runtimes/{agent-id}-DEFAULT`

### Add Identity (OAuth)

Integrate with enterprise identity providers:
```bash
agentcore configure -e my_agent.py --enable-identity
```

Then configure OAuth in the AgentCore console.

## Cost Breakdown

- **AgentCore Runtime**: ~$0.10/hour when active
- **Model invocation**: ~$3 per million input tokens (Claude Sonnet 4.0)
- **Memory**: ~$0.30/GB-month for LTM storage
- **Typical conversation**: $0.01 - $0.05

A production agent handling 1000 conversations/day costs roughly $30-50/month.

## Troubleshooting

### Permission Denied
```bash
aws sts get-caller-identity  # Verify credentials
```
Ensure you have `bedrock-agentcore:*` permissions.

### Model Access Denied
Enable Claude Sonnet 4.0 in the Bedrock console for your region.

### Port 8080 in Use (Local Testing)
```bash
# Mac/Linux
lsof -ti:8080 | xargs kill -9

# Windows
# Find and stop process in Task Manager
```

### Memory Not Ready
Memory provisioning takes 2-5 minutes. Check status:
```bash
agentcore status
```

## Resources

- [AWS Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)
- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [Starter Toolkit](https://aws.github.io/bedrock-agentcore-starter-toolkit/)
- [Strands Agents](https://strandsagents.com/)
- [AgentCore SDK](https://github.com/aws/bedrock-agentcore-sdk-python)

## Next Steps

1. Add custom tools for your use case
2. Integrate with enterprise APIs via Gateway
3. Enable long-term memory for personalization
4. Set up observability and monitoring
5. Deploy multiple agents with different capabilities
6. Implement policy controls for production

---

Built with AWS Bedrock AgentCore and Strands Agents
