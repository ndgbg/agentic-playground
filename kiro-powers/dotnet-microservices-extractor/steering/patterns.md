# .NET Patterns Reference Guide

Comprehensive reference for handling specific .NET patterns during monolith-to-microservices decomposition. Consult this when encountering these patterns during assessment or transformation.

---

## ASP.NET MVC 5 / Web API 2 (.NET Framework)

### Controllers with Mixed Responsibilities
**Pattern:** A single controller handles multiple domain concerns (e.g., OrderController managing orders, inventory, and shipping).
**Resolution:**
- Split controller actions by bounded context
- Each microservice gets only the actions relevant to its domain
- Shared action filters and attributes need to be moved to a shared package or duplicated
- If controller has 500+ lines, it almost certainly spans multiple contexts

### Areas
**Pattern:** ASP.NET MVC Areas used to organize features (e.g., Areas/Admin, Areas/Storefront).
**Resolution:**
- Areas often map naturally to bounded contexts
- Each area may become its own microservice or be grouped with related services
- Shared layouts and partial views need resolution — each service gets its own UI or a shared UI gateway handles composition
- Area registration code (AreaRegistration classes) maps to service routing

### Global.asax and OWIN Startup
**Pattern:** Application startup configured in Global.asax or OWIN Startup class.
**Resolution:**
- Each microservice gets its own Program.cs / Startup.cs
- Migrate relevant middleware and configuration per service
- Global filters, route config, and bundle config split by service
- Application_Start event handlers → service-specific initialization
- Application_Error → ExceptionHandlingMiddleware per service

### Web.config Transformation
**Pattern:** Monolithic Web.config with connection strings, app settings, system configuration, and config transforms for environments.
**Resolution:**
- Each service gets its own appsettings.json (if migrating to .NET Core) or Web.config
- Connection strings scoped to service-specific databases
- Shared settings moved to environment variables or a configuration service
- Config transforms → appsettings.{Environment}.json files
- Custom config sections → strongly-typed IOptions<T> classes
- httpModules/httpHandlers → middleware pipeline

### Bundling and Minification
**Pattern:** BundleConfig.cs with CSS/JS bundles for the monolith UI.
**Resolution:**
- If services have their own UI, each gets its own bundling
- If using a shared UI gateway / BFF, bundling stays there
- Consider migrating to modern bundling (webpack, Vite) during extraction
- Static assets may move to a CDN or dedicated static file service

### Route Configuration
**Pattern:** RouteConfig.cs with centralized route definitions.
**Resolution:**
- Each service defines its own routes via attribute routing
- API services use [Route("api/[controller]")] convention
- Legacy route patterns may need URL rewriting at the gateway level
- Custom route constraints move with their owning service

### HTTP Modules and Handlers
**Pattern:** Custom IHttpModule and IHttpHandler implementations.
**Resolution:**
- Convert to ASP.NET Core middleware
- Authentication modules → JWT middleware
- Logging modules → Serilog middleware
- Custom handlers → controller actions or minimal API endpoints
- Module ordering → middleware pipeline ordering

---

## ASP.NET Core Patterns

### Minimal APIs
**Pattern:** Endpoints defined directly in Program.cs using MapGet, MapPost, etc.
**Resolution:**
- Group endpoints by domain concern
- Each service gets its own set of minimal API endpoints
- Shared endpoint filters and middleware duplicated or packaged
- Consider organizing with Carter or endpoint grouping for larger services

### Razor Pages
**Pattern:** Page-based model with .cshtml + .cshtml.cs pairs.
**Resolution:**
- Pages grouped by feature/domain become part of the owning service
- If services need UI, each gets its own Razor Pages project
- Consider a BFF (Backend for Frontend) pattern for UI composition
- Shared _Layout.cshtml → each service has its own or use micro-frontends

### Blazor Components
**Pattern:** Blazor Server or WebAssembly components with shared state.
**Resolution:**
- Components grouped by domain
- Shared component libraries for UI primitives (buttons, forms, layouts)
- Each service can expose its own Blazor components
- State management scoped per service (no shared cascading state across services)
- Blazor Server circuits → one per service or use a BFF
- Blazor WASM → can call multiple service APIs directly

### Middleware Pipeline
**Pattern:** Custom middleware in the request pipeline.
**Resolution:**
- Cross-cutting middleware (auth, logging, error handling) → shared NuGet package (BuildingBlocks)
- Domain-specific middleware → moves with its service
- Order-dependent middleware chains need careful replication per service
- Middleware that accesses multiple DbContexts → split or move to gateway

### Feature Folders / Vertical Slices
**Pattern:** Code organized by feature rather than by layer (e.g., Features/Orders/ contains controller, handler, validator, DTO).
**Resolution:**
- Feature folders often map directly to bounded contexts
- Each feature folder may become a microservice
- Shared features need careful analysis — they may indicate a shared kernel
- MediatR handlers within features move with their service

### IHostedService / BackgroundService
**Pattern:** Background tasks running within the web host.
**Resolution:**
- Tasks scoped to one domain → move with that service
- Tasks that span domains → split into service-specific tasks with event coordination
- Consider extracting long-running tasks into dedicated worker services
- Ensure graceful shutdown handling in each service

---

## Entity Framework Patterns

### Single Large DbContext (God Context)
**Pattern:** One DbContext with 50+ DbSets covering the entire domain.
**Resolution:**
- Split into one DbContext per microservice
- Each context includes only its owned entities
- Remove navigation properties that cross service boundaries
- Cross-service relationships become ID-only references
- OnModelCreating configurations split by entity ownership
- Shared configurations (e.g., audit columns) → base configuration class

### Multiple DbContexts (Already Split)
**Pattern:** Monolith already uses multiple DbContexts for different areas.
**Resolution:**
- Existing context boundaries may align with service boundaries
- Validate that context boundaries match domain boundaries
- May need to further split or merge contexts
- Check for entities registered in multiple contexts (shared entities)

### EDMX (Database First)
**Pattern:** Entity Framework using .edmx visual designer files.
**Resolution:**
- Convert to Code First during migration
- Use EF Power Tools or `Scaffold-DbContext` to generate entity classes from database
- Create Fluent API configurations from EDMX mappings
- Each service gets Code First entities for its owned tables
- Complex EDMX mappings (table splitting, entity splitting) need manual conversion

### Table-Per-Hierarchy (TPH) Inheritance
**Pattern:** Multiple entity types stored in a single table with a discriminator column.
**Resolution:**
- If all types belong to one service → move the entire hierarchy
- If types span services → split the table (each service gets its own table for its types)
- Discriminator column may need to be replicated or removed
- Consider converting to Table-Per-Type (TPT) during migration for cleaner separation

### Table-Per-Type (TPT) Inheritance
**Pattern:** Each entity type in the hierarchy has its own table.
**Resolution:**
- Base table ownership must be assigned to one service
- Derived type tables move with their owning service
- Cross-service inheritance hierarchies need to be broken (use composition instead)

### Many-to-Many Relationships
**Pattern:** Join tables for many-to-many relationships (explicit or implicit in EF Core 5+).
**Resolution:**
- If both entities are in the same service → keep the join table
- If entities are in different services → the join table goes with the service that "owns" the relationship
- The other service queries via API to get related IDs
- Consider denormalizing if query performance is critical

### Owned Types and Value Objects
**Pattern:** EF Core Owned Types or DDD Value Objects mapped to database columns.
**Resolution:**
- Owned types stay with their owning entity
- If the parent entity moves to a service, owned types move with it
- Value objects shared across services → duplicate in each service or put in shared kernel
- Complex owned types with their own table → move with parent entity

### Global Query Filters
**Pattern:** HasQueryFilter() for soft delete, multi-tenancy, etc.
**Resolution:**
- Each service's DbContext replicates relevant filters
- Tenant filtering may need a shared approach (tenant ID from JWT claims)
- Soft delete filters move with their entities
- Be careful with IgnoreQueryFilters() calls — they need to move too

### Interceptors and SaveChanges Overrides
**Pattern:** Custom logic in SaveChanges or via EF interceptors (auditing, timestamps, etc.).
**Resolution:**
- Audit interceptors → shared infrastructure package (BuildingBlocks)
- Domain-specific interceptors → move with their service
- Cross-cutting interceptors → replicate per service
- SaveChanges overrides → convert to interceptors for better separation

### Compiled Queries
**Pattern:** EF.CompileQuery() or EF.CompileAsyncQuery() for performance.
**Resolution:**
- Move compiled queries with their owning service
- Queries that join across service boundaries need rewriting
- Consider if compiled queries are still needed (EF Core has better query caching)

### Raw SQL and FromSqlRaw
**Pattern:** Direct SQL execution via FromSqlRaw, ExecuteSqlRaw, or SqlQuery.
**Resolution:**
- Queries scoped to one service's tables → move with that service
- Cross-service SQL queries → split into multiple service calls
- Ensure SQL references correct schema/database after migration
- Parameterized queries must remain parameterized (security)

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

## Authentication & Authorization Patterns

### ASP.NET Identity (Full Framework)
**Pattern:** ASP.NET Identity with IdentityDbContext, UserManager, SignInManager.
**Resolution:**
- Extract into a dedicated Identity/Auth microservice
- Other services validate JWT tokens (no direct Identity dependency)
- Identity service owns: AspNetUsers, AspNetRoles, AspNetUserRoles, AspNetUserClaims, etc.
- Migrate from cookie auth to JWT for service-to-service communication
- Keep cookie auth at the gateway/BFF level for browser clients

### ASP.NET Core Identity
**Pattern:** ASP.NET Core Identity with modern configuration.
**Resolution:**
- Same as above but easier migration (already uses modern patterns)
- Identity service can use IdentityServer/Duende for token issuance
- Other services only need JWT validation middleware

### IdentityServer / Duende IdentityServer
**Pattern:** OAuth2/OpenID Connect server for token issuance.
**Resolution:**
- IdentityServer becomes the Identity microservice (or stays as a standalone service)
- All other services validate tokens against IdentityServer's JWKS endpoint
- Client credentials flow for service-to-service authentication
- Authorization code flow for user-facing applications

### Custom Authorization Attributes
**Pattern:** Custom [Authorize] attributes with business logic.
**Resolution:**
- Simple role/policy checks → replicate per service
- Complex authorization with data access → move to the owning service
- Consider a centralized authorization service for complex policies (e.g., OPA, Casbin)
- Resource-based authorization → stays with the resource-owning service

### Windows Authentication
**Pattern:** Integrated Windows Authentication (IWA) in intranet apps.
**Resolution:**
- May need to convert to token-based auth for microservices
- Use a gateway that handles Windows Auth and issues JWT tokens
- Services validate JWT tokens internally
- Kerberos delegation → replace with token forwarding

### Claims Transformation
**Pattern:** Custom IClaimsTransformation that enriches claims from database.
**Resolution:**
- Claims transformation moves to the Identity service
- Or: each service enriches claims from its own data as needed
- Avoid cross-service claims enrichment (adds coupling)

---

## Configuration Patterns

### Static Configuration Classes
**Pattern:** Static classes holding configuration values loaded at startup.
**Resolution:**
- Replace with IOptions<T> pattern per service
- Each service defines its own strongly-typed configuration classes
- Configuration loaded from appsettings.json and environment variables
- Add validation with ValidateDataAnnotations() and ValidateOnStart()

### ConfigurationManager (.NET Framework)
**Pattern:** System.Configuration.ConfigurationManager for .NET Framework.
**Resolution:**
- Migrate to Microsoft.Extensions.Configuration
- Each service gets its own configuration pipeline
- Replace ConfigurationManager.AppSettings with IConfiguration
- Replace custom ConfigurationSection with IOptions<T>

### Custom Configuration Providers
**Pattern:** Custom IConfigurationProvider for database-backed or remote configuration.
**Resolution:**
- Each service can have its own configuration provider
- Shared configuration → environment variables or centralized config service
- Database-backed config → consider if each service needs its own config table

---

## Caching Patterns

### In-Memory Cache (MemoryCache)
**Pattern:** IMemoryCache or System.Runtime.Caching.MemoryCache for local caching.
**Resolution:**
- Each service gets its own in-memory cache
- Cache keys must be scoped to the service (no cross-service cache sharing)
- Consider if in-memory cache is sufficient or if distributed cache (Redis) is needed
- Cache invalidation → event-driven (subscribe to change events from owning service)

### Distributed Cache (Redis)
**Pattern:** IDistributedCache with Redis backend.
**Resolution:**
- Each service can use Redis but with service-prefixed keys
- Or: each service gets its own Redis database (0-15)
- Cache invalidation across services → pub/sub events
- Session state in Redis → move to Identity/Gateway service

### Output Caching / Response Caching
**Pattern:** [ResponseCache] attribute or output caching middleware.
**Resolution:**
- Each service configures its own response caching
- API Gateway can add caching layer on top
- Cache-Control headers set per service based on data volatility

---

## Logging Patterns

### Multiple Logging Frameworks
**Pattern:** Mix of Serilog, NLog, log4net, and Microsoft.Extensions.Logging.
**Resolution:**
- Standardize on one framework (Serilog recommended) during extraction
- Each service configures logging independently
- Shared logging configuration → BuildingBlocks package
- Ensure all services use structured logging with consistent property names

### Custom Log Enrichers
**Pattern:** Custom Serilog enrichers or NLog layout renderers.
**Resolution:**
- Cross-cutting enrichers (CorrelationId, ServiceName) → BuildingBlocks
- Domain-specific enrichers → move with their service
- Ensure consistent enricher names across all services for log aggregation

---

## Testing Patterns

### Integration Tests with Shared Database
**Pattern:** Integration tests that use a shared test database.
**Resolution:**
- Each service gets its own integration test project
- Use Testcontainers for isolated database per test run
- Or use EF Core InMemory/SQLite provider for fast tests
- No cross-service integration tests at the unit/integration level
- Cross-service testing → contract tests (Pact) or end-to-end tests

### Test Fixtures with Cross-Domain Setup
**Pattern:** Test fixtures that set up data across multiple bounded contexts.
**Resolution:**
- Split fixtures by service
- Each service's tests only set up data for that service
- Mock external service dependencies (WireMock, NSubstitute)
- Shared test utilities → test infrastructure package

---

## Anti-Patterns to Watch For

### God Classes
**Pattern:** Large classes with many responsibilities (e.g., a 2000-line OrderService that handles orders, payments, shipping, and notifications).
**Resolution:**
- Split by responsibility during extraction
- Each microservice gets only the methods relevant to its domain
- Shared helper methods → utility package or duplicate
- Use the Single Responsibility Principle as a guide

### Circular Dependencies
**Pattern:** Project A references Project B which references Project A.
**Resolution:**
- Must be broken before extraction
- Extract shared interfaces into a separate project
- Use dependency inversion (depend on abstractions)
- May indicate incorrect bounded context boundaries

### Tight Database Coupling
**Pattern:** Services directly querying each other's tables via joins or views.
**Resolution:**
- Replace with API calls between services
- Create materialized views or read models for query-heavy scenarios
- Accept eventual consistency for cross-service data
- See database-migration steering file for detailed strategies

### Shared Mutable State
**Pattern:** Static variables, singletons, or in-memory caches shared across features.
**Resolution:**
- Each service gets its own cache/state
- Shared state → distributed cache (Redis) or dedicated state service
- Remove static mutable state during extraction
- AsyncLocal/ThreadLocal → scoped DI services

### Distributed Monolith
**Warning:** Splitting a monolith into services that are still tightly coupled creates a distributed monolith — worse than the original.
**Prevention:**
- Each service must be independently deployable
- Minimize synchronous inter-service calls
- Prefer events over direct API calls where possible
- Each service owns its data completely
- No shared databases in the final state
- Test: can you deploy Service A without deploying Service B? If not, boundaries are wrong.

### Anemic Domain Model
**Pattern:** Entity classes with only properties (no behavior), all logic in service classes.
**Resolution:**
- During extraction, consider enriching entities with domain behavior
- Move validation and business rules into entity methods
- This is optional but improves the domain model
- Don't force it if the team prefers a transaction script style

### Leaky Abstractions
**Pattern:** Interfaces that expose infrastructure details (e.g., IQueryable<T> in repository interfaces).
**Resolution:**
- Repository interfaces should return domain types, not IQueryable
- Service interfaces should use domain DTOs, not EF entities
- Each service's Core project should have zero infrastructure dependencies

### Over-Engineering
**Warning:** Don't add patterns that aren't needed.
**Guidance:**
- Not every service needs CQRS
- Not every service needs event sourcing
- Not every service needs a message broker (start with HTTP, add messaging when needed)
- Keep it simple — complexity should be justified by requirements
- Start with the simplest architecture that works, evolve as needed

---

## Framework Migration Patterns

### .NET Framework → .NET 8+ Migration

When the monolith is on .NET Framework and services target modern .NET:

#### Step 1: Identify Compatibility
- Check all NuGet packages for .NET 8 compatibility
- Identify System.Web dependencies (not available in .NET Core)
- Check for Windows-specific APIs (Registry, WMI, COM interop)
- Use the .NET Upgrade Assistant tool for automated analysis

#### Step 2: Bridge with .NET Standard
- Create .NET Standard 2.0 libraries for shared code
- Both .NET Framework and .NET 8 can reference .NET Standard 2.0
- Gradually move code from .NET Framework projects to .NET Standard
- This enables incremental migration

#### Step 3: Replace Incompatible APIs
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

#### Step 4: Strangler Fig Pattern
- New microservices built on .NET 8
- Monolith stays on .NET Framework during transition
- API Gateway routes requests to new services or monolith
- Gradually move functionality from monolith to services
- Monolith shrinks over time until it can be decommissioned
