# AgentCore Gateway Integration

Connect AI agents to external tools using AWS Bedrock AgentCore Gateway. This demo shows a working implementation of an agent with multiple tools.

## What's Implemented

A fully functional agent with 4 tools:
- **Weather Tool**: Get weather for any city
- **Database Search**: Query simulated customer/order database
- **Notifications**: Send messages to users
- **Calculator**: Perform mathematical calculations

The agent automatically selects and uses the right tool based on user queries.

## Quick Start

### Run Locally

```bash
cd agentcore-features/gateway-integration

# Install dependencies
pip install -r requirements.txt

# Run demo with test cases
python gateway_agent.py
```

**Output:**
```
Gateway Integration Demo
==================================================

Query: What's the weather in Seattle?
Response: Weather in Seattle: Rainy, 52°F
--------------------------------------------------

Query: Search for customers in the database
Response: Found 2 customers: Alice Smith (C001), Bob Jones (C002)
--------------------------------------------------

Query: Calculate 25 * 4
Response: The result is 100.0
--------------------------------------------------
```

### Deploy to AgentCore

```bash
# Configure for deployment
agentcore configure -e gateway_agent.py

# Deploy to AWS
agentcore deploy

# Test deployed agent
agentcore invoke '{"prompt": "What is the weather in Miami?"}'
```

### Test with curl

```bash
# Start local server
python gateway_agent.py

# In another terminal
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Calculate 15 + 27"}'
```

## How It Works

### Tool Definition

Tools are defined with the `@tool` decorator:

```python
@tool
def get_weather(location: str) -> str:
    """
    Get current weather for a location.
    
    Args:
        location: City name (e.g., "Seattle")
    
    Returns:
        Weather description
    """
    # Implementation
    return f"Weather in {location}: Sunny, 72°F"
```

### Agent Setup

The agent is configured with all available tools:

```python
agent = Agent()
agent.add_tool(get_weather)
agent.add_tool(search_database)
agent.add_tool(send_notification)
agent.add_tool(calculate)

# Agent automatically uses tools as needed
result = agent(user_message)
```

### Automatic Tool Selection

The agent analyzes the query and selects appropriate tools:

```
User: "What's the weather in Seattle?"
→ Agent calls get_weather("Seattle")
→ Returns: "Weather in Seattle: Rainy, 52°F"

User: "Calculate 25 * 4"
→ Agent calls calculate("25 * 4")
→ Returns: "100.0"
```

## Customizing Tools

### Add Your Own Tool

```python
@tool
def your_custom_tool(param: str) -> str:
    """
    Description of what your tool does.
    
    Args:
        param: Parameter description
    
    Returns:
        What the tool returns
    """
    # Your implementation
    return result

# Add to agent
agent.add_tool(your_custom_tool)
```

### Connect to Real APIs

Replace simulated data with actual API calls:

```python
@tool
def get_weather(location: str) -> str:
    """Get real weather data"""
    import requests
    
    api_key = os.getenv("WEATHER_API_KEY")
    response = requests.get(
        f"https://api.weather.com/v1/current",
        params={"location": location, "key": api_key}
    )
    
    data = response.json()
    return f"Weather in {location}: {data['condition']}, {data['temp']}°F"
```

### Database Integration

```python
@tool
def search_database(query: str) -> dict:
    """Search real database"""
    import psycopg2
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM customers WHERE name LIKE %s", (f"%{query}%",))
    results = cursor.fetchall()
    
    return {"results": results, "count": len(results)}
```

## Example Queries

Try these queries with the demo:

**Weather:**
- "What's the weather in New York?"
- "Is it raining in Seattle?"
- "Tell me the weather in San Francisco"

**Database:**
- "Search for customers"
- "Find orders in the database"
- "Look up customer information"

**Calculations:**
- "Calculate 123 * 456"
- "What is 50 + 75?"
- "Compute 100 / 4"

**Notifications:**
- "Send a notification to alice@example.com saying 'Meeting at 3pm'"
- "Notify bob@example.com about the deadline"

**Multi-Tool:**
- "Check the weather in Miami and send a notification to alice@example.com"
- "Search for customer orders and calculate the total"

## Tool Best Practices

### Clear Descriptions

```python
@tool
def process_data(data: str) -> dict:
    """
    Process customer data and return insights.
    
    This tool analyzes customer behavior patterns and returns
    actionable insights for marketing campaigns.
    
    Args:
        data: Customer data in JSON format
    
    Returns:
        Dictionary with insights and recommendations
    """
```

### Type Hints

Always use type hints for parameters and return values:

```python
from typing import List, Dict, Optional

@tool
def search_items(
    query: str,
    category: Optional[str] = None,
    limit: int = 10
) -> List[Dict]:
    """Search with optional filters"""
```

### Error Handling

```python
@tool
def api_call(endpoint: str) -> dict:
    """Call external API with error handling"""
    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.Timeout:
        return {"success": False, "error": "Request timed out"}
    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
```

## Security Considerations

### API Keys

Store sensitive data in environment variables:

```python
import os

API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
```

### Input Validation

```python
@tool
def safe_calculation(expression: str) -> float:
    """Safely evaluate math expressions"""
    # Only allow numbers and basic operators
    allowed_chars = set("0123456789+-*/(). ")
    if not all(c in allowed_chars for c in expression):
        return "Error: Invalid characters in expression"
    
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        return f"Error: {str(e)}"
```

### Rate Limiting

```python
from functools import lru_cache
from time import time

@tool
@lru_cache(maxsize=100)
def cached_api_call(endpoint: str) -> dict:
    """Cached API call to reduce requests"""
    return requests.get(endpoint).json()
```

## Monitoring

### Tool Usage Tracking

```python
tool_calls = {}

@tool
def tracked_tool(param: str) -> str:
    """Tool with usage tracking"""
    tool_calls["tracked_tool"] = tool_calls.get("tracked_tool", 0) + 1
    # Implementation
    return result

# View usage
print(f"Tool called {tool_calls['tracked_tool']} times")
```

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def logged_tool(param: str) -> str:
    """Tool with logging"""
    logger.info(f"Tool called with param: {param}")
    result = process(param)
    logger.info(f"Tool returned: {result}")
    return result
```

## Troubleshooting

### Tool Not Being Called

**Issue:** Agent doesn't use your tool

**Solutions:**
1. Check tool description is clear
2. Verify tool is added to agent: `agent.add_tool(your_tool)`
3. Make sure query matches tool's purpose
4. Add more descriptive docstring

### Import Errors

**Issue:** `ModuleNotFoundError`

**Solution:**
```bash
pip install -r requirements.txt
```

### Agent Returns Generic Response

**Issue:** Agent doesn't use tools, just answers directly

**Solution:**
- Make tool descriptions more specific
- Explicitly mention tool capabilities in system prompt
- Test with queries that clearly need tool usage

## Next Steps

1. **Add Real APIs**: Replace simulated data with actual API calls
2. **Add More Tools**: Implement tools for your specific use case
3. **Deploy to Production**: Use `agentcore deploy` for production deployment
4. **Add Authentication**: Implement OAuth or API key validation
5. **Monitor Usage**: Set up CloudWatch dashboards

## Resources

- [AgentCore Gateway Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html)
- [Tool Development Guide](https://strandsagents.com/latest/documentation/docs/user-guide/tools/)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Status:** ✅ Fully implemented and tested  
**Complexity:** Low-Medium  
**Time to Deploy:** 30 minutes

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
