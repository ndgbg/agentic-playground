# .NET Patterns Reference Guide

Comprehensive reference for handling specific .NET patterns during monolith-to-microservices decomposition. This file covers the most commonly needed patterns during transformation. For specialized topics, consult the targeted sub-files:

- **patterns-aspnet.md** — ASP.NET MVC 5, Web API 2, ASP.NET Core, Razor Pages, Blazor, Minimal APIs
- **patterns-ef.md** — Entity Framework 6 and EF Core patterns (DbContext splitting, inheritance, relationships, interceptors)
- **patterns-auth.md** — Authentication and authorization (ASP.NET Identity, IdentityServer, Windows Auth, claims)

---

## Dependency Injection Patterns

### Autofac Modules
**Pattern:** Autofac modules organizing DI registrations by feature.
**Resolution:**
- Modules often map to bounded contexts
- Each service gets its own DI configuration (can use built-in .NET DI or keep Autofac)
- Module registrations split by service ownership
- Autofac lifetime scopes → built-in DI scopes (Scoped, Transient, Singleton)

### Unity Container
**Pattern:** Unity DI container with XML or code-based registration.
**Resolution:**
- Convert to built-in .NET Core DI during migration
- Unity's hierarchical containers → DI scopes
- Named registrations → use factory pattern or keyed services (.NET 8+)
- Property injection → constructor injection

### Service Locator Anti-Pattern
**Pattern:** Using IServiceProvider.GetService() or a static service locator throughout code.
**Resolution:**
- Refactor to constructor injection during extraction
- Each service should use proper DI
- Remove static service locator references
- If service locator is deeply embedded, refactor incrementally

### Decorator and Pipeline Patterns
**Pattern:** DI-based decorators or MediatR pipeline behaviors.
**Resolution:**
- Cross-cutting decorators (logging, validation, caching) → shared package
- Domain-specific decorators → move with their service
- MediatR pipelines replicated per service
- Scrutor-based decorators → replicate registration per service

### Factory Patterns
**Pattern:** Abstract factories or factory methods registered in DI.
**Resolution:**
- Factories that create entities for one service → move with that service
- Factories that create cross-cutting infrastructure → shared package
- Factory registrations move with their consumers

### Keyed Services (.NET 8+)
**Pattern:** Multiple implementations of the same interface resolved by key.
**Resolution:**
- If all implementations belong to one service → move together
- If implementations span services → each service registers only its own
- Key-based resolution may simplify to single implementation per service

---

## Data Access Patterns

### Repository Pattern
**Pattern:** Generic or specific repository classes wrapping DbContext.
**Resolution:**
- Each service gets its own repository implementations
- Generic repository base class → shared infrastructure package
- Specific repositories → move with their service's domain
- Repository interfaces in Core, implementations in Infrastructure

### Unit of Work
**Pattern:** UnitOfWork class coordinating multiple repository saves.
**Resolution:**
- Each service gets its own Unit of Work scoped to its DbContext
- Cross-service transactions → replace with saga pattern or eventual consistency
- Remove cross-context transaction coordination
- DbContext itself acts as Unit of Work in EF Core

### CQRS (Command Query Responsibility Segregation)
**Pattern:** Separate read and write models, often with MediatR.
**Resolution:**
- Commands and queries split by service ownership
- Each service gets its own command/query handlers
- Read models may need to aggregate data from multiple services → use API composition or materialized views
- Event sourcing (if used) → each service has its own event store

### Specification Pattern
**Pattern:** Specification classes encapsulating query criteria.
**Resolution:**
- Specifications move with their entity's owning service
- Shared specification base class → shared kernel
- Cross-entity specifications → split or move to the primary entity's service

### Stored Procedures
**Pattern:** Business logic in SQL stored procedures.
**Resolution:**
- Procedures that touch single-service tables → move with that service
- Procedures that join across service boundaries → rewrite as service calls + in-memory joins
- Consider replacing simple procedures with EF queries
- Complex procedures may need to become domain services
- See database-migration steering file for detailed procedure migration strategies

### Raw SQL and Dapper Queries
**Pattern:** Inline SQL or Dapper queries in repositories or services.
**Resolution:**
- Queries scoped to one service's tables → move with that service
- Cross-service joins → split into multiple service calls
- Ensure connection strings point to service-specific databases
- Dapper query objects → move with their service

---

## Communication Patterns

### Direct Service Calls (In-Process)
**Pattern:** Service A directly calls Service B's methods (both in same process).
**Resolution:**
- Replace with HTTP/gRPC calls between services
- Define API contracts in Contracts projects
- Add resilience (retry, circuit breaker) with Polly
- Consider async messaging for non-time-sensitive operations
- Performance impact: ~1-10ms in-process → ~10-100ms HTTP (plan accordingly)

### MediatR Notifications
**Pattern:** In-process domain events via MediatR INotification.
**Resolution:**
- Intra-service notifications → keep as MediatR within the service
- Cross-service notifications → convert to integration events via message broker
- Define integration event contracts in Contracts projects
- Ensure handlers are idempotent when converting to distributed events

### SignalR Hubs
**Pattern:** Real-time communication via SignalR hubs.
**Resolution:**
- Hub stays with the service that owns the real-time feature
- If multiple services need to push to clients → use a dedicated notification service
- Consider SignalR backplane (Redis) for scaling across service instances
- Client connections managed by gateway or dedicated SignalR service

### Background Jobs (Hangfire/Quartz)
**Pattern:** Background job processing with Hangfire or Quartz.NET.
**Resolution:**
- Jobs scoped to one domain → move with that service
- Jobs that span domains → split into service-specific jobs with event coordination
- Each service gets its own job storage/database
- Consider replacing cross-service jobs with event-driven workflows
- Hangfire dashboard → per-service or centralized monitoring

### gRPC Services
**Pattern:** gRPC service definitions with .proto files.
**Resolution:**
- Each .proto file typically maps to one service
- Shared .proto definitions → Contracts project
- gRPC is excellent for inter-service communication (faster than REST)
- Consider gRPC for internal service-to-service, REST for external APIs

### OData Endpoints
**Pattern:** OData controllers with queryable endpoints.
**Resolution:**
- OData endpoints move with their entity's owning service
- Cross-entity OData queries ($expand across services) → not supported, use API composition
- Consider replacing OData with purpose-built REST endpoints for simpler contracts

### GraphQL
**Pattern:** GraphQL schema with resolvers spanning multiple domains.
**Resolution:**
- Option 1: GraphQL gateway that federates across services (Apollo Federation pattern)
- Option 2: Per-service GraphQL schemas composed at the gateway
- Option 3: Replace with REST APIs per service (simpler)
- Resolvers that fetch from multiple domains → gateway handles composition

---

## Configuration and Caching Patterns

### Static Configuration Classes
**Pattern:** Static classes holding configuration values loaded at startup.
**Resolution:** Replace with IOptions<T> pattern per service. Each service defines its own strongly-typed configuration classes.

### ConfigurationManager (.NET Framework)
**Pattern:** System.Configuration.ConfigurationManager for .NET Framework.
**Resolution:** Migrate to Microsoft.Extensions.Configuration. Replace ConfigurationManager.AppSettings with IConfiguration.

### In-Memory Cache (MemoryCache)
**Pattern:** IMemoryCache or System.Runtime.Caching.MemoryCache.
**Resolution:** Each service gets its own in-memory cache. Cache keys must be scoped to the service. Consider distributed cache (Redis) for shared data.

### Distributed Cache (Redis)
**Pattern:** IDistributedCache with Redis backend.
**Resolution:** Each service can use Redis but with service-prefixed keys. Or each service gets its own Redis database (0-15). Cache invalidation across services → pub/sub events.

---

## Anti-Patterns to Watch For

### God Classes
**Pattern:** Large classes with many responsibilities (e.g., a 2000-line OrderService).
**Resolution:** Split by responsibility during extraction. Each microservice gets only the methods relevant to its domain.

### Circular Dependencies
**Pattern:** Project A references Project B which references Project A.
**Resolution:** Must be broken before extraction. Extract shared interfaces into a separate project. Use dependency inversion.

### Tight Database Coupling
**Pattern:** Services directly querying each other's tables via joins or views.
**Resolution:** Replace with API calls between services. Create materialized views or read models for query-heavy scenarios. See database-migration steering file.

### Shared Mutable State
**Pattern:** Static variables, singletons, or in-memory caches shared across features.
**Resolution:** Each service gets its own cache/state. Shared state → distributed cache (Redis) or dedicated state service.

### Distributed Monolith
**Warning:** Splitting a monolith into services that are still tightly coupled creates a distributed monolith — worse than the original.
**Prevention:**
- Each service must be independently deployable
- Minimize synchronous inter-service calls
- Prefer events over direct API calls where possible
- Each service owns its data completely
- No shared databases in the final state
- Test: can you deploy Service A without deploying Service B? If not, boundaries are wrong

### Anemic Domain Model
**Pattern:** Entity classes with only properties (no behavior), all logic in service classes.
**Resolution:** During extraction, consider enriching entities with domain behavior. This is optional but improves the domain model.

### Leaky Abstractions
**Pattern:** Interfaces that expose infrastructure details (e.g., IQueryable<T> in repository interfaces).
**Resolution:** Repository interfaces should return domain types, not IQueryable. Service interfaces should use domain DTOs, not EF entities.

### Over-Engineering
**Warning:** Don't add patterns that aren't needed.
**Guidance:**
- Not every service needs CQRS or event sourcing
- Not every service needs a message broker (start with HTTP, add messaging when needed)
- Keep it simple — complexity should be justified by requirements

---

## Framework Migration: .NET Framework → .NET 8+

When the monolith is on .NET Framework and services target modern .NET:

### Step 1: Identify Compatibility
- Check all NuGet packages for .NET 8 compatibility
- Identify System.Web dependencies (not available in .NET Core)
- Check for Windows-specific APIs (Registry, WMI, COM interop)
- Use the .NET Upgrade Assistant tool for automated analysis

### Step 2: Bridge with .NET Standard
- Create .NET Standard 2.0 libraries for shared code
- Both .NET Framework and .NET 8 can reference .NET Standard 2.0
- Gradually move code from .NET Framework projects to .NET Standard

### Step 3: Replace Incompatible APIs

| .NET Framework API | .NET 8 Replacement |
|--------------------|--------------------|
| System.Web.HttpContext | Microsoft.AspNetCore.Http.HttpContext |
| System.Web.Mvc | Microsoft.AspNetCore.Mvc |
| System.Web.Http | Microsoft.AspNetCore.Mvc (unified) |
| ConfigurationManager | IConfiguration |
| HttpRuntime.AppDomainAppPath | IWebHostEnvironment.ContentRootPath |
| System.Drawing | SkiaSharp or ImageSharp |
| System.Data.SqlClient | Microsoft.Data.SqlClient |
| EntityFramework 6 | EntityFrameworkCore |
| WCF client | gRPC or HttpClient |

### Step 4: Strangler Fig Pattern
- New microservices built on .NET 8
- Monolith stays on .NET Framework during transition
- API Gateway routes requests to new services or monolith
- Gradually move functionality from monolith to services
- Monolith shrinks over time until it can be decommissioned
- See traffic-cutover steering file for detailed implementation
