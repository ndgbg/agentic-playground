# Phase 2 & 3: Planning and Executing the Transformation

This steering file covers both the planning and execution phases. Complete planning first, get user approval, then execute.

---

## Phase 2: Transformation Planning

### Step 1: Define Service Boundaries and Contracts

For each microservice identified in the assessment, produce a complete service definition.

#### Service Identity Card

```
Service Name: {PascalCase, e.g., OrderService}
Responsibility: {Single sentence — what this service owns}
Bounded Context: {Which bounded context from assessment}
```

#### Owned Domain

List every entity, value object, and enum this service is the source of truth for:
- Aggregate roots with their child entities
- Value objects owned by this context
- Enums specific to this domain
- Domain events defined by this context

#### API Surface

For each service, define the complete API:

```
## {ServiceName} API

### REST Endpoints
POST   /api/{resource}          - Create
GET    /api/{resource}          - List (with pagination, filtering, sorting)
GET    /api/{resource}/{id}     - Get by ID
PUT    /api/{resource}/{id}     - Full update
PATCH  /api/{resource}/{id}     - Partial update
DELETE /api/{resource}/{id}     - Delete

### Events Published
- {EntityName}Created   { Id, Key properties }
- {EntityName}Updated   { Id, Changed properties }
- {EntityName}Deleted   { Id }

### Events Consumed
- From {OtherService}: {EventName} → Handler action

### APIs Consumed
- From {OtherService}: GET /api/{resource}/{id} → Used in {workflow}
```

#### Project Structure Per Service

Each service follows clean architecture:

```
{ServiceName}/
├── {ServiceName}.Api/
│   ├── Controllers/
│   │   └── {Resource}Controller.cs
│   ├── Middleware/
│   │   ├── CorrelationIdMiddleware.cs
│   │   ├── ExceptionHandlingMiddleware.cs
│   │   └── RequestLoggingMiddleware.cs
│   ├── Filters/
│   │   └── ValidationFilter.cs
│   ├── Extensions/
│   │   ├── ServiceCollectionExtensions.cs
│   │   └── ApplicationBuilderExtensions.cs
│   ├── Program.cs
│   ├── appsettings.json
│   ├── appsettings.Development.json
│   ├── Dockerfile
│   └── {ServiceName}.Api.csproj
├── {ServiceName}.Core/
│   ├── Entities/
│   ├── ValueObjects/
│   ├── Enums/
│   ├── Interfaces/
│   │   ├── Repositories/
│   │   └── Services/
│   ├── Services/
│   ├── Events/
│   ├── Exceptions/
│   ├── Specifications/
│   └── {ServiceName}.Core.csproj
├── {ServiceName}.Infrastructure/
│   ├── Data/
│   │   ├── {ServiceName}DbContext.cs
│   │   ├── Configurations/
│   │   │   └── {Entity}Configuration.cs
│   │   └── Migrations/
│   ├── Repositories/
│   ├── Services/
│   │   └── External service clients
│   ├── Caching/
│   └── {ServiceName}.Infrastructure.csproj
├── {ServiceName}.Contracts/
│   ├── Requests/
│   ├── Responses/
│   ├── Events/
│   │   └── Integration event contracts
│   └── {ServiceName}.Contracts.csproj
└── {ServiceName}.Tests/
    ├── Unit/
    ├── Integration/
    └── {ServiceName}.Tests.csproj
```

### Step 2: Shared Library Strategy

Define precisely what is shared vs duplicated vs packaged.

#### Shared Kernel (SharedKernel project)

Only include types that are truly universal across ALL services:

```csharp
// SharedKernel/
├── BaseEntity.cs           // public abstract class BaseEntity { public Guid Id; public DateTime CreatedAt; public DateTime UpdatedAt; }
├── IAuditableEntity.cs     // public interface IAuditableEntity { string CreatedBy; string ModifiedBy; }
├── ISoftDeletable.cs       // public interface ISoftDeletable { bool IsDeleted; DateTime? DeletedAt; }
├── ValueObject.cs          // Abstract base for value objects with equality
├── DomainEvent.cs          // Base class for domain events
├── Result.cs               // Result<T> pattern for operation outcomes
├── PagedResult.cs          // Pagination wrapper
├── Enumeration.cs          // Smart enum base class
├── Guard.cs                // Guard clauses (Guard.Against.Null, etc.)
└── Exceptions/
    ├── DomainException.cs
    ├── NotFoundException.cs
    └── ConflictException.cs
```

Rules for shared kernel:
- Must be stable — changes here affect ALL services
- No business logic — only structural types
- No infrastructure dependencies — pure C#
- Version carefully — breaking changes require coordinated deployment

#### Building Blocks (BuildingBlocks project)

Cross-cutting infrastructure shared via NuGet package or project reference:

```
BuildingBlocks/
├── Authentication/
│   ├── JwtConfiguration.cs
│   ├── ServiceCollectionExtensions.cs
│   └── ClaimsPrincipalExtensions.cs
├── Logging/
│   ├── SerilogConfiguration.cs
│   ├── CorrelationIdMiddleware.cs
│   └── RequestResponseLoggingMiddleware.cs
├── ErrorHandling/
│   ├── ExceptionHandlingMiddleware.cs
│   ├── ProblemDetailsFactory.cs
│   └── ValidationProblemDetails.cs
├── HealthChecks/
│   ├── DatabaseHealthCheck.cs
│   └── ServiceHealthCheck.cs
├── Messaging/
│   ├── IEventBus.cs
│   ├── IntegrationEvent.cs
│   └── IIntegrationEventHandler.cs
├── Resilience/
│   ├── PollyPolicies.cs
│   └── CircuitBreakerConfiguration.cs
├── Swagger/
│   └── SwaggerConfiguration.cs
└── Observability/
    ├── OpenTelemetryConfiguration.cs
    └── MetricsConfiguration.cs
```

#### What to Duplicate Per Service (NOT shared)

- Entity classes — each service defines its own representation of domain concepts
- DTOs — each service defines its own request/response models
- Validation rules — each service validates its own inputs independently
- Configuration models — each service has its own strongly-typed config
- AutoMapper profiles — each service maps its own entities
- DbContext — each service has its own data context
- Repository implementations — each service implements its own data access

### Step 3: Data Decomposition Plan

For each service, define the complete data strategy. Consult the database-migration steering file for detailed patterns.

#### Per-Service Database Strategy

```
## {ServiceName} Data Plan

### Owned Tables
- {Table1} (full ownership, read-write)
- {Table2} (full ownership, read-write)

### Tables to Split
- {SharedTable} → Extract columns {A, B, C} into {ServiceName}.{NewTable}
  - Migration: Copy data, add sync mechanism, remove from monolith after cutover

### Foreign Key Resolution
- {Table}.{OtherServiceEntityId} → Keep as simple ID column, remove FK constraint
  - Data fetched via API call to {OtherService} when needed
  - Cache with {TTL} for performance

### Read Model / Denormalization
- Need {OtherService}.{Entity}.{Property} for display purposes
  - Strategy: Subscribe to {OtherService}.{Entity}Updated event
  - Store denormalized copy in local read table
  - Eventual consistency acceptable: {Yes/No, with justification}

### Connection String
- Separate database: {ServiceName}Db
- Or separate schema: {ServiceName} schema in shared database (interim step)
```

### Step 4: Inter-Service Communication Design

#### Synchronous Communication (HTTP/gRPC)

For each service-to-service API call:

```
Caller: {ServiceA}
Callee: {ServiceB}
Endpoint: GET /api/{resource}/{id}
Purpose: {Why this call is needed}
Frequency: {Estimated calls per minute}
Latency requirement: {Max acceptable latency}
Failure handling: {Retry with backoff / Circuit breaker / Fallback / Cache}
```

HTTP Client Configuration per service:

```csharp
// In {ServiceA}.Infrastructure/Services/{ServiceB}Client.cs
public class {ServiceB}Client : I{ServiceB}Client
{
    private readonly HttpClient _httpClient;
    
    // Configured with:
    // - Base URL from configuration
    // - Retry policy: 3 retries with exponential backoff
    // - Circuit breaker: 5 failures, 30s break duration
    // - Timeout: 5 seconds per request
    // - Authentication: JWT token forwarding or client credentials
}
```

#### Asynchronous Communication (Events)

For each integration event:

```
Event: {EventName}
Publisher: {ServiceA}
Subscribers: {ServiceB, ServiceC}
Payload: { Id: Guid, Property1: string, Property2: decimal, Timestamp: DateTime }
Delivery guarantee: At-least-once
Idempotency: Subscriber uses {EventId} for deduplication
Ordering: {Required / Not required}
Transport: {RabbitMQ / Azure Service Bus / AWS SQS / In-memory for dev}
```

#### Saga / Process Manager (for distributed transactions)

For each workflow that previously used a database transaction spanning multiple contexts:

```
Saga: {WorkflowName}Saga (e.g., PlaceOrderSaga)
Steps:
  1. {ServiceA}: {Action} → On success: proceed to 2 → On failure: abort
  2. {ServiceB}: {Action} → On success: proceed to 3 → On failure: compensate step 1
  3. {ServiceC}: {Action} → On success: complete → On failure: compensate steps 1, 2

Compensation:
  - Step 1 compensation: {Undo action}
  - Step 2 compensation: {Undo action}

Timeout: {Max saga duration before auto-compensation}
```

### Step 5: Cross-Cutting Concerns Plan

#### Authentication & Authorization Strategy

```
Identity Service:
  - Owns: User accounts, roles, permissions, tokens
  - Provides: Token issuance (JWT), user management API
  - Technology: ASP.NET Core Identity / IdentityServer / Duende / Auth0 / Azure AD

Per-Service Auth:
  - JWT validation middleware (from BuildingBlocks)
  - Authorization policies defined per service
  - Claims-based authorization for fine-grained control
  - Service-to-service: Client credentials flow (OAuth2)
  
Token Flow:
  1. Client authenticates with Identity Service → receives JWT
  2. Client sends JWT in Authorization header to any service
  3. Each service validates JWT independently (shared signing key or JWKS endpoint)
  4. Service extracts claims for authorization decisions
  5. Service-to-service calls: originating service forwards user JWT or uses client credentials
```

#### Observability Strategy

```
Logging:
  - Framework: Serilog with structured logging
  - Sinks: Console (dev), Seq/Elasticsearch/CloudWatch (prod)
  - Enrichers: CorrelationId, ServiceName, MachineName, Environment
  - Log levels: Information for requests, Warning for retries, Error for failures
  - Sensitive data: Mask PII in logs

Distributed Tracing:
  - Framework: OpenTelemetry
  - Exporters: Jaeger (dev), AWS X-Ray / Azure Monitor / Datadog (prod)
  - Propagation: W3C TraceContext headers
  - Instrumentation: HTTP clients, database queries, message bus

Metrics:
  - Framework: OpenTelemetry Metrics or Prometheus
  - Per-service metrics: Request rate, error rate, latency (RED)
  - Business metrics: Orders placed, items shipped, etc.
  - Infrastructure: CPU, memory, connection pool usage

Health Checks:
  - /health/live — liveness (is the process running)
  - /health/ready — readiness (can it serve traffic: DB connected, dependencies available)
  - /health/startup — startup probe (has initialization completed)
```

#### Configuration Strategy

```
Per-Service Configuration:
  - appsettings.json — defaults
  - appsettings.{Environment}.json — environment overrides
  - Environment variables — secrets and deployment-specific values
  - User secrets (dev only) — local development secrets

Strongly-Typed Configuration:
  - Each service defines its own IOptions<T> classes
  - Validation on startup (ValidateOnStart)
  - No static configuration classes

Secrets Management:
  - Development: dotnet user-secrets
  - Production: AWS Secrets Manager / Azure Key Vault / HashiCorp Vault
  - Never in appsettings.json or source control
```

### Step 6: API Gateway and BFF Strategy

Determine if an API Gateway is needed:

```
API Gateway (recommended if 3+ services):
  - Technology: YARP / Ocelot / Kong / AWS API Gateway / Azure API Management
  - Responsibilities:
    - Request routing to appropriate service
    - Authentication (JWT validation at gateway level)
    - Rate limiting
    - Request/response transformation
    - API versioning
    - SSL termination
    - CORS handling
    - Request aggregation (optional)

BFF Pattern (if UI needs data from multiple services):
  - Create a Backend-for-Frontend service
  - Aggregates data from multiple microservices
  - Tailored API for specific UI needs (web, mobile)
  - Handles UI-specific concerns (pagination, formatting)
```

### Step 7: Infrastructure Plan

```
Containerization:
  - Dockerfile per service (multi-stage build)
  - docker-compose.yml for local development
  - docker-compose.override.yml for dev-specific settings

Orchestration (production):
  - Kubernetes / ECS / Azure Container Apps
  - Service discovery
  - Load balancing
  - Auto-scaling policies

Database:
  - Per-service database (or schema) in SQL Server / PostgreSQL
  - Connection pooling configuration
  - Migration strategy (EF Core migrations per service)

Message Broker:
  - RabbitMQ (docker container for dev)
  - Or cloud-managed: Azure Service Bus / AWS SQS+SNS / Google Pub/Sub

Caching:
  - Redis (docker container for dev)
  - Per-service cache with appropriate TTLs
  - Cache invalidation via events
```

### Step 8: Rollback Strategy

For each service extraction, define a rollback plan:

```
Service: {ServiceName}
Extraction Step: {What was done}
Rollback Trigger: {What failure condition triggers rollback}
Rollback Steps:
  1. {Step to undo the extraction}
  2. {Step to restore monolith functionality}
  3. {Step to verify rollback succeeded}
Rollback Time Estimate: {How long to roll back}
Data Considerations: {Any data that needs to be migrated back}
```

### Step 9: Test Coverage Strategy During Migration

Maintaining test coverage during extraction is critical. Tests that worked in the monolith may break when boundaries change, and new integration points need coverage.

#### 9a: Characterization Tests (Before Extraction)

Before extracting any service, write characterization tests that capture the current behavior of the code being extracted:

```
For each service being extracted:
  1. Identify all public API endpoints that will move to the new service
  2. Write integration tests against the MONOLITH that exercise these endpoints
  3. Capture request/response pairs as golden files
  4. These tests become the acceptance criteria for the new service
  5. The new service must pass the same tests (with URL changes)
```

```csharp
// Characterization test example — run against monolith first, then against new service
[Fact]
public async Task CreateOrder_WithValidRequest_ReturnsCreatedOrder()
{
    var request = new CreateOrderRequest { /* ... */ };
    var response = await _client.PostAsJsonAsync("/api/orders", request);
    response.StatusCode.Should().Be(HttpStatusCode.Created);
    var order = await response.Content.ReadFromJsonAsync<OrderResponse>();
    order.Should().NotBeNull();
    order.Status.Should().Be("Pending");
}
```

#### 9b: Contract Tests (Between Services)

Use consumer-driven contract tests to verify that service APIs don't break their consumers:

```
Tool: Pact (PactNet for .NET)

Flow:
  1. Consumer (e.g., OrderService) defines expected API contract with Provider (e.g., ProductService)
  2. Consumer generates a Pact file describing expected interactions
  3. Provider verifies it can fulfill the contract
  4. Run contract tests in CI — broken contracts block deployment

When to add:
  - Every synchronous service-to-service API call needs a contract test
  - Add contract tests BEFORE cutting over traffic to the new service
```

```csharp
// Consumer side (OrderService tests)
[Fact]
public async Task GetProduct_ReturnsExpectedProduct()
{
    _pactBuilder
        .UponReceiving("a request for product by ID")
        .WithRequest(HttpMethod.Get, "/api/products/123")
        .WillRespond()
        .WithStatus(HttpStatusCode.OK)
        .WithJsonBody(new { id = "123", name = "Widget", price = 9.99 });

    await _pactBuilder.VerifyAsync(async ctx =>
    {
        var client = new ProductServiceClient(ctx.MockServerUri);
        var product = await client.GetProductAsync("123");
        product.Name.Should().Be("Widget");
    });
}
```

#### 9c: Integration Tests That Span Boundaries

Existing integration tests that touch entities from multiple bounded contexts will break after extraction. Plan for this:

```
For each existing integration test:
  1. Identify which services it touches
  2. If single service → move test to that service's test project
  3. If multiple services → split into:
     a. Per-service integration tests (mock external service dependencies)
     b. Contract tests (verify API compatibility)
     c. End-to-end tests (run against full docker-compose environment, sparingly)
  4. Never mock the database in integration tests — use Testcontainers or EF InMemory
```

#### 9d: Test Migration Checklist

```
Before extracting each service:
- [ ] Characterization tests written and passing against monolith
- [ ] Contract tests defined for all consumed APIs

During extraction:
- [ ] Service-specific unit tests written for new code
- [ ] Integration tests using Testcontainers for database
- [ ] Contract tests passing (consumer and provider sides)
- [ ] Existing monolith tests still pass (monolith functionality unchanged)

After extraction:
- [ ] Characterization tests pass against new service
- [ ] Remove or update monolith tests that covered extracted functionality
- [ ] End-to-end smoke tests pass in docker-compose environment
```

### Step 10: API Versioning During Migration

When extracting a service, existing consumers of the monolith's endpoints must not break. Plan for API coexistence.

#### Versioning Strategy

Choose one approach and apply consistently:

| Strategy | When to Use | Implementation |
|----------|-------------|----------------|
| URL path versioning (`/api/v1/orders`) | Simple, explicit, easy to route | `[Route("api/v{version:apiVersion}/[controller]")]` |
| Header versioning (`Api-Version: 2.0`) | Cleaner URLs, harder to test in browser | `[ApiVersion("2.0")]` with header reader |
| Gateway routing (transparent) | Clients don't change, gateway handles it | YARP/Ocelot routes by path to different backends |

Recommended: Gateway routing for internal services, URL versioning for external APIs.

#### Backward Compatibility Rules

During migration, the new service API must be backward compatible with the monolith API:

```
DO:
  - Add new fields to responses (non-breaking)
  - Add new optional fields to requests (non-breaking)
  - Support both old and new field names during transition (aliases)
  - Return the same HTTP status codes for the same scenarios

DON'T:
  - Remove fields from responses (breaking)
  - Make previously optional request fields required (breaking)
  - Change field types (breaking)
  - Change URL paths without gateway routing (breaking)
  - Change error response format (breaking)
```

#### Deprecation Timeline

```
1. Deploy new service with new API alongside monolith
2. Add Deprecation header to monolith responses: "Deprecation: true"
3. Log all requests to deprecated endpoints
4. Notify consumers with migration timeline (minimum 30 days for external APIs)
5. Monitor deprecated endpoint traffic — don't remove until traffic is zero
6. Remove deprecated endpoints from monolith
```

Consult the traffic-cutover steering file for detailed routing and canary deployment strategies.

### Step 11: Present the Complete Plan

Present to the user:

1. Complete service breakdown with project structures
2. Shared library strategy (kernel, building blocks, per-service)
3. Data decomposition plan per service
4. Inter-service communication design (sync + async)
5. Saga definitions for distributed workflows
6. Cross-cutting concerns strategy
7. API gateway / BFF recommendation
8. Infrastructure plan
9. Rollback strategy per extraction step
10. Test coverage strategy (characterization tests, contract tests, migration plan)
11. API versioning and backward compatibility plan
12. Traffic cutover strategy (feature flags, canary deployment, parallel run)
13. Migration order with dependencies and estimated effort

**Get explicit approval before executing. The user may want to adjust boundaries, reorder migrations, or modify the communication strategy.**

---

## Phase 3: Execution

### Step 1: Create Solution Structure

Create the complete solution skeleton:

```
{SolutionName}.Microservices/
├── src/
│   ├── Services/
│   │   ├── {Service1}/
│   │   │   ├── {Service1}.Api/
│   │   │   ├── {Service1}.Core/
│   │   │   ├── {Service1}.Infrastructure/
│   │   │   └── {Service1}.Contracts/
│   │   ├── {Service2}/
│   │   │   ├── ...
│   │   └── Identity/
│   │       ├── Identity.Api/
│   │       ├── Identity.Core/
│   │       └── Identity.Infrastructure/
│   ├── Shared/
│   │   ├── SharedKernel/
│   │   └── BuildingBlocks/
│   └── Gateway/
│       └── ApiGateway/
├── tests/
│   ├── {Service1}.UnitTests/
│   ├── {Service1}.IntegrationTests/
│   └── ...
├── docker/
│   ├── docker-compose.yml
│   ├── docker-compose.override.yml
│   └── .env
├── docs/
│   ├── architecture.md
│   └── api-contracts.md
├── Directory.Build.props
├── Directory.Packages.props
├── global.json
├── .editorconfig
└── {SolutionName}.Microservices.sln
```

#### Solution-Level Files

Create Directory.Build.props for shared build settings:
```xml
<Project>
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

Create Directory.Packages.props for centralized package management:
```xml
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <!-- Shared package versions across all projects -->
    <PackageVersion Include="Microsoft.EntityFrameworkCore" Version="8.0.0" />
    <PackageVersion Include="Serilog.AspNetCore" Version="8.0.0" />
    <PackageVersion Include="Swashbuckle.AspNetCore" Version="6.5.0" />
    <!-- Add all shared packages here -->
  </ItemGroup>
</Project>
```

Create global.json:
```json
{
  "sdk": {
    "version": "8.0.100",
    "rollForward": "latestMinor"
  }
}
```

#### Per-Service .csproj Files

{ServiceName}.Api.csproj:
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <RootNamespace>{SolutionName}.{ServiceName}.Api</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\{ServiceName}.Core\{ServiceName}.Core.csproj" />
    <ProjectReference Include="..\{ServiceName}.Infrastructure\{ServiceName}.Infrastructure.csproj" />
    <ProjectReference Include="..\..\Shared\BuildingBlocks\BuildingBlocks.csproj" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="Swashbuckle.AspNetCore" />
    <PackageReference Include="Serilog.AspNetCore" />
    <PackageReference Include="AspNetCore.HealthChecks.UI.Client" />
  </ItemGroup>
</Project>
```

{ServiceName}.Core.csproj:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <RootNamespace>{SolutionName}.{ServiceName}.Core</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\Shared\SharedKernel\SharedKernel.csproj" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="FluentValidation" />
    <PackageReference Include="MediatR" />
  </ItemGroup>
</Project>
```

{ServiceName}.Infrastructure.csproj:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <RootNamespace>{SolutionName}.{ServiceName}.Infrastructure</RootNamespace>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\{ServiceName}.Core\{ServiceName}.Core.csproj" />
    <ProjectReference Include="..\..\Shared\BuildingBlocks\BuildingBlocks.csproj" />
  </ItemGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" />
  </ItemGroup>
</Project>
```

{ServiceName}.Contracts.csproj:
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <RootNamespace>{SolutionName}.{ServiceName}.Contracts</RootNamespace>
  </PropertyGroup>
  <!-- Minimal dependencies - this is consumed by other services -->
</Project>
```

### Step 2: Create Shared Libraries

#### SharedKernel Implementation

Create the base types that all services will use. Keep this minimal and stable:

```csharp
// SharedKernel/BaseEntity.cs
public abstract class BaseEntity
{
    public Guid Id { get; protected set; } = Guid.NewGuid();
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}

// SharedKernel/ValueObject.cs
public abstract class ValueObject
{
    protected abstract IEnumerable<object> GetEqualityComponents();
    // Implement Equals, GetHashCode, operator==, operator!=
}

// SharedKernel/DomainEvent.cs
public abstract class DomainEvent
{
    public Guid EventId { get; } = Guid.NewGuid();
    public DateTime OccurredAt { get; } = DateTime.UtcNow;
}

// SharedKernel/Result.cs
public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }
    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string error) => new(false, default, error);
}
```

#### BuildingBlocks Implementation

Create cross-cutting infrastructure. Key components:

Correlation ID Middleware:
```csharp
public class CorrelationIdMiddleware
{
    // Extract X-Correlation-ID from incoming request header
    // Generate new one if not present
    // Add to response headers
    // Store in AsyncLocal for logging enrichment
    // Forward to outgoing HTTP client calls
}
```

Exception Handling Middleware:
```csharp
public class ExceptionHandlingMiddleware
{
    // Catch all unhandled exceptions
    // Map domain exceptions to appropriate HTTP status codes:
    //   NotFoundException → 404
    //   ConflictException → 409
    //   ValidationException → 400 (with ProblemDetails)
    //   DomainException → 422
    //   Unhandled → 500 (with generic message, log full details)
    // Return RFC 7807 ProblemDetails response
}
```

### Step 3: Extract Domain Layer (per service, in migration order)

For each service, following the migration order from the plan:

#### 3a: Create Entity Classes

For each entity owned by this service:

1. Copy the entity class from the monolith
2. Remove navigation properties that reference entities in OTHER services
3. Replace cross-service foreign keys with simple ID properties (no FK constraint)
4. Keep navigation properties for entities WITHIN this service
5. Add domain methods if moving toward rich domain model
6. Ensure entity inherits from SharedKernel.BaseEntity

```csharp
// BEFORE (monolith): Order has navigation to Customer and Product
public class Order
{
    public int Id { get; set; }
    public int CustomerId { get; set; }
    public Customer Customer { get; set; }  // Cross-boundary navigation
    public List<OrderItem> Items { get; set; }
}

public class OrderItem
{
    public int Id { get; set; }
    public int ProductId { get; set; }
    public Product Product { get; set; }  // Cross-boundary navigation
    public int Quantity { get; set; }
    public decimal UnitPrice { get; set; }
}

// AFTER (microservice): Order only references own entities
public class Order : BaseEntity
{
    public Guid CustomerId { get; private set; }  // Just an ID, no navigation
    public string CustomerName { get; private set; }  // Denormalized for display
    public List<OrderItem> Items { get; private set; } = new();
    public OrderStatus Status { get; private set; }
    public decimal TotalAmount => Items.Sum(i => i.TotalPrice);
    
    public void AddItem(Guid productId, string productName, int quantity, decimal unitPrice)
    {
        Items.Add(new OrderItem(productId, productName, quantity, unitPrice));
    }
}

public class OrderItem : BaseEntity
{
    public Guid ProductId { get; private set; }  // Just an ID, no navigation
    public string ProductName { get; private set; }  // Denormalized
    public int Quantity { get; private set; }
    public decimal UnitPrice { get; private set; }
    public decimal TotalPrice => Quantity * UnitPrice;
}
```

#### 3b: Create Interfaces

Define repository and service interfaces in Core (no infrastructure dependencies):

```csharp
// {Service}.Core/Interfaces/Repositories/I{Entity}Repository.cs
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default);
    Task<IReadOnlyList<Order>> GetByCustomerIdAsync(Guid customerId, CancellationToken ct = default);
    Task<PagedResult<Order>> GetPagedAsync(int page, int pageSize, CancellationToken ct = default);
    Task AddAsync(Order order, CancellationToken ct = default);
    Task UpdateAsync(Order order, CancellationToken ct = default);
    Task DeleteAsync(Guid id, CancellationToken ct = default);
}

// {Service}.Core/Interfaces/Services/I{ExternalService}Client.cs
public interface IProductServiceClient
{
    Task<ProductDto?> GetProductAsync(Guid productId, CancellationToken ct = default);
    Task<bool> CheckStockAsync(Guid productId, int quantity, CancellationToken ct = default);
}
```

#### 3c: Create Domain Services

Move business logic from monolith services, scoped to this service's domain:

```csharp
// {Service}.Core/Services/OrderDomainService.cs
public class OrderDomainService
{
    // Contains business rules that don't belong to a single entity
    // Example: order total calculation with discounts, tax rules
    // Does NOT depend on infrastructure (no DbContext, no HttpClient)
    // Uses interfaces for external dependencies
}
```

#### 3d: Create Domain Events

Define events for state changes other services need to know about:

```csharp
// {Service}.Core/Events/OrderPlacedEvent.cs
public class OrderPlacedEvent : DomainEvent
{
    public Guid OrderId { get; }
    public Guid CustomerId { get; }
    public decimal TotalAmount { get; }
    public List<OrderItemInfo> Items { get; }
}
```

#### 3e: Create Integration Event Contracts

In the Contracts project (consumed by other services):

```csharp
// {Service}.Contracts/Events/OrderPlacedIntegrationEvent.cs
public record OrderPlacedIntegrationEvent(
    Guid EventId,
    DateTime OccurredAt,
    Guid OrderId,
    Guid CustomerId,
    decimal TotalAmount,
    IReadOnlyList<OrderItemDto> Items
);

// {Service}.Contracts/Responses/OrderResponse.cs
public record OrderResponse(
    Guid Id,
    Guid CustomerId,
    string CustomerName,
    decimal TotalAmount,
    string Status,
    DateTime CreatedAt,
    IReadOnlyList<OrderItemResponse> Items
);

// {Service}.Contracts/Requests/CreateOrderRequest.cs
public record CreateOrderRequest(
    Guid CustomerId,
    IReadOnlyList<CreateOrderItemRequest> Items
);
```

### Step 4: Extract Data Layer (per service)

#### 4a: Create Service-Specific DbContext

```csharp
// {Service}.Infrastructure/Data/{ServiceName}DbContext.cs
public class OrderDbContext : DbContext
{
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<OrderItem> OrderItems => Set<OrderItem>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(OrderDbContext).Assembly);
        
        // Apply global query filters if needed
        modelBuilder.Entity<Order>().HasQueryFilter(o => !o.IsDeleted);
    }
}

// {Service}.Infrastructure/Data/Configurations/OrderConfiguration.cs
public class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> builder)
    {
        builder.ToTable("Orders");
        builder.HasKey(o => o.Id);
        builder.Property(o => o.CustomerName).HasMaxLength(200).IsRequired();
        builder.HasMany(o => o.Items).WithOne().HasForeignKey("OrderId").OnDelete(DeleteBehavior.Cascade);
        builder.HasIndex(o => o.CustomerId);
    }
}
```

#### 4b: Create Repository Implementations

```csharp
// {Service}.Infrastructure/Repositories/OrderRepository.cs
public class OrderRepository : IOrderRepository
{
    private readonly OrderDbContext _context;

    public async Task<Order?> GetByIdAsync(Guid id, CancellationToken ct = default)
    {
        return await _context.Orders
            .Include(o => o.Items)
            .FirstOrDefaultAsync(o => o.Id == id, ct);
    }

    public async Task<PagedResult<Order>> GetPagedAsync(int page, int pageSize, CancellationToken ct = default)
    {
        var query = _context.Orders.Include(o => o.Items).OrderByDescending(o => o.CreatedAt);
        var total = await query.CountAsync(ct);
        var items = await query.Skip((page - 1) * pageSize).Take(pageSize).ToListAsync(ct);
        return new PagedResult<Order>(items, total, page, pageSize);
    }
}
```

#### 4c: Handle Database Migration

For each service, create the initial EF Core migration:

```bash
dotnet ef migrations add InitialCreate --project {Service}.Infrastructure --startup-project {Service}.Api
```

If splitting tables from the monolith, create SQL migration scripts:

```sql
-- Migration script: Split shared tables
-- Step 1: Create new service-specific table
CREATE TABLE [{ServiceSchema}].[Orders] (
    [Id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    [CustomerId] UNIQUEIDENTIFIER NOT NULL,
    [CustomerName] NVARCHAR(200) NOT NULL,
    [TotalAmount] DECIMAL(18,2) NOT NULL,
    [Status] INT NOT NULL,
    [CreatedAt] DATETIME2 NOT NULL,
    [UpdatedAt] DATETIME2 NULL
);

-- Step 2: Migrate data from monolith table
INSERT INTO [{ServiceSchema}].[Orders] (Id, CustomerId, CustomerName, TotalAmount, Status, CreatedAt)
SELECT o.Id, o.CustomerId, c.Name, o.TotalAmount, o.Status, o.CreatedAt
FROM [dbo].[Orders] o
INNER JOIN [dbo].[Customers] c ON o.CustomerId = c.Id;

-- Step 3: Create indexes
CREATE INDEX IX_Orders_CustomerId ON [{ServiceSchema}].[Orders] (CustomerId);
```

### Step 5: Create API Layer (per service)

#### 5a: Create Controllers

```csharp
// {Service}.Api/Controllers/{Resource}Controller.cs
[ApiController]
[Route("api/[controller]")]
[Produces("application/json")]
public class OrdersController : ControllerBase
{
    private readonly IMediator _mediator;  // or inject services directly

    [HttpGet]
    [ProducesResponseType(typeof(PagedResult<OrderResponse>), StatusCodes.Status200OK)]
    public async Task<IActionResult> GetAll([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var result = await _mediator.Send(new GetOrdersQuery(page, pageSize));
        return Ok(result);
    }

    [HttpGet("{id:guid}")]
    [ProducesResponseType(typeof(OrderResponse), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetById(Guid id)
    {
        var result = await _mediator.Send(new GetOrderByIdQuery(id));
        return result is null ? NotFound() : Ok(result);
    }

    [HttpPost]
    [ProducesResponseType(typeof(OrderResponse), StatusCodes.Status201Created)]
    [ProducesResponseType(typeof(ValidationProblemDetails), StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> Create([FromBody] CreateOrderRequest request)
    {
        var result = await _mediator.Send(new CreateOrderCommand(request));
        return CreatedAtAction(nameof(GetById), new { id = result.Id }, result);
    }

    [HttpPut("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Update(Guid id, [FromBody] UpdateOrderRequest request)
    {
        await _mediator.Send(new UpdateOrderCommand(id, request));
        return NoContent();
    }

    [HttpDelete("{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> Delete(Guid id)
    {
        await _mediator.Send(new DeleteOrderCommand(id));
        return NoContent();
    }
}
```

#### 5b: Configure Program.cs

Create a complete, production-ready Program.cs for each service:

```csharp
// {Service}.Api/Program.cs
var builder = WebApplication.CreateBuilder(args);

// Serilog
builder.Host.UseSerilog((context, config) =>
    config.ReadFrom.Configuration(context.Configuration));

// DbContext
builder.Services.AddDbContext<{Service}DbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("{Service}Db")));

// Repositories
builder.Services.AddScoped<I{Entity}Repository, {Entity}Repository>();

// Domain Services
builder.Services.AddScoped<{Service}DomainService>();

// MediatR (if using CQRS)
builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(typeof({Service}DbContext).Assembly));

// Validation
builder.Services.AddValidatorsFromAssemblyContaining<Create{Entity}RequestValidator>();

// AutoMapper (if using)
builder.Services.AddAutoMapper(typeof({Service}DbContext).Assembly);

// HTTP Clients for consumed services
builder.Services.AddHttpClient<I{OtherService}Client, {OtherService}Client>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["{OtherService}:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(5);
})
.AddPolicyHandler(PollyPolicies.GetRetryPolicy())
.AddPolicyHandler(PollyPolicies.GetCircuitBreakerPolicy());

// Health Checks
builder.Services.AddHealthChecks()
    .AddSqlServer(builder.Configuration.GetConnectionString("{Service}Db")!, name: "database")
    .AddUrlGroup(new Uri(builder.Configuration["{OtherService}:BaseUrl"] + "/health/live"), name: "{other-service}");

// Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = builder.Configuration["Identity:Authority"];
        options.Audience = builder.Configuration["Identity:Audience"];
    });

builder.Services.AddAuthorization();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "{ServiceName} API", Version = "v1" });
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme { /* JWT config */ });
});

builder.Services.AddControllers();

var app = builder.Build();

// Middleware pipeline (order matters)
app.UseSerilogRequestLogging();
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<ExceptionHandlingMiddleware>();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.MapHealthChecks("/health/live", new() { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new() { ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse });

app.Run();
```

#### 5c: Create HTTP Clients for Consumed Services

```csharp
// {Service}.Infrastructure/Services/{OtherService}Client.cs
public class ProductServiceClient : IProductServiceClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<ProductServiceClient> _logger;

    public ProductServiceClient(HttpClient httpClient, ILogger<ProductServiceClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
    }

    public async Task<ProductDto?> GetProductAsync(Guid productId, CancellationToken ct = default)
    {
        try
        {
            var response = await _httpClient.GetAsync($"api/products/{productId}", ct);
            if (response.StatusCode == HttpStatusCode.NotFound)
                return null;
            response.EnsureSuccessStatusCode();
            return await response.Content.ReadFromJsonAsync<ProductDto>(ct);
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Failed to get product {ProductId} from Product Service", productId);
            throw;
        }
    }
}
```

### Step 6: Wire Up Cross-Cutting Concerns

#### 6a: Correlation ID Propagation

Ensure correlation IDs flow through the entire request chain:

1. Incoming request → extract or generate correlation ID
2. Store in AsyncLocal for logging enrichment
3. All log entries include the correlation ID
4. Outgoing HTTP calls → forward correlation ID in header
5. Published events → include correlation ID in metadata

#### 6b: Distributed Tracing Setup

```csharp
// In BuildingBlocks or per-service Program.cs
builder.Services.AddOpenTelemetry()
    .WithTracing(tracing => tracing
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddSource("{ServiceName}")
        .AddJaegerExporter());
```

#### 6c: Health Check Configuration

Each service exposes three health check endpoints:
- `/health/live` — always returns 200 if process is running
- `/health/ready` — checks database connectivity and critical dependencies
- `/health/startup` — checks if initialization is complete

### Step 7: Create Docker Support

#### Dockerfile Per Service

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS base
WORKDIR /app
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src

# Copy project files for restore (layer caching)
COPY ["src/Services/{Service}/{Service}.Api/{Service}.Api.csproj", "Services/{Service}/{Service}.Api/"]
COPY ["src/Services/{Service}/{Service}.Core/{Service}.Core.csproj", "Services/{Service}/{Service}.Core/"]
COPY ["src/Services/{Service}/{Service}.Infrastructure/{Service}.Infrastructure.csproj", "Services/{Service}/{Service}.Infrastructure/"]
COPY ["src/Services/{Service}/{Service}.Contracts/{Service}.Contracts.csproj", "Services/{Service}/{Service}.Contracts/"]
COPY ["src/Shared/SharedKernel/SharedKernel.csproj", "Shared/SharedKernel/"]
COPY ["src/Shared/BuildingBlocks/BuildingBlocks.csproj", "Shared/BuildingBlocks/"]
RUN dotnet restore "Services/{Service}/{Service}.Api/{Service}.Api.csproj"

# Copy source and build
COPY src/ .
WORKDIR "/src/Services/{Service}/{Service}.Api"
RUN dotnet build -c Release -o /app/build --no-restore

FROM build AS publish
RUN dotnet publish -c Release -o /app/publish --no-restore --no-build

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .

# Non-root user for security
RUN adduser --disabled-password --no-create-home appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health/live || exit 1

ENTRYPOINT ["dotnet", "{Service}.Api.dll"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  # Databases (one per service)
  order-db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      SA_PASSWORD: "${DB_PASSWORD:-YourStrong!Passw0rd}"
      ACCEPT_EULA: "Y"
    ports:
      - "1433:1433"
    volumes:
      - order-db-data:/var/opt/mssql

  # Add more service databases as needed

  # Message Broker
  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"

  # Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Services
  order-service:
    build:
      context: .
      dockerfile: src/Services/Order/Order.Api/Dockerfile
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
      - ConnectionStrings__OrderDb=Server=order-db;Database=OrderDb;User=sa;Password=${DB_PASSWORD:-YourStrong!Passw0rd};TrustServerCertificate=true
      - RabbitMQ__Host=rabbitmq
      - Redis__Connection=redis:6379
    ports:
      - "5001:8080"
    depends_on:
      - order-db
      - rabbitmq
      - redis

  # Add more services following the same pattern

  # API Gateway (optional)
  api-gateway:
    build:
      context: .
      dockerfile: src/Gateway/ApiGateway/Dockerfile
    ports:
      - "5000:8080"
    depends_on:
      - order-service

volumes:
  order-db-data:
```

### Step 8: Comprehensive Validation

After extracting each service, run this complete validation checklist:

#### Compilation Validation
- [ ] Each service solution compiles independently with `dotnet build`
- [ ] No references to monolith projects remain
- [ ] All NuGet packages resolve correctly
- [ ] No compilation warnings (TreatWarningsAsErrors should catch these)

#### Architectural Validation
- [ ] No cross-service entity references (only IDs)
- [ ] No cross-service DbContext usage
- [ ] No shared database connections between services
- [ ] Each service has its own DbContext with only owned entities
- [ ] Core project has zero infrastructure dependencies
- [ ] Contracts project has zero internal dependencies

#### API Validation
- [ ] All endpoints return proper HTTP status codes
- [ ] All endpoints have request/response DTOs (no entity exposure)
- [ ] Swagger documentation generates correctly
- [ ] Authentication is configured on all non-public endpoints
- [ ] CORS is configured appropriately

#### Infrastructure Validation
- [ ] Health check endpoints respond correctly
- [ ] Logging produces structured output with correlation IDs
- [ ] Docker build succeeds
- [ ] docker-compose up starts all services
- [ ] Services can communicate with each other

#### Data Validation
- [ ] EF migrations generate and apply correctly
- [ ] Database schema matches entity configurations
- [ ] Seed data loads correctly (if applicable)
- [ ] No orphaned foreign keys to other service tables

### Step 9: Post-Transformation Summary

Present to the user:

```
## Transformation Complete

### Services Created
For each service:
- Name, responsibility, port number
- Entity count, endpoint count
- Dependencies on other services

### Architecture Diagram
Text-based diagram showing:
- All services and their APIs
- Inter-service communication (sync and async)
- Databases per service
- Shared infrastructure (gateway, message broker, cache)

### What Was Extracted
- List of entities moved to each service
- List of controllers/endpoints per service
- Business logic distribution

### What Remains in Monolith (if incremental)
- Entities not yet extracted
- Features still in the monolith
- Planned next extractions

### Inter-Service Dependencies
- Service A → Service B: {endpoints called}
- Service A → Event Bus → Service C: {events}

### Next Steps
1. Run all services locally with docker-compose
2. Test each service's API independently (Swagger UI)
3. Test inter-service communication
4. Set up CI/CD pipelines per service
5. Plan production deployment strategy
6. Set up monitoring and alerting
7. Plan data migration from monolith database
8. Implement integration tests

### Known Limitations
- {Any manual steps still needed}
- {Any features that need additional work}
- {Performance considerations to monitor}

### Rollback Instructions
- How to revert to monolith if needed
- Data migration rollback steps
```
