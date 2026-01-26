"""
API Gateway Integration

REST API for agent invocation with auth and rate limiting.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from datetime import datetime
import hashlib

app = BedrockAgentCoreApp()

# Simulated API keys
API_KEYS = {
    "key_123": {"user": "alice", "rate_limit": 100},
    "key_456": {"user": "bob", "rate_limit": 50}
}

# Rate limiting
request_counts = {}

def validate_api_key(api_key: str) -> dict:
    """Validate API key"""
    if api_key in API_KEYS:
        return {"valid": True, "user": API_KEYS[api_key]["user"]}
    return {"valid": False}

def check_rate_limit(api_key: str) -> bool:
    """Check rate limit"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    key = f"{api_key}:{now}"
    
    count = request_counts.get(key, 0)
    limit = API_KEYS[api_key]["rate_limit"]
    
    if count >= limit:
        return False
    
    request_counts[key] = count + 1
    return True

@app.entrypoint
def invoke(payload):
    """
    API Gateway handler with auth and rate limiting.
    """
    # Extract headers
    api_key = payload.get("headers", {}).get("X-API-Key")
    
    # Validate API key
    auth = validate_api_key(api_key)
    if not auth["valid"]:
        return {"error": "Invalid API key", "status": 401}
    
    # Check rate limit
    if not check_rate_limit(api_key):
        return {"error": "Rate limit exceeded", "status": 429}
    
    # Process request
    query = payload.get("prompt")
    agent = Agent()
    result = agent(query)
    
    return {
        "result": result.message,
        "user": auth["user"],
        "status": 200
    }

if __name__ == "__main__":
    print("API Gateway Integration Demo")
    print("=" * 60)
    
    tests = [
        {"headers": {"X-API-Key": "key_123"}, "prompt": "Hello"},
        {"headers": {"X-API-Key": "invalid"}, "prompt": "Hello"},
        {"headers": {"X-API-Key": "key_456"}, "prompt": "What is AI?"}
    ]
    
    for test in tests:
        print(f"\nAPI Key: {test['headers']['X-API-Key']}")
        response = invoke(test)
        print(f"Status: {response.get('status')}")
        print(f"Response: {response.get('result') or response.get('error')}")
        print("-" * 60)
    
    app.run()
