#!/usr/bin/env python3
"""
AI Product Review Board
Your toughest stakeholder — automated.
"""

import json
from datetime import datetime

class ReviewBoard:
    def __init__(self):
        self.name = "AI Product Review Board"
        self.personas = {
            "skeptical_cto": "Questions technical feasibility and scalability",
            "data_driven_ceo": "Demands metrics and business impact",
            "user_advocate": "Challenges assumptions about user needs",
            "risk_manager": "Identifies safety and compliance issues"
        }
    
    def review_spec(self, spec_text: str) -> dict:
        """Review a product spec and flag issues."""
        
        issues = []
        questions = []
        
        # Check for ambiguous goals
        if not self._has_clear_goal(spec_text):
            issues.append({
                "type": "🎯 Ambiguous Goal",
                "severity": "HIGH",
                "finding": "Goal is unclear or missing",
                "question": "What specific problem are we solving? For whom?"
            })
        
        # Check for missing evaluation criteria
        if not self._has_eval_criteria(spec_text):
            issues.append({
                "type": "📊 Missing Eval",
                "severity": "HIGH",
                "finding": "No success metrics defined",
                "question": "How will we know if this works? What does success look like?"
            })
        
        # Check for unsafe autonomy
        if self._has_autonomy_risks(spec_text):
            issues.append({
                "type": "⚠️ Unsafe Autonomy",
                "severity": "CRITICAL",
                "finding": "AI autonomy without proper guardrails",
                "question": "What happens when the AI makes a mistake? Who's accountable?"
            })
        
        # Check for weak success metrics
        if self._has_weak_metrics(spec_text):
            issues.append({
                "type": "📉 Weak Metrics",
                "severity": "MEDIUM",
                "finding": "Success metrics are vague or unmeasurable",
                "question": "Can we measure this objectively? What's the baseline?"
            })
        
        # Generate brutal questions from each persona
        questions.extend(self._generate_questions(spec_text))
        
        return {
            "reviewed_at": datetime.now().isoformat(),
            "spec_length": len(spec_text),
            "issues_found": len(issues),
            "issues": issues,
            "brutal_questions": questions,
            "verdict": self._get_verdict(issues)
        }
    
    def _has_clear_goal(self, text: str) -> bool:
        """Check if spec has clear goal."""
        goal_keywords = ["goal", "objective", "problem", "purpose", "why"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in goal_keywords) and len(text) > 100
    
    def _has_eval_criteria(self, text: str) -> bool:
        """Check if spec has evaluation criteria."""
        eval_keywords = ["metric", "measure", "kpi", "success", "evaluate", "track"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in eval_keywords)
    
    def _has_autonomy_risks(self, text: str) -> bool:
        """Check for AI autonomy without guardrails."""
        autonomy_keywords = ["autonomous", "automatically", "ai decides", "without human"]
        guardrail_keywords = ["review", "approval", "human-in-loop", "oversight", "guardrail"]
        
        text_lower = text.lower()
        has_autonomy = any(keyword in text_lower for keyword in autonomy_keywords)
        has_guardrails = any(keyword in text_lower for keyword in guardrail_keywords)
        
        return has_autonomy and not has_guardrails
    
    def _has_weak_metrics(self, text: str) -> bool:
        """Check for vague metrics."""
        weak_phrases = ["improve", "better", "enhance", "optimize", "increase engagement"]
        text_lower = text.lower()
        
        has_weak = any(phrase in text_lower for phrase in weak_phrases)
        has_numbers = any(char.isdigit() for char in text)
        
        return has_weak and not has_numbers
    
    def _generate_questions(self, text: str) -> list:
        """Generate brutal questions from different personas."""
        questions = []
        
        # Skeptical CTO
        questions.append({
            "persona": "😤 Skeptical CTO",
            "question": "How does this scale to 10x users? What breaks first?"
        })
        
        # Data-driven CEO
        questions.append({
            "persona": "📊 Data-Driven CEO",
            "question": "What's the ROI? Show me the numbers, not the vision."
        })
        
        # User Advocate
        questions.append({
            "persona": "👥 User Advocate",
            "question": "Did you actually talk to users? Or are we building what we think they want?"
        })
        
        # Risk Manager
        questions.append({
            "persona": "🛡️ Risk Manager",
            "question": "What's the worst that could happen? Have we thought through edge cases?"
        })
        
        # Add context-specific questions
        if "ai" in text.lower() or "ml" in text.lower():
            questions.append({
                "persona": "🤖 AI Ethics Officer",
                "question": "What biases might this perpetuate? How do we audit the AI's decisions?"
            })
        
        if "user" in text.lower() or "customer" in text.lower():
            questions.append({
                "persona": "💰 Finance Director",
                "question": "What's the customer acquisition cost? How long to break even?"
            })
        
        return questions
    
    def _get_verdict(self, issues: list) -> dict:
        """Determine overall verdict."""
        critical = sum(1 for i in issues if i["severity"] == "CRITICAL")
        high = sum(1 for i in issues if i["severity"] == "HIGH")
        
        if critical > 0:
            return {
                "status": "🚫 BLOCKED",
                "message": "Critical issues must be addressed before proceeding"
            }
        elif high > 2:
            return {
                "status": "⚠️ NEEDS WORK",
                "message": "Multiple high-severity issues found"
            }
        elif high > 0:
            return {
                "status": "🤔 CONCERNS",
                "message": "Some issues to address"
            }
        else:
            return {
                "status": "✅ APPROVED",
                "message": "Looks solid, but still answer the questions"
            }
    
    def format_review(self, review: dict) -> str:
        """Format review as readable text."""
        output = []
        output.append("=" * 60)
        output.append("🎭 AI PRODUCT REVIEW BOARD")
        output.append("Your toughest stakeholder — automated")
        output.append("=" * 60)
        output.append("")
        
        # Verdict
        verdict = review["verdict"]
        output.append(f"VERDICT: {verdict['status']}")
        output.append(f"{verdict['message']}")
        output.append("")
        
        # Issues
        if review["issues"]:
            output.append("🚨 ISSUES FOUND:")
            output.append("-" * 60)
            for issue in review["issues"]:
                output.append(f"\n{issue['type']} [{issue['severity']}]")
                output.append(f"  Finding: {issue['finding']}")
                output.append(f"  Question: {issue['question']}")
        else:
            output.append("✅ No major issues found")
        
        output.append("")
        output.append("💬 BRUTAL QUESTIONS:")
        output.append("-" * 60)
        for q in review["brutal_questions"]:
            output.append(f"\n{q['persona']}")
            output.append(f"  {q['question']}")
        
        output.append("")
        output.append("=" * 60)
        output.append(f"Reviewed at: {review['reviewed_at']}")
        output.append(f"Issues found: {review['issues_found']}")
        output.append("=" * 60)
        
        return "\n".join(output)

def main():
    """Demo the review board."""
    
    board = ReviewBoard()
    
    # Example spec (intentionally flawed)
    spec = """
    New Feature: AI-Powered Content Generator
    
    We want to build an AI that automatically generates social media posts for users.
    It will analyze their past content and create new posts in their style.
    
    The AI will post automatically to save users time.
    
    This will improve engagement and make our platform better.
    
    Users will love it because it's innovative and uses AI.
    """
    
    print("📝 REVIEWING SPEC:")
    print("-" * 60)
    print(spec)
    print()
    
    # Review the spec
    review = board.review_spec(spec)
    
    # Print formatted review
    print(board.format_review(review))
    
    # Also save as JSON
    with open("review_output.json", "w") as f:
        json.dump(review, f, indent=2)
    
    print("\n💾 Full review saved to: review_output.json")

if __name__ == "__main__":
    main()
