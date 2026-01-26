"""
AgentCore Gateway Integration Demo

Demonstrates connecting agents to external tools via AgentCore Gateway.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
import os
import json

app = BedrockAgentCoreApp()

# Example tools that agents can use

@tool
def get_weather(location: str) -> str:
    """
    Get current weather for a location.
    
    Args:
        location: City name (e.g., "Seattle", "New York")
    
    Returns:
        Weather description
    """
    # Simulated weather API call
    weather_data = {
        "seattle": "Rainy, 52°F",
        "new york": "Sunny, 68°F",
        "san francisco": "Foggy, 58°F",
        "miami": "Hot and humid, 85°F"
    }
    
    location_lower = location.lower()
    if location_lower in weather_data:
        return f"Weather in {location}: {weather_data[location_lower]}"
    else:
        return f"Weather data not available for {location}"

@tool
def search_database(query: str) -> dict:
    """
    Search a database for information.
    
    Args:
        query: Search query
    
    Returns:
        Search results
    """
    # Simulated database search
    results = {
        "customer": [
            {"id": "C001", "name": "Alice Smith", "status": "active"},
            {"id": "C002", "name": "Bob Jones", "status": "active"}
        ],
        "order": [
            {"id": "O001", "customer": "C001", "total": 150.00, "status": "shipped"},
            {"id": "O002", "customer": "C002", "total": 89.99, "status": "pending"}
        ]
    }
    
    query_lower = query.lower()
    for key in results:
        if key in query_lower:
            return {"results": results[key], "count": len(results[key])}
    
    return {"results": [], "count": 0}

@tool
def send_notification(recipient: str, message: str) -> str:
    """
    Send a notification to a user.
    
    Args:
        recipient: Email or username
        message: Notification message
    
    Returns:
        Confirmation message
    """
    # Simulated notification
    print(f"[NOTIFICATION] To: {recipient}")
    print(f"[NOTIFICATION] Message: {message}")
    return f"Notification sent to {recipient}"

@tool
def calculate(expression: str) -> float:
    """
    Perform mathematical calculations.
    
    Args:
        expression: Math expression (e.g., "2 + 2", "10 * 5")
    
    Returns:
        Calculation result
    """
    try:
        # Safe eval for basic math
        result = eval(expression, {"__builtins__": {}}, {})
        return float(result)
    except Exception as e:
        return f"Error: {str(e)}"

@app.entrypoint
def invoke(payload):
    """
    Agent with multiple tools available via Gateway.
    """
    user_message = payload.get("prompt")
    
    # Create agent and add tools
    agent = Agent()
    agent.add_tool(get_weather)
    agent.add_tool(search_database)
    agent.add_tool(send_notification)
    agent.add_tool(calculate)
    
    # Agent will automatically use tools as needed
    result = agent(user_message)
    
    return {
        "result": result.message,
        "tools_available": ["get_weather", "search_database", "send_notification", "calculate"]
    }

if __name__ == "__main__":
    # Test locally
    print("Gateway Integration Demo")
    print("=" * 50)
    
    test_queries = [
        "What's the weather in Seattle?",
        "Search for customers in the database",
        "Calculate 25 * 4",
        "Send a notification to alice@example.com saying 'Meeting at 3pm'"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = invoke({"prompt": query})
        print(f"Response: {response['result']}")
        print("-" * 50)
    
    # Run as server
    print("\nStarting server on port 8080...")
    app.run()
