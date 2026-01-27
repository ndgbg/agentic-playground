# Data Analysis Agent

Natural language to SQL queries and insights. Ask questions about your data in plain English.

## Quick Start

```bash
pip install -r requirements.txt
python data_analysis_agent.py
```

## What It Does

- Converts natural language to database queries
- Calculates statistics (sum, average, min, max)
- Groups and aggregates data
- Provides insights in plain English

## Example Queries

```
"How many customers do we have?" → 3 customers
"What's the total revenue?" → $484.99
"Average order amount?" → $121.25
"Orders per customer?" → Alice: 2, Bob: 2
```

## Tools

- `query_database()` - Query tables with filters
- `calculate_statistics()` - Compute stats on numeric fields
- `aggregate_by_field()` - Group and aggregate data

## Use Cases

- Business intelligence without SQL knowledge
- Ad-hoc data analysis
- Report generation
- Data exploration

## Deploy

```bash
agentcore configure -e data_analysis_agent.py
agentcore deploy
```

**Status:** ✅ Implemented | **Complexity:** Medium | **Time:** 45 min
