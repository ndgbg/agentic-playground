# Quick Start Guide: AWS MCP Servers

Get started with AWS MCP servers in 5 minutes.

## Prerequisites

1. **Python 3.8+**
```bash
python --version
```

2. **AWS Credentials**
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

3. **Install Dependencies**
```bash
cd mcp-servers
pip install -r requirements.txt
```

## Test a Server Locally

### 1. Resource Inspector
```bash
python aws_resource_inspector.py
```

In another terminal, test it:
```bash
# List EC2 instances
echo '{"method":"tools/call","params":{"name":"list_ec2_instances","arguments":{"region":"us-east-1"}}}' | python aws_resource_inspector.py

# List S3 buckets
echo '{"method":"tools/call","params":{"name":"list_s3_buckets","arguments":{"include_details":true}}}' | python aws_resource_inspector.py
```

### 2. Cost Optimizer
```bash
python aws_cost_optimizer.py
```

Test queries:
```bash
# Get cost by service
echo '{"method":"tools/call","params":{"name":"get_cost_by_service","arguments":{"days":30}}}' | python aws_cost_optimizer.py

# Find unused resources
echo '{"method":"tools/call","params":{"name":"find_unused_resources","arguments":{"region":"us-east-1"}}}' | python aws_cost_optimizer.py
```

### 3. Security Auditor
```bash
python aws_security_auditor.py
```

Test queries:
```bash
# Audit S3 public access
echo '{"method":"tools/call","params":{"name":"audit_s3_public_access","arguments":{"check_acls":true}}}' | python aws_security_auditor.py

# Check security groups
echo '{"method":"tools/call","params":{"name":"audit_security_groups","arguments":{"region":"us-east-1"}}}' | python aws_security_auditor.py
```

### 4. CloudWatch Insights
```bash
python aws_cloudwatch_insights.py
```

Test queries:
```bash
# Get error logs
echo '{"method":"tools/call","params":{"name":"get_error_logs","arguments":{"log_group":"/aws/lambda/my-function","hours":1}}}' | python aws_cloudwatch_insights.py

# Analyze Lambda errors
echo '{"method":"tools/call","params":{"name":"analyze_lambda_errors","arguments":{"function_name":"my-function","hours":24}}}' | python aws_cloudwatch_insights.py
```

## Use with Kiro CLI

### 1. Configure Kiro CLI

Create or edit `~/.kiro/mcp-config.json`:

```json
{
  "mcpServers": {
    "aws-resources": {
      "command": "python",
      "args": ["/Users/nidabeig/Documents/agentic-playground/mcp-servers/aws_resource_inspector.py"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    },
    "aws-costs": {
      "command": "python",
      "args": ["/Users/nidabeig/Documents/agentic-playground/mcp-servers/aws_cost_optimizer.py"]
    },
    "aws-security": {
      "command": "python",
      "args": ["/Users/nidabeig/Documents/agentic-playground/mcp-servers/aws_security_auditor.py"]
    },
    "aws-cloudwatch": {
      "command": "python",
      "args": ["/Users/nidabeig/Documents/agentic-playground/mcp-servers/aws_cloudwatch_insights.py"]
    }
  }
}
```

### 2. Start Kiro CLI

```bash
kiro-cli chat
```

### 3. Ask Questions

Now you can ask natural language questions:

**Resource Queries:**
- "Show me all EC2 instances in us-east-1"
- "List my S3 buckets with encryption details"
- "What Lambda functions are using Python 3.8?"

**Cost Analysis:**
- "What are my top 5 most expensive AWS services?"
- "Find unused EBS volumes in us-west-2"
- "Show me rightsizing recommendations for EC2"

**Security Audits:**
- "Check all S3 buckets for public access"
- "Find security groups with SSH open to the internet"
- "Show me unencrypted RDS databases"

**CloudWatch Insights:**
- "Show me Lambda errors from the last hour"
- "What's the error rate for my API Gateway?"
- "Analyze performance of my-function Lambda"

## Example Conversation

```
You: What are my most expensive AWS services this month?

Kiro: [Uses aws-costs MCP server]
Here are your top 5 most expensive services:
1. EC2: $1,234.56
2. RDS: $567.89
3. S3: $234.56
4. Lambda: $123.45
5. CloudWatch: $89.12

Total: $2,249.58

You: Find unused resources in us-east-1

Kiro: [Uses aws-costs MCP server]
Found 12 unused resources:
- 5 unattached EBS volumes (potential savings: $50/month)
- 3 unused Elastic IPs (potential savings: $10.80/month)
- 4 old snapshots (potential savings: $20/month)

Total potential savings: $80.80/month

You: Check my S3 buckets for security issues

Kiro: [Uses aws-security MCP server]
Security audit found 2 issues:
1. Bucket "my-public-bucket" - Public access not fully blocked (HIGH severity)
2. Bucket "old-bucket" - Encryption not configured (HIGH severity)

Recommendation: Enable public access block and encryption on these buckets.
```

## IAM Permissions

Create an IAM policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "s3:List*",
        "s3:GetBucket*",
        "rds:Describe*",
        "lambda:List*",
        "lambda:Get*",
        "cloudwatch:GetMetricStatistics",
        "cloudwatch:ListMetrics",
        "logs:StartQuery",
        "logs:GetQueryResults",
        "ce:GetCostAndUsage",
        "ce:GetCostForecast",
        "ce:GetRightsizingRecommendation",
        "iam:List*",
        "iam:Get*",
        "cloudtrail:DescribeTrails"
      ],
      "Resource": "*"
    }
  ]
}
```

Attach this policy to your IAM user or role.

## Troubleshooting

**"No credentials found"**
- Run `aws configure` to set up credentials
- Or set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

**"Access Denied"**
- Check IAM permissions
- Verify you have the required permissions for the operation

**"Region not found"**
- Set default region: `aws configure set region us-east-1`
- Or specify region in queries

**Server not responding**
- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check MCP server logs

## Next Steps

1. **Customize queries** - Modify the tools to match your needs
2. **Add new tools** - Extend servers with additional AWS operations
3. **Create dashboards** - Use the data for monitoring dashboards
4. **Automate workflows** - Integrate with CI/CD pipelines
5. **Set up alerts** - Trigger actions based on findings

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS CLI Reference](https://docs.aws.amazon.com/cli/)
- [Kiro CLI Documentation](https://docs.aws.amazon.com/kiro/)

## Support

Issues or questions? Open an issue on GitHub or reach out on LinkedIn.
