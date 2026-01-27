# AgentCore Memory Demo

Demonstrates short-term and long-term memory capabilities in AI agents using AWS Bedrock AgentCore.

## What's Implemented

A fully functional agent that:
- **Short-Term Memory (STM)**: Maintains conversation context within a session
- **Long-Term Memory (LTM)**: Persists facts and preferences across sessions
- **Automatic Fact Extraction**: Learns from conversations
- **Context-Aware Responses**: Uses memory to personalize interactions

## Quick Start

```bash
cd agentcore-features/memory-demo
pip install -r requirements.txt
python memory_agent.py
```

**Output:**
```
[Session 1 - Learning]
User: My name is Alice and I love Python programming
Agent: Nice to meet you, Alice! Python is a great language.
Learned: ['name: alice', 'likes: python programming']

User: What's my name?
Agent: Your name is Alice.

[Session 2 - Recall from LTM]
User: What's my name?
Agent: Your name is Alice.
Memory: {'stm_items': 1, 'ltm_facts': 2, 'ltm_preferences': 1}
```

## How It Works

### Memory Types

**Short-Term Memory (STM)**
- Session-based storage
- Conversation history
- Expires after session ends
- Fast access

**Long-Term Memory (LTM)**
- Persistent across sessions
- Facts about users
- Preferences and interests
- Survives restarts

### Fact Extraction

The agent automatically extracts facts from conversations:

```python
"My name is Alice" → Stores: name=Alice
"I love Python" → Stores: preference=Python
"I work at Tech Corp" → Stores: occupation=Tech Corp
```

### Context Building

Each query includes relevant memory:

```
What I know about you: name: Alice, occupation: Tech Corp
Your preferences: likes: Python programming
Recent conversation: [last 3 messages]

User: [current question]
```

## Example Interactions

### Learning Phase

```
User: My name is Bob and I'm a software engineer
Agent: Hello Bob! Software engineering is a great field.
[Stores: name=Bob, occupation=software engineer]

User: I love working with AWS
Agent: AWS is a powerful platform!
[Stores: preference=AWS]
```

### Recall Phase (New Session)

```
User: What's my name?
Agent: Your name is Bob.

User: What do I do?
Agent: You're a software engineer.

User: What technologies do I like?
Agent: You love working with AWS.
```

## Customization

### Add Custom Fact Extraction

```python
def extract_facts(text: str) -> list:
    facts = []
    
    # Add your patterns
    if "my birthday is" in text.lower():
        date = extract_date(text)
        facts.append(f"birthday: {date}")
    
    if "i live in" in text.lower():
        location = extract_location(text)
        facts.append(f"location: {location}")
    
    return facts
```

### Configure Memory Persistence

```python
# Use database for LTM
import psycopg2

def save_to_ltm(user_id: str, fact_type: str, value: str):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_memory (user_id, fact_type, value) VALUES (%s, %s, %s)",
        (user_id, fact_type, value)
    )
    conn.commit()
```

### Memory Expiration

```python
from datetime import datetime, timedelta

def save_with_ttl(key: str, value: str, ttl_hours: int = 24):
    expiry = datetime.now() + timedelta(hours=ttl_hours)
    memory[key] = {"value": value, "expires": expiry}
```

## Deploy to AgentCore

```bash
# Configure with memory enabled
agentcore configure -e memory_agent.py --enable-memory

# Deploy
agentcore deploy

# Test
agentcore invoke '{
  "prompt": "My name is Alice",
  "session_id": "session_001",
  "user_id": "alice"
}'
```

## Use Cases

- **Customer Support**: Remember customer preferences and history
- **Personal Assistants**: Learn user habits and preferences
- **Educational Tools**: Track learning progress
- **Healthcare**: Maintain patient context across visits
- **Sales**: Remember customer interactions and needs

## Best Practices

### Clear User IDs
Use consistent user identifiers across sessions:
```python
user_id = hash_email(user_email)  # Consistent ID
```

### Privacy Considerations
```python
# Don't store sensitive data
SENSITIVE_KEYWORDS = ["password", "ssn", "credit card"]

def is_sensitive(text: str) -> bool:
    return any(kw in text.lower() for kw in SENSITIVE_KEYWORDS)

if not is_sensitive(fact):
    save_to_ltm(user_id, fact)
```

### Memory Limits
```python
# Limit memory size
MAX_STM_ITEMS = 10
MAX_LTM_FACTS = 100

if len(stm) > MAX_STM_ITEMS:
    stm = stm[-MAX_STM_ITEMS:]  # Keep recent
```

## Monitoring

```python
# Track memory usage
memory_stats = {
    "stm_sessions": len(short_term_memory),
    "ltm_users": len(long_term_memory),
    "total_facts": sum(len(v["facts"]) for v in long_term_memory.values())
}
```

## Troubleshooting

**Memory Not Persisting**
- Check user_id is consistent
- Verify LTM storage is working
- Check fact extraction patterns

**Context Too Large**
- Limit conversation history
- Summarize old conversations
- Use only relevant facts

**Facts Not Extracted**
- Review extraction patterns
- Add logging to see what's detected
- Test with explicit statements

## Resources

- [AgentCore Memory Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)
- [Memory Best Practices](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-best-practices.html)

---

**Status:** ✅ Fully implemented  
**Complexity:** Medium  
**Time to Deploy:** 30 minutes
