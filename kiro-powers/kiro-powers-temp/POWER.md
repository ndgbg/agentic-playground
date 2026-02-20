---
name: "dotnet-microservices-extractor"
displayName: ".NET Microservices Extractor"
description: "Analyzes .NET monolithic codebases, produces detailed assessments of bounded contexts and coupling, then executes a structured transformation into microservices."
keywords: ["dotnet", "microservices", "monolith", "csharp", "decomposition"]
author: "Nida Beig"
---

# .NET Microservices Extractor

## Overview

This power guides Kiro through a structured monolith-to-microservices transformation for .NET codebases. It works in three phases: assessment, planning, and execution.

The power handles the full spectrum of .NET application patterns including ASP.NET MVC (3/4/5), Web API 2, ASP.NET Core MVC, Web API, Razor Pages, Blazor (Server and WebAssembly), Minimal APIs, WCF, gRPC, SignalR, Windows Services, and console applications. It understands Entity Framework 6, Entity Framework Core (all versions), Dapper, ADO.NET, NHibernate, and Linq2Db for data access. It handles all major DI containers (built-in, Autofac, Unity, Ninject, StructureMap, Castle Windsor, Simple Injector, Lamar), messaging frameworks (MediatR, MassTransit, NServiceBus, Rebus, Brighter, Wolverine), and background processing (Hangfire, Quartz.NET, IHostedService, Windows Services).

It supports both .NET Framework (3.5, 4.0, 4.5, 4.6, 4.7, 4.8) and modern .NET (5, 6, 7, 8, 9) project structures, including mixed-framework solutions and .NET Standard bridging libraries.

Rather than blindly splitting code, this power performs deep analysis of domain boundaries, data ownership, coupling patterns, shared dependencies, transactional boundaries, and runtime behavior to produce an informed decomposition strategy before making any changes.

## Available Steering Files

This power has four steering files for the phased workflow:

- **assessment** — Phase 1: Codebase scanning, dependency analysis, bounded context identification, complexity metrics, and comprehensive assessment report generation
- **transformation** — Phase 2: Microservices breakdown planning and Phase 3: Executing the code transformation with full project scaffolding
- **patterns** — Reference guide for .NET-specific patterns, anti-patterns, framework migration strategies, and how to handle them during decomposition
- **database-migration** — Detailed guide for database decomposition, schema splitting, data migration scripts, and eventual consistency patterns

Read these in order. Start with assessment, then move to transformation once the assessment is reviewed and approved. Consult patterns and database-migration as reference during any phase.

## Workflow Overview

### Phase 1: Assessment (steering/assessment.md)

Scan the monolith and produce a detailed report covering:
- Solution and project structure inventory with framework versions
- Technology stack fingerprinting (web frameworks, data access, DI, messaging, caching, logging)
- Domain model analysis and bounded context identification using DDD principles
- Entity relationship mapping with cross-boundary reference detection
- Dependency graph analysis (project-level, namespace-level, class-level)
- NuGet package audit with version compatibility assessment
- Data access layer deep analysis (DbContext boundaries, stored procedures, raw SQL, cross-context joins)
- Coupling metrics (afferent/efferent coupling, instability index, abstractness)
- Shared state detection (statics, singletons, session, HttpContext, ambient contexts)
- Communication pattern analysis (synchronous calls, events, shared databases, file system)
- Configuration and secrets management analysis
- Authentication and authorization flow mapping
- Background job and scheduled task inventory
- External integration points (third-party APIs, file systems, message queues, email)
- Complexity scoring per proposed service boundary
- Risk assessment with mitigation strategies

### Phase 2: Planning (steering/transformation.md — first half)

Based on the assessment, produce a transformation plan:
- Proposed microservice boundaries with DDD justification
- Service contract definitions (owned entities, exposed APIs, events published/consumed)
- Migration order determined by coupling analysis (least coupled first)
- Shared library extraction strategy (shared kernel vs duplication vs packages)
- Data ownership mapping and database splitting plan
- API contract definitions with versioning strategy
- Inter-service communication design (sync vs async, request/reply vs pub/sub)
- Cross-cutting concerns strategy (auth, logging, configuration, health checks, tracing)
- API gateway and BFF pattern recommendations
- Service mesh and infrastructure considerations
- Rollback strategy for each migration step
- Estimated effort and complexity per service extraction

### Phase 3: Execution (steering/transformation.md — second half)

Execute the transformation:
- Create new solution structure with clean architecture per service
- Scaffold all project files (.csproj) with correct dependencies
- Extract domain models, value objects, and aggregates into bounded contexts
- Create API contracts (DTOs, request/response models, integration events)
- Build API controllers with proper REST conventions and error handling
- Rewire dependency injection with service-specific registrations
- Split data access layers with service-scoped DbContexts
- Create inter-service communication infrastructure (HTTP clients, event bus)
- Implement cross-cutting concerns (auth middleware, logging, health checks, correlation IDs)
- Generate Dockerfiles per service with multi-stage builds
- Generate docker-compose for full local development environment
- Create API gateway configuration (if applicable)
- Produce validation checklist and compilation verification
- Generate migration scripts for database decomposition

## Onboarding

When this power is activated for a .NET codebase:

1. Read the **assessment** steering file first
2. Follow every step in the assessment phase — do not skip any analysis
3. Present the complete assessment report to the user
4. Wait for explicit user approval before proceeding
5. Read the **transformation** steering file
6. Present the transformation plan for approval
7. Execute the transformation only after plan approval
8. Consult **patterns** whenever encountering a specific .NET pattern during any phase
9. Consult **database-migration** when planning or executing data layer changes

## Best Practices

- Always complete the full assessment before proposing any changes — never skip to execution
- Present the assessment to the user for review before proceeding to transformation
- Migrate incrementally — extract one service at a time, starting with the least coupled
- Preserve existing functionality — the transformation must not change business logic
- Keep shared kernel minimal — only truly shared domain concepts belong in a shared library
- Prefer API contracts over shared model libraries between services
- Each microservice must own its data — no shared databases in the final state
- Generate integration points (API clients, message contracts) alongside the services
- Always consider the Strangler Fig pattern — the monolith and microservices can coexist during migration
- Plan for rollback at every step — each extraction should be reversible
- Favor eventual consistency over distributed transactions
- Design APIs contract-first before implementing
- Include health checks and observability from day one
- Never create a distributed monolith — if services can't be deployed independently, the boundaries are wrong
- Consider team structure and Conway's Law when defining service boundaries
- Document every decision and trade-off in the assessment and plan

## Complexity Indicators

Use these to gauge the overall difficulty of the transformation:

| Indicator | Low Complexity | Medium Complexity | High Complexity |
|-----------|---------------|-------------------|-----------------|
| Project count | 1-5 | 6-15 | 16+ |
| Entity count | 1-20 | 21-50 | 51+ |
| DbContext count | 1 | 2-3 | 4+ |
| Circular dependencies | 0 | 1-2 | 3+ |
| Shared tables | 0-2 | 3-8 | 9+ |
| Stored procedures | 0-5 | 6-20 | 21+ |
| External integrations | 0-2 | 3-5 | 6+ |
| Framework version | .NET 6+ | .NET Framework 4.7+ | .NET Framework < 4.7 |
| Cross-boundary references | 0-5 | 6-15 | 16+ |
