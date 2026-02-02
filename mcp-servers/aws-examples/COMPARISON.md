# MCP Server Comparison Guide

## Quick Reference Table

| Server | Primary Use | Key Tools | Typical Users | Response Time |
|--------|-------------|-----------|---------------|---------------|
| **Resource Inspector** | Infrastructure inventory | List EC2, S3, RDS, Lambda | DevOps, SRE | Fast (1-3s) |
| **Cost Optimizer** | Cost analysis & savings | Cost breakdown, unused resources | FinOps, Management | Medium (3-10s) |
| **Security Auditor** | Security assessment | S3 public access, IAM audit, SG review | Security, Compliance | Medium (5-15s) |
| **CloudWatch Insights** | Troubleshooting & monitoring | Log queries, metrics, error analysis | DevOps, SRE | Slow (10-30s) |
| **Well-Architected** | Architecture review | 5 pillar assessment, best practices | Architects, Leadership | Slow (30-60s) |

## When to Use Each Server

### Use Resource Inspector When:
- ✅ You need a quick inventory of resources
- ✅ You want to filter resources by tags or state
- ✅ You're doing capacity planning
- ✅ You need to verify resource configurations
- ❌ NOT for: Cost analysis, security audits, log analysis

**Example Queries:**
- "Show me all running EC2 instances"
- "List S3 buckets created in the last month"
- "What Lambda functions are using Python 3.8?"

### Use Cost Optimizer When:
- ✅ You're doing monthly cost reviews
- ✅ You need to find cost savings opportunities
- ✅ You want rightsizing recommendations
- ✅ You're forecasting future costs
- ❌ NOT for: Real-time monitoring, security issues, performance problems

**Example Queries:**
- "What are my top 5 most expensive services?"
- "Find unused resources that are costing money"
- "Should I buy Reserved Instances?"

### Use Security Auditor When:
- ✅ You're doing security assessments
- ✅ You need compliance reports
- ✅ You're checking for misconfigurations
- ✅ You want to validate security posture
- ❌ NOT for: Cost optimization, performance tuning, log analysis

**Example Queries:**
- "Check all S3 buckets for public access"
- "Find security groups with SSH open to the world"
- "Are my RDS databases encrypted?"

### Use CloudWatch Insights When:
- ✅ You're troubleshooting production issues
- ✅ You need to analyze logs or metrics
- ✅ You're investigating errors or performance problems
- ✅ You want to track API performance
- ❌ NOT for: Cost analysis, security audits, architecture reviews

**Example Queries:**
- "Show me Lambda errors from the last hour"
- "What's the average API response time?"
- "Find all 5xx errors in production"

### Use Well-Architected Advisor When:
- ✅ You're doing architecture reviews
- ✅ You need comprehensive best practice assessment
- ✅ You're preparing for audits or reviews
- ✅ You want to improve overall architecture quality
- ❌ NOT for: Quick checks, real-time monitoring, specific troubleshooting

**Example Queries:**
- "Assess my security posture"
- "Generate a Well-Architected report"
- "What are my reliability issues?"

## Combining Servers

Many scenarios benefit from using multiple servers together:

### Monthly Review Workflow
1. **Cost Optimizer** - Identify expensive services
2. **Resource Inspector** - Verify resource utilization
3. **Security Auditor** - Check for security issues
4. **Well-Architected** - Overall architecture assessment

### Incident Response Workflow
1. **CloudWatch Insights** - Find errors and analyze logs
2. **Resource Inspector** - Check resource status
3. **Security Auditor** - Rule out security issues

### New Project Setup
1. **Well-Architected** - Baseline assessment
2. **Security Auditor** - Security configuration
3. **Cost Optimizer** - Set up cost tracking

### Optimization Sprint
1. **Cost Optimizer** - Find savings opportunities
2. **Resource Inspector** - Identify underutilized resources
3. **Well-Architected** - Performance efficiency assessment

## Performance Characteristics

### Resource Inspector
- **Speed:** Fast (1-3 seconds)
- **API Calls:** 1-5 per query
- **Best For:** Quick lookups
- **Limitations:** No historical data

### Cost Optimizer
- **Speed:** Medium (3-10 seconds)
- **API Calls:** 5-20 per query
- **Best For:** Cost analysis
- **Limitations:** Cost data has 24-hour delay

### Security Auditor
- **Speed:** Medium (5-15 seconds)
- **API Calls:** 10-50 per query
- **Best For:** Security checks
- **Limitations:** Requires broad IAM permissions

### CloudWatch Insights
- **Speed:** Slow (10-30 seconds)
- **API Calls:** 2-10 per query (with polling)
- **Best For:** Deep analysis
- **Limitations:** Query timeout after 30 seconds

### Well-Architected Advisor
- **Speed:** Slow (30-60 seconds)
- **API Calls:** 50-100+ per query
- **Best For:** Comprehensive reviews
- **Limitations:** Resource intensive

## IAM Permission Requirements

### Minimal (Read-Only)
- Resource Inspector
- CloudWatch Insights (metrics only)

### Moderate (Read + List)
- Cost Optimizer
- Security Auditor

### Comprehensive (Full Read Access)
- Well-Architected Advisor

See README.md for detailed IAM policies.

## Cost Considerations

### API Call Costs
All servers use AWS APIs that are generally free or very low cost:
- EC2 Describe* calls: Free
- S3 List operations: Free
- CloudWatch GetMetricStatistics: Free
- Cost Explorer API: $0.01 per request
- CloudWatch Insights queries: $0.005 per GB scanned

**Typical monthly cost:** $1-10 depending on usage

### Cost Savings Potential
- Cost Optimizer: $500-5000/month savings
- Security Auditor: Prevent costly breaches
- Well-Architected: 10-30% infrastructure cost reduction

**ROI:** Typically 100-1000x the API costs

## Choosing Your First Server

### Start with Resource Inspector if:
- You're new to MCP servers
- You want quick wins
- You need basic infrastructure visibility

### Start with Cost Optimizer if:
- Cost is your primary concern
- You have budget pressure
- You want immediate savings

### Start with Security Auditor if:
- Security is your top priority
- You need compliance reports
- You're preparing for an audit

### Start with CloudWatch Insights if:
- You're troubleshooting issues
- You need better observability
- You're doing incident response

### Start with Well-Architected if:
- You're doing architecture reviews
- You need comprehensive assessment
- You have time for deep analysis

## Advanced Usage Patterns

### Scheduled Assessments
Run Well-Architected assessments monthly:
```bash
# Cron job
0 0 1 * * python aws_well_architected_advisor.py --report
```

### Continuous Monitoring
Use CloudWatch Insights for real-time alerts:
```bash
# Check for errors every 5 minutes
*/5 * * * * python aws_cloudwatch_insights.py --check-errors
```

### Cost Optimization Pipeline
1. Weekly: Run Cost Optimizer
2. Identify savings > $100/month
3. Create tickets for remediation
4. Track savings over time

### Security Compliance
1. Daily: Run Security Auditor
2. Alert on CRITICAL findings
3. Weekly report to security team
4. Monthly compliance dashboard

## Troubleshooting Guide

### Server Not Responding
1. Check AWS credentials: `aws sts get-caller-identity`
2. Verify IAM permissions
3. Check network connectivity
4. Review server logs

### Slow Performance
1. Reduce query scope (specific regions)
2. Use filters to limit results
3. Check AWS service health
4. Consider pagination

### Incomplete Results
1. Check IAM permissions
2. Verify resource exists in specified region
3. Look for API throttling
4. Review error messages

### Authentication Errors
1. Refresh AWS credentials
2. Check credential expiration
3. Verify IAM role trust policy
4. Test with AWS CLI first

## Best Practices

1. **Start Small** - Test with one server before deploying all
2. **Use Filters** - Narrow queries to specific regions/resources
3. **Monitor Costs** - Track Cost Explorer API usage
4. **Rotate Credentials** - Use IAM roles when possible
5. **Document Findings** - Keep track of recommendations
6. **Automate Remediation** - Build on these foundations
7. **Share Results** - Democratize AWS insights across teams
8. **Regular Reviews** - Schedule periodic assessments

## Getting Help

- **Documentation:** See README.md and QUICKSTART.md
- **Examples:** Check example queries in each server
- **Issues:** Open GitHub issue
- **Questions:** Connect on LinkedIn

---

**Last Updated:** January 2026
**Version:** 1.0
