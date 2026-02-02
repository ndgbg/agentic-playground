#!/usr/bin/env python3
"""
AWS Well-Architected Advisor MCP Server
Provides recommendations based on AWS Well-Architected Framework pillars.
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError

server = Server("aws-well-architected-advisor")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Well-Architected tools."""
    return [
        Tool(
            name="assess_operational_excellence",
            description="Assess operational excellence pillar (monitoring, automation, incident response)",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="assess_security",
            description="Assess security pillar (IAM, encryption, network security)",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="assess_reliability",
            description="Assess reliability pillar (backup, disaster recovery, fault tolerance)",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="assess_performance_efficiency",
            description="Assess performance efficiency pillar (resource selection, monitoring, optimization)",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="assess_cost_optimization",
            description="Assess cost optimization pillar (rightsizing, reserved capacity, waste elimination)",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="generate_full_report",
            description="Generate comprehensive Well-Architected assessment across all pillars",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"},
                    "workload_name": {"type": "string", "description": "Name of the workload being assessed"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute Well-Architected assessment tools."""
    
    try:
        region = arguments.get("region", "us-east-1")
        
        if name == "assess_operational_excellence":
            findings = []
            score = 100
            
            # Check CloudWatch alarms
            cloudwatch = boto3.client("cloudwatch", region_name=region)
            alarms = cloudwatch.describe_alarms()
            if len(alarms["MetricAlarms"]) == 0:
                findings.append({
                    "pillar": "Operational Excellence",
                    "check": "CloudWatch Alarms",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "finding": "No CloudWatch alarms configured",
                    "recommendation": "Set up alarms for critical metrics (CPU, memory, errors)",
                    "impact": "Cannot detect and respond to operational issues"
                })
                score -= 20
            
            # Check CloudTrail
            cloudtrail = boto3.client("cloudtrail", region_name=region)
            trails = cloudtrail.describe_trails()
            if not trails["trailList"]:
                findings.append({
                    "pillar": "Operational Excellence",
                    "check": "CloudTrail",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "finding": "CloudTrail not enabled",
                    "recommendation": "Enable CloudTrail for audit logging and compliance",
                    "impact": "No audit trail of API calls and changes"
                })
                score -= 20
            
            # Check Systems Manager
            ssm = boto3.client("ssm", region_name=region)
            try:
                documents = ssm.list_documents(Filters=[{"Key": "Owner", "Values": ["Self"]}])
                if len(documents["DocumentIdentifiers"]) == 0:
                    findings.append({
                        "pillar": "Operational Excellence",
                        "check": "Automation",
                        "status": "WARNING",
                        "severity": "MEDIUM",
                        "finding": "No Systems Manager automation documents found",
                        "recommendation": "Create runbooks for common operational tasks",
                        "impact": "Manual operations increase risk of errors"
                    })
                    score -= 10
            except ClientError:
                pass
            
            # Check Lambda functions for monitoring
            lambda_client = boto3.client("lambda", region_name=region)
            functions = lambda_client.list_functions()
            unmonitored = 0
            for func in functions["Functions"]:
                func_name = func["FunctionName"]
                alarms_for_func = cloudwatch.describe_alarms_for_metric(
                    MetricName="Errors",
                    Namespace="AWS/Lambda",
                    Dimensions=[{"Name": "FunctionName", "Value": func_name}]
                )
                if not alarms_for_func["MetricAlarms"]:
                    unmonitored += 1
            
            if unmonitored > 0:
                findings.append({
                    "pillar": "Operational Excellence",
                    "check": "Lambda Monitoring",
                    "status": "WARNING",
                    "severity": "MEDIUM",
                    "finding": f"{unmonitored} Lambda functions without error alarms",
                    "recommendation": "Set up error alarms for all Lambda functions",
                    "impact": "Function failures may go unnoticed"
                })
                score -= 10
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "pillar": "Operational Excellence",
                    "score": max(0, score),
                    "findings": findings,
                    "summary": f"Found {len(findings)} issues affecting operational excellence"
                }, indent=2)
            )]
        
        elif name == "assess_security":
            findings = []
            score = 100
            
            # Check root account MFA
            iam = boto3.client("iam")
            summary = iam.get_account_summary()
            if summary["SummaryMap"].get("AccountMFAEnabled", 0) == 0:
                findings.append({
                    "pillar": "Security",
                    "check": "Root Account MFA",
                    "status": "FAIL",
                    "severity": "CRITICAL",
                    "finding": "Root account MFA not enabled",
                    "recommendation": "Enable MFA on root account immediately",
                    "impact": "Account vulnerable to credential compromise"
                })
                score -= 30
            
            # Check S3 bucket encryption
            s3 = boto3.client("s3")
            buckets = s3.list_buckets()
            unencrypted = 0
            for bucket in buckets["Buckets"]:
                try:
                    s3.get_bucket_encryption(Bucket=bucket["Name"])
                except ClientError as e:
                    if e.response["Error"]["Code"] == "ServerSideEncryptionConfigurationNotFoundError":
                        unencrypted += 1
            
            if unencrypted > 0:
                findings.append({
                    "pillar": "Security",
                    "check": "S3 Encryption",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "finding": f"{unencrypted} S3 buckets without encryption",
                    "recommendation": "Enable default encryption on all S3 buckets",
                    "impact": "Data at rest not protected"
                })
                score -= 20
            
            # Check security groups
            ec2 = boto3.client("ec2", region_name=region)
            security_groups = ec2.describe_security_groups()
            open_to_world = 0
            for sg in security_groups["SecurityGroups"]:
                for rule in sg.get("IpPermissions", []):
                    for ip_range in rule.get("IpRanges", []):
                        if ip_range.get("CidrIp") == "0.0.0.0/0":
                            from_port = rule.get("FromPort", 0)
                            if from_port in [22, 3389, 3306, 5432]:
                                open_to_world += 1
                                break
            
            if open_to_world > 0:
                findings.append({
                    "pillar": "Security",
                    "check": "Network Security",
                    "status": "FAIL",
                    "severity": "CRITICAL",
                    "finding": f"{open_to_world} security groups with sensitive ports open to 0.0.0.0/0",
                    "recommendation": "Restrict access to specific IP ranges or use VPN",
                    "impact": "Resources exposed to internet attacks"
                })
                score -= 30
            
            # Check IAM password policy
            try:
                password_policy = iam.get_account_password_policy()
                policy = password_policy["PasswordPolicy"]
                if not policy.get("RequireUppercaseCharacters") or not policy.get("RequireLowercaseCharacters"):
                    findings.append({
                        "pillar": "Security",
                        "check": "IAM Password Policy",
                        "status": "WARNING",
                        "severity": "MEDIUM",
                        "finding": "Weak password policy",
                        "recommendation": "Enforce strong password requirements",
                        "impact": "Increased risk of password compromise"
                    })
                    score -= 10
            except ClientError:
                findings.append({
                    "pillar": "Security",
                    "check": "IAM Password Policy",
                    "status": "FAIL",
                    "severity": "HIGH",
                    "finding": "No password policy configured",
                    "recommendation": "Set up IAM password policy with strong requirements",
                    "impact": "No password complexity enforcement"
                })
                score -= 20
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "pillar": "Security",
                    "score": max(0, score),
                    "findings": findings,
                    "summary": f"Found {len(findings)} security issues"
                }, indent=2)
            )]
        
        elif name == "assess_reliability":
            findings = []
            score = 100
            
            # Check RDS backups
            rds = boto3.client("rds", region_name=region)
            instances = rds.describe_db_instances()
            no_backup = 0
            single_az = 0
            for db in instances["DBInstances"]:
                if db.get("BackupRetentionPeriod", 0) == 0:
                    no_backup += 1
                if not db.get("MultiAZ", False):
                    single_az += 1
            
            if no_backup > 0:
                findings.append({
                    "pillar": "Reliability",
                    "check": "RDS Backups",
                    "status": "FAIL",
                    "severity": "CRITICAL",
                    "finding": f"{no_backup} RDS instances without automated backups",
                    "recommendation": "Enable automated backups with appropriate retention",
                    "impact": "Data loss risk in case of failure"
                })
                score -= 30
            
            if single_az > 0:
                findings.append({
                    "pillar": "Reliability",
                    "check": "RDS Multi-AZ",
                    "status": "WARNING",
                    "severity": "HIGH",
                    "finding": f"{single_az} RDS instances not using Multi-AZ",
                    "recommendation": "Enable Multi-AZ for production databases",
                    "impact": "No automatic failover capability"
                })
                score -= 20
            
            # Check EBS snapshots
            ec2 = boto3.client("ec2", region_name=region)
            volumes = ec2.describe_volumes()
            snapshots = ec2.describe_snapshots(OwnerIds=["self"])
            
            volume_ids = {vol["VolumeId"] for vol in volumes["Volumes"]}
            snapshot_volumes = {snap["VolumeId"] for snap in snapshots["Snapshots"]}
            no_snapshot = volume_ids - snapshot_volumes
            
            if len(no_snapshot) > 0:
                findings.append({
                    "pillar": "Reliability",
                    "check": "EBS Snapshots",
                    "status": "WARNING",
                    "severity": "MEDIUM",
                    "finding": f"{len(no_snapshot)} EBS volumes without snapshots",
                    "recommendation": "Create snapshot schedule for important volumes",
                    "impact": "No point-in-time recovery for volumes"
                })
                score -= 15
            
            # Check Auto Scaling groups
            autoscaling = boto3.client("autoscaling", region_name=region)
            asgs = autoscaling.describe_auto_scaling_groups()
            single_instance = 0
            for asg in asgs["AutoScalingGroups"]:
                if asg["MaxSize"] == 1:
                    single_instance += 1
            
            if single_instance > 0:
                findings.append({
                    "pillar": "Reliability",
                    "check": "Auto Scaling",
                    "status": "WARNING",
                    "severity": "MEDIUM",
                    "finding": f"{single_instance} Auto Scaling groups with max size of 1",
                    "recommendation": "Configure ASGs for multiple instances",
                    "impact": "No horizontal scaling capability"
                })
                score -= 10
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "pillar": "Reliability",
                    "score": max(0, score),
                    "findings": findings,
                    "summary": f"Found {len(findings)} reliability issues"
                }, indent=2)
            )]
        
        elif name == "assess_performance_efficiency":
            findings = []
            score = 100
            
            # Check for old generation instances
            ec2 = boto3.client("ec2", region_name=region)
            instances = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])
            old_gen = 0
            for reservation in instances["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_type = instance["InstanceType"]
                    # Check for older generation types (t2, m4, c4, etc.)
                    if any(instance_type.startswith(prefix) for prefix in ["t2.", "m4.", "c4.", "r4."]):
                        old_gen += 1
            
            if old_gen > 0:
                findings.append({
                    "pillar": "Performance Efficiency",
                    "check": "Instance Generations",
                    "status": "WARNING",
                    "severity": "MEDIUM",
                    "finding": f"{old_gen} instances using older generation types",
                    "recommendation": "Migrate to current generation instances (t3, m5, c5, r5)",
                    "impact": "Missing out on better price/performance"
                })
                score -= 15
            
            # Check CloudWatch detailed monitoring
            unmonitored = 0
            for reservation in instances["Reservations"]:
                for instance in reservation["Instances"]:
                    if instance.get("Monitoring", {}).get("State") != "enabled":
                        unmonitored += 1
            
            if unmonitored > 0:
                findings.append({
                    "pillar": "Performance Efficiency",
                    "check": "Detailed Monitoring",
                    "status": "WARNING",
                    "severity": "LOW",
                    "finding": f"{unmonitored} EC2 instances without detailed monitoring",
                    "recommendation": "Enable detailed monitoring for better performance insights",
                    "impact": "Limited visibility into performance metrics"
                })
                score -= 10
            
            # Check for GP2 volumes (should use GP3)
            volumes = ec2.describe_volumes()
            gp2_volumes = sum(1 for vol in volumes["Volumes"] if vol["VolumeType"] == "gp2")
            
            if gp2_volumes > 0:
                findings.append({
                    "pillar": "Performance Efficiency",
                    "check": "EBS Volume Types",
                    "status": "WARNING",
                    "severity": "LOW",
                    "finding": f"{gp2_volumes} volumes using GP2 instead of GP3",
                    "recommendation": "Migrate to GP3 for better performance and cost",
                    "impact": "Paying more for same or worse performance"
                })
                score -= 10
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "pillar": "Performance Efficiency",
                    "score": max(0, score),
                    "findings": findings,
                    "summary": f"Found {len(findings)} performance optimization opportunities"
                }, indent=2)
            )]
        
        elif name == "assess_cost_optimization":
            findings = []
            score = 100
            
            # Check for unattached EBS volumes
            ec2 = boto3.client("ec2", region_name=region)
            volumes = ec2.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}])
            unused_cost = sum(vol["Size"] * 0.10 for vol in volumes["Volumes"])
            
            if len(volumes["Volumes"]) > 0:
                findings.append({
                    "pillar": "Cost Optimization",
                    "check": "Unused EBS Volumes",
                    "status": "WARNING",
                    "severity": "MEDIUM",
                    "finding": f"{len(volumes['Volumes'])} unattached EBS volumes",
                    "recommendation": "Delete unused volumes or create snapshots",
                    "impact": f"Wasting ~${unused_cost:.2f}/month"
                })
                score -= 15
            
            # Check for unassociated Elastic IPs
            addresses = ec2.describe_addresses()
            unused_eips = sum(1 for addr in addresses["Addresses"] if "InstanceId" not in addr)
            
            if unused_eips > 0:
                findings.append({
                    "pillar": "Cost Optimization",
                    "check": "Unused Elastic IPs",
                    "status": "WARNING",
                    "severity": "LOW",
                    "finding": f"{unused_eips} unassociated Elastic IPs",
                    "recommendation": "Release unused Elastic IPs",
                    "impact": f"Wasting ~${unused_eips * 3.60:.2f}/month"
                })
                score -= 10
            
            # Check Reserved Instance coverage
            instances = ec2.describe_instances(Filters=[{"Name": "instance-state-name", "Values": ["running"]}])
            reserved = ec2.describe_reserved_instances(Filters=[{"Name": "state", "Values": ["active"]}])
            
            running_count = sum(len(r["Instances"]) for res in instances["Reservations"] for r in [res])
            ri_count = sum(ri["InstanceCount"] for ri in reserved["ReservedInstances"])
            coverage = (ri_count / running_count * 100) if running_count > 0 else 100
            
            if coverage < 70:
                findings.append({
                    "pillar": "Cost Optimization",
                    "check": "Reserved Instance Coverage",
                    "status": "WARNING",
                    "severity": "HIGH",
                    "finding": f"Only {coverage:.1f}% RI coverage",
                    "recommendation": "Purchase Reserved Instances for steady-state workloads",
                    "impact": "Paying on-demand prices unnecessarily"
                })
                score -= 20
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "pillar": "Cost Optimization",
                    "score": max(0, score),
                    "findings": findings,
                    "summary": f"Found {len(findings)} cost optimization opportunities"
                }, indent=2)
            )]
        
        elif name == "generate_full_report":
            workload_name = arguments.get("workload_name", "AWS Workload")
            
            # Run all assessments
            pillars = []
            for pillar_name in ["assess_operational_excellence", "assess_security", 
                               "assess_reliability", "assess_performance_efficiency", 
                               "assess_cost_optimization"]:
                result = await call_tool(pillar_name, {"region": region})
                pillar_data = json.loads(result[0].text)
                pillars.append(pillar_data)
            
            overall_score = sum(p["score"] for p in pillars) / len(pillars)
            total_findings = sum(len(p["findings"]) for p in pillars)
            
            critical = sum(1 for p in pillars for f in p["findings"] if f.get("severity") == "CRITICAL")
            high = sum(1 for p in pillars for f in p["findings"] if f.get("severity") == "HIGH")
            medium = sum(1 for p in pillars for f in p["findings"] if f.get("severity") == "MEDIUM")
            
            report = {
                "workload": workload_name,
                "assessment_date": str(datetime.utcnow()),
                "region": region,
                "overall_score": round(overall_score, 1),
                "total_findings": total_findings,
                "severity_breakdown": {
                    "critical": critical,
                    "high": high,
                    "medium": medium
                },
                "pillar_scores": {p["pillar"]: p["score"] for p in pillars},
                "detailed_findings": pillars,
                "recommendations": [
                    "Address all CRITICAL findings immediately",
                    "Create remediation plan for HIGH severity issues",
                    "Schedule review of MEDIUM severity items",
                    "Re-assess after implementing changes"
                ]
            }
            
            return [TextContent(type="text", text=json.dumps(report, indent=2))]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except ClientError as e:
        return [TextContent(
            type="text",
            text=f"AWS Error: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        )]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(main())
