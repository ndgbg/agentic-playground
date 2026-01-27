# AutoGen Conversational Agents

Multi-agent conversations with code generation and execution. Agents discuss, write code, run it, and iterate based on results.

## Overview

AutoGen enables building conversational agent systems where agents can discuss problems, generate code, execute it, and iterate based on results. Perfect for code generation, data analysis, and problem-solving tasks.

## Quick Start

```bash
cd agent-framework-demos/autogen-conversational
pip install -r requirements.txt
python code_assistant.py
```

**Output:**
```
AutoGen Code Assistant
============================================================

User: Calculate the first 10 Fibonacci numbers

[Assistant] I'll write a Python function to calculate Fibonacci numbers.

```python
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

result = fibonacci(10)
print(result)
```

[Executor] Running code...

Output:
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

[Assistant] The first 10 Fibonacci numbers are: 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

============================================================

User: Now plot them

[Assistant] I'll create a visualization using matplotlib.

```python
import matplotlib.pyplot as plt

fib = fibonacci(10)
plt.plot(fib, marker='o')
plt.title('First 10 Fibonacci Numbers')
plt.xlabel('Index')
plt.ylabel('Value')
plt.grid(True)
plt.savefig('fibonacci.png')
print("Plot saved to fibonacci.png")
```

[Executor] Running code...

Output:
Plot saved to fibonacci.png

[Assistant] I've created a plot showing the growth of Fibonacci numbers.
The plot has been saved to fibonacci.png.

============================================================
```

## Architecture

### Agent Types

**Assistant Agent**
- Generates code
- Explains solutions
- Suggests improvements
- Responds to feedback

**User Proxy Agent**
- Executes code
- Provides feedback
- Asks questions
- Approves/rejects solutions

**Custom Agents**
- Specialized roles
- Domain expertise
- Tool access
- Custom behaviors

### Basic Setup

```python
import autogen

# Configure LLM
config_list = [{
    "model": "gpt-4",
    "api_key": "your-key"
}]

# Create assistant
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config={"config_list": config_list}
)

# Create user proxy (executes code)
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False
    }
)

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Calculate the first 10 Fibonacci numbers"
)
```

## Features

### Code Generation

Agents write code to solve problems:

```python
assistant = autogen.AssistantAgent(
    name="coder",
    system_message="""You are a helpful AI assistant that writes Python code.
    Always provide complete, runnable code.""",
    llm_config=llm_config
)
```

### Code Execution

Automatically run generated code:

```python
executor = autogen.UserProxyAgent(
    name="executor",
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": True,  # Safer execution
        "timeout": 60
    }
)
```

### Multi-Turn Conversations

Agents iterate based on results:

```
User: "Analyze this data"
→ Assistant: Writes analysis code
→ Executor: Runs code, returns results
→ Assistant: Interprets results
→ User: "Now visualize it"
→ Assistant: Writes visualization code
→ Executor: Creates plot
```

### Human-in-the-Loop

Get human input when needed:

```python
user_proxy = autogen.UserProxyAgent(
    name="user",
    human_input_mode="ALWAYS",  # Always ask for input
    # or "TERMINATE" - ask only at termination
    # or "NEVER" - fully automated
)
```

## Example Use Cases

### Data Analysis

```python
user_proxy.initiate_chat(
    assistant,
    message="""
    Analyze the CSV file 'sales.csv':
    1. Load the data
    2. Calculate total sales by region
    3. Find top 5 products
    4. Create a bar chart
    """
)
```

### Web Scraping

```python
user_proxy.initiate_chat(
    assistant,
    message="""
    Scrape the top 10 articles from Hacker News:
    1. Use requests and BeautifulSoup
    2. Extract title and URL
    3. Save to JSON file
    """
)
```

### API Integration

```python
user_proxy.initiate_chat(
    assistant,
    message="""
    Fetch weather data from OpenWeather API:
    1. Get current weather for New York
    2. Extract temperature and conditions
    3. Format as readable text
    """
)
```

## Customization

### Add Custom Functions

```python
def search_database(query: str) -> str:
    """Search internal database"""
    results = db.query(query)
    return str(results)

# Register function
autogen.register_function(
    search_database,
    caller=assistant,
    executor=user_proxy,
    description="Search the internal database"
)
```

### Multi-Agent Conversations

```python
# Create multiple agents
planner = autogen.AssistantAgent(name="planner", ...)
coder = autogen.AssistantAgent(name="coder", ...)
tester = autogen.AssistantAgent(name="tester", ...)

# Group chat
groupchat = autogen.GroupChat(
    agents=[planner, coder, tester, user_proxy],
    messages=[],
    max_round=10
)

manager = autogen.GroupChatManager(groupchat=groupchat)

# Start conversation
user_proxy.initiate_chat(
    manager,
    message="Build a REST API for user management"
)
```

### Custom Termination

```python
def is_termination_msg(msg):
    """Custom termination condition"""
    return "TERMINATE" in msg.get("content", "") or \
           "task complete" in msg.get("content", "").lower()

user_proxy = autogen.UserProxyAgent(
    name="user",
    is_termination_msg=is_termination_msg
)
```

## Integration Examples

### Jupyter Notebook

```python
# In Jupyter
import autogen

assistant = autogen.AssistantAgent(...)
user_proxy = autogen.UserProxyAgent(
    code_execution_config={"use_docker": False}
)

# Interactive conversation
user_proxy.initiate_chat(assistant, message="Your task here")
```

### Web API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/code-assist", methods=["POST"])
def code_assist():
    task = request.json["task"]
    
    # Run conversation
    user_proxy.initiate_chat(assistant, message=task)
    
    # Get conversation history
    messages = user_proxy.chat_messages[assistant]
    
    return jsonify({"messages": messages})
```

### Slack Bot

```python
from slack_bolt import App

app = App(token=SLACK_TOKEN)

@app.command("/code")
def handle_code(ack, command, say):
    ack()
    
    task = command['text']
    user_proxy.initiate_chat(assistant, message=task)
    
    # Get final result
    result = user_proxy.last_message()["content"]
    say(f"```\n{result}\n```")
```

## Deploy to Production

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install pyautogen

COPY code_assistant.py .

CMD ["python", "code_assistant.py"]
```

### AWS Lambda

```python
import json
import autogen

# Initialize agents globally
assistant = autogen.AssistantAgent(...)
user_proxy = autogen.UserProxyAgent(...)

def lambda_handler(event, context):
    task = event['task']
    
    user_proxy.initiate_chat(assistant, message=task)
    
    result = user_proxy.last_message()["content"]
    
    return {
        'statusCode': 200,
        'body': json.dumps({'result': result})
    }
```

## Use Cases

### Code Generation
Generate code from natural language descriptions.

### Data Analysis
Analyze datasets with automatic code generation.

### Debugging
Iteratively fix code based on error messages.

### API Testing
Generate and run API test cases.

## Best Practices

### Clear Instructions
```python
# ✅ Specific
message="Load sales.csv, calculate total by region, create bar chart"

# ❌ Vague
message="Analyze sales data"
```

### Safe Execution
```python
# ✅ Use Docker for isolation
code_execution_config={
    "use_docker": True,
    "timeout": 60
}

# ⚠️ Direct execution (less safe)
code_execution_config={"use_docker": False}
```

### Error Handling
```python
try:
    user_proxy.initiate_chat(assistant, message=task)
except Exception as e:
    print(f"Error: {e}")
    # Handle gracefully
```

## Troubleshooting

**Code Not Executing**
- Check code_execution_config
- Verify Docker is running (if use_docker=True)
- Check file permissions in work_dir

**Infinite Loops**
- Set max_consecutive_auto_reply
- Define clear termination conditions
- Add timeout limits

**Poor Code Quality**
- Improve system message
- Provide examples
- Use better models (GPT-4 vs GPT-3.5)

## Next Steps

1. Set up your agents
2. Define conversation flow
3. Test with sample tasks
4. Add custom functions
5. Deploy to production
