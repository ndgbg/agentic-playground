"""
Data Analysis Agent

Natural language to SQL and insights.
"""

from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
import json

app = BedrockAgentCoreApp()

# Simulated database
DATABASE = {
    "customers": [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "status": "active"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com", "status": "inactive"}
    ],
    "orders": [
        {"id": 101, "customer_id": 1, "amount": 150.00, "date": "2026-01-15", "status": "completed"},
        {"id": 102, "customer_id": 1, "amount": 89.99, "date": "2026-01-20", "status": "shipped"},
        {"id": 103, "customer_id": 2, "amount": 45.00, "date": "2026-01-18", "status": "pending"},
        {"id": 104, "customer_id": 2, "amount": 200.00, "date": "2026-01-22", "status": "completed"}
    ]
}

@tool
def query_database(table: str, filter_field: str = None, filter_value: str = None) -> list:
    """
    Query database table with optional filter.
    
    Args:
        table: Table name (customers, orders)
        filter_field: Field to filter on
        filter_value: Value to filter for
    
    Returns:
        List of matching records
    """
    if table not in DATABASE:
        return []
    
    results = DATABASE[table]
    
    if filter_field and filter_value:
        results = [r for r in results if str(r.get(filter_field)) == str(filter_value)]
    
    return results

@tool
def calculate_statistics(data: list, field: str) -> dict:
    """
    Calculate statistics for a numeric field.
    
    Args:
        data: List of records
        field: Numeric field to analyze
    
    Returns:
        Statistics (sum, average, min, max)
    """
    values = [float(r[field]) for r in data if field in r and r[field] is not None]
    
    if not values:
        return {"error": "No data"}
    
    return {
        "count": len(values),
        "sum": sum(values),
        "average": sum(values) / len(values),
        "min": min(values),
        "max": max(values)
    }

@tool
def aggregate_by_field(data: list, group_field: str, agg_field: str = None) -> dict:
    """
    Group data by field and optionally aggregate.
    
    Args:
        data: List of records
        group_field: Field to group by
        agg_field: Field to aggregate (sum)
    
    Returns:
        Grouped results
    """
    groups = {}
    
    for record in data:
        key = record.get(group_field)
        if key not in groups:
            groups[key] = []
        groups[key].append(record)
    
    if agg_field:
        result = {}
        for key, records in groups.items():
            values = [float(r[agg_field]) for r in records if agg_field in r]
            result[key] = sum(values) if values else 0
        return result
    
    return {k: len(v) for k, v in groups.items()}

@app.entrypoint
def invoke(payload):
    """
    Data analysis agent with SQL-like capabilities.
    """
    query = payload.get("prompt")
    
    agent = Agent()
    agent.add_tool(query_database)
    agent.add_tool(calculate_statistics)
    agent.add_tool(aggregate_by_field)
    
    result = agent(query)
    
    return {"answer": result.message}

if __name__ == "__main__":
    print("Data Analysis Agent")
    print("=" * 60)
    
    test_queries = [
        "How many customers do we have?",
        "Show me all orders",
        "What's the total revenue from all orders?",
        "What's the average order amount?",
        "How many orders does each customer have?",
        "Show me orders for customer Alice"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        response = invoke({"prompt": query})
        print(f"Response: {response['answer']}")
        print("=" * 60)
    
    print("\nStarting server on port 8080...")
    app.run()
