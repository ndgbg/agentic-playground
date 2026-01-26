"""
Slack Bot with AgentCore

Slack integration with slash commands and interactive messages.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
import json
import os
from datetime import datetime

app = BedrockAgentCoreApp()

# Simulated Slack API
class SlackAPI:
    @staticmethod
    def post_message(channel: str, text: str) -> dict:
        """Post message to Slack channel"""
        print(f"[SLACK] Channel: {channel}")
        print(f"[SLACK] Message: {text}")
        return {"ok": True, "ts": datetime.now().timestamp()}
    
    @staticmethod
    def get_user_info(user_id: str) -> dict:
        """Get user information"""
        users = {
            "U001": {"name": "Alice", "email": "alice@company.com"},
            "U002": {"name": "Bob", "email": "bob@company.com"}
        }
        return users.get(user_id, {"name": "Unknown"})

slack = SlackAPI()

@tool
def send_slack_message(channel: str, message: str) -> str:
    """
    Send a message to a Slack channel.
    
    Args:
        channel: Channel name (e.g., "#general", "#alerts")
        message: Message text
    
    Returns:
        Confirmation message
    """
    result = slack.post_message(channel, message)
    if result["ok"]:
        return f"Message sent to {channel}"
    else:
        return f"Failed to send message"

@tool
def get_team_status() -> dict:
    """
    Get team status and availability.
    
    Returns:
        Team member status
    """
    return {
        "online": ["Alice", "Bob"],
        "away": ["Charlie"],
        "offline": ["David"]
    }

@tool
def create_reminder(user: str, message: str, time: str) -> str:
    """
    Create a reminder for a user.
    
    Args:
        user: Username or user ID
        message: Reminder message
        time: When to remind (e.g., "in 1 hour", "tomorrow at 9am")
    
    Returns:
        Confirmation message
    """
    return f"Reminder set for {user}: '{message}' {time}"

def handle_slash_command(command: str, text: str, user_id: str) -> dict:
    """Handle Slack slash commands"""
    
    agent = Agent()
    agent.add_tool(send_slack_message)
    agent.add_tool(get_team_status)
    agent.add_tool(create_reminder)
    
    user_info = slack.get_user_info(user_id)
    
    # Route based on command
    if command == "/ask":
        # General question
        result = agent(text)
        return {
            "response_type": "in_channel",
            "text": result.message
        }
    
    elif command == "/status":
        # Team status
        status = get_team_status()
        return {
            "response_type": "ephemeral",
            "text": f"Team Status:\nOnline: {', '.join(status['online'])}\nAway: {', '.join(status['away'])}\nOffline: {', '.join(status['offline'])}"
        }
    
    elif command == "/remind":
        # Create reminder
        result = agent(f"Create a reminder: {text}")
        return {
            "response_type": "ephemeral",
            "text": result.message
        }
    
    else:
        return {
            "response_type": "ephemeral",
            "text": f"Unknown command: {command}"
        }

@app.entrypoint
def invoke(payload):
    """
    Handle Slack events and commands.
    """
    event_type = payload.get("type", "slash_command")
    
    if event_type == "slash_command":
        command = payload.get("command")
        text = payload.get("text", "")
        user_id = payload.get("user_id", "U001")
        
        return handle_slash_command(command, text, user_id)
    
    elif event_type == "message":
        # Handle direct messages
        text = payload.get("text")
        user_id = payload.get("user")
        
        agent = Agent()
        agent.add_tool(send_slack_message)
        agent.add_tool(get_team_status)
        
        result = agent(text)
        
        return {
            "text": result.message
        }
    
    else:
        return {"text": "Event type not supported"}

if __name__ == "__main__":
    print("Slack Bot Demo")
    print("=" * 60)
    
    test_commands = [
        {
            "type": "slash_command",
            "command": "/ask",
            "text": "What's the weather like?",
            "user_id": "U001"
        },
        {
            "type": "slash_command",
            "command": "/status",
            "text": "",
            "user_id": "U001"
        },
        {
            "type": "slash_command",
            "command": "/remind",
            "text": "me about the meeting in 1 hour",
            "user_id": "U002"
        },
        {
            "type": "message",
            "text": "Send a message to #general saying 'Deployment complete'",
            "user": "U001"
        }
    ]
    
    for i, test in enumerate(test_commands, 1):
        print(f"\n[Test {i}]")
        if test["type"] == "slash_command":
            print(f"Command: {test['command']} {test['text']}")
        else:
            print(f"Message: {test['text']}")
        
        response = invoke(test)
        print(f"Response: {response['text']}")
        print("-" * 60)
    
    print("\nStarting server on port 8080...")
    app.run()
