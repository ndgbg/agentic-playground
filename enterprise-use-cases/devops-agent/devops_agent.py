"""
DevOps Intelligence Agent

Automated infrastructure monitoring and troubleshooting.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from datetime import datetime
import random

app = BedrockAgentCoreApp()

# Simulated infrastructure data
INFRASTRUCTURE = {
    "servers": [
        {"id": "srv-001", "name": "web-1", "cpu": 45, "memory": 60, "status": "healthy"},
        {"id": "srv-002", "name": "web-2", "cpu": 78, "memory": 85, "status": "warning"},
        {"id": "srv-003", "name": "db-1", "cpu": 92, "memory": 95, "status": "critical"}
    ],
    "services": [
        {"name": "api", "status": "running", "uptime": "15d 3h"},
        {"name": "database", "status": "running", "uptime": "30d 12h"},
        {"name": "cache", "status": "degraded", "uptime": "2d 5h"}
    ]
}

LOGS = [
    {"time": "2026-01-26 14:30:00", "level": "ERROR", "service": "api", "message": "Connection timeout to database"},
    {"time": "2026-01-26 14:31:00", "level": "WARN", "service": "cache", "message": "High memory usage detected"},
    {"time": "2026-01-26 14:32:00", "level": "ERROR", "service": "database", "message": "Slow query detected: SELECT * FROM users"}
]

@tool
def check_server_health() -> dict:
    """Check health of all servers"""
    return {
        "servers": INFRASTRUCTURE["servers"],
        "summary": {
            "healthy": sum(1 for s in INFRASTRUCTURE["servers"] if s["status"] == "healthy"),
            "warning": sum(1 for s in INFRASTRUCTURE["servers"] if s["status"] == "warning"),
            "critical": sum(1 for s in INFRASTRUCTURE["servers"] if s["status"] == "critical")
        }
    }

@tool
def get_service_status() -> dict:
    """Get status of all services"""
    return {"services": INFRASTRUCTURE["services"]}

@tool
def analyze_logs(service: str = None, level: str = None) -> list:
    """Analyze recent logs"""
    filtered = LOGS
    
    if service:
        filtered = [log for log in filtered if log["service"] == service]
    if level:
        filtered = [log for log in filtered if log["level"] == level]
    
    return filtered

@tool
def restart_service(service_name: str) -> str:
    """Restart a service"""
    for service in INFRASTRUCTURE["services"]:
        if service["name"] == service_name:
            service["status"] = "running"
            service["uptime"] = "0d 0h"
            return f"✅ Service {service_name} restarted successfully"
    
    return f"❌ Service {service_name} not found"

@tool
def scale_server(server_id: str, action: str) -> str:
    """Scale server resources up or down"""
    for server in INFRASTRUCTURE["servers"]:
        if server["id"] == server_id:
            if action == "up":
                server["cpu"] = max(0, server["cpu"] - 20)
                server["memory"] = max(0, server["memory"] - 20)
                server["status"] = "healthy"
                return f"✅ Scaled up {server['name']}, resources freed"
            elif action == "down":
                return f"✅ Scaled down {server['name']}"
    
    return f"❌ Server {server_id} not found"

@tool
def create_alert(severity: str, message: str) -> str:
    """Create an alert for ops team"""
    alert_id = f"ALT-{random.randint(1000, 9999)}"
    print(f"[ALERT {alert_id}] {severity}: {message}")
    return f"Alert {alert_id} created"

@app.entrypoint
def invoke(payload):
    """
    DevOps agent with monitoring and troubleshooting capabilities.
    """
    query = payload.get("prompt")
    
    # Create agent with tools
    agent = Agent()
    agent.add_tool(check_server_health)
    agent.add_tool(get_service_status)
    agent.add_tool(analyze_logs)
    agent.add_tool(restart_service)
    agent.add_tool(scale_server)
    agent.add_tool(create_alert)
    
    result = agent(query)
    
    return {"answer": result.message}

if __name__ == "__main__":
    print("DevOps Intelligence Agent")
    print("=" * 60)
    
    test_queries = [
        "Check the health of all servers",
        "What services are running?",
        "Show me recent ERROR logs",
        "The cache service is degraded, what should I do?",
        "Server srv-003 has high CPU, help me fix it"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        response = invoke({"prompt": query})
        print(f"Response: {response['answer']}")
        print("=" * 60)
    
    print("\nStarting server on port 8080...")
    app.run()
