# Data Analysis Agent

Natural language interface for querying and analyzing data. Ask questions about your data in plain English and get instant insights.

## Overview

This agent converts natural language questions into database queries, performs statistical analysis, and provides insights without requiring SQL knowledge. Perfect for business users who need data insights quickly.

## Quick Start

```bash
cd enterprise-use-cases/data-analysis
pip install -r requirements.txt
python data_analysis_agent.py
```

**Output:**
```
Data Analysis Agent
============================================================

Query: How many customers do we have?
Response: We have 3 customers in the database: Alice, Bob, and Charlie.
============================================================

Query: What's the total revenue from all orders?
Response: Total revenue is $484.99 from 4 orders.
============================================================

Query: What's the average order amount?
Response: The average order amount is $121.25.
============================================================
```

## What It Does

### Natural Language to Data Queries

Ask questions naturally:
- "How many customers do we have?" → Queries customer table
- "What's the total revenue?" → Sums order amounts
- "Show me orders for Alice" → Filters by customer
- "Average order amount?" → Calculates statistics

### Statistical Analysis

Automatically computes:
- Count, sum, average
- Min, max values
- Grouping and aggregation
- Trend analysis

### Data Insights

Provides business-friendly explanations:
- "Revenue increased 15% this month"
- "Top customer: Alice with 2 orders totaling $239.99"
- "3 pending orders need attention"

## Available Tools

### query_database()
Query any table with optional filters:
```python
query_database(table="customers", filter_field="status", filter_value="active")
```

### calculate_statistics()
Compute stats on numeric fields:
```python
calculate_statistics(data=orders, field="amount")
# Returns: {sum, average, min, max, count}
```

### aggregate_by_field()
Group data and aggregate:
```python
aggregate_by_field(data=orders, group_field="customer_id", agg_field="amount")
# Returns: {customer_1: 150.00, customer_2: 200.00}
```

## Example Queries

### Simple Queries
```
"How many customers do we have?"
"Show me all orders"
"List active customers"
"What services are available?"
```

### Analytical Queries
```
"What's the total revenue?"
"Average order amount?"
"Which customer has the most orders?"
"Revenue by customer?"
```

### Complex Queries
```
"Show me orders over $100"
"Which customers have pending orders?"
"Total revenue from active customers"
"Orders placed in the last week"
```

## Customization

### Connect to Real Database

```python
import psycopg2

@tool
def query_database(table: str, filter_field: str = None) -> list:
    """Query real PostgreSQL database"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    
    query = f"SELECT * FROM {table}"
    if filter_field:
        query += f" WHERE {filter_field} = %s"
    
    cursor.execute(query)
    return cursor.fetchall()
```

### Add Visualization

```python
import matplotlib.pyplot as plt

@tool
def create_chart(data: list, chart_type: str) -> str:
    """Generate charts from data"""
    if chart_type == "bar":
        plt.bar(range(len(data)), data)
        plt.savefig("chart.png")
        return "Chart saved to chart.png"
```

### Add Export

```python
@tool
def export_to_csv(data: list, filename: str) -> str:
    """Export results to CSV"""
    import csv
    
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    
    return f"Exported to {filename}"
```

## Integration Examples

### Slack Integration

```python
# Query from Slack
@slack_command("/data")
def handle_data_query(text):
    response = invoke({"prompt": text})
    return response["answer"]
```

### API Endpoint

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query_endpoint():
    data = request.json
    response = invoke({"prompt": data["query"]})
    return response
```

### Scheduled Reports

```python
import schedule

def daily_report():
    response = invoke({"prompt": "Total revenue today"})
    send_email(response["answer"])

schedule.every().day.at("17:00").do(daily_report)
```

## Deploy to AgentCore

```bash
# Configure
agentcore configure -e data_analysis_agent.py

# Deploy
agentcore deploy

# Test
agentcore invoke '{"prompt": "How many customers?"}'
```

## Use Cases

### Business Intelligence
- Ad-hoc queries without SQL
- Quick insights for decisions
- Self-service analytics

### Data Exploration
- Understand data structure
- Find patterns
- Identify anomalies

### Report Generation
- Automated daily/weekly reports
- KPI tracking
- Trend analysis

### Customer Analytics
- Customer segmentation
- Purchase patterns
- Lifetime value analysis

## Best Practices

### Clear Questions
```
❌ "Show me stuff"
✅ "Show me all customers"

❌ "Numbers"
✅ "What's the total revenue?"
```

### Validate Results
```python
def validate_query_result(result: list) -> bool:
    if not result:
        return False
    if len(result) > 10000:  # Too many rows
        return False
    return True
```

### Cache Common Queries
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query: str):
    return query_database(query)
```

## Troubleshooting

**No Results Returned**
- Check table names are correct
- Verify filter values match data
- Review database connection

**Slow Queries**
- Add database indexes
- Limit result size
- Use aggregation instead of full scans

**Incorrect Results**
- Verify data types match
- Check filter logic
- Test queries manually

## Next Steps

1. Connect to your actual database
2. Add more tables and relationships
3. Implement visualization tools
4. Create scheduled reports
5. Add export capabilities
