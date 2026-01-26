# Customer Support Agent

AI-powered customer support system using AWS Bedrock AgentCore with knowledge base integration, ticket management, and sentiment analysis.

## Overview

This demo implements a production-ready customer support agent that can:
- Answer common questions from a knowledge base
- Access customer data and order history
- Create and update support tickets
- Escalate complex issues to human agents
- Analyze sentiment and prioritize urgent requests

## Architecture

```
Customer Query
    ↓
Router Agent (classifies intent)
    ↓
┌──────────┬──────────┬──────────┐
│   FAQ    │ Account  │Technical │
│  Agent   │  Agent   │  Agent   │
└──────────┴──────────┴──────────┘
    ↓           ↓          ↓
Knowledge   CRM/DB    Escalation
  Base                 to Human
```

## Key Features

### Multi-Agent System
- **Router Agent**: Classifies queries and routes to specialists
- **FAQ Agent**: Handles common questions from knowledge base
- **Account Agent**: Accesses customer data, orders, subscriptions
- **Technical Agent**: Troubleshoots technical issues
- **Escalation Agent**: Creates tickets for human review

### Knowledge Base Integration
- Semantic search across documentation
- Automatic answer retrieval
- Source citation
- Confidence scoring

### CRM Integration
- Customer profile lookup
- Order history
- Subscription status
- Previous interactions

### Sentiment Analysis
- Detects frustrated customers
- Prioritizes urgent requests
- Triggers escalation when needed

### Memory
- Remembers customer preferences
- Maintains conversation context
- Learns from interactions

## Quick Start

### Prerequisites
- AWS account with Bedrock AgentCore access
- Python 3.10+
- Knowledge base documents
- CRM API access (optional)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Prepare knowledge base
python prepare_knowledge_base.py --docs ./docs

# Configure agent
agentcore configure -e support_agent.py --enable-memory

# Deploy
agentcore deploy
```

### Test

```bash
# Test locally
python support_agent.py

# Test deployed agent
agentcore invoke '{"prompt": "What is your return policy?"}'
```

## Implementation

### Router Agent

```python
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent

app = BedrockAgentCoreApp()

def route_query(query: str) -> str:
    """Classify query intent"""
    intents = {
        "faq": ["policy", "hours", "shipping", "return"],
        "account": ["order", "subscription", "billing", "account"],
        "technical": ["error", "not working", "broken", "issue"]
    }
    
    query_lower = query.lower()
    for intent, keywords in intents.items():
        if any(keyword in query_lower for keyword in keywords):
            return intent
    
    return "general"

@app.entrypoint
def invoke(payload):
    query = payload.get("prompt")
    intent = route_query(query)
    
    # Route to appropriate agent
    if intent == "faq":
        return faq_agent(query)
    elif intent == "account":
        return account_agent(query, payload.get("customer_id"))
    elif intent == "technical":
        return technical_agent(query)
    else:
        return general_agent(query)
```

### FAQ Agent with Knowledge Base

```python
from bedrock_agentcore.knowledge_base import KnowledgeBase

kb = KnowledgeBase(kb_id="your-kb-id")

def faq_agent(query: str) -> dict:
    """Answer questions from knowledge base"""
    # Search knowledge base
    results = kb.search(query, max_results=3)
    
    if results and results[0].score > 0.7:
        # High confidence answer
        return {
            "answer": results[0].content,
            "source": results[0].source,
            "confidence": results[0].score
        }
    else:
        # Low confidence, escalate
        return {
            "answer": "I'm not sure about that. Let me connect you with a specialist.",
            "escalate": True
        }
```

### Account Agent with CRM

```python
import requests

def account_agent(query: str, customer_id: str) -> dict:
    """Handle account-related queries"""
    # Fetch customer data
    customer = get_customer_data(customer_id)
    orders = get_customer_orders(customer_id)
    
    # Use agent with customer context
    agent = Agent()
    
    context = f"""
    Customer: {customer['name']}
    Email: {customer['email']}
    Status: {customer['status']}
    Recent Orders: {orders[:3]}
    """
    
    result = agent(f"{context}\n\nQuery: {query}")
    
    return {
        "answer": result.message,
        "customer_context": customer
    }

def get_customer_data(customer_id: str) -> dict:
    """Fetch from CRM"""
    response = requests.get(
        f"{CRM_API}/customers/{customer_id}",
        headers={"Authorization": f"Bearer {CRM_TOKEN}"}
    )
    return response.json()
```

### Sentiment Analysis & Escalation

```python
def analyze_sentiment(query: str) -> dict:
    """Detect customer sentiment"""
    negative_indicators = [
        "frustrated", "angry", "terrible", "worst",
        "unacceptable", "disappointed", "furious"
    ]
    
    urgent_indicators = [
        "urgent", "asap", "immediately", "emergency"
    ]
    
    query_lower = query.lower()
    
    is_negative = any(word in query_lower for word in negative_indicators)
    is_urgent = any(word in query_lower for word in urgent_indicators)
    
    return {
        "sentiment": "negative" if is_negative else "neutral",
        "urgency": "high" if is_urgent else "normal",
        "should_escalate": is_negative or is_urgent
    }

def escalate_to_human(query: str, customer_id: str, sentiment: dict) -> dict:
    """Create ticket for human agent"""
    ticket = {
        "customer_id": customer_id,
        "query": query,
        "sentiment": sentiment["sentiment"],
        "urgency": sentiment["urgency"],
        "created_at": datetime.now().isoformat()
    }
    
    # Create ticket in system
    ticket_id = create_ticket(ticket)
    
    # Notify human agent
    notify_agent(ticket_id, urgency=sentiment["urgency"])
    
    return {
        "answer": f"I've created ticket #{ticket_id} and a specialist will help you shortly.",
        "ticket_id": ticket_id
    }
```

## Example Interactions

### Simple FAQ

```
Customer: "What is your return policy?"

Agent: "You can return items within 30 days of purchase for a full refund. 
        Items must be unused and in original packaging. 
        
        Source: Return Policy (https://docs.example.com/returns)"
```

### Account Query

```
Customer: "Where is my order?"

Agent: "Hi Sarah! Your order #12345 shipped yesterday via FedEx. 
        Tracking: 1Z999AA10123456784
        Expected delivery: Tomorrow by 8pm
        
        Would you like me to send tracking updates to your email?"
```

### Escalation

```
Customer: "This is the third time I'm asking! Your product is broken!"

Agent: [Detects negative sentiment + urgency]
       "I sincerely apologize for the frustration. I've created priority 
        ticket #789 and our senior support specialist will contact you 
        within 30 minutes. 
        
        In the meantime, I've also issued a $20 credit to your account."
```

## Configuration

### Knowledge Base Setup

```python
# prepare_knowledge_base.py
from bedrock_agentcore.knowledge_base import create_knowledge_base

kb = create_knowledge_base(
    name="support-kb",
    documents=[
        "./docs/faq.md",
        "./docs/policies.md",
        "./docs/troubleshooting.md"
    ],
    embedding_model="amazon.titan-embed-text-v1"
)

print(f"Knowledge Base ID: {kb.id}")
```

### Memory Configuration

```yaml
memory:
  short_term:
    enabled: true
    ttl: 3600  # 1 hour
  
  long_term:
    enabled: true
    extract_facts: true
    extract_preferences: true
```

### Tool Configuration

```python
@tool
def get_order_status(order_id: str) -> dict:
    """Get order status from order management system"""
    # Implementation
    pass

@tool
def create_ticket(title: str, description: str, priority: str) -> str:
    """Create support ticket"""
    # Implementation
    pass

@tool
def issue_refund(order_id: str, amount: float) -> dict:
    """Issue refund to customer"""
    # Implementation
    pass
```

## Metrics & Monitoring

### Key Metrics

```yaml
operational:
  - queries_per_day
  - response_time_seconds
  - resolution_rate
  - escalation_rate
  
quality:
  - customer_satisfaction_score
  - first_contact_resolution
  - answer_accuracy
  
business:
  - cost_per_query
  - agent_time_saved
  - ticket_deflection_rate
```

### Monitoring Dashboard

```python
# CloudWatch metrics
metrics = {
    "QueryDeflection": 0.75,  # 75% handled by AI
    "AvgResponseTime": 2.3,   # seconds
    "CSAT": 4.2,              # out of 5
    "EscalationRate": 0.15    # 15% escalated
}
```

## Testing

### Unit Tests

```python
def test_router():
    assert route_query("What's your return policy?") == "faq"
    assert route_query("Where's my order?") == "account"
    assert route_query("App won't load") == "technical"

def test_sentiment():
    result = analyze_sentiment("This is terrible!")
    assert result["sentiment"] == "negative"
    assert result["should_escalate"] == True
```

### Integration Tests

```python
def test_end_to_end():
    response = invoke({
        "prompt": "What's your shipping policy?",
        "customer_id": "CUST-123"
    })
    
    assert "shipping" in response["answer"].lower()
    assert response.get("source") is not None
```

## Deployment

### Staging

```bash
agentcore deploy --environment staging
agentcore invoke '{"prompt": "test query"}' --environment staging
```

### Production

```bash
# Deploy with monitoring
agentcore deploy --environment production --enable-observability

# Canary deployment (10% traffic)
agentcore deploy --canary 0.1

# Full rollout
agentcore deploy --promote-canary
```

## Cost Optimization

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_faq_answer(question: str) -> str:
    """Cache common FAQ answers"""
    return kb.search(question)[0].content
```

### Prompt Optimization

```python
# Use shorter prompts for simple queries
if is_simple_query(query):
    prompt = f"Answer briefly: {query}"
else:
    prompt = f"Detailed answer with context: {query}"
```

## Security

### PII Protection

```python
def mask_pii(text: str) -> str:
    """Mask sensitive information"""
    # Mask email
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL]', text)
    # Mask phone
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)
    # Mask credit card
    text = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]', text)
    return text
```

### Access Control

```yaml
permissions:
  faq_agent: read_only
  account_agent: read_customer_data
  technical_agent: read_logs
  escalation_agent: create_tickets
```

## Next Steps

1. Add voice support (phone integration)
2. Multi-language support
3. Proactive support (predict issues)
4. Advanced analytics dashboard
5. A/B testing for response quality

## Resources

- [AgentCore Documentation](https://docs.aws.amazon.com/bedrock-agentcore/)
- [Knowledge Bases Guide](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Best Practices](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/best-practices.html)

---

**Status:** Reference implementation  
**Complexity:** Medium-High  
**Estimated Time:** 1-2 weeks to implement  
**ROI:** High (typical 60-80% query deflection)
