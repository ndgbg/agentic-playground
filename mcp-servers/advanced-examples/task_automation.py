#!/usr/bin/env python3
"""
Task Automation Engine MCP Server
Workflow automation with conditions, scheduling, and integrations.
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import hashlib

class TaskAutomationServer:
    def __init__(self, db_path: str = "automation.db"):
        self.name = "task-automation"
        self.db_path = db_path
        self.tools = {}
        self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS workflows
                     (id TEXT PRIMARY KEY,
                      name TEXT,
                      description TEXT,
                      trigger_type TEXT,
                      trigger_config TEXT,
                      steps TEXT,
                      enabled INTEGER,
                      created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS executions
                     (id TEXT PRIMARY KEY,
                      workflow_id TEXT,
                      status TEXT,
                      started_at TEXT,
                      completed_at TEXT,
                      result TEXT,
                      error TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS variables
                     (key TEXT PRIMARY KEY,
                      value TEXT,
                      updated_at TEXT)''')
        
        conn.commit()
        conn.close()
    
    def register_tool(self, name: str, description: str, handler, schema: dict):
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "inputSchema": schema
        }
    
    def call_tool(self, name: str, arguments: dict):
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        return self.tools[name]["handler"](arguments)
    
    def create_workflow(self, args: dict) -> dict:
        """Create a new workflow."""
        workflow_id = hashlib.md5(args["name"].encode()).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT OR REPLACE INTO workflows
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (workflow_id, args["name"], args.get("description", ""),
                   args["trigger_type"], json.dumps(args.get("trigger_config", {})),
                   json.dumps(args["steps"]), 1, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "workflow_id": workflow_id,
            "name": args["name"],
            "steps": len(args["steps"]),
            "message": "Workflow created successfully"
        }
    
    def execute_workflow(self, args: dict) -> dict:
        """Execute a workflow."""
        workflow_id = args["workflow_id"]
        context = args.get("context", {})
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get workflow
        c.execute('SELECT name, steps FROM workflows WHERE id = ? AND enabled = 1',
                  (workflow_id,))
        row = c.fetchone()
        
        if not row:
            conn.close()
            return {"error": "Workflow not found or disabled"}
        
        name, steps_json = row
        steps = json.loads(steps_json)
        
        # Create execution record
        exec_id = hashlib.md5(f"{workflow_id}{datetime.now()}".encode()).hexdigest()
        started = datetime.now().isoformat()
        
        c.execute('''INSERT INTO executions
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (exec_id, workflow_id, "running", started, None, None, None))
        conn.commit()
        
        # Execute steps
        results = []
        try:
            for i, step in enumerate(steps):
                step_result = self._execute_step(step, context)
                results.append({
                    "step": i + 1,
                    "action": step["action"],
                    "result": step_result
                })
                
                # Update context with step output
                if "output_var" in step:
                    context[step["output_var"]] = step_result
                
                # Check conditions
                if not self._check_condition(step.get("condition"), context):
                    break
            
            # Update execution as completed
            completed = datetime.now().isoformat()
            c.execute('''UPDATE executions
                         SET status = ?, completed_at = ?, result = ?
                         WHERE id = ?''',
                      ("completed", completed, json.dumps(results), exec_id))
            conn.commit()
            
            return {
                "execution_id": exec_id,
                "workflow": name,
                "status": "completed",
                "steps_executed": len(results),
                "results": results
            }
        
        except Exception as e:
            # Update execution as failed
            c.execute('''UPDATE executions
                         SET status = ?, completed_at = ?, error = ?
                         WHERE id = ?''',
                      ("failed", datetime.now().isoformat(), str(e), exec_id))
            conn.commit()
            
            return {
                "execution_id": exec_id,
                "status": "failed",
                "error": str(e),
                "steps_executed": len(results)
            }
        
        finally:
            conn.close()
    
    def _execute_step(self, step: dict, context: dict) -> Any:
        """Execute a single workflow step."""
        action = step["action"]
        params = step.get("params", {})
        
        # Replace variables in params
        params = self._replace_variables(params, context)
        
        if action == "http_request":
            return self._http_request(params)
        elif action == "set_variable":
            return self._set_variable(params)
        elif action == "get_variable":
            return self._get_variable(params)
        elif action == "delay":
            return self._delay(params)
        elif action == "log":
            return self._log(params)
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _check_condition(self, condition: dict, context: dict) -> bool:
        """Check if condition is met."""
        if not condition:
            return True
        
        var = condition.get("variable")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if var not in context:
            return False
        
        ctx_value = context[var]
        
        if operator == "equals":
            return ctx_value == value
        elif operator == "not_equals":
            return ctx_value != value
        elif operator == "greater_than":
            return ctx_value > value
        elif operator == "less_than":
            return ctx_value < value
        elif operator == "contains":
            return value in str(ctx_value)
        
        return True
    
    def _replace_variables(self, params: dict, context: dict) -> dict:
        """Replace {{variable}} placeholders with context values."""
        result = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                var_name = value[2:-2]
                result[key] = context.get(var_name, value)
            else:
                result[key] = value
        return result
    
    def _http_request(self, params: dict) -> dict:
        """Simulate HTTP request."""
        return {
            "status": 200,
            "url": params.get("url"),
            "method": params.get("method", "GET"),
            "simulated": True
        }
    
    def _set_variable(self, params: dict) -> dict:
        """Set a variable."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT OR REPLACE INTO variables
                     VALUES (?, ?, ?)''',
                  (params["key"], json.dumps(params["value"]),
                   datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {"key": params["key"], "value": params["value"]}
    
    def _get_variable(self, params: dict) -> Any:
        """Get a variable."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT value FROM variables WHERE key = ?', (params["key"],))
        row = c.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def _delay(self, params: dict) -> dict:
        """Simulate delay."""
        return {"delayed": params.get("seconds", 1)}
    
    def _log(self, params: dict) -> dict:
        """Log a message."""
        print(f"[LOG] {params.get('message', '')}")
        return {"logged": params.get("message")}
    
    def list_workflows(self, args: dict) -> dict:
        """List all workflows."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT id, name, description, trigger_type, enabled
                     FROM workflows''')
        
        workflows = []
        for row in c.fetchall():
            workflows.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "trigger": row[3],
                "enabled": bool(row[4])
            })
        
        conn.close()
        
        return {"workflows": workflows, "count": len(workflows)}
    
    def get_execution_history(self, args: dict) -> dict:
        """Get execution history."""
        workflow_id = args.get("workflow_id")
        limit = args.get("limit", 10)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if workflow_id:
            c.execute('''SELECT id, status, started_at, completed_at
                         FROM executions
                         WHERE workflow_id = ?
                         ORDER BY started_at DESC
                         LIMIT ?''', (workflow_id, limit))
        else:
            c.execute('''SELECT id, workflow_id, status, started_at, completed_at
                         FROM executions
                         ORDER BY started_at DESC
                         LIMIT ?''', (limit,))
        
        executions = []
        for row in c.fetchall():
            executions.append({
                "id": row[0],
                "workflow_id": row[1] if not workflow_id else workflow_id,
                "status": row[2 if workflow_id else 2],
                "started_at": row[3 if workflow_id else 3],
                "completed_at": row[4 if workflow_id else 4]
            })
        
        conn.close()
        
        return {"executions": executions, "count": len(executions)}

# Initialize server
server = TaskAutomationServer()

# Register tools
server.register_tool(
    "create_workflow",
    "Create a new automation workflow",
    server.create_workflow,
    {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "description": {"type": "string"},
            "trigger_type": {"type": "string", "enum": ["manual", "schedule", "webhook"]},
            "trigger_config": {"type": "object"},
            "steps": {"type": "array"}
        },
        "required": ["name", "trigger_type", "steps"]
    }
)

server.register_tool(
    "execute_workflow",
    "Execute a workflow",
    server.execute_workflow,
    {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string"},
            "context": {"type": "object"}
        },
        "required": ["workflow_id"]
    }
)

server.register_tool(
    "list_workflows",
    "List all workflows",
    server.list_workflows,
    {"type": "object", "properties": {}}
)

server.register_tool(
    "get_execution_history",
    "Get workflow execution history",
    server.get_execution_history,
    {
        "type": "object",
        "properties": {
            "workflow_id": {"type": "string"},
            "limit": {"type": "integer"}
        }
    }
)

def main():
    print("⚙️  Task Automation Engine")
    print("=" * 60)
    
    # Create workflow
    print("\n1. Creating workflow...")
    result = server.call_tool("create_workflow", {
        "name": "Daily Report Generator",
        "description": "Generate and send daily reports",
        "trigger_type": "schedule",
        "trigger_config": {"cron": "0 9 * * *"},
        "steps": [
            {
                "action": "log",
                "params": {"message": "Starting daily report generation"}
            },
            {
                "action": "set_variable",
                "params": {"key": "report_date", "value": "2026-02-02"},
                "output_var": "date_set"
            },
            {
                "action": "http_request",
                "params": {"url": "https://api.example.com/data", "method": "GET"},
                "output_var": "api_response"
            },
            {
                "action": "log",
                "params": {"message": "Report generated successfully"}
            }
        ]
    })
    print(f"✓ Created workflow: {result['name']} ({result['steps']} steps)")
    workflow_id = result['workflow_id']
    
    print("\n" + "-" * 60)
    
    # Execute workflow
    print("\n2. Executing workflow...")
    result = server.call_tool("execute_workflow", {
        "workflow_id": workflow_id,
        "context": {"user": "admin"}
    })
    print(f"Status: {result['status']}")
    print(f"Steps executed: {result['steps_executed']}")
    for step in result.get('results', []):
        print(f"  Step {step['step']}: {step['action']} → {step['result']}")
    
    print("\n" + "-" * 60)
    
    # List workflows
    print("\n3. All workflows...")
    result = server.call_tool("list_workflows", {})
    print(f"Total workflows: {result['count']}")
    for wf in result['workflows']:
        print(f"  • {wf['name']} ({wf['trigger']}) - {'Enabled' if wf['enabled'] else 'Disabled'}")
    
    print("\n" + "-" * 60)
    
    # Execution history
    print("\n4. Execution history...")
    result = server.call_tool("get_execution_history", {"limit": 5})
    print(f"Recent executions: {result['count']}")
    for exec in result['executions']:
        print(f"  • {exec['id'][:8]}... - {exec['status']} at {exec['started_at']}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
