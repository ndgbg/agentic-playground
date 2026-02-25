# Phase 1c: Scoring, Viability Gate, and Report

This steering file covers Steps 7-9 of the assessment phase: team structure analysis, complexity scoring, migration viability gate, and final report generation. Run this after completing assessment-analysis.md.

---

## Step 7: Team Structure and Conway's Law Analysis

This step is critical for large organizations. Service boundaries that don't align with team structure will fail in practice regardless of technical merit.

### 7a: Current Team Topology

Map the current team structure against the codebase:

```
For each team or developer group:
  - Which projects/namespaces do they primarily own?
  - Which areas of the codebase do they modify most frequently? (check git log)
  - What is the team size?
  - What is their deployment cadence?
  - Do they have on-call/operational responsibilities?
```

### 7b: Boundary Alignment Check

For each proposed bounded context, evaluate:

| Question | Impact |
|----------|--------|
| Can a single team own this service end-to-end? | If no, the boundary may be wrong |
| Does this boundary split code that one team currently owns? | Creates handoff overhead |
| Does this boundary merge code from multiple teams? | May cause ownership conflicts |
| Does the team have the skills to operate this service independently? | Training/hiring needed |
| Can the team handle the operational burden (on-call, monitoring, deployments)? | Capacity constraint |

### 7c: Viability Assessment

If proposed service boundaries cannot be cleanly mapped to teams, or if teams lack capacity for independent service ownership, flag this as a high-severity risk. Options:
1. Adjust boundaries to match team structure
2. Reorganize teams to match proposed boundaries (requires organizational buy-in)
3. Reduce the number of services to match available team capacity
4. Recommend modular monolith if team structure doesn't support microservices

Include the team topology analysis in the assessment report under a dedicated section.

---

## Step 8: Complexity and Risk Scoring

### 8a: Per-Service Complexity Score

For each proposed microservice, calculate a complexity score:

| Factor | Weight | Score (1-5) |
|--------|--------|-------------|
| Entity count | 1x | 1 (1-3), 2 (4-7), 3 (8-12), 4 (13-20), 5 (21+) |
| Cross-boundary references | 2x | 1 (0-1), 2 (2-3), 3 (4-6), 4 (7-10), 5 (11+) |
| Shared tables | 3x | 1 (0), 2 (1), 3 (2-3), 4 (4-5), 5 (6+) |
| Stored procedures | 1x | 1 (0), 2 (1-2), 3 (3-5), 4 (6-10), 5 (11+) |
| External integrations | 1x | 1 (0), 2 (1), 3 (2), 4 (3-4), 5 (5+) |
| Transactional dependencies | 3x | 1 (0), 2 (1), 3 (2), 4 (3-4), 5 (5+) |
| Shared state instances | 2x | 1 (0), 2 (1), 3 (2-3), 4 (4-5), 5 (6+) |
| Framework migration needed | 2x | 1 (same framework), 3 (minor upgrade), 5 (.NET Framework to .NET Core) |

Total score interpretation:
- 15-25: Easy extraction
- 26-40: Medium complexity
- 41-55: Hard extraction
- 56+: Very hard — consider breaking into smaller steps

### 8b: Migration Viability Gate

Before calculating migration order, evaluate whether microservices extraction is justified. If any of the following conditions are true, recommend against decomposition and explain why:

**Recommend AGAINST microservices if:**

| Condition | Threshold | Rationale |
|-----------|-----------|-----------|
| Total project count | 3 or fewer | Too small to benefit from distribution overhead |
| Total entity count | 15 or fewer | Insufficient domain complexity to justify service boundaries |
| Proposed service count | 2 or fewer | Not enough distinct bounded contexts |
| All complexity scores | < 15 (Easy) | Monolith is manageable as-is |
| No team scaling problem | Single team, < 8 devs | Conway's Law doesn't demand splitting |
| No independent deployment need | Single release cadence | Key microservices benefit is absent |
| High cross-boundary coupling | > 60% of entities have cross-boundary refs | Will produce a distributed monolith |

**Recommend CAUTION (modular monolith instead) if:**
- 4-8 projects with moderate coupling — a modular monolith with clean boundaries may deliver 80% of the benefit at 20% of the cost
- Team is < 4 developers — operational overhead of microservices will exceed development velocity gains
- No existing CI/CD, containerization, or observability — infrastructure prerequisites are missing

**When recommending against decomposition, suggest alternatives:**
1. Modular monolith — enforce bounded contexts via project structure and access modifiers without network boundaries
2. Vertical slice architecture — organize by feature within the monolith
3. Strangler Fig for specific pain points — extract only the 1-2 components that genuinely need independent scaling or deployment
4. Do nothing — if the monolith is working and the team is productive, document that finding

Include the viability assessment in the Executive Summary of the report. The recommendation field should be one of:
- **Proceed** — clear benefits, manageable complexity
- **Proceed with Caution** — benefits exist but significant risks; consider phased approach
- **Modular Monolith Recommended** — enforce boundaries without distribution
- **Do Not Decompose** — monolith is appropriate for this codebase and team

### 8c: Migration Order Algorithm

Determine extraction order using this formula:

```
Migration Priority Score = 
  (100 / Complexity Score) x 30                    [Lower complexity = higher priority]
  + (1 / (Cross-Boundary References + 1)) x 25     [Fewer cross-refs = higher priority]
  + (1 / (Inbound Dependencies + 1)) x 20          [Fewer dependents = higher priority]
  + (Independent Deployability Factor x 15)         [0.0-1.0: can it run alone?]
  + (Business Value Factor x 10)                    [0 (low), 1 (medium), 2 (high)]

Where:
  - Complexity Score: from Step 8a weighted calculation
  - Cross-Boundary References: count of entities/APIs this service references in other services
  - Inbound Dependencies: count of other services that call this service's APIs
  - Independent Deployability Factor: 1.0 if no sync dependencies, 0.5 if 1-2, 0.0 if 3+
  - Business Value Factor: user-provided or inferred from change frequency
```

Apply these ordering rules after scoring:
1. Services with zero inbound dependencies go first (nothing breaks if they're extracted)
2. Services that are depended upon by many others go last (extract consumers before providers)
3. Break ties using complexity score (lower first)
4. Never extract a service before its synchronous dependencies are available (as APIs or still in monolith)
5. Identity/Auth service should be extracted early if multiple services need token validation
6. Group related services that share transaction boundaries into the same migration phase

Present the ordered list with scores:

```
| Order | Service | Complexity | Cross-Refs | Inbound Deps | Priority Score | Rationale |
|-------|---------|-----------|------------|--------------|----------------|-----------|
| 1     | ...     | ...       | ...        | ...          | ...            | ...       |
```

### 8d: Risk Register

For each proposed service, document risks:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Shared table X needs splitting | High | High | Create migration script, test with production data copy |
| Transaction spanning Order and Inventory | Medium | High | Implement saga pattern with compensation |
| Performance degradation from API calls replacing in-process calls | Medium | Medium | Add caching, optimize API contracts |
| Authentication flow disruption | Low | Critical | Extract auth service first, test thoroughly |

---

## Step 9: Generate Assessment Report

Present a comprehensive report to the user. The report must include ALL of the following sections:

### Report Structure

```
## Monolith Assessment Report

### 1. Executive Summary
- One paragraph overview of the monolith
- Migration viability recommendation (Proceed / Proceed with Caution / Modular Monolith Recommended / Do Not Decompose)
- If "Do Not Decompose" or "Modular Monolith Recommended", explain why and suggest alternatives — do not proceed to transformation
- Number of proposed microservices (if proceeding)
- Overall complexity rating (Easy/Medium/Hard/Very Hard)
- Estimated effort (see Effort Estimation below)
- Key risks in 2-3 bullet points
```

### Effort Estimation

Map the sum of all per-service complexity scores to an effort range:

| Total Complexity Score | Effort Estimate | Typical Duration (1 team) | Description |
|----------------------|-----------------|--------------------------|-------------|
| 15-50 | Small | 2-6 weeks | Few services, low coupling, straightforward extraction |
| 51-120 | Medium | 6-16 weeks | Multiple services, moderate coupling, some refactoring needed |
| 121-250 | Large | 4-8 months | Many services, significant coupling, database splitting required |
| 251+ | Very Large | 8-18 months | Complex system, extensive refactoring, phased migration essential |

### Effort Adjustment Multipliers

Apply these multipliers to the base duration estimate. Multiply cumulatively when multiple apply:

| Condition | Multiplier | Rationale |
|-----------|------------|-----------|
| Framework migration required (.NET Framework to .NET 8) | 1.5x | API surface changes, package incompatibilities, startup rewrite |
| No existing test coverage | 1.3x | Must write characterization tests before extraction |
| Stored procedure heavy (20+ procedures) | 1.2x | Each procedure needs analysis, rewrite, or migration |
| Team unfamiliar with microservices | 1.3x | Learning curve for distributed patterns, Docker, orchestration |
| Multiple databases or database vendors | 1.2x | Different migration strategies per vendor, connection management |
| Complex authentication (Windows Auth, custom SSO) | 1.15x | Token migration, identity federation setup |
| Heavy use of shared mutable state (10+ instances) | 1.15x | Requires distributed cache or state service introduction |
| No CI/CD pipeline exists | 1.2x | Must build deployment infrastructure alongside services |

**Example calculation:**
- Base estimate: Medium (6-16 weeks)
- Framework migration: 1.5x
- No test coverage: 1.3x
- Cumulative multiplier: 1.5 x 1.3 = 1.95x
- Adjusted estimate: 12-31 weeks (round to "12-32 weeks")
- Present as: "Medium-Large: 12-32 weeks (adjusted for framework migration and missing test coverage)"

Present the estimate as a range with the multipliers that apply.

### Remaining Report Sections

```
### 2. Codebase Overview
- Solution structure diagram (text-based tree)
- Project inventory table (from Step 1)
- Technology stack summary (from Step 2)
- Lines of code estimates per project
- Test coverage summary
- Framework version compatibility notes

### 3. Domain Model Map
- Complete entity inventory with relationships
- Aggregate boundaries identified
- Entity relationship diagram (text-based)

### 4. Identified Bounded Contexts
For EACH context:
- Name and business capability description
- Entities and aggregates included (with justification)
- Controllers/endpoints included
- Services and business logic included
- Data access components included
- External integrations owned
- Background jobs owned

### 5. Dependency Analysis
- Project reference graph (text-based diagram)
- Hub projects and their role
- God projects and their responsibilities
- Circular dependencies found (with resolution strategy)
- Namespace-level coupling hotspots
- Shared library inventory

### 6. Data Layer Analysis
- Database context inventory with entity sets
- Table ownership matrix
- Shared tables with resolution strategy
- Stored procedure ownership mapping
- Cross-context query inventory
- Transaction boundary analysis results
- Database migration complexity assessment

### 7. Coupling Metrics
- Per-context coupling scores (Ca, Ce, I, A, D)
- Cross-boundary reference inventory
- Shared state instances with resolution strategy
- External integration mapping

### 8. Security Analysis
- Authentication mechanism and flow
- Authorization model summary
- Identity data ownership
- Security-sensitive cross-boundary flows

### 8.5. Team Structure Analysis
- Current team topology mapped to codebase ownership
- Proposed service-to-team mapping
- Boundary alignment assessment (do proposed services match team structure?)
- Capacity assessment (can teams handle independent service ownership?)
- Skills gap analysis (what training or hiring is needed?)
- If boundaries don't align with teams, flag as high risk and recommend adjustments

### 9. Proposed Microservices
For EACH proposed service:
- Service name and responsibility
- Bounded context it covers
- Entities it owns (source of truth)
- APIs it will expose
- APIs it will consume from other services
- Events it will publish
- Events it will consume
- Dependencies on other services
- Complexity score and breakdown
- Extraction difficulty rating (Easy/Medium/Hard)
- Key risks specific to this service

### 10. Recommended Migration Order
- Ordered list from first to last extraction
- Complexity score for each
- Dependencies between migration steps
- Justification for the ordering
- Estimated relative effort per step

### 11. Risk Register
- Complete risk table with likelihood, impact, and mitigation
- High-risk areas highlighted
- Data migration challenges
- Performance considerations
- Security considerations
- Rollback strategy overview

### 12. Recommendations
- Framework upgrade recommendations (if applicable)
- Suggested shared library strategy
- Recommended inter-service communication patterns
- Infrastructure recommendations (containers, orchestration, observability)
- Suggested next steps
```

### After Presenting the Report

Ask the user these specific questions:

1. Does the bounded context identification look correct? Are there business domains I missed or incorrectly grouped?
2. Would you like to adjust any service boundaries? (e.g., merge two contexts, split one further)
3. Are there business constraints that should influence the migration order? (e.g., "we need the payment service extracted first for PCI compliance")
4. Are there any entities or components I missed in the analysis?
5. Do you agree with the risk assessment? Are there risks I haven't considered?
6. Are you ready to proceed to the transformation planning phase?

**Do not proceed to transformation until the user explicitly approves the assessment.**
