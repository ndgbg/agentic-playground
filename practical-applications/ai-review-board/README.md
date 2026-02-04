# AI Product Review Board 🎭

**Your toughest stakeholder — automated.**

## Two Versions

### 1. Rule-Based (review_board.py)
Simple pattern matching for quick checks. No API key needed.

### 2. Agentic (agentic_review_board.py) ⭐ NEW
**True agentic AI** that:
- ✅ Uses LLM reasoning to understand specs
- ✅ Asks contextual follow-up questions
- ✅ Suggests specific improvements
- ✅ Adapts analysis based on content
- ✅ Provides evidence-based feedback

## Quick Start

### Agentic Version (Recommended)

```bash
# Set your API key
export ANTHROPIC_API_KEY=your_key_here

# Install dependencies
pip install -r requirements.txt

# Run review
python agentic_review_board.py
```

### Rule-Based Version

```bash
# No setup needed
python review_board.py
```

### Web Interface

```bash
open index.html
```

## What Makes It Agentic?

**Rule-based version:**
- Pattern matching (if "autonomous" then flag)
- Fixed questions
- No reasoning

**Agentic version:**
- LLM understands context
- Reasons about implications
- Asks relevant follow-ups
- Suggests specific fixes
- Quotes evidence from spec

## Example: Agentic Review

```python
from agentic_review_board import AgenticReviewBoard

board = AgenticReviewBoard()

# Review spec
review = board.review_spec(your_spec_text)

# Ask follow-up
answer = board.ask_followup(
    your_spec_text,
    review,
    "What metrics should we track?"
)

# Get improvement suggestions
improvements = board.suggest_improvements(
    your_spec_text,
    focus_area="success metrics"
)
```

## Agentic Features

### 1. Intelligent Analysis
Understands nuance and context, not just keywords.

### 2. Evidence-Based Feedback
Quotes specific parts of your spec when identifying issues.

### 3. Follow-Up Questions
Ask anything about the spec and get intelligent answers.

### 4. Improvement Suggestions
Get concrete rewrites and additions, not just criticism.

### 5. Adaptive Personas
Questions adapt based on what's actually in your spec.

## Output Example

```
🎭 AGENTIC AI PRODUCT REVIEW BOARD
Powered by Claude - Intelligent spec analysis with reasoning
======================================================================

VERDICT: 🚫 BLOCKED
Reasoning: This spec has critical gaps in safety, metrics, and user validation
that must be addressed before development.

🚨 CRITICAL ISSUES:
----------------------------------------------------------------------

❌ No user consent mechanism for AI-generated content
   Evidence: "The AI will post automatically"
   Impact: Users may not want AI posting on their behalf without review

❌ Missing success metrics and evaluation criteria
   Evidence: "improve engagement and make our platform better"
   Impact: No way to measure if feature actually works

💬 QUESTIONS FROM THE BOARD:
----------------------------------------------------------------------

😤 Skeptical CTO
  • What happens when the AI generates inappropriate content?
  • How do you prevent the AI from learning and amplifying harmful patterns?

📊 Data-Driven CEO
  • What's the baseline engagement rate we're trying to improve?
  • How much will this cost to build and operate vs. expected revenue impact?

👥 User Advocate
  • Have you validated that users actually want AI posting for them?
  • What control do users have over the AI's output?

💡 SUGGESTED IMPROVEMENTS:
----------------------------------------------------------------------

📌 Add User Control
   Implement approval workflow where users review AI-generated posts before publishing

📌 Define Success Metrics
   Specify: engagement rate increase target, user adoption rate, content quality score
```

## API Usage

### Basic Review
```python
review = board.review_spec(spec_text)
print(board.format_review(review))
```

### Follow-Up Questions
```python
answer = board.ask_followup(
    spec_text,
    review,
    "How should we handle edge cases?"
)
```

### Get Improvements
```python
improvements = board.suggest_improvements(
    spec_text,
    focus_area="metrics"  # Optional focus
)
```

## Why Agentic Matters

**Rule-based** catches obvious issues.  
**Agentic** understands your specific context and provides tailored feedback.

Example:
- Rule-based: "Missing metrics" (generic)
- Agentic: "You mention 'improve engagement' but don't specify baseline engagement rate or target improvement. Consider: 'Increase average engagement rate from 2.3% to 3.5% within 3 months'" (specific)

## Configuration

Set environment variable:
```bash
export ANTHROPIC_API_KEY=your_key
```

Or pass directly:
```python
board = AgenticReviewBoard(api_key="your_key")
```

## Cost

Uses Claude 3.5 Sonnet:
- ~$0.01-0.05 per spec review
- Worth it for the quality of feedback

## Comparison

| Feature | Rule-Based | Agentic |
|---------|-----------|---------|
| Setup | None | API key |
| Cost | Free | ~$0.03/review |
| Speed | Instant | 2-5 seconds |
| Accuracy | Pattern matching | Understands context |
| Follow-ups | No | Yes |
| Improvements | Generic | Specific |
| Evidence | No | Quotes spec |

## Integration Ideas

- **Slack bot** - Review specs in channels
- **GitHub Action** - Auto-review PRs
- **Notion integration** - Review docs inline
- **CLI tool** - `review-spec my-prd.md`

## Roadmap

- [x] Agentic LLM-powered review
- [x] Follow-up questions
- [x] Improvement suggestions
- [ ] Web interface for agentic version
- [ ] Compare multiple specs
- [ ] Track improvements over time
- [ ] Team-specific training

## License

MIT

---

**The agentic version is the real deal. The rule-based version is a demo of what NOT to call "agentic."** 😉

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
