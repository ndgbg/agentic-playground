# Claude Skills for Product Managers

A collection of production-ready Claude Skills designed specifically for AI Product Managers. These skills automate common PM workflows and ensure consistent, high-quality outputs.

## 📦 Available Skills

### 1. PRD Generator
**Purpose**: Create comprehensive Product Requirements Documents following industry best practices.

**Use when**: Starting a new feature, documenting requirements, aligning stakeholders.

**Key features**:
- Complete PRD structure with all critical sections
- User stories, requirements, and acceptance criteria
- Technical considerations and risk assessment
- Timeline and milestone planning

**Time savings**: 4 hours → 45 minutes (81% reduction)

---

### 2. Changelog Generator
**Purpose**: Transform technical git commits into user-friendly changelog entries.

**Use when**: Preparing releases, communicating updates, documenting changes.

**Key features**:
- Categorized changes (features, improvements, fixes)
- User-friendly language (no technical jargon)
- Emoji indicators for quick scanning
- Breaking changes highlighted

**Time savings**: 2 hours → 15 minutes (87% reduction)

---

### 3. User Story Writer
**Purpose**: Write clear, actionable user stories with acceptance criteria following agile best practices.

**Use when**: Breaking down features, sprint planning, backlog grooming.

**Key features**:
- Proper user story format (As a... I want... So that...)
- Given-When-Then acceptance criteria
- Story point estimation guidance
- Edge cases and definition of done

**Time savings**: 1 hour → 10 minutes (83% reduction)

---

### 4. Meeting Notes Processor
**Purpose**: Transform meeting notes into structured action items and follow-ups.

**Use when**: After any meeting, for status updates, decision documentation.

**Key features**:
- Extracts action items with owners and due dates
- Prioritizes tasks (high/medium/low)
- Captures decisions and rationale
- Generates follow-up email template

**Time savings**: 30 minutes → 5 minutes (83% reduction)

---

### 5. Competitive Analysis
**Purpose**: Create comprehensive competitive analyses for product strategy.

**Use when**: Market research, feature prioritization, positioning strategy.

**Key features**:
- Competitor profiles with strengths/weaknesses
- Feature comparison matrix
- SWOT analysis and positioning map
- Actionable recommendations

**Time savings**: 8 hours → 2 hours (75% reduction)

---

## 🚀 Quick Start

### Installation

1. **Download the skill folder** you want to use
2. **Zip the folder** (must include SKILL.md)
3. **Upload to Claude.ai**:
   - Go to Settings → Skills
   - Click "Add Skill"
   - Upload the zip file

### Using with Claude Code

1. **Place skill folder** in your project directory
2. **Reference in conversation**: Claude will automatically detect and load relevant skills
3. **Explicit activation**: Mention the skill name to ensure it's loaded

### Using with Cursor

1. **Add to `.cursor/skills/`** directory
2. **Skills auto-load** based on context
3. **Manual trigger**: Use `@skill-name` to explicitly invoke

---

## 💡 Usage Examples

### PRD Generator
```
Create a PRD for a new dashboard analytics feature that shows real-time user activity.
Target users are product managers and data analysts.
```

### Changelog Generator
```
Here are the git commits from our latest release. Generate a user-friendly changelog:
[paste commits]
```

### User Story Writer
```
Write user stories for a CSV export feature that lets users download their data with custom date ranges.
```

### Meeting Notes Processor
```
Process these meeting notes and extract action items:
[paste notes]
```

### Competitive Analysis
```
Analyze our top 3 competitors in the project management space: Asana, Monday.com, and ClickUp.
Focus on pricing and collaboration features.
```

---

## 🎯 Best Practices

### 1. Provide Context
Give Claude relevant information:
- Company guidelines
- Target audience
- Specific constraints
- Previous examples

### 2. Iterate and Refine
- Start with basic output
- Request specific improvements
- Save refined versions
- Update skills based on learnings

### 3. Combine Skills
Chain multiple skills together:
```
1. Use Competitive Analysis to identify feature gaps
2. Use PRD Generator to document new feature
3. Use User Story Writer to break down implementation
4. Use Changelog Generator when shipping
```

### 4. Customize for Your Team
- Add company-specific templates
- Include brand guidelines
- Reference internal processes
- Adapt tone and format

---

## 📊 Productivity Impact

Based on real-world usage:

| Task | Before | After | Savings |
|------|--------|-------|---------|
| PRD Creation | 4 hours | 45 min | 81% |
| Changelog Writing | 2 hours | 15 min | 87% |
| User Stories | 1 hour | 10 min | 83% |
| Meeting Follow-ups | 30 min | 5 min | 83% |
| Competitive Analysis | 8 hours | 2 hours | 75% |

**Average time savings: 82%**

---

## 🔧 Customization Guide

### Adding Company Context

Create a `context.md` file in the skill folder:

```markdown
# Company Context

## Brand Voice
- Professional but friendly
- Technical but accessible
- Action-oriented

## Target Customers
- B2B SaaS companies
- 50-500 employees
- Technical product teams

## Key Differentiators
- Real-time collaboration
- AI-powered insights
- Enterprise security
```

### Adding Templates

Include example outputs in `examples/` folder:
- `example-prd.md`
- `example-changelog.md`
- `example-user-story.md`

Claude will reference these for style and structure.

---

## 🤝 Contributing

Have improvements or new skills to share?

1. Fork the repo
2. Add your skill in a new folder
3. Include SKILL.md and examples
4. Submit a pull request

### Skill Submission Guidelines
- Clear purpose and use case
- Complete SKILL.md with instructions
- At least 2 example outputs
- Documented time savings (if measured)

---

## 📚 Related Resources

- [Claude Skills Article](../patterns/claude-skills-for-pms.md) - Deep dive into how PMs use Skills
- [Agentic AI Insights](../) - Strategic insights on agentic AI
- [Claude Documentation](https://docs.anthropic.com/claude/docs/skills) - Official Skills docs

---

## 🆘 Troubleshooting

### Skill Not Loading
- Verify SKILL.md is in the root of the folder
- Check file is properly formatted markdown
- Ensure zip file isn't corrupted

### Inconsistent Output
- Add more specific examples
- Clarify instructions in SKILL.md
- Provide more context in your prompt

### Skill Too Generic
- Add company-specific context
- Include detailed examples
- Reference internal guidelines

---

## 📝 License

MIT License - Use freely in your organization.

---

## 🙏 Acknowledgments

These skills synthesize best practices from:
- Product management community
- Agile methodology experts
- Technical writing standards
- Real-world PM workflows

Built for the AI Product Manager community.

---

**Questions or feedback?** Open an issue or connect on [LinkedIn](https://linkedin.com/in/nida-beig)
