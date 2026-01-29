"""
Kiro Powers Demo - Conceptual Implementation

This demonstrates the Kiro Powers pattern: loading specialized expertise on-demand
rather than maintaining all knowledge in context simultaneously.

NOTE: This is an educational demo simulating the Kiro Powers concept.
Real AWS Kiro Powers is available at kiro.dev with actual tool integrations.
"""

from strands import Agent, tool
from typing import Dict, Optional
import json

# Simulated "Powers" - specialized knowledge modules
AVAILABLE_POWERS = {
    "stripe": {
        "name": "Stripe Payment Processing",
        "description": "Expert knowledge of Stripe API, webhooks, and payment flows",
        "capabilities": ["create_payment", "refund", "manage_subscriptions", "handle_webhooks"]
    },
    "figma": {
        "name": "Figma Design Integration",
        "description": "Expert knowledge of Figma API and design workflows",
        "capabilities": ["export_designs", "create_components", "manage_styles", "collaborate"]
    },
    "datadog": {
        "name": "Datadog Monitoring",
        "description": "Expert knowledge of Datadog metrics, logs, and APM",
        "capabilities": ["query_metrics", "create_dashboards", "set_alerts", "analyze_traces"]
    },
    "aws": {
        "name": "AWS Cloud Services",
        "description": "Expert knowledge of AWS services and infrastructure",
        "capabilities": ["deploy_lambda", "manage_s3", "configure_vpc", "setup_rds"]
    }
}

class KiroPowersAgent:
    """Agent with on-demand specialized capabilities"""
    
    def __init__(self):
        self.agent = Agent()
        self.active_powers = []
        self.base_tools = []
        
        # Add base tools
        self.agent.add_tool(self.list_available_powers)
        self.agent.add_tool(self.activate_power)
        self.agent.add_tool(self.deactivate_power)
        self.agent.add_tool(self.show_active_powers)
    
    @tool
    def list_available_powers(self) -> Dict:
        """List all available Kiro Powers that can be activated"""
        return {
            "available_powers": AVAILABLE_POWERS,
            "message": "Use activate_power(power_name) to load specialized expertise"
        }
    
    @tool
    def activate_power(self, power_name: str) -> str:
        """
        Activate a Kiro Power to gain specialized expertise.
        
        Args:
            power_name: Name of the power to activate (stripe, figma, datadog, aws)
        """
        if power_name not in AVAILABLE_POWERS:
            return f"❌ Power '{power_name}' not found. Available: {list(AVAILABLE_POWERS.keys())}"
        
        if power_name in self.active_powers:
            return f"⚠️ Power '{power_name}' is already active"
        
        # Activate the power by loading its specialized tools
        self._load_power_tools(power_name)
        self.active_powers.append(power_name)
        
        power_info = AVAILABLE_POWERS[power_name]
        return f"""✅ Activated: {power_info['name']}
        
{power_info['description']}

New capabilities available:
{chr(10).join(f'  • {cap}' for cap in power_info['capabilities'])}

You now have specialized expertise in {power_name}!"""
    
    @tool
    def deactivate_power(self, power_name: str) -> str:
        """Deactivate a Kiro Power to free up context"""
        if power_name not in self.active_powers:
            return f"⚠️ Power '{power_name}' is not active"
        
        self.active_powers.remove(power_name)
        return f"✅ Deactivated: {power_name}"
    
    @tool
    def show_active_powers(self) -> Dict:
        """Show currently active Kiro Powers"""
        if not self.active_powers:
            return {"active_powers": [], "message": "No powers currently active"}
        
        return {
            "active_powers": self.active_powers,
            "capabilities": {
                power: AVAILABLE_POWERS[power]["capabilities"]
                for power in self.active_powers
            }
        }
    
    def _load_power_tools(self, power_name: str):
        """Load specialized tools for a power"""
        if power_name == "stripe":
            self.agent.add_tool(self._stripe_create_payment)
            self.agent.add_tool(self._stripe_refund)
        elif power_name == "figma":
            self.agent.add_tool(self._figma_export_design)
            self.agent.add_tool(self._figma_create_component)
        elif power_name == "datadog":
            self.agent.add_tool(self._datadog_query_metrics)
            self.agent.add_tool(self._datadog_create_alert)
        elif power_name == "aws":
            self.agent.add_tool(self._aws_deploy_lambda)
            self.agent.add_tool(self._aws_manage_s3)
    
    # Stripe Power Tools
    @tool
    def _stripe_create_payment(self, amount: float, currency: str = "usd") -> Dict:
        """Create a Stripe payment intent"""
        return {
            "payment_intent_id": "pi_1234567890",
            "amount": amount,
            "currency": currency,
            "status": "requires_payment_method",
            "message": f"Payment intent created for {amount} {currency}"
        }
    
    @tool
    def _stripe_refund(self, payment_id: str, amount: Optional[float] = None) -> Dict:
        """Process a Stripe refund"""
        return {
            "refund_id": "re_1234567890",
            "payment_id": payment_id,
            "amount": amount or "full",
            "status": "succeeded",
            "message": "Refund processed successfully"
        }
    
    # Figma Power Tools
    @tool
    def _figma_export_design(self, file_id: str, format: str = "png") -> Dict:
        """Export a Figma design"""
        return {
            "file_id": file_id,
            "format": format,
            "export_url": f"https://figma.com/exports/{file_id}.{format}",
            "message": f"Design exported as {format}"
        }
    
    @tool
    def _figma_create_component(self, name: str, type: str) -> Dict:
        """Create a Figma component"""
        return {
            "component_id": "comp_1234567890",
            "name": name,
            "type": type,
            "message": f"Component '{name}' created"
        }
    
    # Datadog Power Tools
    @tool
    def _datadog_query_metrics(self, metric: str, timeframe: str = "1h") -> Dict:
        """Query Datadog metrics"""
        return {
            "metric": metric,
            "timeframe": timeframe,
            "values": [0.5, 0.7, 0.6, 0.8, 0.9],
            "avg": 0.7,
            "message": f"Retrieved {metric} for last {timeframe}"
        }
    
    @tool
    def _datadog_create_alert(self, metric: str, threshold: float) -> Dict:
        """Create a Datadog alert"""
        return {
            "alert_id": "alert_1234567890",
            "metric": metric,
            "threshold": threshold,
            "status": "active",
            "message": f"Alert created for {metric} > {threshold}"
        }
    
    # AWS Power Tools
    @tool
    def _aws_deploy_lambda(self, function_name: str, runtime: str = "python3.11") -> Dict:
        """Deploy an AWS Lambda function"""
        return {
            "function_arn": f"arn:aws:lambda:us-west-2:123456789:function:{function_name}",
            "runtime": runtime,
            "status": "Active",
            "message": f"Lambda function '{function_name}' deployed"
        }
    
    @tool
    def _aws_manage_s3(self, bucket_name: str, action: str) -> Dict:
        """Manage AWS S3 bucket"""
        return {
            "bucket": bucket_name,
            "action": action,
            "region": "us-west-2",
            "message": f"S3 bucket '{bucket_name}' {action} completed"
        }
    
    def invoke(self, query: str) -> str:
        """Invoke the agent with a query"""
        return self.agent(query).message


def demo_scenario_1():
    """Demo: Payment processing workflow"""
    print("\n" + "="*60)
    print("SCENARIO 1: Payment Processing")
    print("="*60)
    
    agent = KiroPowersAgent()
    
    print("\n1. Agent starts with no specialized knowledge")
    print(agent.invoke("What can you do?"))
    
    print("\n2. Activate Stripe Power for payment processing")
    print(agent.invoke("Activate the stripe power"))
    
    print("\n3. Now agent can process payments")
    print(agent.invoke("Create a payment for $99.99"))
    
    print("\n4. Process a refund")
    print(agent.invoke("Refund payment pi_1234567890"))


def demo_scenario_2():
    """Demo: Multi-power workflow"""
    print("\n" + "="*60)
    print("SCENARIO 2: Full-Stack Development")
    print("="*60)
    
    agent = KiroPowersAgent()
    
    print("\n1. Activate Figma Power for design")
    print(agent.invoke("Activate figma power"))
    
    print("\n2. Export design assets")
    print(agent.invoke("Export design file-123 as SVG"))
    
    print("\n3. Activate AWS Power for deployment")
    print(agent.invoke("Activate aws power"))
    
    print("\n4. Deploy to AWS")
    print(agent.invoke("Deploy a Lambda function called 'payment-processor'"))
    
    print("\n5. Activate Datadog Power for monitoring")
    print(agent.invoke("Activate datadog power"))
    
    print("\n6. Set up monitoring")
    print(agent.invoke("Create an alert for lambda.errors > 10"))
    
    print("\n7. Check active powers")
    print(agent.invoke("What powers are currently active?"))


def demo_scenario_3():
    """Demo: Context efficiency"""
    print("\n" + "="*60)
    print("SCENARIO 3: Context Efficiency")
    print("="*60)
    
    agent = KiroPowersAgent()
    
    print("\n1. List available powers")
    print(agent.invoke("What powers are available?"))
    
    print("\n2. Activate only what's needed (Stripe)")
    print(agent.invoke("Activate stripe"))
    
    print("\n3. Work with Stripe")
    print(agent.invoke("Create a payment for $49.99"))
    
    print("\n4. Done with payments, deactivate to free context")
    print(agent.invoke("Deactivate stripe"))
    
    print("\n5. Activate different power (Datadog)")
    print(agent.invoke("Activate datadog"))
    
    print("\n6. Work with Datadog")
    print(agent.invoke("Query cpu.usage metrics for the last hour"))


if __name__ == "__main__":
    print("\n🚀 Kiro Powers Demo")
    print("Demonstrating on-demand specialized agent capabilities\n")
    
    # Run demo scenarios
    demo_scenario_1()
    demo_scenario_2()
    demo_scenario_3()
    
    print("\n" + "="*60)
    print("✅ Demo Complete!")
    print("="*60)
    print("\nKey Concepts Demonstrated:")
    print("  • On-demand expertise loading")
    print("  • Context efficiency (activate only what's needed)")
    print("  • Multi-power workflows")
    print("  • Dynamic capability expansion")
    print("\nThis pattern prevents context overload by loading")
    print("specialized knowledge only when required.")
