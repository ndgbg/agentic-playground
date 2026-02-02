#!/usr/bin/env python3
"""
AWS Resource Inspector MCP Server
Provides tools to query and analyze AWS resources across accounts.
"""

import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError

server = Server("aws-resource-inspector")

def get_client(service: str, region: str = None):
    """Get boto3 client with optional region."""
    if region:
        return boto3.client(service, region_name=region)
    return boto3.client(service)

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available AWS resource inspection tools."""
    return [
        Tool(
            name="list_ec2_instances",
            description="List EC2 instances with optional filtering by state, tag, or instance type",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region (default: us-east-1)"},
                    "state": {"type": "string", "description": "Instance state filter (running, stopped, etc.)"},
                    "tag_key": {"type": "string", "description": "Filter by tag key"},
                    "tag_value": {"type": "string", "description": "Filter by tag value"}
                }
            }
        ),
        Tool(
            name="list_s3_buckets",
            description="List S3 buckets with details including size, public access, and encryption",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_details": {"type": "boolean", "description": "Include detailed bucket info"}
                }
            }
        ),
        Tool(
            name="list_rds_instances",
            description="List RDS database instances with configuration details",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="list_lambda_functions",
            description="List Lambda functions with runtime, memory, and last modified info",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"},
                    "runtime": {"type": "string", "description": "Filter by runtime (e.g., python3.11)"}
                }
            }
        ),
        Tool(
            name="get_cloudwatch_metrics",
            description="Get CloudWatch metrics for a resource",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "CloudWatch namespace (e.g., AWS/EC2)"},
                    "metric_name": {"type": "string", "description": "Metric name (e.g., CPUUtilization)"},
                    "dimensions": {"type": "object", "description": "Metric dimensions"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["namespace", "metric_name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute AWS resource inspection tools."""
    
    try:
        if name == "list_ec2_instances":
            region = arguments.get("region", "us-east-1")
            ec2 = get_client("ec2", region)
            
            filters = []
            if arguments.get("state"):
                filters.append({"Name": "instance-state-name", "Values": [arguments["state"]]})
            if arguments.get("tag_key") and arguments.get("tag_value"):
                filters.append({"Name": f"tag:{arguments['tag_key']}", "Values": [arguments["tag_value"]]})
            
            response = ec2.describe_instances(Filters=filters) if filters else ec2.describe_instances()
            
            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append({
                        "InstanceId": instance["InstanceId"],
                        "InstanceType": instance["InstanceType"],
                        "State": instance["State"]["Name"],
                        "LaunchTime": str(instance["LaunchTime"]),
                        "PrivateIpAddress": instance.get("PrivateIpAddress", "N/A"),
                        "Tags": {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps({"instances": instances, "count": len(instances)}, indent=2)
            )]
        
        elif name == "list_s3_buckets":
            s3 = get_client("s3")
            response = s3.list_buckets()
            
            buckets = []
            for bucket in response["Buckets"]:
                bucket_info = {
                    "Name": bucket["Name"],
                    "CreationDate": str(bucket["CreationDate"])
                }
                
                if arguments.get("include_details"):
                    try:
                        # Check public access
                        public_access = s3.get_public_access_block(Bucket=bucket["Name"])
                        bucket_info["PublicAccess"] = public_access["PublicAccessBlockConfiguration"]
                        
                        # Check encryption
                        encryption = s3.get_bucket_encryption(Bucket=bucket["Name"])
                        bucket_info["Encryption"] = encryption["ServerSideEncryptionConfiguration"]
                    except ClientError:
                        bucket_info["Details"] = "Unable to fetch (permissions required)"
                
                buckets.append(bucket_info)
            
            return [TextContent(
                type="text",
                text=json.dumps({"buckets": buckets, "count": len(buckets)}, indent=2)
            )]
        
        elif name == "list_rds_instances":
            region = arguments.get("region", "us-east-1")
            rds = get_client("rds", region)
            response = rds.describe_db_instances()
            
            instances = []
            for db in response["DBInstances"]:
                instances.append({
                    "DBInstanceIdentifier": db["DBInstanceIdentifier"],
                    "Engine": db["Engine"],
                    "EngineVersion": db["EngineVersion"],
                    "DBInstanceClass": db["DBInstanceClass"],
                    "Status": db["DBInstanceStatus"],
                    "AllocatedStorage": db["AllocatedStorage"],
                    "MultiAZ": db["MultiAZ"],
                    "Endpoint": db.get("Endpoint", {}).get("Address", "N/A")
                })
            
            return [TextContent(
                type="text",
                text=json.dumps({"databases": instances, "count": len(instances)}, indent=2)
            )]
        
        elif name == "list_lambda_functions":
            region = arguments.get("region", "us-east-1")
            lambda_client = get_client("lambda", region)
            response = lambda_client.list_functions()
            
            functions = []
            for func in response["Functions"]:
                if arguments.get("runtime") and func["Runtime"] != arguments["runtime"]:
                    continue
                    
                functions.append({
                    "FunctionName": func["FunctionName"],
                    "Runtime": func["Runtime"],
                    "MemorySize": func["MemorySize"],
                    "Timeout": func["Timeout"],
                    "LastModified": func["LastModified"],
                    "CodeSize": func["CodeSize"]
                })
            
            return [TextContent(
                type="text",
                text=json.dumps({"functions": functions, "count": len(functions)}, indent=2)
            )]
        
        elif name == "get_cloudwatch_metrics":
            region = arguments.get("region", "us-east-1")
            cloudwatch = get_client("cloudwatch", region)
            
            from datetime import datetime, timedelta
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)
            
            dimensions = [{"Name": k, "Value": v} for k, v in arguments.get("dimensions", {}).items()]
            
            response = cloudwatch.get_metric_statistics(
                Namespace=arguments["namespace"],
                MetricName=arguments["metric_name"],
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=["Average", "Maximum", "Minimum"]
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(response["Datapoints"], indent=2, default=str)
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
