# 🔧 AgentCore Features

Demonstrations of AWS Bedrock AgentCore platform capabilities.

## Demos

### [Memory Demo](./memory-demo/)
Short-term and long-term memory for personalized agents.

### [Gateway Integration](./gateway-integration/)
Connect agents to enterprise APIs and MCP tools.

### [Code Interpreter](./code-interpreter/)
Safe Python/JavaScript execution in sandbox.

### [Browser Tool](./browser-tool/)
Web scraping and browser automation.

## Setup

All demos require:
```bash
pip install bedrock-agentcore strands-agents bedrock-agentcore-starter-toolkit
```

Deploy with:
```bash
agentcore configure -e <agent_file>.py
agentcore deploy
```
