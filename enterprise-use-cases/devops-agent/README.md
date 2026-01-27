# DevOps Intelligence Agent

Automated infrastructure monitoring, troubleshooting, and incident response using AI.

## What's Implemented

A fully functional DevOps agent with:
- **Server Health Monitoring**: Check CPU, memory, status
- **Service Status**: Monitor running services
- **Log Analysis**: Parse and analyze error logs
- **Auto-Remediation**: Restart services, scale resources
- **Alert Creation**: Notify ops team of issues

## Quick Start

```bash
cd enterprise-use-cases/devops-agent
pip install -r requirements.txt
python devops_agent.py
```

**Output:**
```
DevOps Intelligence Agent
============================================================

Query: Check the health of all servers
Response: Found 3 servers: 1 healthy, 1 warning, 1 critical.
Server srv-003 (db-1) needs attention - CPU at 92%, Memory at 95%
------------------------------------------------------------

Query: The cache service is degraded, what should I do?
Response: I'll restart the cache service for you.
✅ Service cache restarted successfully
------------------------------------------------------------
```

## How It Works

### Monitoring Tools

```python
@tool
def check_server_health() -> dict:
    """Check all servers"""
    return {"servers": [...], "summary": {...}}

@tool
def analyze_logs(service: str, level: str) -> list:
    """Analyze logs for errors"""
    return [{"time": "...", "message": "..."}]
```

### Auto-Remediation

```python
@tool
def restart_service(service_name: str) -> str:
    """Restart a degraded service"""
    return "Service restarted"

@tool
def scale_server(server_id: str, action: str) -> str:
    """Scale resources up/down"""
    return "Resources scaled"
```

## Example Queries

```
"Check the health of all servers"
"What services are running?"
"Show me recent ERROR logs"
"Restart the cache service"
"Server srv-003 has high CPU, help me fix it"
"Create an alert for the ops team"
```

## Use Cases

- **24/7 Monitoring**: Continuous infrastructure health checks
- **Incident Response**: Automated troubleshooting
- **Alert Triage**: Classify and prioritize alerts
- **Auto-Remediation**: Fix common issues automatically
- **Root Cause Analysis**: Correlate logs and metrics

## Integration

Connect to real monitoring systems:

```python
import boto3

@tool
def check_server_health() -> dict:
    """Check real AWS EC2 instances"""
    ec2 = boto3.client('ec2')
    cloudwatch = boto3.client('cloudwatch')
    
    instances = ec2.describe_instances()
    # Get metrics from CloudWatch
    return health_data
```

## Deploy

```bash
agentcore configure -e devops_agent.py
agentcore deploy
```

---

**Status:** ✅ Fully implemented  
**Complexity:** Medium-High  
**Time to Deploy:** 1 hour
