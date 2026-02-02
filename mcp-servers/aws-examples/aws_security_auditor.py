#!/usr/bin/env python3
"""
AWS Security Auditor MCP Server
Security posture assessment and compliance checking for AWS resources.
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError

server = Server("aws-security-auditor")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available security audit tools."""
    return [
        Tool(
            name="audit_s3_public_access",
            description="Check all S3 buckets for public access configurations",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_acls": {"type": "boolean", "description": "Also check bucket ACLs"}
                }
            }
        ),
        Tool(
            name="audit_iam_policies",
            description="Audit IAM users, roles, and policies for security issues",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_admin_access": {"type": "boolean", "description": "Flag users with admin access"},
                    "check_unused": {"type": "boolean", "description": "Find unused IAM users"}
                }
            }
        ),
        Tool(
            name="audit_security_groups",
            description="Check security groups for overly permissive rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"},
                    "check_ports": {"type": "array", "items": {"type": "integer"}, "description": "Specific ports to check (e.g., [22, 3389])"}
                }
            }
        ),
        Tool(
            name="check_encryption_status",
            description="Verify encryption status of EBS volumes, RDS instances, and S3 buckets",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"},
                    "resource_types": {"type": "array", "items": {"type": "string"}, "description": "Resources to check (ebs, rds, s3)"}
                }
            }
        ),
        Tool(
            name="compliance_check",
            description="Run compliance checks against AWS best practices",
            inputSchema={
                "type": "object",
                "properties": {
                    "framework": {"type": "string", "enum": ["CIS", "PCI-DSS", "HIPAA"], "description": "Compliance framework"},
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute security audit tools."""
    
    try:
        if name == "audit_s3_public_access":
            s3 = boto3.client("s3")
            response = s3.list_buckets()
            
            findings = []
            for bucket in response["Buckets"]:
                bucket_name = bucket["Name"]
                
                try:
                    # Check public access block
                    public_block = s3.get_public_access_block(Bucket=bucket_name)
                    config = public_block["PublicAccessBlockConfiguration"]
                    
                    if not all([
                        config.get("BlockPublicAcls"),
                        config.get("BlockPublicPolicy"),
                        config.get("IgnorePublicAcls"),
                        config.get("RestrictPublicBuckets")
                    ]):
                        findings.append({
                            "Bucket": bucket_name,
                            "Issue": "Public access not fully blocked",
                            "Severity": "HIGH",
                            "Config": config
                        })
                    
                    # Check ACLs if requested
                    if arguments.get("check_acls"):
                        acl = s3.get_bucket_acl(Bucket=bucket_name)
                        for grant in acl["Grants"]:
                            grantee = grant["Grantee"]
                            if grantee.get("Type") == "Group" and "AllUsers" in grantee.get("URI", ""):
                                findings.append({
                                    "Bucket": bucket_name,
                                    "Issue": "Public ACL grants access to all users",
                                    "Severity": "CRITICAL",
                                    "Permission": grant["Permission"]
                                })
                
                except ClientError as e:
                    if e.response["Error"]["Code"] != "NoSuchPublicAccessBlockConfiguration":
                        findings.append({
                            "Bucket": bucket_name,
                            "Issue": "Unable to check public access",
                            "Severity": "MEDIUM",
                            "Error": str(e)
                        })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "findings": findings,
                    "total_buckets_checked": len(response["Buckets"]),
                    "issues_found": len(findings)
                }, indent=2)
            )]
        
        elif name == "audit_iam_policies":
            iam = boto3.client("iam")
            findings = []
            
            # Check for admin users
            if arguments.get("check_admin_access"):
                users = iam.list_users()
                for user in users["Users"]:
                    user_name = user["UserName"]
                    
                    # Check attached policies
                    policies = iam.list_attached_user_policies(UserName=user_name)
                    for policy in policies["AttachedPolicies"]:
                        if "Admin" in policy["PolicyName"] or policy["PolicyArn"].endswith("AdministratorAccess"):
                            findings.append({
                                "User": user_name,
                                "Issue": "User has administrator access",
                                "Severity": "HIGH",
                                "Policy": policy["PolicyName"]
                            })
                    
                    # Check inline policies
                    inline_policies = iam.list_user_policies(UserName=user_name)
                    for policy_name in inline_policies["PolicyNames"]:
                        policy_doc = iam.get_user_policy(UserName=user_name, PolicyName=policy_name)
                        if '"Effect":"Allow"' in str(policy_doc) and '"Action":"*"' in str(policy_doc):
                            findings.append({
                                "User": user_name,
                                "Issue": "Inline policy grants wildcard permissions",
                                "Severity": "HIGH",
                                "Policy": policy_name
                            })
            
            # Check for unused users
            if arguments.get("check_unused"):
                from datetime import datetime, timedelta
                cutoff = datetime.utcnow() - timedelta(days=90)
                
                users = iam.list_users()
                for user in users["Users"]:
                    user_name = user["UserName"]
                    
                    try:
                        access_keys = iam.list_access_keys(UserName=user_name)
                        last_used = None
                        
                        for key in access_keys["AccessKeyMetadata"]:
                            key_last_used = iam.get_access_key_last_used(AccessKeyId=key["AccessKeyId"])
                            if "LastUsedDate" in key_last_used["AccessKeyLastUsed"]:
                                key_date = key_last_used["AccessKeyLastUsed"]["LastUsedDate"]
                                if not last_used or key_date > last_used:
                                    last_used = key_date
                        
                        if not last_used or last_used.replace(tzinfo=None) < cutoff:
                            findings.append({
                                "User": user_name,
                                "Issue": "User inactive for 90+ days",
                                "Severity": "MEDIUM",
                                "LastUsed": str(last_used) if last_used else "Never"
                            })
                    except ClientError:
                        pass
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "findings": findings,
                    "issues_found": len(findings)
                }, indent=2)
            )]
        
        elif name == "audit_security_groups":
            region = arguments.get("region", "us-east-1")
            ec2 = boto3.client("ec2", region_name=region)
            
            response = ec2.describe_security_groups()
            findings = []
            check_ports = arguments.get("check_ports", [22, 3389, 3306, 5432])
            
            for sg in response["SecurityGroups"]:
                for rule in sg.get("IpPermissions", []):
                    from_port = rule.get("FromPort", 0)
                    to_port = rule.get("ToPort", 65535)
                    
                    # Check for 0.0.0.0/0 access
                    for ip_range in rule.get("IpRanges", []):
                        if ip_range.get("CidrIp") == "0.0.0.0/0":
                            # Check if it's a sensitive port
                            for port in check_ports:
                                if from_port <= port <= to_port:
                                    findings.append({
                                        "SecurityGroup": sg["GroupId"],
                                        "GroupName": sg["GroupName"],
                                        "Issue": f"Port {port} open to 0.0.0.0/0",
                                        "Severity": "CRITICAL" if port in [22, 3389] else "HIGH",
                                        "Protocol": rule.get("IpProtocol", "all")
                                    })
                            
                            # Check for all ports open
                            if from_port == 0 and to_port == 65535:
                                findings.append({
                                    "SecurityGroup": sg["GroupId"],
                                    "GroupName": sg["GroupName"],
                                    "Issue": "All ports open to 0.0.0.0/0",
                                    "Severity": "CRITICAL",
                                    "Protocol": rule.get("IpProtocol", "all")
                                })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "findings": findings,
                    "security_groups_checked": len(response["SecurityGroups"]),
                    "issues_found": len(findings)
                }, indent=2)
            )]
        
        elif name == "check_encryption_status":
            region = arguments.get("region", "us-east-1")
            resource_types = arguments.get("resource_types", ["ebs", "rds", "s3"])
            findings = []
            
            if "ebs" in resource_types:
                ec2 = boto3.client("ec2", region_name=region)
                volumes = ec2.describe_volumes()
                
                for vol in volumes["Volumes"]:
                    if not vol.get("Encrypted", False):
                        findings.append({
                            "ResourceType": "EBS Volume",
                            "ResourceId": vol["VolumeId"],
                            "Issue": "Volume not encrypted",
                            "Severity": "HIGH",
                            "Size": vol["Size"]
                        })
            
            if "rds" in resource_types:
                rds = boto3.client("rds", region_name=region)
                instances = rds.describe_db_instances()
                
                for db in instances["DBInstances"]:
                    if not db.get("StorageEncrypted", False):
                        findings.append({
                            "ResourceType": "RDS Instance",
                            "ResourceId": db["DBInstanceIdentifier"],
                            "Issue": "Database not encrypted",
                            "Severity": "CRITICAL",
                            "Engine": db["Engine"]
                        })
            
            if "s3" in resource_types:
                s3 = boto3.client("s3")
                buckets = s3.list_buckets()
                
                for bucket in buckets["Buckets"]:
                    try:
                        encryption = s3.get_bucket_encryption(Bucket=bucket["Name"])
                    except ClientError as e:
                        if e.response["Error"]["Code"] == "ServerSideEncryptionConfigurationNotFoundError":
                            findings.append({
                                "ResourceType": "S3 Bucket",
                                "ResourceId": bucket["Name"],
                                "Issue": "Bucket encryption not configured",
                                "Severity": "HIGH"
                            })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "findings": findings,
                    "issues_found": len(findings)
                }, indent=2)
            )]
        
        elif name == "compliance_check":
            framework = arguments.get("framework", "CIS")
            region = arguments.get("region", "us-east-1")
            
            # Run basic CIS AWS Foundations checks
            findings = []
            
            # Check 1: Root account MFA
            iam = boto3.client("iam")
            summary = iam.get_account_summary()
            if summary["SummaryMap"].get("AccountMFAEnabled", 0) == 0:
                findings.append({
                    "Check": "CIS 1.13",
                    "Description": "Root account MFA not enabled",
                    "Severity": "CRITICAL",
                    "Compliance": framework
                })
            
            # Check 2: CloudTrail enabled
            cloudtrail = boto3.client("cloudtrail", region_name=region)
            trails = cloudtrail.describe_trails()
            if not trails["trailList"]:
                findings.append({
                    "Check": "CIS 2.1",
                    "Description": "CloudTrail not enabled",
                    "Severity": "HIGH",
                    "Compliance": framework
                })
            
            # Check 3: VPC Flow Logs
            ec2 = boto3.client("ec2", region_name=region)
            vpcs = ec2.describe_vpcs()
            for vpc in vpcs["Vpcs"]:
                flow_logs = ec2.describe_flow_logs(
                    Filters=[{"Name": "resource-id", "Values": [vpc["VpcId"]]}]
                )
                if not flow_logs["FlowLogs"]:
                    findings.append({
                        "Check": "CIS 2.9",
                        "Description": f"VPC Flow Logs not enabled for {vpc['VpcId']}",
                        "Severity": "MEDIUM",
                        "Compliance": framework
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "framework": framework,
                    "findings": findings,
                    "checks_failed": len(findings)
                }, indent=2)
            )]
        
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
    asyncio.run(main())
