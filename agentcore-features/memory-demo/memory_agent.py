"""
AgentCore Memory Demo

Demonstrates short-term and long-term memory in agents.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from typing import Dict
import json

app = BedrockAgentCoreApp()

# Simulated memory stores
short_term_memory = {}  # Session-based
long_term_memory = {}   # Persistent across sessions

class MemoryManager:
    @staticmethod
    def save_to_stm(session_id: str, key: str, value: str):
        """Save to short-term memory"""
        if session_id not in short_term_memory:
            short_term_memory[session_id] = {}
        short_term_memory[session_id][key] = value
    
    @staticmethod
    def get_from_stm(session_id: str, key: str) -> str:
        """Retrieve from short-term memory"""
        return short_term_memory.get(session_id, {}).get(key)
    
    @staticmethod
    def save_to_ltm(user_id: str, fact_type: str, value: str):
        """Save to long-term memory"""
        if user_id not in long_term_memory:
            long_term_memory[user_id] = {"facts": [], "preferences": []}
        
        if fact_type == "fact":
            long_term_memory[user_id]["facts"].append(value)
        elif fact_type == "preference":
            long_term_memory[user_id]["preferences"].append(value)
    
    @staticmethod
    def get_from_ltm(user_id: str) -> Dict:
        """Retrieve from long-term memory"""
        return long_term_memory.get(user_id, {"facts": [], "preferences": []})

memory = MemoryManager()

def extract_facts(text: str) -> list:
    """Extract facts from conversation"""
    facts = []
    
    # Simple fact extraction
    if "my name is" in text.lower():
        name = text.lower().split("my name is")[1].split()[0]
        facts.append(f"name: {name}")
    
    if "i love" in text.lower() or "i like" in text.lower():
        preference = text.lower().split("love" if "love" in text.lower() else "like")[1].strip()
        facts.append(f"likes: {preference}")
    
    if "i work at" in text.lower() or "i'm a" in text.lower():
        work = text.lower().split("work at" if "work at" in text.lower() else "i'm a")[1].strip()
        facts.append(f"occupation: {work}")
    
    return facts

@app.entrypoint
def invoke(payload):
    """
    Agent with memory capabilities.
    """
    user_message = payload.get("prompt")
    session_id = payload.get("session_id", "default")
    user_id = payload.get("user_id", "user_001")
    
    # Get conversation history from STM
    history = memory.get_from_stm(session_id, "history") or []
    
    # Get user facts from LTM
    user_data = memory.get_from_ltm(user_id)
    
    # Build context
    context = ""
    if user_data["facts"]:
        context += f"What I know about you: {', '.join(user_data['facts'])}\n"
    if user_data["preferences"]:
        context += f"Your preferences: {', '.join(user_data['preferences'])}\n"
    if history:
        context += f"Recent conversation: {' '.join(history[-3:])}\n"
    
    # Create agent with context
    agent = Agent()
    full_prompt = f"{context}\nUser: {user_message}"
    result = agent(full_prompt)
    
    # Extract and save facts
    facts = extract_facts(user_message)
    for fact in facts:
        if "likes:" in fact or "loves:" in fact:
            memory.save_to_ltm(user_id, "preference", fact)
        else:
            memory.save_to_ltm(user_id, "fact", fact)
    
    # Save to STM
    history.append(user_message)
    memory.save_to_stm(session_id, "history", history)
    
    return {
        "answer": result.message,
        "session_id": session_id,
        "facts_learned": facts,
        "memory_context": {
            "stm_items": len(history),
            "ltm_facts": len(user_data["facts"]),
            "ltm_preferences": len(user_data["preferences"])
        }
    }

if __name__ == "__main__":
    print("Memory Demo")
    print("=" * 60)
    
    # Session 1: Learning about user
    print("\n[Session 1 - Learning]")
    session1 = "session_001"
    
    queries1 = [
        "My name is Alice and I love Python programming",
        "I work at a tech company",
        "What's my name?"
    ]
    
    for query in queries1:
        print(f"\nUser: {query}")
        response = invoke({
            "prompt": query,
            "session_id": session1,
            "user_id": "alice"
        })
        print(f"Agent: {response['answer']}")
        if response['facts_learned']:
            print(f"Learned: {response['facts_learned']}")
    
    # Session 2: Different session, same user
    print("\n\n[Session 2 - Recall from LTM]")
    session2 = "session_002"
    
    queries2 = [
        "What's my name?",
        "What do I like?",
        "Where do I work?"
    ]
    
    for query in queries2:
        print(f"\nUser: {query}")
        response = invoke({
            "prompt": query,
            "session_id": session2,
            "user_id": "alice"
        })
        print(f"Agent: {response['answer']}")
        print(f"Memory: {response['memory_context']}")
    
    print("\n\nStarting server on port 8080...")
    app.run()
