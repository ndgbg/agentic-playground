# AgentCore Gateway Integration

Connect AI agents to enterprise APIs and tools using AWS Bedrock AgentCore Gateway and Model Context Protocol (MCP).

## Overview

AgentCore Gateway enables agents to securely access external tools, APIs, and data sources. This demo shows how to:
- Connect agents to enterprise systems (Slack, JIRA, Salesforce)
- Create custom MCP-compatible tools
- Manage tool permissions and access control
- Monitor tool usage and performance

## What is AgentCore Gateway?

AgentCore Gateway converts your APIs, Lambda functions, and services into MCP-compatible tools that agents can discover and use. It provides:
- **Automatic Tool Discovery**: Agents see available tools
- **Secure Access**: OAuth and API key management
- **Rate Limiting**: Control tool usage
- **Observability**: Track tool calls and performance

## Architecture

```
Agent → AgentCore Gateway → External Systems
                ↓
        Tool Registry (MCP)
                ↓
        ┌─────────┬─────────┬─────────┐
        │  Slack  │  JIRA   │ Custom  │
        │   API   │   API   │   API   │
        └─────────┴─────────┴─────────┘
```

## Quick Start

### Prerequisites
- AWS account with AgentCore access
- Python 3.10+
- External API credentials (Slack, JIRA, etc.)

### Setup

```bash
pip install -r requirements.txt

# Configure gateway
agentcore configure -e gateway_agent.py --enable-gateway

# Deploy
agentcore deploy
```

## Example: Slack Integration

### 1. Define Tool

```python
from bedrock_agentcore import BedrockAgentCoreApp, tool

app = BedrockAgentCoreApp()

@tool
def send_slack_message(channel: str, message: str) -> str:
    """Send a message to a Slack channel"""
    import requests
    
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={"Authorization": f"Bearer {SLACK_TOKEN}"},
        json={"channel": channel, "text": message}
    )
    
    return f"Message sent to {channel}"

@app.entrypoint
def invoke(payload):
    from strands import Agent
    
    agent = Agent()
    agent.add_tool(send_slack_message)
    
    result = agent(payload.get("prompt"))
    return {"result": result.message}
```

### 2. Test Locally

```bash
python gateway_agent.py
```

```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Send a message to #general saying Hello World"}'
```

### 3. Deploy

```bash
agentcore deploy
```

## Supported Integrations

### Pre-Built MCP Tools

**Communication:**
- Slack (messages, channels, users)
- Microsoft Teams
- Email (SMTP, SendGrid)

**Project Management:**
- JIRA (issues, projects, workflows)
- Asana
- Monday.com

**CRM:**
- Salesforce (accounts, contacts, opportunities)
- HubSpot
- Zendesk

**Development:**
- GitHub (repos, issues, PRs)
- GitLab
- Bitbucket

### Custom Tools

Create your own tools for:
- Internal APIs
- Databases
- Legacy systems
- Third-party services

## Tool Definition Best Practices

### Clear Descriptions

```python
@tool
def get_customer_data(customer_id: str) -> dict:
    """
    Retrieve customer information from CRM.
    
    Args:
        customer_id: Unique customer identifier (e.g., "CUST-12345")
        
    Returns:
        Dictionary with customer name, email, status, and account details
    """
    # Implementation
```

### Type Hints

```python
from typing import List, Optional

@tool
def search_orders(
    customer_id: str,
    status: Optional[str] = None,
    limit: int = 10
) -> List[dict]:
    """Search customer orders with optional filters"""
    # Implementation
```

### Error Handling

```python
@tool
def call_external_api(endpoint: str) -> dict:
    """Call external API with retry logic"""
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e), "success": False}
```

## Security

### API Key Management

```python
import os
from aws_secretsmanager import get_secret

SLACK_TOKEN = get_secret("slack/bot-token")
JIRA_API_KEY = get_secret("jira/api-key")
```

### Access Control

```yaml
gateway_config:
  tools:
    - name: send_slack_message
      allowed_channels: ["#general", "#alerts"]
      rate_limit: 10/minute
    
    - name: create_jira_ticket
      allowed_projects: ["PROJ1", "PROJ2"]
      requires_approval: true
```

### Audit Logging

All tool calls are logged:
- Timestamp
- Agent ID
- Tool name
- Parameters
- Result
- User context

## Monitoring

### Key Metrics

```yaml
metrics:
  - tool_calls_total
  - tool_latency_seconds
  - tool_errors_total
  - tool_rate_limit_hits
```

### CloudWatch Dashboard

```python
# View tool usage
aws cloudwatch get-metric-statistics \
  --namespace AgentCore/Gateway \
  --metric-name ToolCalls \
  --dimensions Name=ToolName,Value=send_slack_message
```

## Advanced Patterns

### Conditional Tool Access

```python
@tool
def admin_action(action: str) -> str:
    """Admin-only action"""
    if not user_is_admin():
        return "Access denied: Admin privileges required"
    
    # Execute action
    return f"Executed: {action}"
```

### Tool Chaining

```python
@tool
def create_ticket_and_notify(title: str, assignee: str) -> dict:
    """Create JIRA ticket and notify via Slack"""
    # Create ticket
    ticket = create_jira_ticket(title, assignee)
    
    # Notify assignee
    send_slack_message(
        channel=f"@{assignee}",
        message=f"New ticket assigned: {ticket['key']}"
    )
    
    return ticket
```

### Async Tools

```python
@tool
async def fetch_multiple_sources(query: str) -> dict:
    """Fetch data from multiple sources in parallel"""
    results = await asyncio.gather(
        fetch_from_api_a(query),
        fetch_from_api_b(query),
        fetch_from_api_c(query)
    )
    
    return {"sources": results}
```

## Cost Optimization

### Caching

```python
from functools import lru_cache

@tool
@lru_cache(maxsize=100)
def get_static_data(resource_id: str) -> dict:
    """Cached tool for static data"""
    return fetch_data(resource_id)
```

### Rate Limiting

```python
from ratelimit import limits, sleep_and_retry

@tool
@sleep_and_retry
@limits(calls=10, period=60)
def rate_limited_api_call(endpoint: str) -> dict:
    """API call with rate limiting"""
    return requests.get(endpoint).json()
```

## Testing

### Unit Tests

```python
def test_send_slack_message():
    result = send_slack_message("#test", "Hello")
    assert "Message sent" in result
```

### Integration Tests

```python
def test_agent_with_tools():
    agent = Agent()
    agent.add_tool(send_slack_message)
    
    result = agent("Send hello to #general")
    assert result.success
```

## Troubleshooting

### Tool Not Found
- Verify tool is registered with `@tool` decorator
- Check tool is added to agent: `agent.add_tool()`
- Ensure agent is deployed with gateway enabled

### Authentication Errors
- Verify API keys in Secrets Manager
- Check IAM permissions for secret access
- Validate token expiration

### Rate Limit Exceeded
- Implement caching for repeated calls
- Add rate limiting decorators
- Use batch operations where possible

## Next Steps

1. Add more custom tools for your use case
2. Implement tool approval workflows
3. Set up monitoring dashboards
4. Create tool usage analytics
5. Build tool marketplace for your organization

## Resources

- [AgentCore Gateway Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Tool Development Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-tools.html)

---

**Status:** Reference implementation  
**Complexity:** Medium  
**Estimated Time:** 3-5 hours to implement
