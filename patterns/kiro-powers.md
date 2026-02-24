# Kiro Powers: How I Built Two Production-Ready Microservices Extractors

Kiro's real leverage isn't in what it does out of the box — it's in how far you can extend it. Powers are the mechanism for that extension. This article walks through what powers are, why I built two of them, and the design decisions that went into each.

The two powers: a **.NET Microservices Extractor** and a **Java Microservices Extractor**. Both tackle the same genuinely hard problem — guiding an AI agent through a structured, phased monolith-to-microservices transformation — but against entirely different technology stacks and ecosystems.

---

## What Are Kiro Powers?

Kiro is an AI-powered IDE built for agentic development. Unlike a general-purpose coding assistant, Kiro is designed around the idea that software development work can be structured, reviewed, and executed through a loop of specs, tasks, and hooks.

**Powers** are a first-class extension mechanism in Kiro. A power packages a set of **steering files** — markdown documents that shape how Kiro approaches a specific problem domain. When you activate a power on a project, Kiro reads those steering files and uses them as persistent instructions, domain knowledge, and workflow guidance throughout the session.

Think of a power as a domain-expert persona you install into Kiro for a specific task. The POWER.md file is the entry point — it declares what the power does, what steering files are available, and how Kiro should use them. The steering files contain the actual substance: step-by-step workflows, pattern references, decision frameworks, and checklists.

This is related to but distinct from the [Skills, Scripts, and Knowledge](./skills-scripts-knowledge.md) framework:

| Concept | Maps To |
|---|---|
| Power (POWER.md) | Orchestrator — defines scope and reading order |
| Workflow steering files | Scripts — phased procedures |
| Pattern reference files | Knowledge — domain expertise to consult |
| Kiro itself | Skills — executes tool calls, writes code |

The steering file model lets you encode months of hard-won domain expertise into a form that an AI agent can actually use — not as a vague system prompt, but as structured, navigable reference material.

---

## Why These Two Powers?

Monolith decomposition is one of the most requested and most mishandled things in software engineering. Teams attempt it, hit unexpected coupling, stall mid-migration, or end up with a distributed monolith that's worse than what they started with.

The failure modes are predictable:

- Starting the transformation before fully understanding the coupling
- Splitting code along technical layers instead of domain boundaries
- Ignoring data ownership — shared databases defeat the purpose
- Missing team structure alignment (Conway's Law violations)
- No rollback strategy, so each step feels irreversible

An AI agent without guidance will reproduce every one of these mistakes, enthusiastically. It will split code eagerly, ignore coupling analysis, and produce a plan that looks like microservices but behaves like a distributed monolith.

The powers encode the *right* approach: assess before you plan, plan before you execute, and be willing to recommend against decomposition when the codebase doesn't warrant it.

I built two separate powers — one for .NET, one for Java — because the technology stacks are different enough that a single power would either be too shallow or too confusing. A .NET team using Entity Framework 6 has completely different migration concerns than a Java team using JPA with Hibernate XML mappings. The pattern files, framework detection logic, and transformation guidance needed to be stack-specific.

---

## Anatomy of a Power

Both powers share the same structural model.

### POWER.md

The entry point. It declares:

- The power's name, description, and keywords (used for discoverability)
- A summary of what the power can handle (framework coverage, tech stack breadth)
- The full list of steering files and what each one does
- The phased workflow summary
- Onboarding instructions — what to read first and in what order
- Best practices that apply throughout all phases
- Complexity indicators — a reference table for gauging migration difficulty

The POWER.md is what Kiro reads when you first activate the power. It tells Kiro: here's what you're dealing with, here's how to proceed, here's where to look for specific guidance.

### Steering Files

Each power has two types:

**Core workflow files** — read in sequence, they drive the three-phase process:
- `assessment.md` — Phase 1
- `transformation.md` — Phases 2 and 3

**Reference files** — consulted as needed throughout any phase:
- `patterns.md` — core patterns index
- `patterns-aspnet.md` / `patterns-spring.md` — framework-specific patterns
- `patterns-ef.md` / `patterns-jpa.md` — data access patterns
- `patterns-auth.md` — authentication and authorization patterns
- `database-migration.md` — database decomposition guidance
- `traffic-cutover.md` — production migration strategy

The separation between workflow and reference matters. Kiro reads workflow files in order. It consults reference files on-demand when it encounters a specific technology or pattern. This keeps the core workflow readable and focused while still providing deep coverage for every edge case.

---

## The Three-Phase Design

Both powers use the same three-phase structure. This was the central design decision, and it's the thing that most distinguishes these powers from ad-hoc AI decomposition attempts.

### Phase 1: Assessment

Before any code changes, Kiro performs a deep analysis of the monolith. The assessment covers:

- **Project structure inventory** — modules, projects, framework versions
- **Technology stack fingerprinting** — every web framework, data access library, DI container, messaging system, and background processor detected
- **Domain model analysis** — entity relationships, aggregate boundaries, cross-boundary references
- **Dependency graph analysis** — at the project, namespace/package, and class levels
- **Coupling metrics** — afferent/efferent coupling, instability index, abstractness (following Robert Martin's metrics)
- **Shared state detection** — statics, singletons, ThreadLocal, ambient contexts
- **Communication pattern analysis** — synchronous calls, events, shared databases, file system coupling
- **Team structure analysis** — Conway's Law alignment between proposed service boundaries and actual team structure
- **Complexity scoring** — a defined formula produces a score per proposed boundary
- **Effort estimation** — mapped to complexity scores with technology-specific adjustment multipliers

The output is a comprehensive assessment report. It's not a plan — it's a diagnosis.

#### The Viability Gate

The most important thing the assessment can do is recommend against proceeding.

This is explicit in both powers' onboarding instructions:

> *If the viability gate recommends against decomposition, present that finding and do not proceed to transformation unless the user explicitly overrides.*

A small, well-structured monolith with a team of three engineers has no business being decomposed into microservices. The assessment will say so. This is not a failure — it's the power working correctly.

The viability gate evaluates:
- Team size and operational maturity
- Codebase size and coupling density
- Whether the complexity is inherent (domain) or accidental (bad architecture)
- Whether independent deployability actually matters for this team's release cadence

If the gate fires, the power presents the finding with specifics and stops. Proceeding requires explicit user override, which forces a conscious decision rather than an automated runaway.

### Phase 2: Planning

After the assessment is reviewed and approved, Kiro produces a transformation plan:

- Proposed service boundaries with DDD justification for each
- Service contract definitions — owned entities, exposed APIs, events published and consumed
- Migration order using a priority formula (least coupled extracts first)
- Shared library strategy — shared kernel vs. duplication vs. published packages
- Data ownership mapping and database splitting plan
- API contract definitions with versioning strategy
- Inter-service communication design (sync vs. async, request/reply vs. pub/sub)
- Cross-cutting concerns strategy — auth, logging, distributed tracing, health checks
- Rollback strategy for every migration step
- Traffic cutover strategy — feature flags, canary deployment, parallel-run validation

This plan requires explicit approval before any code is written. The human stays in the loop at the most important decision point.

### Phase 3: Execution

Only after plan approval does Kiro begin writing code. The execution phase scaffolds the entire new solution structure:

- New project/module structure per service
- Shared libraries extracted
- Domain models moved into bounded contexts
- API layers created
- DI rewired per service
- Data access split into service-scoped contexts/configurations
- Inter-service communication infrastructure built
- Dockerfiles and docker-compose generated
- Validation checklist produced

Phase 3 is designed to be incremental — one service at a time, starting with the least coupled. Each extraction is independently verifiable before the next begins.

---

## Power 1: .NET Microservices Extractor

### Coverage

The .NET extractor handles the full spectrum of .NET application patterns:

**Web frameworks:** ASP.NET MVC 3/4/5, Web API 2, ASP.NET Core MVC, Razor Pages, Blazor (Server and WebAssembly), Minimal APIs, WCF, gRPC, SignalR, Windows Services, console applications

**Data access:** Entity Framework 6, EF Core (all versions), Dapper, ADO.NET, NHibernate, Linq2Db

**DI containers:** Built-in, Autofac, Unity, Ninject, StructureMap, Castle Windsor, Simple Injector, Lamar

**Messaging:** MediatR, MassTransit, NServiceBus, Rebus, Brighter, Wolverine

**Runtime targets:** .NET Framework 3.5 through 4.8, .NET 5 through 9, .NET Standard bridging libraries, mixed-framework solutions

This breadth matters because real-world .NET monoliths are rarely clean. They're often multi-project solutions that have accumulated dependencies over a decade, mixing .NET Framework and .NET Core projects, using Autofac for registration in one area and Unity in another, calling stored procedures in some data access code while using EF in other parts.

### .NET-Specific Design Decisions

**DbContext splitting.** The patterns-ef.md file dedicates significant coverage to this because it's the hardest part of .NET decomposition. A shared DbContext that references entities across domain boundaries is common. The file provides concrete guidance on splitting it, handling cross-context references during the transition period, and migrating to service-scoped DbContexts without breaking existing behavior.

**Framework migration tracking.** When a solution mixes .NET Framework 4.7 and .NET Core 3.1 projects, the assessment needs to flag this and the transformation plan needs to account for it. The complexity indicator table uses framework version as a signal — .NET Framework 4.6 or older is high complexity, not because the code is worse but because the migration path involves more compatibility work.

**Strangler Fig via middleware.** The traffic-cutover.md file walks through implementing the Strangler Fig pattern using ASP.NET Core middleware and YARP (Yet Another Reverse Proxy) for routing. This lets the monolith and new services coexist during the transition with feature-flag controlled routing per endpoint.

**Complexity indicator table for .NET:**

| Indicator | Low | Medium | High |
|---|---|---|---|
| Project count | 1–5 | 6–15 | 16+ |
| Entity count | 1–20 | 21–50 | 51+ |
| DbContext count | 1 | 2–3 | 4+ |
| Circular dependencies | 0 | 1–2 | 3+ |
| Shared tables | 0–2 | 3–8 | 9+ |
| Stored procedures | 0–5 | 6–20 | 21+ |
| External integrations | 0–2 | 3–5 | 6+ |
| Framework version | .NET 6+ | .NET Framework 4.7+ | .NET Framework < 4.7 |
| Cross-boundary references | 0–5 | 6–15 | 16+ |

---

## Power 2: Java Microservices Extractor

### Coverage

The Java extractor covers the Java ecosystem with equivalent depth:

**Web frameworks:** Spring MVC, Spring Boot 1.x through 3.x, Spring WebFlux, JAX-RS (Jersey, RESTEasy), Jakarta EE, Servlets, JSP/Thymeleaf/Freemarker, Struts, Vaadin, Micronaut, Quarkus

**Data access:** Spring Data JPA, Hibernate (XML and annotation mappings), MyBatis, plain JDBC, jOOQ, Spring JDBC Template, R2DBC

**DI frameworks:** Spring IoC, CDI/Weld, Guice, Dagger, HK2

**Messaging:** Spring Events, Spring Integration, Apache Camel, Kafka Streams, JMS (ActiveMQ, IBM MQ, WebSphere MQ)

**Build systems:** Maven and Gradle, including multi-module projects

**Deployment targets:** Spring Boot fat JARs, WAR deployments to Tomcat/Jetty/WildFly, EAR deployments to WebSphere/WebLogic/JBoss

**Java versions:** 8 through 21, including modular Java (JPMS)

The deployment target coverage is important. A Spring Boot 3.x application and a WAR deployed to WebSphere have very different decomposition paths. The assessment detects which model is in use and adjusts the guidance accordingly.

### Java-Specific Design Decisions

**JPA entity splitting.** The patterns-jpa.md file is the most complex reference file in either power. JPA entity relationships across domain boundaries — particularly bidirectional associations and shared tables — are the most common source of failed Java decompositions. The file covers entity splitting strategies, handling of `@ManyToMany` with join tables, aggregate root identification, second-level cache implications, and multi-tenancy.

**Spring Security extraction.** Authentication is tightly coupled to the application context in Spring monoliths. The patterns-auth.md file provides guidance for each major Spring Security configuration style — XML config, Java config, OAuth2 resource servers, SAML — and maps each to a microservices-appropriate equivalent using Spring Security, Spring Authorization Server, or Keycloak.

**Feign vs. WebClient.** The transformation phase generates inter-service communication infrastructure. For Spring Boot 2.x codebases, Feign clients are idiomatic. For Spring Boot 3.x reactive codebases, WebClient is appropriate. The transformation.md file guides this decision based on detected stack.

**Strangler Fig via Spring Cloud Gateway.** The Java power implements the traffic routing pattern using Spring Cloud Gateway with route predicates and filters. This integrates naturally with Spring Boot service discovery (Eureka, Consul) and allows feature-flag-controlled routing per path.

**Database migration tooling.** Both Flyway and Liquibase are prevalent in Java codebases. The database-migration.md file covers both, plus Change Data Capture (CDC) using Debezium for scenarios where the database splitting must happen incrementally without application downtime.

**Complexity indicator table for Java:**

| Indicator | Low | Medium | High |
|---|---|---|---|
| Maven/Gradle module count | 1–5 | 6–15 | 16+ |
| JPA entity count | 1–20 | 21–50 | 51+ |
| DataSource count | 1 | 2–3 | 4+ |
| Circular package deps | 0 | 1–2 | 3+ |
| Shared tables | 0–2 | 3–8 | 9+ |
| Stored procedures / native queries | 0–5 | 6–20 | 21+ |
| External integrations | 0–2 | 3–5 | 6+ |
| Java version | 17+ | 11–16 | 8 or older |
| Spring Boot version | 3.x | 2.x | 1.x or none |
| Cross-boundary entity refs | 0–5 | 6–15 | 16+ |
| App server dependency | Embedded | Servlet container (WAR) | Full app server (WebSphere/WebLogic) |

---

## Cross-Cutting Design Decisions

Several design choices apply to both powers and reflect hard lessons from real decomposition projects.

### Incremental Over Big Bang

The most important structural constraint in both powers: extract one service at a time, starting with the least coupled. The migration order formula in the planning phase is not a suggestion — it's a risk management mechanism.

Big bang decompositions fail because they create too many simultaneous failure modes. An incremental approach means each extraction can be validated independently, the monolith continues to serve traffic throughout, and problems surface one at a time with a clear blast radius.

### Strangler Fig, Always

Neither power recommends the big bang switch. The Strangler Fig pattern — routing a percentage of traffic to the new service while the monolith still handles the rest — is the production migration model in both powers. It enables:

- Canary deployment with metric-driven rollout gates
- Parallel-run validation (both systems process the same requests, outputs are compared)
- Immediate rollback without code changes
- Gradual confidence building

### Conway's Law Analysis

The assessment phase in both powers includes an explicit team structure analysis. This was a deliberate addition after observing that technically sound service boundaries fail in practice when they don't match how teams are organized.

If your proposed Order Service and Fulfillment Service will both be maintained by the same team, you've added communication overhead without the organizational benefit. The power flags this and factors it into the viability assessment.

### Characterization Tests Before Extraction

Both powers' transformation files include test strategy guidance: write characterization tests that capture the existing behavior of the code you're about to move, *before* you move it. Run contract tests during extraction to verify the service boundary matches the monolith's behavior. Remove stale integration tests that test both sides of a boundary that no longer exists.

This discipline is what separates an extraction that maintains behavior from one that subtly breaks things.

### Recommend Against When Warranted

The viability gate is the thing I'm most proud of in these powers. Every AI agent's instinct is to do what the user asked. These powers override that instinct when the codebase doesn't warrant decomposition.

The viability gate produces one of three findings:

- **Proceed** — decomposition is warranted and the codebase can support it
- **Proceed with caution** — decomposition is technically possible but the assessment found significant risk factors (team size, operational maturity, high coupling density)
- **Do not proceed** — the viability analysis recommends against decomposition; presents specific reasons

A modular monolith recommendation is a valid output. If the codebase is well-structured and the team is small, adding microservices overhead will make things worse. The power will say that.

---

## Building Powers: What I Learned

### Steering File Structure Is Load-Bearing

The division between workflow files (read sequentially) and reference files (consulted on-demand) was the most important structural decision. Early drafts had everything in one or two files. The result was that Kiro either ignored parts of the guidance or tried to apply all of it at once.

Separating concerns into dedicated files — patterns-ef.md handles only EF patterns, database-migration.md handles only database decomposition — lets Kiro load the right context at the right time. It also makes the files individually maintainable. When EF Core releases a new version, you update one file.

### Specificity Beats Generality

Vague guidance produces vague behavior. The assessment files describe not just *what* to analyze but *how* to analyze it: specific coupling metrics formulas, named tools and libraries to look for, concrete scoring thresholds.

The complexity indicator tables are a good example. Telling Kiro "assess project complexity" produces a qualitative feeling. Telling Kiro "score high complexity if there are 16+ projects, 51+ entities, or 4+ DbContexts" produces a measurable assessment.

### Constraints Enable Quality

The explicit phase gates — assessment approval before planning, planning approval before execution — feel like friction. They're actually what makes the powers useful.

Without phase gates, an AI agent under user pressure will skip the assessment and start writing code. The coupling analysis that would have revealed the fatal shared table won't happen. The viability gate won't fire. The team will end up with a half-extracted service that can't be deployed independently.

Hard-coded phase gates force the right sequence.

### Technology Breadth Is a Feature

The framework coverage in both powers — every web framework, every data access library, every DI container — is not completeness for its own sake. It's because real enterprise monoliths use all of it.

A power that can only handle Spring Boot 3.x MVC with Spring Data JPA is not useful for the majority of Java monoliths that need decomposing. Those monoliths are running Spring Boot 1.5, mixing Hibernate XML configs with annotation-based JPA, deployed as WARs to Tomcat, and using LDAP for authentication. The power needs to handle that.

---

## Using the Powers

Both powers are in the [agentic-playground repository](https://github.com/ndgbg/agentic-playground/tree/main/kiro-powers):

```
kiro-powers/
├── dotnet-microservices-extractor/
│   ├── POWER.md
│   └── steering/
│       ├── assessment.md
│       ├── transformation.md
│       ├── patterns.md
│       ├── patterns-aspnet.md
│       ├── patterns-ef.md
│       ├── patterns-auth.md
│       ├── database-migration.md
│       └── traffic-cutover.md
└── java-microservices-extractor/
    ├── POWER.md
    └── steering/
        ├── assessment.md
        ├── transformation.md
        ├── patterns.md
        ├── patterns-spring.md
        ├── patterns-jpa.md
        ├── patterns-auth.md
        ├── database-migration.md
        └── traffic-cutover.md
```

### What to Expect

When you activate one of these powers on a monolith, here's what happens:

1. Kiro reads POWER.md and the assessment steering file
2. It scans your codebase — this takes time proportional to codebase size
3. It produces a written assessment report covering every analysis dimension
4. **You review the report.** This is where you provide domain knowledge Kiro can't infer — team structure, organizational constraints, planned feature work that would change the boundaries
5. If the viability gate fires, the power stops. You decide whether to override
6. After approval, Kiro produces the transformation plan
7. **You review the plan.** Service boundaries, migration order, shared library decisions
8. After plan approval, execution begins incrementally

The powers are designed to keep humans in the loop at the decisions that matter. Everything between those gates is automated.

---

## What's Next

The three-phase assessment-plan-execute model works for any large-scale codebase transformation, not just microservices extraction. Possible extensions:

- **Ruby on Rails extractor** — same model, Rails-specific patterns (Active Record associations, concerns, engines)
- **Database modernization power** — assess stored procedure usage, plan migration to application-level logic, execute incrementally
- **Monolith modularization power** — for teams that run the viability gate and get "proceed with caution," a power that guides them to a well-structured modular monolith instead

The underlying insight is that AI agents are most useful for complex transformations when they have structured domain knowledge and explicit procedural constraints. Powers are the mechanism for encoding both.

---

## Conclusion

Kiro powers let you package domain expertise into a form that an AI agent can reliably use. The microservices extractors aren't clever — they're thorough. They encode the same discipline that experienced engineers apply when guiding a real migration: assess first, plan before coding, migrate incrementally, be honest about whether decomposition is warranted.

The difference is that the discipline now travels with the power, not just with the engineer.

Both powers are open and available. Point them at a monolith and see what the assessment says.
