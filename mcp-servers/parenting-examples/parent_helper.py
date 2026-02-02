#!/usr/bin/env python3
"""
Quick Parent Helper MCP Server
Practical tools for exhausted parents: timers, conversions, quick answers.
"""

from datetime import datetime, timedelta
import json

class ParentHelperServer:
    def __init__(self):
        self.name = "parent-helper"
        self.tools = {}
    
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

server = ParentHelperServer()

def bottle_temp_check(args):
    temp_f = args["temp_fahrenheit"]
    
    if temp_f < 95:
        status = "❄️ Too cold"
        advice = "Warm it up a bit more"
    elif temp_f <= 100:
        status = "✓ Perfect"
        advice = "Good to go!"
    elif temp_f <= 105:
        status = "⚠️ Slightly warm"
        advice = "Let it cool for 30 seconds"
    else:
        status = "🔥 Too hot"
        advice = "Let it cool down - test on wrist"
    
    return {
        "result": status,
        "text": f"Bottle temp: {temp_f}°F\n  {status}\n  {advice}"
    }

def formula_calculator(args):
    weight_lbs = args["weight_lbs"]
    
    # Rule of thumb: 2.5 oz per pound per day
    daily_oz = weight_lbs * 2.5
    feedings_per_day = args.get("feedings_per_day", 8)
    oz_per_feeding = daily_oz / feedings_per_day
    
    return {
        "result": {"daily": daily_oz, "per_feeding": oz_per_feeding},
        "text": f"For {weight_lbs} lbs baby:\n  Daily: {daily_oz:.1f} oz\n  Per feeding ({feedings_per_day}x/day): {oz_per_feeding:.1f} oz"
    }

def crying_checklist(args):
    duration_min = args.get("duration_minutes", 0)
    
    checklist = [
        "🍼 Hungry? (Last feeding >2-3 hours ago?)",
        "💩 Diaper? (Check for wet/dirty)",
        "😴 Tired? (Awake >90 minutes?)",
        "🌡️ Temperature? (Too hot/cold?)",
        "🤗 Comfort? (Needs cuddles/rocking?)",
        "💨 Gas? (Try burping/bicycle legs)",
        "🤒 Sick? (Fever, unusual symptoms?)"
    ]
    
    if duration_min > 30:
        checklist.append("⚠️ Crying >30min - consider calling pediatrician")
    
    return {
        "result": checklist,
        "text": "Crying Checklist:\n" + "\n".join(f"  {item}" for item in checklist)
    }

def milestone_tracker(args):
    age_weeks = args["age_weeks"]
    
    milestones = {
        4: ["Lifts head during tummy time", "Follows objects with eyes", "Smiles"],
        8: ["Holds head steady", "Pushes up on arms", "Coos and babbles"],
        12: ["Rolls over", "Reaches for toys", "Laughs"],
        16: ["Sits with support", "Grabs objects", "Responds to name"],
        24: ["Sits without support", "Transfers objects", "Babbles chains"]
    }
    
    closest_week = min(milestones.keys(), key=lambda x: abs(x - age_weeks))
    current_milestones = milestones[closest_week]
    
    return {
        "result": current_milestones,
        "text": f"Milestones around {closest_week} weeks:\n" + "\n".join(f"  • {m}" for m in current_milestones)
    }

def emergency_check(args):
    symptoms = args["symptoms"].lower()
    
    emergency_signs = {
        "fever": "🚨 Fever in baby <3 months - Call doctor immediately",
        "breathing": "🚨 Difficulty breathing - Call 911",
        "blue": "🚨 Blue lips/face - Call 911",
        "unresponsive": "🚨 Unresponsive - Call 911",
        "seizure": "🚨 Seizure - Call 911",
        "dehydrated": "⚠️ No wet diapers in 6+ hours - Call doctor",
        "vomit": "⚠️ Persistent vomiting - Call doctor",
        "rash": "⚠️ Unusual rash - Call doctor if concerned"
    }
    
    alerts = []
    for key, message in emergency_signs.items():
        if key in symptoms:
            alerts.append(message)
    
    if not alerts:
        alerts.append("✓ No immediate red flags, but trust your instincts")
    
    return {
        "result": alerts,
        "text": "\n".join(alerts) + "\n\nWhen in doubt, always call your pediatrician!"
    }

def quick_conversion(args):
    value = args["value"]
    from_unit = args["from_unit"].lower()
    to_unit = args["to_unit"].lower()
    
    conversions = {
        ("oz", "ml"): lambda x: x * 29.5735,
        ("ml", "oz"): lambda x: x / 29.5735,
        ("lbs", "kg"): lambda x: x * 0.453592,
        ("kg", "lbs"): lambda x: x / 0.453592,
        ("f", "c"): lambda x: (x - 32) * 5/9,
        ("c", "f"): lambda x: x * 9/5 + 32
    }
    
    key = (from_unit, to_unit)
    if key in conversions:
        result = conversions[key](value)
        return {
            "result": result,
            "text": f"{value} {from_unit} = {result:.1f} {to_unit}"
        }
    else:
        return {"error": f"Conversion {from_unit} to {to_unit} not supported"}

# Register tools
server.register_tool("bottle_temp_check", "Check if bottle temperature is safe", bottle_temp_check,
    {"type": "object", "properties": {"temp_fahrenheit": {"type": "number"}}, "required": ["temp_fahrenheit"]})

server.register_tool("formula_calculator", "Calculate formula amounts", formula_calculator,
    {"type": "object", "properties": {"weight_lbs": {"type": "number"}, "feedings_per_day": {"type": "integer"}}, "required": ["weight_lbs"]})

server.register_tool("crying_checklist", "Get checklist for crying baby", crying_checklist,
    {"type": "object", "properties": {"duration_minutes": {"type": "integer"}}})

server.register_tool("milestone_tracker", "Check developmental milestones", milestone_tracker,
    {"type": "object", "properties": {"age_weeks": {"type": "integer"}}, "required": ["age_weeks"]})

server.register_tool("emergency_check", "Check if symptoms need immediate attention", emergency_check,
    {"type": "object", "properties": {"symptoms": {"type": "string"}}, "required": ["symptoms"]})

server.register_tool("quick_conversion", "Convert units (oz/ml, lbs/kg, F/C)", quick_conversion,
    {"type": "object", "properties": {"value": {"type": "number"}, "from_unit": {"type": "string"}, "to_unit": {"type": "string"}}, "required": ["value", "from_unit", "to_unit"]})

def main():
    print("👶 Quick Parent Helper")
    print("=" * 50)
    
    print("\n1. Bottle Temperature Check")
    result = server.call_tool("bottle_temp_check", {"temp_fahrenheit": 98})
    print(result["text"])
    
    print("\n" + "-" * 50)
    print("\n2. Formula Calculator")
    result = server.call_tool("formula_calculator", {"weight_lbs": 10, "feedings_per_day": 6})
    print(result["text"])
    
    print("\n" + "-" * 50)
    print("\n3. Crying Checklist")
    result = server.call_tool("crying_checklist", {"duration_minutes": 15})
    print(result["text"])
    
    print("\n" + "-" * 50)
    print("\n4. Milestone Tracker")
    result = server.call_tool("milestone_tracker", {"age_weeks": 12})
    print(result["text"])
    
    print("\n" + "-" * 50)
    print("\n5. Quick Conversion")
    result = server.call_tool("quick_conversion", {"value": 4, "from_unit": "oz", "to_unit": "ml"})
    print(result["text"])
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
