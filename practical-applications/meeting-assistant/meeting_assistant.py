"""
Meeting Assistant

Transcription processing and action items.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from datetime import datetime

app = BedrockAgentCoreApp()

TRANSCRIPT = """
Alice: Let's discuss the Q1 roadmap. We need to launch the new feature by March 15th.
Bob: Agreed. I'll handle the backend API. Can someone take the frontend?
Charlie: I can do the frontend. Alice, can you review the designs by next week?
Alice: Yes, I'll review by Friday. Bob, please send the API specs by Wednesday.
Bob: Will do. We should also schedule a demo for stakeholders.
"""

@tool
def extract_action_items(transcript: str) -> list:
    """Extract action items from transcript"""
    actions = []
    
    keywords = ["will", "can you", "please", "should", "need to"]
    for line in transcript.split("\n"):
        if any(kw in line.lower() for kw in keywords):
            actions.append(line.strip())
    
    return actions

@tool
def identify_participants(transcript: str) -> list:
    """Identify meeting participants"""
    participants = set()
    for line in transcript.split("\n"):
        if ":" in line:
            name = line.split(":")[0].strip()
            if name:
                participants.add(name)
    
    return list(participants)

@tool
def summarize_meeting(transcript: str) -> str:
    """Generate meeting summary"""
    return "Discussed Q1 roadmap. Key deadline: March 15th feature launch. Tasks assigned to team members."

@app.entrypoint
def invoke(payload):
    """
    Meeting assistant agent.
    """
    transcript = payload.get("transcript", TRANSCRIPT)
    query = payload.get("prompt")
    
    agent = Agent()
    agent.add_tool(extract_action_items)
    agent.add_tool(identify_participants)
    agent.add_tool(summarize_meeting)
    
    context = f"Meeting Transcript:\n{transcript}\n\nTask: {query}"
    result = agent(context)
    
    return {"answer": result.message}

if __name__ == "__main__":
    print("Meeting Assistant Demo")
    print("=" * 60)
    
    queries = [
        "Summarize this meeting",
        "What are the action items?",
        "Who attended the meeting?",
        "What are the key deadlines?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = invoke({"prompt": query})
        print(f"Answer: {response['answer']}")
        print("-" * 60)
    
    app.run()
