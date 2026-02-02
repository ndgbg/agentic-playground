#!/usr/bin/env python3
"""
AWS Cost Optimizer MCP Server
Analyzes AWS costs and provides optimization recommendations.
"""

import asyncio
import json
from typing import Any
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError

server = Server("aws-cost-optimizer")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available cost optimization tools."""
    return [
        Tool(
            name="get_cost_by_service",
            description="Get cost breakdown by AWS service for a time period",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days to analyze (default: 30)"},
                    "granularity": {"type": "string", "enum": ["DAILY", "MONTHLY"], "description": "Cost granularity"}
                }
            }
        ),
        Tool(
            name="find_unused_resources",
            description="Identify unused AWS resources that can be deleted to save costs",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region to scan"},
                    "resource_types": {"type": "array", "items": {"type": "string"}, "description": "Resource types to check (ebs, eip, snapshots)"}
                }
            }
        ),
        Tool(
            name="get_rightsizing_recommendations",
            description="Get EC2 rightsizing recommendations to optimize instance types",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="analyze_reserved_instances",
            description="Analyze Reserved Instance coverage and utilization",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "AWS region"}
                }
            }
        ),
        Tool(
            name="forecast_costs",
            description="Forecast AWS costs for the next 30 days based on current usage",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "Specific service to forecast (optional)"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute cost optimization tools."""
    
    try:
        if name == "get_cost_by_service":
            ce = boto3.client("ce")
            days = arguments.get("days", 30)
            granularity = arguments.get("granularity", "MONTHLY")
            
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            response = ce.get_cost_and_usage(
                TimePeriod={
                    "Start": str(start_date),
                    "End": str(end_date)
                },
                Granularity=granularity,
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}]
            )
            
            costs = []
            for result in response["ResultsByTime"]:
                period = result["TimePeriod"]
                for group in result["Groups"]:
                    service = group["Keys"][0]
                    amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    if amount > 0:
                        costs.append({
                            "Service": service,
                            "Amount": round(amount, 2),
                            "Period": f"{period['Start']} to {period['End']}"
                        })
            
            # Sort by cost descending
            costs.sort(key=lambda x: x["Amount"], reverse=True)
            total = sum(c["Amount"] for c in costs)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "costs": costs[:20],  # Top 20 services
                    "total": round(total, 2),
                    "currency": "USD"
                }, indent=2)
            )]
        
        elif name == "find_unused_resources":
            region = arguments.get("region", "us-east-1")
            resource_types = arguments.get("resource_types", ["ebs", "eip", "snapshots"])
            
            unused = {"region": region, "resources": []}
            
            if "ebs" in resource_types:
                ec2 = boto3.client("ec2", region_name=region)
                volumes = ec2.describe_volumes(Filters=[{"Name": "status", "Values": ["available"]}])
                
                for vol in volumes["Volumes"]:
                    unused["resources"].append({
                        "Type": "EBS Volume",
                        "Id": vol["VolumeId"],
                        "Size": vol["Size"],
                        "State": vol["State"],
                        "EstimatedMonthlyCost": vol["Size"] * 0.10  # $0.10/GB-month estimate
                    })
            
            if "eip" in resource_types:
                ec2 = boto3.client("ec2", region_name=region)
                addresses = ec2.describe_addresses()
                
                for addr in addresses["Addresses"]:
                    if "InstanceId" not in addr:
                        unused["resources"].append({
                            "Type": "Elastic IP",
                            "Id": addr["PublicIp"],
                            "AllocationId": addr.get("AllocationId", "N/A"),
                            "EstimatedMonthlyCost": 3.60  # $0.005/hour * 720 hours
                        })
            
            if "snapshots" in resource_types:
                ec2 = boto3.client("ec2", region_name=region)
                snapshots = ec2.describe_snapshots(OwnerIds=["self"])
                
                # Find snapshots older than 90 days
                cutoff = datetime.utcnow() - timedelta(days=90)
                for snap in snapshots["Snapshots"]:
                    if snap["StartTime"].replace(tzinfo=None) < cutoff:
                        unused["resources"].append({
                            "Type": "Old Snapshot",
                            "Id": snap["SnapshotId"],
                            "Size": snap["VolumeSize"],
                            "Age": (datetime.utcnow() - snap["StartTime"].replace(tzinfo=None)).days,
                            "EstimatedMonthlyCost": snap["VolumeSize"] * 0.05  # $0.05/GB-month
                        })
            
            total_savings = sum(r.get("EstimatedMonthlyCost", 0) for r in unused["resources"])
            unused["total_monthly_savings"] = round(total_savings, 2)
            unused["count"] = len(unused["resources"])
            
            return [TextContent(type="text", text=json.dumps(unused, indent=2))]
        
        elif name == "get_rightsizing_recommendations":
            ce = boto3.client("ce")
            
            response = ce.get_rightsizing_recommendation(
                Service="AmazonEC2",
                Configuration={
                    "RecommendationTarget": "SAME_INSTANCE_FAMILY",
                    "BenefitsConsidered": True
                }
            )
            
            recommendations = []
            for rec in response.get("RightsizingRecommendations", []):
                current = rec["CurrentInstance"]
                if rec.get("ModifyRecommendationDetail"):
                    target = rec["ModifyRecommendationDetail"]["TargetInstances"][0]
                    recommendations.append({
                        "InstanceId": current.get("ResourceId", "N/A"),
                        "CurrentType": current.get("InstanceType", "N/A"),
                        "RecommendedType": target.get("InstanceType", "N/A"),
                        "EstimatedMonthlySavings": target.get("EstimatedMonthlySavings", "N/A"),
                        "Reason": rec.get("RightsizingType", "N/A")
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "recommendations": recommendations,
                    "count": len(recommendations)
                }, indent=2)
            )]
        
        elif name == "analyze_reserved_instances":
            region = arguments.get("region", "us-east-1")
            ec2 = boto3.client("ec2", region_name=region)
            
            # Get reserved instances
            reserved = ec2.describe_reserved_instances(
                Filters=[{"Name": "state", "Values": ["active"]}]
            )
            
            # Get running instances
            running = ec2.describe_instances(
                Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
            )
            
            ri_count = sum(ri["InstanceCount"] for ri in reserved["ReservedInstances"])
            running_count = sum(
                len(r["Instances"]) 
                for reservation in running["Reservations"] 
                for r in [reservation]
            )
            
            coverage = (ri_count / running_count * 100) if running_count > 0 else 0
            
            analysis = {
                "reserved_instances": ri_count,
                "running_instances": running_count,
                "coverage_percentage": round(coverage, 2),
                "uncovered_instances": max(0, running_count - ri_count),
                "recommendation": "Consider purchasing RIs" if coverage < 70 else "Good RI coverage"
            }
            
            return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
        
        elif name == "forecast_costs":
            ce = boto3.client("ce")
            
            end_date = datetime.utcnow().date() + timedelta(days=30)
            start_date = datetime.utcnow().date()
            
            filter_config = {}
            if arguments.get("service"):
                filter_config = {
                    "Dimensions": {
                        "Key": "SERVICE",
                        "Values": [arguments["service"]]
                    }
                }
            
            response = ce.get_cost_forecast(
                TimePeriod={
                    "Start": str(start_date),
                    "End": str(end_date)
                },
                Metric="UNBLENDED_COST",
                Granularity="MONTHLY",
                Filter=filter_config if filter_config else None
            )
            
            forecast = {
                "period": f"{start_date} to {end_date}",
                "forecasted_cost": round(float(response["Total"]["Amount"]), 2),
                "currency": "USD"
            }
            
            if arguments.get("service"):
                forecast["service"] = arguments["service"]
            
            return [TextContent(type="text", text=json.dumps(forecast, indent=2))]
        
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
