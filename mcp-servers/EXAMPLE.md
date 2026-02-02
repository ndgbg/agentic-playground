# Simple MCP Server Example

Two examples demonstrating MCP server concepts:

1. **example_standalone.py** - Works without dependencies (start here!)
2. **example_simple.py** - Full MCP implementation (requires mcp package)

## Quick Start (No Dependencies)

```bash
python3 example_standalone.py
```

Output:
Output:
```
Simple MCP Server
==================================================
Server: example-server
Tools: 3

Available Tools:
  - add: Add two numbers
  - reverse_text: Reverse a string
  - count_words: Count words in text

Running Tests:
--------------------------------------------------

Test 1: add
  Input: {"a": 5, "b": 3}
  Output: ✓ Result: 8

Test 2: add
  Input: {"a": 10.5, "b": 2.5}
  Output: ✓ Result: 13.0

Test 3: reverse_text
  Input: {"text": "Hello World"}
  Output: ✓ Reversed: dlroW olleH

Test 4: reverse_text
  Input: {"text": "MCP Server"}
  Output: ✓ Reversed: revreS PCM

Test 5: count_words
  Input: {"text": "This is a test"}
  Output: ✓ Word count: 4

Test 6: count_words
  Input: {"text": "Model Context Protocol"}
  Output: ✓ Word count: 3

==================================================
All tests complete!
```

## What It Does

Provides three simple tools:
1. **add** - Adds two numbers
2. **reverse_text** - Reverses a string
3. **count_words** - Counts words in text

## Full MCP Version (Requires Dependencies)

### 1. Install dependencies
```bash
pip install mcp
```

### 2. Run the server
```

### 2. Run the server
```bash
python example_simple.py
```

### 3. Test it
```bash
python test_example.py
```

## Code Structure (Standalone Version)

```python
# 1. Create server class
class SimpleMCPServer:
    def __init__(self, name):
        self.name = name
        self.tools = {}

# 2. Create server instance
server = SimpleMCPServer("example-server")

# 3. Define tool handler
def add_handler(args):
    result = args["a"] + args["b"]
    return {"result": result, "text": f"Result: {result}"}

# 4. Register tool
server.register_tool(
    "add",
    "Add two numbers",
    add_handler,
    {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"]
    }
)

# 5. Call tool
result = server.call_tool("add", {"a": 5, "b": 3})
print(result["text"])  # Output: Result: 8
```

## Extending the Server

Add a new tool to the standalone version:

```python
# Define handler
def multiply_handler(args):
    result = args["a"] * args["b"]
    return {"result": result, "text": f"Result: {result}"}

# Register tool
server.register_tool(
    "multiply",
    "Multiply two numbers",
    multiply_handler,
    {
        "type": "object",
        "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
        },
        "required": ["a", "b"]
    }
)

# Use it
result = server.call_tool("multiply", {"a": 6, "b": 7})
print(result["text"])  # Output: Result: 42
```

## Use with Kiro CLI

For the full MCP version (example_simple.py), add to Kiro config:
```json
{
  "mcpServers": {
    "example": {
      "command": "python3",
      "args": ["/path/to/example_simple.py"]
    }
  }
}
```

Then ask:
- "Add 5 and 3"
- "Reverse the text 'Hello World'"
- "Count words in 'This is a test'"

## Next Steps

1. Run the standalone example: `python3 example_standalone.py`
2. Modify the tools and add your own
3. Try the full MCP version with `pip install mcp`
4. Check the AWS MCP servers for production examples

## Key Concepts

**MCP Server** = Collection of tools that AI agents can use

**Tool** = Function with:
- Name (identifier)
- Description (what it does)
- Input schema (parameters)
- Handler (implementation)

**Flow:**
1. Agent asks: "Add 5 and 3"
2. Server receives: `call_tool("add", {"a": 5, "b": 3})`
3. Handler executes: `5 + 3 = 8`
4. Server returns: `{"text": "Result: 8"}`
5. Agent responds: "The result is 8"

