"""
EventBridge Integration

Event-driven agent triggers.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
import json

app = BedrockAgentCoreApp()

@tool
def process_s3_event(bucket: str, key: str) -> str:
    """Process S3 file upload event"""
    return f"Processed file: s3://{bucket}/{key}"

@tool
def process_cloudwatch_alarm(alarm_name: str, state: str) -> str:
    """Process CloudWatch alarm"""
    return f"Alarm {alarm_name} is {state}"

@tool
def send_notification(message: str) -> str:
    """Send notification"""
    print(f"[NOTIFICATION] {message}")
    return "Notification sent"

@app.entrypoint
def invoke(payload):
    """
    Handle EventBridge events.
    """
    event_type = payload.get("detail-type")
    detail = payload.get("detail", {})
    
    agent = Agent()
    agent.add_tool(process_s3_event)
    agent.add_tool(process_cloudwatch_alarm)
    agent.add_tool(send_notification)
    
    if event_type == "Object Created":
        bucket = detail.get("bucket")
        key = detail.get("key")
        result = agent(f"Process S3 upload: {bucket}/{key}")
    
    elif event_type == "CloudWatch Alarm":
        alarm = detail.get("alarmName")
        state = detail.get("state")
        result = agent(f"Handle alarm: {alarm} is {state}")
    
    else:
        result = agent(f"Process event: {event_type}")
    
    return {"result": result.message}

if __name__ == "__main__":
    print("EventBridge Integration Demo")
    print("=" * 60)
    
    events = [
        {
            "detail-type": "Object Created",
            "detail": {"bucket": "my-bucket", "key": "data.csv"}
        },
        {
            "detail-type": "CloudWatch Alarm",
            "detail": {"alarmName": "HighCPU", "state": "ALARM"}
        }
    ]
    
    for event in events:
        print(f"\nEvent: {event['detail-type']}")
        response = invoke(event)
        print(f"Response: {response['result']}")
        print("-" * 60)
    
    app.run()
