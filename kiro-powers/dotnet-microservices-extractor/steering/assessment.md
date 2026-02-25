# Phase 1: Codebase Assessment

This steering file is the entry point for the assessment phase. The assessment has been split into three focused files to improve adherence and reduce context pressure. Complete them in order.

---

## Assessment Workflow

### Step 1: Read and execute assessment-discovery.md
Covers Steps 1-2: Project structure scanning, configuration inventory, database artifacts, infrastructure files, and full technology stack fingerprinting.

**Output:** Project inventory table and technology stack summary.

### Step 2: Read and execute assessment-analysis.md
Covers Steps 3-6: Domain model analysis (entity discovery, aggregate roots, bounded contexts, cross-boundary mapping), dependency and coupling analysis (project references, namespace dependencies, class-level metrics, shared state, database coupling, external integrations, transaction boundaries), communication pattern analysis, and security/identity analysis.

**Output:** Bounded context map, dependency graph, coupling metrics, table ownership matrix.

### Step 3: Read and execute assessment-scoring.md
Covers Steps 7-9: Team structure and Conway's Law analysis, per-service complexity scoring, migration viability gate, migration order algorithm, risk register, and the complete assessment report.

**Output:** Complete assessment report with viability recommendation, migration order, and effort estimate.

---

## Key Rules

- Complete ALL three files before presenting the assessment to the user
- Do not skip any step — thoroughness here prevents costly mistakes during extraction
- **If the viability gate recommends against decomposition, present that finding and do not proceed to transformation unless the user explicitly overrides**
- Do not proceed to transformation until the user explicitly approves the assessment

---

## Quick Reference: Assessment Steps

| Step | File | What It Covers |
|------|------|---------------|
| 1-2 | assessment-discovery.md | Project inventory, config files, DB artifacts, tech stack |
| 3-6 | assessment-analysis.md | Domain model, dependencies, coupling, communication, security |
| 7-9 | assessment-scoring.md | Team analysis, complexity scores, viability gate, report |
