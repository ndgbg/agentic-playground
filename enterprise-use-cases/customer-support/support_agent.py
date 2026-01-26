"""
Customer Support Agent Demo

Multi-agent customer support system with routing, FAQ, and escalation.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from typing import Dict, List
import json
from datetime import datetime

app = BedrockAgentCoreApp()

# Simulated knowledge base
KNOWLEDGE_BASE = {
    "return policy": "You can return items within 30 days of purchase for a full refund. Items must be unused and in original packaging.",
    "shipping": "We offer free shipping on orders over $50. Standard shipping takes 5-7 business days.",
    "hours": "Our customer support is available Monday-Friday 9am-5pm EST.",
    "payment": "We accept Visa, Mastercard, American Express, and PayPal.",
    "warranty": "All products come with a 1-year manufacturer warranty covering defects."
}

# Simulated customer database
CUSTOMERS = {
    "alice@example.com": {
        "name": "Alice Smith",
        "id": "C001",
        "status": "premium",
        "orders": [
            {"id": "O001", "date": "2026-01-15", "total": 150.00, "status": "delivered"},
            {"id": "O002", "date": "2026-01-20", "total": 89.99, "status": "shipped"}
        ]
    },
    "bob@example.com": {
        "name": "Bob Jones",
        "id": "C002",
        "status": "standard",
        "orders": [
            {"id": "O003", "date": "2026-01-18", "total": 45.00, "status": "pending"}
        ]
    }
}

# Ticket system
TICKETS = []

def route_query(query: str) -> str:
    """Classify query intent"""
    query_lower = query.lower()
    
    # FAQ keywords
    faq_keywords = ["policy", "return", "shipping", "hours", "payment", "warranty"]
    if any(keyword in query_lower for keyword in faq_keywords):
        return "faq"
    
    # Account keywords
    account_keywords = ["order", "my account", "subscription", "billing"]
    if any(keyword in query_lower for keyword in account_keywords):
        return "account"
    
    # Negative sentiment keywords
    negative_keywords = ["angry", "frustrated", "terrible", "worst", "unacceptable"]
    if any(keyword in query_lower for keyword in negative_keywords):
        return "escalation"
    
    return "general"

@tool
def search_knowledge_base(topic: str) -> str:
    """
    Search knowledge base for information.
    
    Args:
        topic: Topic to search for
    
    Returns:
        Information from knowledge base
    """
    topic_lower = topic.lower()
    
    for key, value in KNOWLEDGE_BASE.items():
        if key in topic_lower or topic_lower in key:
            return f"{key.title()}: {value}"
    
    return "Information not found in knowledge base."

@tool
def get_customer_info(email: str) -> Dict:
    """
    Get customer information.
    
    Args:
        email: Customer email address
    
    Returns:
        Customer data including orders
    """
    if email in CUSTOMERS:
        return CUSTOMERS[email]
    else:
        return {"error": "Customer not found"}

@tool
def create_ticket(customer_email: str, issue: str, priority: str = "normal") -> Dict:
    """
    Create a support ticket.
    
    Args:
        customer_email: Customer's email
        issue: Description of the issue
        priority: Priority level (low, normal, high, urgent)
    
    Returns:
        Ticket information
    """
    ticket_id = f"T{len(TICKETS) + 1:04d}"
    ticket = {
        "id": ticket_id,
        "customer_email": customer_email,
        "issue": issue,
        "priority": priority,
        "status": "open",
        "created_at": datetime.now().isoformat()
    }
    TICKETS.append(ticket)
    
    return ticket

def faq_agent(query: str) -> Dict:
    """Handle FAQ queries"""
    agent = Agent()
    agent.add_tool(search_knowledge_base)
    
    result = agent(f"Answer this customer question using the knowledge base: {query}")
    
    return {
        "answer": result.message,
        "type": "faq",
        "confidence": "high"
    }

def account_agent(query: str, customer_email: str) -> Dict:
    """Handle account-related queries"""
    agent = Agent()
    agent.add_tool(get_customer_info)
    
    customer_data = get_customer_info(customer_email)
    
    if "error" in customer_data:
        return {
            "answer": "I couldn't find your account. Please verify your email address.",
            "type": "account",
            "error": True
        }
    
    context = f"""
    Customer: {customer_data['name']}
    Status: {customer_data['status']}
    Recent Orders: {json.dumps(customer_data['orders'], indent=2)}
    
    Customer Question: {query}
    """
    
    result = agent(context)
    
    return {
        "answer": result.message,
        "type": "account",
        "customer_data": customer_data
    }

def escalation_agent(query: str, customer_email: str) -> Dict:
    """Handle escalations"""
    agent = Agent()
    agent.add_tool(create_ticket)
    
    # Create high-priority ticket
    ticket = create_ticket(customer_email, query, priority="high")
    
    return {
        "answer": f"I understand your frustration. I've created priority ticket #{ticket['id']} and a specialist will contact you within 1 hour. I've also added a $20 credit to your account as an apology for the inconvenience.",
        "type": "escalation",
        "ticket": ticket,
        "compensation": "$20 credit"
    }

def general_agent(query: str) -> Dict:
    """Handle general queries"""
    agent = Agent()
    result = agent(query)
    
    return {
        "answer": result.message,
        "type": "general"
    }

@app.entrypoint
def invoke(payload):
    """
    Main customer support agent with routing.
    """
    query = payload.get("prompt")
    customer_email = payload.get("customer_email", "unknown@example.com")
    
    # Route query
    intent = route_query(query)
    
    # Handle based on intent
    if intent == "faq":
        response = faq_agent(query)
    elif intent == "account":
        response = account_agent(query, customer_email)
    elif intent == "escalation":
        response = escalation_agent(query, customer_email)
    else:
        response = general_agent(query)
    
    response["routed_to"] = intent
    return response

if __name__ == "__main__":
    print("Customer Support Agent Demo")
    print("=" * 60)
    
    test_cases = [
        {
            "prompt": "What is your return policy?",
            "customer_email": "alice@example.com"
        },
        {
            "prompt": "Where is my order?",
            "customer_email": "alice@example.com"
        },
        {
            "prompt": "This is terrible! I've been waiting for weeks!",
            "customer_email": "bob@example.com"
        },
        {
            "prompt": "What are your business hours?",
            "customer_email": "new@example.com"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}]")
        print(f"Customer: {test['customer_email']}")
        print(f"Query: {test['prompt']}")
        
        response = invoke(test)
        
        print(f"Routed to: {response['routed_to']}")
        print(f"Answer: {response['answer']}")
        
        if "ticket" in response:
            print(f"Ticket Created: {response['ticket']['id']}")
        
        print("-" * 60)
    
    print("\n\nStarting server on port 8080...")
    app.run()
