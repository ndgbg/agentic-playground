#!/usr/bin/env python3
"""
Test client for the example MCP server.
Run this to test the server without Kiro CLI.
"""

import asyncio
import json

async def test_server():
    """Test the example MCP server."""
    
    print("Testing MCP Server")
    print("=" * 50)
    
    # Simulate tool calls
    tests = [
        {
            "name": "add",
            "arguments": {"a": 5, "b": 3},
            "expected": "Result: 8"
        },
        {
            "name": "add",
            "arguments": {"a": 10.5, "b": 2.5},
            "expected": "Result: 13.0"
        },
        {
            "name": "reverse_text",
            "arguments": {"text": "Hello World"},
            "expected": "Reversed: dlroW olleH"
        },
        {
            "name": "reverse_text",
            "arguments": {"text": "MCP Server"},
            "expected": "Reversed: revreS PCM"
        }
    ]
    
    # Import the server
    from example_simple import call_tool
    
    for i, test in enumerate(tests, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"Input: {json.dumps(test['arguments'])}")
        
        result = await call_tool(test["name"], test["arguments"])
        output = result[0].text
        
        print(f"Output: {output}")
        print(f"Status: {'✓ PASS' if output == test['expected'] else '✗ FAIL'}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_server())
