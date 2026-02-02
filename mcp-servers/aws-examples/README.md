# AWS MCP Servers

5 production-ready MCP servers for AWS operations.

## Servers

1. **aws_resource_inspector.py** - Query EC2, S3, RDS, Lambda, CloudWatch
2. **aws_cost_optimizer.py** - Cost analysis and savings recommendations
3. **aws_security_auditor.py** - Security posture and compliance checks
4. **aws_cloudwatch_insights.py** - Log and metric analysis
5. **aws_well_architected_advisor.py** - Architecture assessment

## Quick Start

```bash
pip install -r requirements.txt
aws configure
python3 aws_resource_inspector.py
```

## Documentation

- **README.md** - This file
- **QUICKSTART.md** - 5-minute setup guide
- **SUMMARY.md** - Business value and ROI
- **COMPARISON.md** - Server selection guide

## Example Queries

- "Show me all EC2 instances in us-east-1"
- "What are my top 5 most expensive services?"
- "Check all S3 buckets for public access"
- "Show me Lambda errors from the last hour"
- "Generate a Well-Architected report"

See individual documentation files for detailed usage.
