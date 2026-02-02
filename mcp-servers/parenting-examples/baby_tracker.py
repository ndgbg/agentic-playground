#!/usr/bin/env python3
"""
Baby Tracker MCP Server
Track feedings, diapers, sleep, and milestones for your newborn.
"""

from datetime import datetime, timedelta
import json

class BabyTrackerServer:
    def __init__(self):
        self.name = "baby-tracker"
        self.tools = {}
        self.data = {
            "feedings": [],
            "diapers": [],
            "sleep": [],
            "milestones": []
        }
    
    def register_tool(self, name, description, handler, schema):
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "inputSchema": schema
        }
    
    def call_tool(self, name, arguments):
        if name not in self.tools:
            return {"error": f"Unknown tool: {name}"}
        return self.tools[name]["handler"](arguments)

server = BabyTrackerServer()

# Tool handlers
def log_feeding(args):
    entry = {
        "time": datetime.now().isoformat(),
        "type": args["type"],
        "amount": args.get("amount", "N/A"),
        "duration": args.get("duration", "N/A"),
        "side": args.get("side", "N/A")
    }
    server.data["feedings"].append(entry)
    return {"result": "logged", "text": f"✓ Logged {args['type']} feeding at {datetime.now().strftime('%I:%M %p')}"}

def log_diaper(args):
    entry = {
        "time": datetime.now().isoformat(),
        "type": args["type"]
    }
    server.data["diapers"].append(entry)
    return {"result": "logged", "text": f"✓ Logged {args['type']} diaper at {datetime.now().strftime('%I:%M %p')}"}

def log_sleep(args):
    entry = {
        "start": args["start"],
        "end": args.get("end", "ongoing"),
        "duration": args.get("duration", "calculating...")
    }
    server.data["sleep"].append(entry)
    return {"result": "logged", "text": f"✓ Logged sleep session"}

def get_last_feeding(args):
    if not server.data["feedings"]:
        return {"result": None, "text": "No feedings logged yet"}
    
    last = server.data["feedings"][-1]
    time_ago = datetime.now() - datetime.fromisoformat(last["time"])
    hours = int(time_ago.total_seconds() // 3600)
    minutes = int((time_ago.total_seconds() % 3600) // 60)
    
    return {
        "result": last,
        "text": f"Last feeding: {last['type']} {hours}h {minutes}m ago"
    }

def get_daily_summary(args):
    today = datetime.now().date()
    
    feedings_today = [f for f in server.data["feedings"] 
                      if datetime.fromisoformat(f["time"]).date() == today]
    diapers_today = [d for d in server.data["diapers"] 
                     if datetime.fromisoformat(d["time"]).date() == today]
    
    summary = f"""Daily Summary for {today}:
    
Feedings: {len(feedings_today)}
Diapers: {len(diapers_today)} ({sum(1 for d in diapers_today if 'wet' in d['type'])} wet, {sum(1 for d in diapers_today if 'dirty' in d['type'])} dirty)

Last feeding: {get_last_feeding({})['text']}
"""
    
    return {"result": {"feedings": len(feedings_today), "diapers": len(diapers_today)}, "text": summary}

def next_feeding_time(args):
    if not server.data["feedings"]:
        return {"result": None, "text": "No feedings logged yet"}
    
    last = server.data["feedings"][-1]
    last_time = datetime.fromisoformat(last["time"])
    interval = timedelta(hours=args.get("interval", 3))
    next_time = last_time + interval
    
    time_until = next_time - datetime.now()
    if time_until.total_seconds() < 0:
        return {"result": "overdue", "text": f"⚠️ Feeding overdue by {abs(int(time_until.total_seconds() // 60))} minutes"}
    
    hours = int(time_until.total_seconds() // 3600)
    minutes = int((time_until.total_seconds() % 3600) // 60)
    
    return {
        "result": next_time.isoformat(),
        "text": f"Next feeding in {hours}h {minutes}m (around {next_time.strftime('%I:%M %p')})"
    }

# Register tools
server.register_tool(
    "log_feeding",
    "Log a feeding session",
    log_feeding,
    {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["breast", "bottle", "formula"], "description": "Type of feeding"},
            "amount": {"type": "string", "description": "Amount (e.g., '4oz')"},
            "duration": {"type": "string", "description": "Duration (e.g., '15min')"},
            "side": {"type": "string", "enum": ["left", "right", "both"], "description": "For breastfeeding"}
        },
        "required": ["type"]
    }
)

server.register_tool(
    "log_diaper",
    "Log a diaper change",
    log_diaper,
    {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": ["wet", "dirty", "both"], "description": "Type of diaper"}
        },
        "required": ["type"]
    }
)

server.register_tool(
    "get_last_feeding",
    "Get time since last feeding",
    get_last_feeding,
    {"type": "object", "properties": {}}
)

server.register_tool(
    "get_daily_summary",
    "Get today's feeding and diaper summary",
    get_daily_summary,
    {"type": "object", "properties": {}}
)

server.register_tool(
    "next_feeding_time",
    "Calculate when next feeding is due",
    next_feeding_time,
    {
        "type": "object",
        "properties": {
            "interval": {"type": "number", "description": "Hours between feedings (default: 3)"}
        }
    }
)

def main():
    print("🍼 Baby Tracker MCP Server")
    print("=" * 50)
    
    # Simulate a day
    print("\nSimulating a typical day...\n")
    
    # Morning feeding
    result = server.call_tool("log_feeding", {"type": "breast", "duration": "20min", "side": "left"})
    print(result["text"])
    
    # Diaper change
    result = server.call_tool("log_diaper", {"type": "wet"})
    print(result["text"])
    
    # Another feeding
    result = server.call_tool("log_feeding", {"type": "bottle", "amount": "4oz"})
    print(result["text"])
    
    # More diapers
    result = server.call_tool("log_diaper", {"type": "dirty"})
    print(result["text"])
    result = server.call_tool("log_diaper", {"type": "both"})
    print(result["text"])
    
    print("\n" + "-" * 50)
    
    # Check last feeding
    result = server.call_tool("get_last_feeding", {})
    print(f"\n{result['text']}")
    
    # Next feeding time
    result = server.call_tool("next_feeding_time", {"interval": 3})
    print(result["text"])
    
    # Daily summary
    result = server.call_tool("get_daily_summary", {})
    print(f"\n{result['text']}")

if __name__ == "__main__":
    main()
