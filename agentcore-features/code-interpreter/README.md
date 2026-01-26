# AgentCore Code Interpreter

Safe Python code execution for data analysis, calculations, and automation using AWS Bedrock AgentCore Code Interpreter.

## What's Implemented

A fully functional agent that:
- Generates Python code based on natural language
- Executes code safely in a sandbox
- Handles data analysis tasks
- Performs calculations
- Creates visualizations

## Quick Start

### Run Locally

```bash
cd agentcore-features/code-interpreter

# Install dependencies
pip install -r requirements.txt

# Run demo with test cases
python code_interpreter_agent.py
```

**Output:**
```
Code Interpreter Demo
============================================================

Query: Calculate the fibonacci sequence up to 10 numbers
------------------------------------------------------------
Answer: Here's the Fibonacci sequence:

Generated Code:
def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib

print(fibonacci(10))

Execution Result:
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
============================================================
```

### Deploy to AgentCore

```bash
# Configure
agentcore configure -e code_interpreter_agent.py

# Deploy
agentcore deploy

# Test
agentcore invoke '{"prompt": "Calculate the mean of [5, 10, 15, 20]"}'
```

## How It Works

### Code Generation Flow

```
User Query
    ↓
Agent analyzes request
    ↓
Generates Python code
    ↓
Code Interpreter executes in sandbox
    ↓
Returns result
```

### Example Execution

```python
# User asks: "Calculate factorial of 5"

# Agent generates:
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

print(factorial(5))

# Code Interpreter executes
# Returns: 120
```

## Example Queries

### Mathematics

```
"Calculate the fibonacci sequence up to 10 numbers"
→ [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

"What is the factorial of 8?"
→ 40320

"Calculate the mean, median, and mode of [5, 2, 8, 2, 9, 1, 3, 2]"
→ Mean: 4.0, Median: 2.5, Mode: 2
```

### Data Analysis

```
"Analyze this data: [10, 20, 30, 40, 50]"
→ Sum: 150, Average: 30, Min: 10, Max: 50, Std Dev: 14.14

"Find prime numbers between 1 and 50"
→ [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

"Calculate compound interest: principal=1000, rate=5%, years=10"
→ Final amount: $1628.89
```

### Data Manipulation

```
"Sort this list: [5, 2, 8, 1, 9]"
→ [1, 2, 5, 8, 9]

"Remove duplicates from [1, 2, 2, 3, 3, 3, 4]"
→ [1, 2, 3, 4]

"Reverse this string: 'hello world'"
→ 'dlrow olleh'
```

### Visualizations

```
"Create a bar chart of sales: Jan=100, Feb=150, Mar=120"
→ [Generates matplotlib chart]

"Plot a line graph of [1, 4, 9, 16, 25]"
→ [Generates line plot]
```

## Customization

### Add Data Sources

```python
import pandas as pd

@app.entrypoint
def invoke(payload):
    user_message = payload.get("prompt")
    
    # Load data
    df = pd.read_csv("data.csv")
    
    # Provide data context to agent
    context = f"""
    Available data:
    {df.head()}
    
    User query: {user_message}
    """
    
    result = agent(context)
    return {"answer": result.message}
```

### Custom Libraries

```python
# Allow specific libraries
allowed_imports = ["numpy", "pandas", "matplotlib", "scipy"]

code_interpreter = CodeInterpreter(
    allowed_imports=allowed_imports
)
```

### Timeout Configuration

```python
# Set execution timeout
execution_result = code_interpreter.execute(
    language="python",
    code=code,
    timeout=30  # seconds
)
```

## Safety Features

### Sandboxed Execution

- No file system access
- No network access
- Limited memory
- Execution timeout
- Restricted imports

### Code Validation

```python
def validate_code(code: str) -> bool:
    """Validate code before execution"""
    dangerous_patterns = [
        "import os",
        "import subprocess",
        "eval(",
        "exec(",
        "__import__"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in code:
            return False
    
    return True
```

### Resource Limits

```python
execution_result = code_interpreter.execute(
    language="python",
    code=code,
    max_memory_mb=512,
    max_execution_time=30
)
```

## Advanced Usage

### Multi-Step Analysis

```python
@app.entrypoint
def invoke(payload):
    query = payload.get("prompt")
    
    # Step 1: Load data
    data_code = "data = [1, 2, 3, 4, 5]"
    code_interpreter.execute("python", data_code)
    
    # Step 2: Analyze
    analysis_code = agent.generate_code(query)
    result = code_interpreter.execute("python", analysis_code)
    
    return {"result": result}
```

### Persistent State

```python
# Maintain state across executions
session_state = {}

@app.entrypoint
def invoke(payload):
    session_id = payload.get("session_id")
    
    # Get session state
    state = session_state.get(session_id, {})
    
    # Execute with state
    result = code_interpreter.execute(
        "python",
        code,
        context=state
    )
    
    # Save state
    session_state[session_id] = result.get("state", {})
    
    return {"result": result}
```

### Error Handling

```python
@app.entrypoint
def invoke(payload):
    try:
        result = code_interpreter.execute("python", code)
        
        if result.get("error"):
            # Retry with error context
            error_msg = result["error"]
            retry_prompt = f"Fix this error: {error_msg}\nOriginal code: {code}"
            fixed_code = agent(retry_prompt)
            result = code_interpreter.execute("python", fixed_code)
        
        return {"result": result}
    
    except Exception as e:
        return {"error": str(e)}
```

## Monitoring

### Execution Metrics

```python
import time

execution_times = []

def execute_with_metrics(code: str):
    start = time.time()
    result = code_interpreter.execute("python", code)
    duration = time.time() - start
    
    execution_times.append(duration)
    
    print(f"Execution time: {duration:.2f}s")
    print(f"Average: {sum(execution_times)/len(execution_times):.2f}s")
    
    return result
```

### Usage Tracking

```python
from collections import Counter

code_types = Counter()

def track_code_type(code: str):
    if "matplotlib" in code:
        code_types["visualization"] += 1
    elif "pandas" in code:
        code_types["data_analysis"] += 1
    elif "def " in code:
        code_types["function"] += 1
    else:
        code_types["calculation"] += 1
```

## Testing

### Unit Tests

```python
def test_fibonacci():
    result = invoke({"prompt": "Calculate fibonacci up to 5"})
    assert "0, 1, 1, 2, 3" in result["answer"]

def test_prime_numbers():
    result = invoke({"prompt": "Find primes between 1 and 10"})
    assert "2, 3, 5, 7" in result["answer"]

def test_statistics():
    result = invoke({"prompt": "Mean of [1, 2, 3, 4, 5]"})
    assert "3" in result["answer"]
```

### Integration Tests

```python
def test_end_to_end():
    queries = [
        "Calculate 10 factorial",
        "Sort [5, 2, 8, 1]",
        "Sum of [1, 2, 3, 4, 5]"
    ]
    
    for query in queries:
        result = invoke({"prompt": query})
        assert "error" not in result
        assert result["answer"]
```

## Troubleshooting

### Code Not Executing

**Issue:** Code generated but not executed

**Solutions:**
1. Check code syntax
2. Verify allowed imports
3. Check timeout settings
4. Review sandbox restrictions

### Import Errors

**Issue:** `ModuleNotFoundError`

**Solutions:**
```python
# Add to allowed imports
allowed_imports = ["numpy", "pandas", "your_module"]
```

### Timeout Errors

**Issue:** Execution exceeds timeout

**Solutions:**
1. Increase timeout limit
2. Optimize generated code
3. Break into smaller steps

### Memory Errors

**Issue:** Code uses too much memory

**Solutions:**
1. Increase memory limit
2. Process data in chunks
3. Use generators instead of lists

## Best Practices

### Clear Prompts

```
❌ "Do some math"
✅ "Calculate the average of [10, 20, 30, 40, 50]"

❌ "Analyze data"
✅ "Find the mean, median, and standard deviation of [5, 10, 15, 20, 25]"
```

### Validate Results

```python
def validate_result(result: dict) -> bool:
    """Validate execution result"""
    if result.get("error"):
        return False
    
    if not result.get("output"):
        return False
    
    return True
```

### Handle Errors Gracefully

```python
@app.entrypoint
def invoke(payload):
    try:
        result = code_interpreter.execute("python", code)
        
        if not validate_result(result):
            return {
                "answer": "I encountered an error. Let me try a different approach.",
                "retry": True
            }
        
        return {"answer": result["output"]}
    
    except Exception as e:
        return {
            "answer": f"I couldn't complete that task: {str(e)}",
            "error": True
        }
```

## Next Steps

1. **Add Data Sources**: Connect to databases, APIs
2. **Custom Libraries**: Add domain-specific libraries
3. **Visualization Export**: Save charts to S3
4. **Scheduled Analysis**: Run reports on schedule
5. **Collaborative Notebooks**: Share analysis results

## Resources

- [AgentCore Code Interpreter Documentation](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter.html)
- [Python Documentation](https://docs.python.org/3/)
- [NumPy Documentation](https://numpy.org/doc/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

**Status:** ✅ Fully implemented and tested  
**Complexity:** Medium  
**Time to Deploy:** 30-45 minutes
