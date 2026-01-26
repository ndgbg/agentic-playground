"""
Policy Controls Agent

Cedar policies for access control and compliance.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from typing import Dict

app = BedrockAgentCoreApp()

# Policy definitions
POLICIES = {
    "read_data": {
        "roles": ["user", "admin", "analyst"],
        "resources": ["customers", "orders"]
    },
    "write_data": {
        "roles": ["admin"],
        "resources": ["customers", "orders"]
    },
    "delete_data": {
        "roles": ["admin"],
        "resources": ["customers", "orders"]
    },
    "deploy_code": {
        "roles": ["admin", "developer"],
        "resources": ["production", "staging"]
    }
}

def check_policy(action: str, user_role: str, resource: str) -> dict:
    """Check if action is allowed by policy"""
    if action not in POLICIES:
        return {"allowed": False, "reason": "Unknown action"}
    
    policy = POLICIES[action]
    
    # Check role
    if user_role not in policy["roles"]:
        return {"allowed": False, "reason": f"Role '{user_role}' not authorized"}
    
    # Check resource
    if resource not in policy["resources"]:
        return {"allowed": False, "reason": f"Resource '{resource}' not in policy"}
    
    return {"allowed": True, "reason": "Policy allows action"}

@app.entrypoint
def invoke(payload):
    """
    Policy enforcement agent.
    """
    action = payload.get("action")
    user_role = payload.get("user_role")
    resource = payload.get("resource")
    
    # Check policy
    policy_check = check_policy(action, user_role, resource)
    
    if policy_check["allowed"]:
        # Execute action
        agent = Agent()
        result = agent(f"Execute {action} on {resource}")
        
        return {
            "status": "success",
            "result": result.message,
            "policy_check": policy_check
        }
    else:
        return {
            "status": "denied",
            "reason": policy_check["reason"],
            "policy_check": policy_check
        }

if __name__ == "__main__":
    print("Policy Controls Demo")
    print("=" * 60)
    
    test_cases = [
        {"action": "read_data", "user_role": "user", "resource": "customers"},
        {"action": "write_data", "user_role": "user", "resource": "customers"},
        {"action": "write_data", "user_role": "admin", "resource": "customers"},
        {"action": "delete_data", "user_role": "analyst", "resource": "orders"},
        {"action": "deploy_code", "user_role": "developer", "resource": "production"}
    ]
    
    for test in test_cases:
        print(f"\nAction: {test['action']}")
        print(f"Role: {test['user_role']}")
        print(f"Resource: {test['resource']}")
        
        response = invoke(test)
        
        if response["status"] == "success":
            print(f"✅ ALLOWED")
        else:
            print(f"❌ DENIED: {response['reason']}")
        
        print("-" * 60)
    
    app.run()
