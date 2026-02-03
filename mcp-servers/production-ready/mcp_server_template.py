#!/usr/bin/env python3
"""
Production-Ready MCP Server Template
Full stdio protocol implementation with logging, monitoring, and error handling.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Tool:
    name: str
    description: str
    inputSchema: dict

@dataclass
class Resource:
    uri: str
    name: str
    description: str
    mimeType: str

class ProductionMCPServer:
    """Production-ready MCP server with full protocol support."""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.tools = {}
        self.resources = {}
        self.prompts = {}
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        logger.info(f"Initializing {name} v{version}")
    
    def register_tool(self, name: str, description: str, handler, schema: dict):
        """Register a tool with the server."""
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "inputSchema": schema
        }
        logger.info(f"Registered tool: {name}")
    
    def register_resource(self, uri: str, name: str, description: str, 
                         mime_type: str, handler):
        """Register a resource provider."""
        self.resources[uri] = {
            "uri": uri,
            "name": name,
            "description": description,
            "mimeType": mime_type,
            "handler": handler
        }
        logger.info(f"Registered resource: {uri}")
    
    async def handle_initialize(self, params: dict) -> dict:
        """Handle initialize request."""
        logger.info(f"Initialize request from client: {params.get('clientInfo', {})}")
        
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": self.name,
                "version": self.version
            },
            "capabilities": {
                "tools": {"listChanged": True} if self.tools else {},
                "resources": {"subscribe": True, "listChanged": True} if self.resources else {},
                "prompts": {"listChanged": True} if self.prompts else {},
                "logging": {}
            }
        }
    
    async def handle_tools_list(self) -> dict:
        """List available tools."""
        tools = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "inputSchema": tool["inputSchema"]
            }
            for tool in self.tools.values()
        ]
        
        logger.info(f"Listed {len(tools)} tools")
        return {"tools": tools}
    
    async def handle_tools_call(self, params: dict) -> dict:
        """Execute a tool."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        logger.info(f"Tool call: {tool_name} with args: {arguments}")
        
        if tool_name not in self.tools:
            error_msg = f"Unknown tool: {tool_name}"
            logger.error(error_msg)
            self.error_count += 1
            raise ValueError(error_msg)
        
        try:
            tool = self.tools[tool_name]
            result = await tool["handler"](arguments)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}", exc_info=True)
            self.error_count += 1
            raise
    
    async def handle_resources_list(self) -> dict:
        """List available resources."""
        resources = [
            {
                "uri": res["uri"],
                "name": res["name"],
                "description": res["description"],
                "mimeType": res["mimeType"]
            }
            for res in self.resources.values()
        ]
        
        logger.info(f"Listed {len(resources)} resources")
        return {"resources": resources}
    
    async def handle_resources_read(self, params: dict) -> dict:
        """Read a resource."""
        uri = params.get("uri")
        
        logger.info(f"Resource read: {uri}")
        
        if uri not in self.resources:
            error_msg = f"Unknown resource: {uri}"
            logger.error(error_msg)
            self.error_count += 1
            raise ValueError(error_msg)
        
        try:
            resource = self.resources[uri]
            content = await resource["handler"]()
            
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": resource["mimeType"],
                        "text": content
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Resource read error: {e}", exc_info=True)
            self.error_count += 1
            raise
    
    async def handle_request(self, request: dict) -> dict:
        """Handle incoming JSON-RPC request."""
        self.request_count += 1
        
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.debug(f"Request {request_id}: {method}")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list()
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list()
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            elif method == "ping":
                result = {}
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        
        except Exception as e:
            logger.error(f"Request error: {e}", exc_info=True)
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    async def run_stdio(self):
        """Run server using stdio transport."""
        logger.info(f"Starting {self.name} stdio server")
        
        try:
            while True:
                # Read request from stdin
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    logger.info("EOF received, shutting down")
                    break
                
                try:
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    
                    # Write response to stdout
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue
        
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        
        finally:
            uptime = (datetime.now() - self.start_time).total_seconds()
            logger.info(f"Server shutdown. Uptime: {uptime:.1f}s, "
                       f"Requests: {self.request_count}, Errors: {self.error_count}")
    
    def get_stats(self) -> dict:
        """Get server statistics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "name": self.name,
            "version": self.version,
            "uptime_seconds": uptime,
            "requests": self.request_count,
            "errors": self.error_count,
            "tools": len(self.tools),
            "resources": len(self.resources)
        }

# Example usage
async def example_tool_handler(args: dict) -> dict:
    """Example tool that echoes input."""
    message = args.get("message", "Hello")
    return {
        "echo": message,
        "length": len(message),
        "timestamp": datetime.now().isoformat()
    }

async def example_resource_handler() -> str:
    """Example resource that returns server stats."""
    server = ProductionMCPServer("example", "1.0.0")
    stats = server.get_stats()
    return json.dumps(stats, indent=2)

async def main():
    """Main entry point."""
    server = ProductionMCPServer("production-example", "1.0.0")
    
    # Register example tool
    server.register_tool(
        "echo",
        "Echo a message with metadata",
        example_tool_handler,
        {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo"
                }
            },
            "required": ["message"]
        }
    )
    
    # Register example resource
    server.register_resource(
        "stats://server",
        "Server Statistics",
        "Current server statistics and metrics",
        "application/json",
        example_resource_handler
    )
    
    # Run server
    await server.run_stdio()

if __name__ == "__main__":
    asyncio.run(main())
