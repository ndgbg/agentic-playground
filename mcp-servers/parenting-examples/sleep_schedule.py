#!/usr/bin/env python3
"""
Sleep Schedule Helper MCP Server
Helps track and optimize baby's sleep schedule.
"""

from datetime import datetime, timedelta
import json

class SleepScheduleServer:
    def __init__(self):
        self.name = "sleep-schedule"
        self.tools = {}
        self.sleep_log = []
    
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

server = SleepScheduleServer()

def calculate_wake_windows(args):
    age_weeks = args["age_weeks"]
    
    if age_weeks < 4:
        window = "45-60 minutes"
        naps = "4-5 naps"
    elif age_weeks < 12:
        window = "60-90 minutes"
        naps = "4 naps"
    elif age_weeks < 16:
        window = "90-120 minutes"
        naps = "3-4 naps"
    else:
        window = "2-3 hours"
        naps = "3 naps"
    
    return {
        "result": {"window": window, "naps": naps},
        "text": f"Age {age_weeks} weeks:\n  Wake window: {window}\n  Expected naps: {naps}"
    }

def suggest_bedtime(args):
    last_nap_end = args["last_nap_end"]
    age_weeks = args.get("age_weeks", 8)
    
    # Parse time
    last_nap = datetime.strptime(last_nap_end, "%H:%M")
    
    # Calculate wake window
    if age_weeks < 12:
        wake_window = timedelta(hours=1.5)
    else:
        wake_window = timedelta(hours=2)
    
    bedtime = last_nap + wake_window
    
    return {
        "result": bedtime.strftime("%H:%M"),
        "text": f"Suggested bedtime: {bedtime.strftime('%I:%M %p')}\n  (Based on last nap ending at {last_nap.strftime('%I:%M %p')})"
    }

def log_sleep_session(args):
    entry = {
        "start": args["start"],
        "end": args.get("end"),
        "type": args.get("type", "nap")
    }
    
    if entry["end"]:
        start = datetime.strptime(entry["start"], "%H:%M")
        end = datetime.strptime(entry["end"], "%H:%M")
        duration = (end - start).total_seconds() / 60
        entry["duration_minutes"] = int(duration)
    
    server.sleep_log.append(entry)
    
    if entry.get("duration_minutes"):
        return {
            "result": entry,
            "text": f"✓ Logged {entry['type']}: {entry['duration_minutes']} minutes"
        }
    else:
        return {
            "result": entry,
            "text": f"✓ Started {entry['type']} at {entry['start']}"
        }

def total_sleep_today(args):
    total_minutes = sum(s.get("duration_minutes", 0) for s in server.sleep_log)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    
    naps = len([s for s in server.sleep_log if s.get("type") == "nap"])
    
    return {
        "result": {"hours": hours, "minutes": minutes, "naps": naps},
        "text": f"Total sleep today: {hours}h {minutes}m ({naps} naps)"
    }

def sleep_regression_check(args):
    age_weeks = args["age_weeks"]
    
    regressions = [4, 8, 12, 18, 24]
    regression_weeks = [r * 4 for r in regressions]
    
    closest = min(regression_weeks, key=lambda x: abs(x - age_weeks))
    
    if abs(closest - age_weeks) <= 2:
        month = closest // 4
        return {
            "result": True,
            "text": f"⚠️ Possible {month}-month sleep regression\n  This is normal and temporary!\n  Tips: Stick to routine, offer extra comfort"
        }
    else:
        return {
            "result": False,
            "text": f"✓ Not in a typical regression period\n  Next regression around {(closest // 4)} months"
        }

# Register tools
server.register_tool(
    "calculate_wake_windows",
    "Get appropriate wake windows for baby's age",
    calculate_wake_windows,
    {
        "type": "object",
        "properties": {
            "age_weeks": {"type": "integer", "description": "Baby's age in weeks"}
        },
        "required": ["age_weeks"]
    }
)

server.register_tool(
    "suggest_bedtime",
    "Suggest bedtime based on last nap",
    suggest_bedtime,
    {
        "type": "object",
        "properties": {
            "last_nap_end": {"type": "string", "description": "Time last nap ended (HH:MM)"},
            "age_weeks": {"type": "integer", "description": "Baby's age in weeks"}
        },
        "required": ["last_nap_end"]
    }
)

server.register_tool(
    "log_sleep_session",
    "Log a sleep session",
    log_sleep_session,
    {
        "type": "object",
        "properties": {
            "start": {"type": "string", "description": "Start time (HH:MM)"},
            "end": {"type": "string", "description": "End time (HH:MM)"},
            "type": {"type": "string", "enum": ["nap", "night"], "description": "Type of sleep"}
        },
        "required": ["start"]
    }
)

server.register_tool(
    "total_sleep_today",
    "Calculate total sleep for today",
    total_sleep_today,
    {"type": "object", "properties": {}}
)

server.register_tool(
    "sleep_regression_check",
    "Check if baby is in a sleep regression period",
    sleep_regression_check,
    {
        "type": "object",
        "properties": {
            "age_weeks": {"type": "integer", "description": "Baby's age in weeks"}
        },
        "required": ["age_weeks"]
    }
)

def main():
    print("😴 Sleep Schedule Helper")
    print("=" * 50)
    
    # Example: 8-week-old baby
    print("\nExample: 8-week-old baby\n")
    
    result = server.call_tool("calculate_wake_windows", {"age_weeks": 8})
    print(result["text"])
    
    print("\n" + "-" * 50)
    
    # Log some naps
    print("\nLogging naps...\n")
    server.call_tool("log_sleep_session", {"start": "09:00", "end": "10:30", "type": "nap"})
    server.call_tool("log_sleep_session", {"start": "12:00", "end": "13:45", "type": "nap"})
    server.call_tool("log_sleep_session", {"start": "15:30", "end": "16:15", "type": "nap"})
    
    result = server.call_tool("total_sleep_today", {})
    print(result["text"])
    
    print("\n" + "-" * 50)
    
    result = server.call_tool("suggest_bedtime", {"last_nap_end": "16:15", "age_weeks": 8})
    print(f"\n{result['text']}")
    
    print("\n" + "-" * 50)
    
    result = server.call_tool("sleep_regression_check", {"age_weeks": 16})
    print(f"\n{result['text']}")

if __name__ == "__main__":
    main()
