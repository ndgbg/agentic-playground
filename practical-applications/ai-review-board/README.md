# AI Product Review Board 🎭

**Your toughest stakeholder — automated.**

## What It Does

Reviews product specs and flags common issues:
- 🎯 **Ambiguous goals** - Unclear problem or purpose
- 📊 **Missing eval** - No success metrics defined
- ⚠️ **Unsafe autonomy** - AI decisions without guardrails
- 📉 **Weak success metrics** - Vague or unmeasurable KPIs

Then asks **brutal questions** from different personas:
- 😤 Skeptical CTO
- 📊 Data-Driven CEO
- 👥 User Advocate
- 🛡️ Risk Manager
- 🤖 AI Ethics Officer
- 💰 Finance Director

## Why It Spreads

✅ **Funny + useful** - Makes review process entertaining  
✅ **Improves quality** - Catches issues early  
✅ **Easy to demo** - Run it, get instant feedback  

## Quick Start

```bash
python review_board.py
```

## Example Output

```
🎭 AI PRODUCT REVIEW BOARD
Your toughest stakeholder — automated
============================================================

VERDICT: 🚫 BLOCKED
Critical issues must be addressed before proceeding

🚨 ISSUES FOUND:
------------------------------------------------------------

⚠️ Unsafe Autonomy [CRITICAL]
  Finding: AI autonomy without proper guardrails
  Question: What happens when the AI makes a mistake? Who's accountable?

📉 Weak Metrics [MEDIUM]
  Finding: Success metrics are vague or unmeasurable
  Question: Can we measure this objectively? What's the baseline?

💬 BRUTAL QUESTIONS:
------------------------------------------------------------

😤 Skeptical CTO
  How does this scale to 10x users? What breaks first?

📊 Data-Driven CEO
  What's the ROI? Show me the numbers, not the vision.

👥 User Advocate
  Did you actually talk to users? Or are we building what we think they want?

🛡️ Risk Manager
  What's the worst that could happen? Have we thought through edge cases?

🤖 AI Ethics Officer
  What biases might this perpetuate? How do we audit the AI's decisions?
```

## Use Cases

### For Product Managers
- Review PRDs before stakeholder meetings
- Catch gaps in feature specs
- Prepare for tough questions

### For Teams
- Gate for spec quality
- Shared review checklist
- Onboarding tool for new PMs

### For Demos
- Show at team meetings
- Use in workshops
- Share on social media

## How It Works

1. **Analyzes spec text** for common anti-patterns
2. **Flags issues** with severity levels
3. **Generates questions** from different stakeholder personas
4. **Provides verdict** (Blocked/Needs Work/Concerns/Approved)

## Customization

Add your own personas in `review_board.py`:

```python
questions.append({
    "persona": "🎨 Design Lead",
    "question": "Where are the mockups? How does this fit our design system?"
})
```

Add custom checks:

```python
def _check_accessibility(self, text: str) -> bool:
    """Check if accessibility is mentioned."""
    return "accessibility" in text.lower() or "a11y" in text.lower()
```

## API Usage

```python
from review_board import ReviewBoard

board = ReviewBoard()
review = board.review_spec(your_spec_text)

print(f"Verdict: {review['verdict']['status']}")
print(f"Issues: {review['issues_found']}")
```

## Integration Ideas

- **Slack bot** - Review specs in channels
- **GitHub Action** - Auto-review PRs with specs
- **CLI tool** - `review-spec my-prd.md`
- **Web app** - Paste spec, get instant review
- **VS Code extension** - Review as you write

## Why This Works

**Psychological safety**: It's easier to hear tough feedback from a bot than a person.

**Consistency**: Same standards applied every time.

**Speed**: Instant feedback vs waiting for stakeholder review.

**Learning**: Teaches PMs what good specs look like.

## Roadmap

- [ ] Web interface
- [ ] Custom persona builder
- [ ] Integration with Notion/Confluence
- [ ] Severity scoring algorithm
- [ ] Historical tracking of spec quality
- [ ] Team-specific rule sets

## Contributing

Add new checks, personas, or integrations! PRs welcome.

## License

MIT - Use freely, share widely

---

**Built for product teams who want better specs without the pain of endless review cycles.**

*"Finally, a stakeholder who's always available and never in back-to-back meetings."*
