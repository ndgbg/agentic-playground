#!/usr/bin/env python3
"""
AWS CloudWatch Insights MCP Server
Query and analyze CloudWatch logs and metrics for troubleshooting and monitoring.
"""

import asyncio
import json
from typing import Any
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.types import Tool, TextContent
import boto3
from botocore.exceptions import ClientError
import time

server = Server("aws-cloudwatch-insights")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available CloudWatch tools."""
    return [
        Tool(
            name="query_logs",
            description="Run CloudWatch Insights query on log groups",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_group": {"type": "string", "description": "Log group name"},
                    "query": {"type": "string", "description": "CloudWatch Insights query"},
                    "hours": {"type": "integer", "description": "Hours to look back (default: 1)"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["log_group", "query"]
            }
        ),
        Tool(
            name="get_error_logs",
            description="Find error logs in a log group",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_group": {"type": "string", "description": "Log group name"},
                    "error_pattern": {"type": "string", "description": "Error pattern to search (default: ERROR)"},
                    "hours": {"type": "integer", "description": "Hours to look back"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["log_group"]
            }
        ),
        Tool(
            name="get_metric_statistics",
            description="Get statistics for a CloudWatch metric",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "description": "Metric namespace (e.g., AWS/EC2)"},
                    "metric_name": {"type": "string", "description": "Metric name"},
                    "dimensions": {"type": "object", "description": "Metric dimensions"},
                    "statistic": {"type": "string", "enum": ["Average", "Sum", "Maximum", "Minimum"], "description": "Statistic type"},
                    "hours": {"type": "integer", "description": "Hours to look back"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["namespace", "metric_name"]
            }
        ),
        Tool(
            name="analyze_lambda_errors",
            description="Analyze Lambda function errors and performance",
            inputSchema={
                "type": "object",
                "properties": {
                    "function_name": {"type": "string", "description": "Lambda function name"},
                    "hours": {"type": "integer", "description": "Hours to analyze"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["function_name"]
            }
        ),
        Tool(
            name="get_api_gateway_metrics",
            description="Get API Gateway performance metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "api_id": {"type": "string", "description": "API Gateway ID"},
                    "stage": {"type": "string", "description": "API stage name"},
                    "hours": {"type": "integer", "description": "Hours to analyze"},
                    "region": {"type": "string", "description": "AWS region"}
                },
                "required": ["api_id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute CloudWatch tools."""
    
    try:
        if name == "query_logs":
            region = arguments.get("region", "us-east-1")
            logs = boto3.client("logs", region_name=region)
            
            hours = arguments.get("hours", 1)
            end_time = int(datetime.utcnow().timestamp())
            start_time = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())
            
            # Start query
            response = logs.start_query(
                logGroupName=arguments["log_group"],
                startTime=start_time,
                endTime=end_time,
                queryString=arguments["query"]
            )
            
            query_id = response["queryId"]
            
            # Poll for results
            max_attempts = 30
            for _ in range(max_attempts):
                result = logs.get_query_results(queryId=query_id)
                status = result["status"]
                
                if status == "Complete":
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "results": result["results"],
                            "statistics": result.get("statistics", {}),
                            "status": status
                        }, indent=2)
                    )]
                elif status == "Failed":
                    return [TextContent(
                        type="text",
                        text=f"Query failed: {result.get('status', 'Unknown error')}"
                    )]
                
                await asyncio.sleep(1)
            
            return [TextContent(type="text", text="Query timeout - results may be incomplete")]
        
        elif name == "get_error_logs":
            region = arguments.get("region", "us-east-1")
            logs = boto3.client("logs", region_name=region)
            
            hours = arguments.get("hours", 1)
            error_pattern = arguments.get("error_pattern", "ERROR")
            
            query = f"""
            fields @timestamp, @message
            | filter @message like /{error_pattern}/
            | sort @timestamp desc
            | limit 100
            """
            
            end_time = int(datetime.utcnow().timestamp())
            start_time = int((datetime.utcnow() - timedelta(hours=hours)).timestamp())
            
            response = logs.start_query(
                logGroupName=arguments["log_group"],
                startTime=start_time,
                endTime=end_time,
                queryString=query
            )
            
            query_id = response["queryId"]
            
            # Poll for results
            for _ in range(30):
                result = logs.get_query_results(queryId=query_id)
                if result["status"] == "Complete":
                    errors = []
                    for record in result["results"]:
                        error_entry = {}
                        for field in record:
                            error_entry[field["field"]] = field["value"]
                        errors.append(error_entry)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "errors": errors,
                            "count": len(errors),
                            "pattern": error_pattern
                        }, indent=2)
                    )]
                
                await asyncio.sleep(1)
            
            return [TextContent(type="text", text="Query timeout")]
        
        elif name == "get_metric_statistics":
            region = arguments.get("region", "us-east-1")
            cloudwatch = boto3.client("cloudwatch", region_name=region)
            
            hours = arguments.get("hours", 1)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            dimensions = [
                {"Name": k, "Value": v} 
                for k, v in arguments.get("dimensions", {}).items()
            ]
            
            statistic = arguments.get("statistic", "Average")
            
            response = cloudwatch.get_metric_statistics(
                Namespace=arguments["namespace"],
                MetricName=arguments["metric_name"],
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=[statistic]
            )
            
            datapoints = sorted(response["Datapoints"], key=lambda x: x["Timestamp"])
            
            if datapoints:
                values = [dp[statistic] for dp in datapoints]
                summary = {
                    "metric": arguments["metric_name"],
                    "namespace": arguments["namespace"],
                    "statistic": statistic,
                    "datapoints": len(datapoints),
                    "latest_value": values[-1] if values else None,
                    "average": sum(values) / len(values) if values else None,
                    "max": max(values) if values else None,
                    "min": min(values) if values else None,
                    "data": [
                        {
                            "timestamp": str(dp["Timestamp"]),
                            "value": dp[statistic]
                        }
                        for dp in datapoints
                    ]
                }
            else:
                summary = {"message": "No datapoints found"}
            
            return [TextContent(type="text", text=json.dumps(summary, indent=2))]
        
        elif name == "analyze_lambda_errors":
            region = arguments.get("region", "us-east-1")
            cloudwatch = boto3.client("cloudwatch", region_name=region)
            logs = boto3.client("logs", region_name=region)
            
            function_name = arguments["function_name"]
            hours = arguments.get("hours", 24)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Get error metrics
            errors = cloudwatch.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName="Errors",
                Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Sum"]
            )
            
            # Get invocation count
            invocations = cloudwatch.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName="Invocations",
                Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Sum"]
            )
            
            # Get duration
            duration = cloudwatch.get_metric_statistics(
                Namespace="AWS/Lambda",
                MetricName="Duration",
                Dimensions=[{"Name": "FunctionName", "Value": function_name}],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=["Average", "Maximum"]
            )
            
            total_errors = sum(dp["Sum"] for dp in errors["Datapoints"])
            total_invocations = sum(dp["Sum"] for dp in invocations["Datapoints"])
            error_rate = (total_errors / total_invocations * 100) if total_invocations > 0 else 0
            
            avg_duration = sum(dp["Average"] for dp in duration["Datapoints"]) / len(duration["Datapoints"]) if duration["Datapoints"] else 0
            max_duration = max((dp["Maximum"] for dp in duration["Datapoints"]), default=0)
            
            analysis = {
                "function": function_name,
                "period_hours": hours,
                "total_invocations": int(total_invocations),
                "total_errors": int(total_errors),
                "error_rate_percent": round(error_rate, 2),
                "avg_duration_ms": round(avg_duration, 2),
                "max_duration_ms": round(max_duration, 2)
            }
            
            return [TextContent(type="text", text=json.dumps(analysis, indent=2))]
        
        elif name == "get_api_gateway_metrics":
            region = arguments.get("region", "us-east-1")
            cloudwatch = boto3.client("cloudwatch", region_name=region)
            
            api_id = arguments["api_id"]
            stage = arguments.get("stage", "prod")
            hours = arguments.get("hours", 1)
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            dimensions = [
                {"Name": "ApiId", "Value": api_id},
                {"Name": "Stage", "Value": stage}
            ]
            
            # Get request count
            count = cloudwatch.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="Count",
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=["Sum"]
            )
            
            # Get 4XX errors
            errors_4xx = cloudwatch.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="4XXError",
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=["Sum"]
            )
            
            # Get 5XX errors
            errors_5xx = cloudwatch.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="5XXError",
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=["Sum"]
            )
            
            # Get latency
            latency = cloudwatch.get_metric_statistics(
                Namespace="AWS/ApiGateway",
                MetricName="Latency",
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=["Average", "Maximum"]
            )
            
            total_requests = sum(dp["Sum"] for dp in count["Datapoints"])
            total_4xx = sum(dp["Sum"] for dp in errors_4xx["Datapoints"])
            total_5xx = sum(dp["Sum"] for dp in errors_5xx["Datapoints"])
            
            avg_latency = sum(dp["Average"] for dp in latency["Datapoints"]) / len(latency["Datapoints"]) if latency["Datapoints"] else 0
            max_latency = max((dp["Maximum"] for dp in latency["Datapoints"]), default=0)
            
            metrics = {
                "api_id": api_id,
                "stage": stage,
                "period_hours": hours,
                "total_requests": int(total_requests),
                "4xx_errors": int(total_4xx),
                "5xx_errors": int(total_5xx),
                "error_rate_percent": round((total_4xx + total_5xx) / total_requests * 100, 2) if total_requests > 0 else 0,
                "avg_latency_ms": round(avg_latency, 2),
                "max_latency_ms": round(max_latency, 2)
            }
            
            return [TextContent(type="text", text=json.dumps(metrics, indent=2))]
        
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
