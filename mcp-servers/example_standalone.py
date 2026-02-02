#!/usr/bin/env python3
"""
Standalone MCP Server Example (No Dependencies)
Demonstrates MCP server pattern without requiring mcp package.
"""

import json
import sys

class SimpleMCPServer:
    def __init__(self, name):
        self.name = name
        self.tools = {}
    
    def register_tool(self, name, description, handler, schema):
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "inputSchema": schema
        }
    
    def list_tools(self):
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in self.tools.values()
        ]
    
    def call_tool(self, name, arguments):
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        
        handler = self.tools[name]["handler"]
        return handler(arguments)

# Create server
server = SimpleMCPServer("example-server")

# Tool handlers
def add_handler(args):
    result = args["a"] + args["b"]
    return {"result": result, "text": f"Result: {result}"}

def reverse_handler(args):
    result = args["text"][::-1]
    return {"result": result, "text": f"Reversed: {result}"}

def count_words_handler(args):
    words = args["text"].split()
    return {"result": len(words), "text": f"Word count: {len(words)}"}

# Register tools
server.register_tool(
    "add",
    "Add two numbers",
    add_handler,
    {
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"}
        },
        "required": ["a", "b"]
    }
)

server.register_tool(
    "reverse_text",
    "Reverse a string",
    reverse_handler,
    {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to reverse"}
        },
        "required": ["text"]
    }
)

server.register_tool(
    "count_words",
    "Count words in text",
    count_words_handler,
    {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to count words in"}
        },
        "required": ["text"]
    }
)

def main():
    print("Simple MCP Server")
    print("=" * 50)
    print(f"Server: {server.name}")
    print(f"Tools: {len(server.tools)}")
    print()
    
    # List tools
    print("Available Tools:")
    for tool in server.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    print()
    
    # Run tests
    tests = [
        ("add", {"a": 5, "b": 3}),
        ("add", {"a": 10.5, "b": 2.5}),
        ("reverse_text", {"text": "Hello World"}),
        ("reverse_text", {"text": "MCP Server"}),
        ("count_words", {"text": "This is a test"}),
        ("count_words", {"text": "Model Context Protocol"})
    ]
    
    print("Running Tests:")
    print("-" * 50)
    
    for i, (tool_name, args) in enumerate(tests, 1):
        print(f"\nTest {i}: {tool_name}")
        print(f"  Input: {json.dumps(args)}")
        
        result = server.call_tool(tool_name, args)
        
        if "error" in result:
            print(f"  Output: ✗ {result['error']}")
        else:
            print(f"  Output: ✓ {result['text']}")
    
    print("\n" + "=" * 50)
    print("All tests complete!")

if __name__ == "__main__":
    main()
