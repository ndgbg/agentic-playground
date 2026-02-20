# Phase 1: Codebase Assessment

This steering file guides the assessment phase of a .NET monolith-to-microservices transformation. Complete this entire phase and present findings to the user before proceeding to transformation. Do not skip any step — thoroughness here prevents costly mistakes during extraction.

---

## Step 1: Project Structure Discovery

Scan the workspace to build a complete picture of the codebase.

### 1a: Solution and Project Inventory

Search for and read every solution and project file:

```
Search for: **/*.sln, **/*.csproj, **/*.vbproj, **/*.fsproj
```

For each solution file (.sln), extract:
- Solution name and path
- All project references within the solution
- Solution folders and their organization
- Build configurations (Debug, Release, custom)

For each project file (.csproj, .vbproj, .fsproj), extract:
- Project name and relative path
- Target framework(s): TargetFramework or TargetFrameworks element
- SDK style vs legacy project format (look for `<Project Sdk="Microsoft.NET.Sdk">` vs `<Project ToolsVersion=`)
- Output type: Exe, Library, WinExe
- Project type GUIDs (legacy format): Web ({349C5851-...}), ClassLib, Console, WCF, Test
- All PackageReference elements with versions
- All ProjectReference elements (project-to-project dependencies)
- All Reference elements (GAC/DLL references — indicates .NET Framework)
- Embedded resources, content files, and linked files
- Pre/post build events (may indicate code generation or deployment steps)
- Conditional compilation symbols (DefineConstants)
- Assembly info (AssemblyName, RootNamespace, Version)

### 1b: Configuration File Inventory

Search for and catalog all configuration:

```
Search for: **/Web.config, **/app.config, **/appsettings*.json, **/launchSettings.json
Also: **/*.settings, **/packages.config, **/nuget.config, **/.editorconfig
```

For each configuration file, note:
- Connection strings (how many databases? what providers? SQL Server, PostgreSQL, MySQL, Oracle, SQLite?)
- App settings and their categories
- Custom configuration sections
- WCF service/client endpoints
- HTTP module and handler registrations (Web.config)
- Authentication configuration (forms auth, Windows auth, JWT settings)
- CORS policies
- Logging configuration
- Caching configuration
- External service URLs and API keys

### 1c: Database Artifact Inventory

Search for all database-related files:

```
Search for: **/*.sql, **/Migrations/*.cs, **/*.edmx, **/*.dbml
Also: **/StoredProcedures/, **/Scripts/, **/Seed/
```

Catalog:
- EF Code First migration files and their chronological order
- EDMX files (Database First models) and their table mappings
- SQL script files (schema creation, stored procedures, views, functions, triggers)
- DBML files (LINQ to SQL models)
- Seed data files
- Database project files (.sqlproj)

### 1d: Infrastructure File Inventory

Search for deployment and infrastructure files:

```
Search for: **/Dockerfile*, **/docker-compose*, **/.github/workflows/*, **/azure-pipelines*
Also: **/*.yaml, **/*.yml, **/Jenkinsfile, **/*.tf, **/deploy/*, **/scripts/
```

Catalog:
- Dockerfiles and their base images
- Docker Compose configurations
- CI/CD pipeline definitions
- Infrastructure as Code files (Terraform, CloudFormation, Bicep, Pulumi)
- Deployment scripts
- Kubernetes manifests

### Output: Project Inventory Table

Produce a comprehensive table:

| Project | Type | Framework | SDK Style | Output | Project Refs | Key Packages | LOC Estimate |
|---------|------|-----------|-----------|--------|-------------|--------------|--------------|
| MyApp.Web | ASP.NET MVC | net48 | No | Exe | Core, Data, Services | Autofac, Newtonsoft.Json | ~5000 |
| MyApp.Core | ClassLib | netstandard2.0 | Yes | Library | — | MediatR, FluentValidation | ~3000 |
| MyApp.Data | ClassLib | net48 | No | Library | Core | EntityFramework 6.4 | ~4000 |
| MyApp.Services | ClassLib | net48 | No | Library | Core, Data | AutoMapper, Hangfire | ~6000 |

---

## Step 2: Technology Stack Fingerprinting

Identify every framework, library, and pattern in use. Be exhaustive — missed dependencies cause extraction failures.

### 2a: Web Framework Detection

Scan for these indicators in project files, using statements, and code:

| Framework | Detection Method |
|-----------|-----------------|
| ASP.NET MVC 3/4/5 | `System.Web.Mvc` namespace, `packages.config` with Microsoft.AspNet.Mvc |
| ASP.NET Web API 2 | `System.Web.Http` namespace, ApiController base class |
| ASP.NET Core MVC | `Microsoft.AspNetCore.Mvc` package, Controller base class |
| ASP.NET Core Web API | `Microsoft.AspNetCore.Mvc` with `[ApiController]` attribute |
| Razor Pages | `Microsoft.AspNetCore.Mvc.RazorPages`, PageModel base class |
| Blazor Server | `Microsoft.AspNetCore.Components.Server`, `_Host.cshtml` |
| Blazor WebAssembly | `Microsoft.AspNetCore.Components.WebAssembly` |
| Minimal APIs | `app.MapGet()`, `app.MapPost()` patterns in Program.cs |
| WCF Services | `System.ServiceModel` namespace, .svc files |
| gRPC | `Grpc.AspNetCore` package, .proto files |
| SignalR | `Microsoft.AspNetCore.SignalR` or `Microsoft.AspNet.SignalR` |
| OData | `Microsoft.AspNetCore.OData` or `Microsoft.AspNet.OData` |
| GraphQL | `HotChocolate`, `GraphQL.NET`, or `GraphQL.Server` packages |
| Nancy | `Nancy` package (lightweight web framework) |
| ServiceStack | `ServiceStack` package |

### 2b: Data Access Detection

| Technology | Detection Method |
|------------|-----------------|
| Entity Framework 6 | `EntityFramework` package, `System.Data.Entity` namespace, DbContext inheriting from EF6 |
| Entity Framework Core | `Microsoft.EntityFrameworkCore` package, DbContext with EF Core patterns |
| Dapper | `Dapper` package, `connection.Query<>()` patterns |
| ADO.NET | `System.Data.SqlClient` or `Microsoft.Data.SqlClient`, SqlCommand usage |
| NHibernate | `NHibernate` package, .hbm.xml mapping files, FluentNHibernate |
| LINQ to SQL | `.dbml` files, DataContext usage |
| Linq2Db | `linq2db` package |
| MongoDB | `MongoDB.Driver` package |
| CosmosDB | `Microsoft.Azure.Cosmos` package |
| Redis | `StackExchange.Redis` package |
| Elasticsearch | `NEST` or `Elastic.Clients.Elasticsearch` package |
| Stored Procedures | `CommandType.StoredProcedure`, `EXEC` or `EXECUTE` in SQL strings |
| Raw SQL | `FromSqlRaw`, `ExecuteSqlRaw`, inline SQL strings |

### 2c: Dependency Injection Detection

| Container | Detection Method |
|-----------|-----------------|
| Built-in .NET Core DI | `Microsoft.Extensions.DependencyInjection`, `builder.Services.Add*` |
| Autofac | `Autofac` package, `ContainerBuilder`, `Module` classes |
| Unity | `Unity` or `Unity.Container` package |
| Ninject | `Ninject` package, `NinjectModule` |
| StructureMap | `StructureMap` package, `Registry` classes |
| Castle Windsor | `Castle.Windsor` package, `IWindsorContainer` |
| Simple Injector | `SimpleInjector` package |
| Lamar | `Lamar` package (StructureMap successor) |
| DryIoc | `DryIoc` package |
| Grace | `Grace` package |

### 2d: Messaging and Event Detection

| Framework | Detection Method |
|-----------|-----------------|
| MediatR | `MediatR` package, `IRequest`, `INotification`, `IRequestHandler` |
| MassTransit | `MassTransit` package, `IConsumer<>`, `IBus` |
| NServiceBus | `NServiceBus` package, `IHandleMessages<>` |
| Rebus | `Rebus` package |
| Brighter | `Paramore.Brighter` package |
| Wolverine | `Wolverine` package (JasperFx successor) |
| RabbitMQ | `RabbitMQ.Client` package |
| Azure Service Bus | `Azure.Messaging.ServiceBus` package |
| AWS SQS/SNS | `AWSSDK.SQS`, `AWSSDK.SimpleNotificationService` |
| Kafka | `Confluent.Kafka` package |
| Custom event bus | Look for `IEventBus`, `IEventHandler`, `Publish()` patterns |

### 2e: Cross-Cutting Concern Detection

Scan for authentication, authorization, logging, caching, validation, mapping, HTTP clients, resilience, and serialization libraries. For each, note the specific package and version.

### 2f: Background Processing Detection

| Framework | Detection Method |
|-----------|-----------------|
| Hangfire | `Hangfire` package, `BackgroundJob.Enqueue`, `RecurringJob` |
| Quartz.NET | `Quartz` package, `IJob`, `IScheduler` |
| IHostedService | Classes implementing `IHostedService` or `BackgroundService` |
| Windows Service | `ServiceBase` class, `TopShelf` package |
| Azure Functions | `Microsoft.Azure.Functions` packages, `[FunctionName]` attribute |
| AWS Lambda | `Amazon.Lambda` packages, `[LambdaFunction]` attribute |
| FluentScheduler | `FluentScheduler` package |
| Coravel | `Coravel` package |

### 2g: Testing Framework Detection

| Framework | Detection Method |
|-----------|-----------------|
| xUnit | `xunit` package, `[Fact]`, `[Theory]` attributes |
| NUnit | `NUnit` package, `[Test]`, `[TestFixture]` attributes |
| MSTest | `Microsoft.VisualStudio.TestTools.UnitTesting`, `[TestMethod]` |
| Moq | `Moq` package |
| NSubstitute | `NSubstitute` package |
| FakeItEasy | `FakeItEasy` package |
| FluentAssertions | `FluentAssertions` package |
| Shouldly | `Shouldly` package |
| SpecFlow | `SpecFlow` package, `.feature` files |
| Bogus | `Bogus` package (test data generation) |
| AutoFixture | `AutoFixture` package |
| Testcontainers | `Testcontainers` package |
| WireMock | `WireMock.Net` package |

### Output: Technology Stack Summary

Produce a categorized summary:

```
## Technology Stack

### Web Layer
- ASP.NET MVC 5 (System.Web.Mvc 5.2.7)
- ASP.NET Web API 2 (System.Web.Http 5.2.7)

### Data Access
- Entity Framework 6.4.4 (Code First with migrations)
- Dapper 2.0.123 (for reporting queries)
- 3 stored procedures in SQL Server

### Dependency Injection
- Autofac 6.4.0 with 12 modules

### Messaging
- MediatR 12.0.0 (47 request handlers, 8 notification handlers)

### Cross-Cutting
- Serilog 3.1.0 (structured logging to Seq)
- AutoMapper 12.0.0 (23 mapping profiles)
- FluentValidation 11.0.0 (31 validators)
- Polly 8.0.0 (retry policies on 4 HTTP clients)

### Background Processing
- Hangfire 1.8.0 (7 recurring jobs, 3 fire-and-forget patterns)

### Testing
- xUnit 2.5.0, Moq 4.18.0, FluentAssertions 6.12.0
- 342 unit tests, 28 integration tests

### Infrastructure
- Docker (1 Dockerfile, docker-compose with SQL Server)
- GitHub Actions CI/CD pipeline
```

---

## Step 3: Domain Model Analysis

This is the most critical step. Identify natural domain boundaries using DDD principles.

### 3a: Entity Discovery

Scan for all domain entities systematically:

```
Search in: **/Models/, **/Entities/, **/Domain/, **/Core/
Look for: classes with [Table], [Key] attributes, DbSet<> properties, IEntityTypeConfiguration<>
Also: classes inheriting from BaseEntity, Entity, AggregateRoot, or similar base classes
```

For EACH entity discovered, create a detailed profile:

| Property | What to Record |
|----------|---------------|
| Name | Class name and full namespace |
| Location | File path and project |
| Properties | All properties with types (especially foreign keys and navigation properties) |
| Data annotations | [Key], [Required], [ForeignKey], [Table], [Column], [MaxLength], etc. |
| Fluent API config | Any IEntityTypeConfiguration<> or OnModelCreating mappings |
| DbContext membership | Which DbContext(s) include this entity as a DbSet |
| Table mapping | Database table name (if different from class name) |
| Relationships | All navigation properties and their cardinality (1:1, 1:N, N:M) |
| Used by services | Which service classes operate on this entity |
| Used by controllers | Which controllers expose this entity |
| Used by repositories | Which repository classes access this entity |
| Validation rules | FluentValidation validators or DataAnnotation rules |
| Mapping profiles | AutoMapper/Mapster profiles that map this entity |

### 3b: Aggregate Root Identification

Identify aggregate boundaries — clusters of entities that must be modified together:

- Look for entities that are always loaded/saved together
- Entities with cascade delete relationships form natural aggregates
- Entities that share transactional boundaries (saved in the same SaveChanges call)
- Parent-child relationships where the child has no independent lifecycle

Example aggregate identification:
```
Aggregate: Order
  - Order (root)
  - OrderItem (child, no independent lifecycle)
  - OrderStatus (value object or child)
  - ShippingAddress (value object, owned type)

Aggregate: Product
  - Product (root)
  - ProductImage (child)
  - ProductVariant (child)
  - Price (value object)
```

### 3c: Bounded Context Identification

Group aggregates into bounded contexts using multiple signals:

1. **Business capability alignment** — map to real business functions:
   - Order Management (placing, tracking, fulfilling orders)
   - Product Catalog (browsing, searching, product details)
   - Customer Management (registration, profiles, preferences)
   - Inventory Management (stock levels, warehousing, replenishment)
   - Payment Processing (charges, refunds, payment methods)
   - Shipping & Delivery (carriers, tracking, delivery scheduling)
   - Notification (email, SMS, push notifications)
   - Identity & Access (authentication, authorization, user management)
   - Reporting & Analytics (dashboards, exports, business intelligence)
   - Content Management (CMS pages, blog posts, media)

2. **Linguistic boundaries** — where the same word means different things:
   - "Product" in Catalog (name, description, images) vs "Product" in Inventory (SKU, quantity, location)
   - "Customer" in Sales (orders, preferences) vs "Customer" in Support (tickets, history)
   - "Account" in Auth (credentials, roles) vs "Account" in Billing (balance, invoices)

3. **Data ownership** — which context is the source of truth for each entity

4. **Change frequency** — entities that change together belong together

5. **Team alignment** — if different teams own different features, those are natural boundaries

6. **Namespace/folder structure** — existing code organization often hints at boundaries

7. **Controller grouping** — controllers often naturally align with bounded contexts

### 3d: Entity Relationship Cross-Boundary Mapping

For each proposed bounded context boundary, create a detailed crossing map:

```
## Cross-Boundary Reference Map

### Order Context → Product Context
- Order.OrderItems[].ProductId (FK reference)
- OrderService.GetProductPrice() calls ProductRepository
- OrderController.Create() reads Product.Price and Product.StockLevel

### Order Context → Customer Context  
- Order.CustomerId (FK reference)
- OrderService.PlaceOrder() reads Customer.ShippingAddress
- OrderController.GetOrders() filters by Customer

### Customer Context → Identity Context
- Customer.UserId (FK reference to AspNetUsers)
- CustomerService.Register() creates Identity user

### Inventory Context → Product Context
- InventoryItem.ProductId (FK reference)
- InventoryService.CheckStock() reads Product.SKU
```

For each crossing, classify:
- **Read-only reference** — service only reads from the other context (can become API call)
- **Write dependency** — service writes to entities in another context (needs event or saga)
- **Transactional dependency** — both contexts must be updated atomically (hardest to break)
- **Query join** — data from both contexts is joined in a query (needs API composition or denormalization)

---

## Step 4: Dependency and Coupling Analysis

### 4a: Project Reference Graph

Build a complete directed graph of project references:

```
For each project:
  List all ProjectReference entries
  List all PackageReference entries
  Calculate fan-in (how many projects reference this one)
  Calculate fan-out (how many projects this one references)
```

Classify each project:

| Classification | Criteria | Implication |
|---------------|----------|-------------|
| Hub | Fan-in > 3 | Shared library, needs careful splitting or packaging |
| God project | Fan-out > 5 | Too many responsibilities, primary extraction target |
| Leaf | Fan-out = 0, Fan-in > 0 | Pure dependency, easy to package |
| Island | Fan-in = 0, Fan-out = 0 | Isolated, may be dead code |
| Circular | Mutual references | Must be broken before extraction |

### 4b: Namespace-Level Dependency Analysis

Go deeper than project references — analyze namespace dependencies:

```
For each namespace in the codebase:
  Scan all using statements
  Map which namespaces depend on which other namespaces
  Identify namespace clusters that form natural modules
```

This reveals hidden coupling that project references don't show (e.g., two namespaces in the same project that should be in different services).

### 4c: Class-Level Coupling Metrics

For each proposed bounded context, calculate:

| Metric | Formula | Meaning |
|--------|---------|---------|
| Afferent Coupling (Ca) | Count of external classes depending on this context | How much others depend on us |
| Efferent Coupling (Ce) | Count of external classes this context depends on | How much we depend on others |
| Instability (I) | Ce / (Ca + Ce) | 0 = stable (hard to extract), 1 = unstable (easy to extract) |
| Abstractness (A) | Abstract types / Total types | Higher = more abstract, easier to decouple |
| Distance from Main Sequence (D) | |A + I - 1| | 0 = ideal balance, higher = problematic |

### 4d: Shared State Analysis

Systematically scan for shared mutable state:

```
Search for: static class, static readonly, static volatile
Search for: Singleton pattern, .Instance property
Search for: HttpContext.Current, HttpContext.Items
Search for: Session[, TempData[
Search for: MemoryCache, IMemoryCache, ObjectCache
Search for: ThreadLocal<, AsyncLocal<, CallContext
Search for: ConcurrentDictionary (used as global state)
Search for: Lazy<> with static fields
```

For each instance found:
- What data is stored
- Which bounded contexts access it
- Is it read-only or read-write
- Can it be replaced with a service call or distributed cache

### 4e: Database Coupling Analysis

This is critical — database coupling is the hardest to break.

```
For each DbContext:
  List all DbSet<> properties (entities it manages)
  List all entity configurations (OnModelCreating or IEntityTypeConfiguration)
  
For each repository or data access class:
  List all tables/entities it queries
  Identify cross-context joins (queries touching entities from multiple proposed contexts)
  Identify stored procedure calls and which tables they touch
  
For each stored procedure/view/function:
  List all tables it reads from
  List all tables it writes to
  Identify cross-context data access
```

Produce a table ownership matrix:

| Table | Context A | Context B | Context C | Resolution |
|-------|-----------|-----------|-----------|------------|
| Orders | Owner (RW) | — | Read | API call from C |
| Products | Read | Owner (RW) | Read | API calls from A, C |
| Customers | Read | — | Owner (RW) | API call from A |
| OrderProducts | Owner (RW) | Read | — | Duplicate or API |
| AuditLog | Write | Write | Write | Shared or per-service |

### 4f: External Integration Analysis

Map all external integration points:

```
Search for: HttpClient, RestClient, WebClient, HttpWebRequest
Search for: SmtpClient, MailMessage (email)
Search for: CloudBlobClient, S3Client (file storage)
Search for: connection strings pointing to external systems
Search for: API keys, tokens, credentials in configuration
```

For each integration:
- What external system does it connect to
- Which bounded contexts use it
- Is it a shared integration or context-specific
- Can it be isolated to a single service

### 4g: Transaction Boundary Analysis

Identify all transactional boundaries:

```
Search for: TransactionScope, BeginTransaction, IDbContextTransaction
Search for: using (var transaction =
Search for: SaveChanges() calls — how many entities are saved together
Search for: [Transaction] attributes
Search for: ambient transactions (TransactionScope with multiple DbContexts)
```

For each transaction:
- Which entities are modified within the transaction
- Do the entities span proposed service boundaries
- Can the transaction be replaced with eventual consistency (saga pattern)
- What is the business impact of eventual consistency for this operation

---

## Step 5: Communication Pattern Analysis

### 5a: Synchronous Call Chains

Trace the call chains from controllers through services to data access:

```
For each controller action:
  Trace: Controller → Service(s) → Repository/DbContext
  Note which bounded contexts are touched in a single request
  Identify the deepest call chain depth
  Flag chains that cross proposed service boundaries
```

### 5b: Event and Message Patterns

Map existing event/message flows:

```
Search for: INotification, INotificationHandler (MediatR)
Search for: IConsumer<>, IEventHandler<>
Search for: Publish(), Send(), Enqueue()
Search for: event keyword (C# events)
Search for: delegate, Action<>, Func<>
```

For each event/message:
- Publisher (which context)
- Subscriber(s) (which contexts)
- Is it in-process or distributed
- Payload contents

### 5c: Shared Resource Access

Identify shared resources beyond the database:

- File system paths accessed by multiple contexts
- Shared network drives or blob storage containers
- Shared Redis keys or cache regions
- Shared message queues or topics
- Shared external API connections (rate limits, connection pools)

---

## Step 6: Security and Identity Analysis

### 6a: Authentication Flow

Map the complete authentication flow:

```
Search for: [Authorize], [AllowAnonymous], AuthorizeAttribute
Search for: IAuthenticationService, SignInManager, UserManager
Search for: JWT, Bearer, cookie authentication configuration
Search for: ClaimsPrincipal, ClaimsIdentity, User.Identity
Search for: Windows Authentication, Negotiate, NTLM
```

Document:
- Authentication mechanism (cookies, JWT, Windows, OAuth, OpenID Connect)
- Identity provider (ASP.NET Identity, IdentityServer, external provider)
- Token issuance and validation flow
- Session management approach

### 6b: Authorization Model

Map authorization patterns:

```
Search for: [Authorize(Roles = ], [Authorize(Policy =
Search for: IAuthorizationHandler, IAuthorizationRequirement
Search for: User.IsInRole(, User.HasClaim(
Search for: custom authorization attributes
```

Document:
- Role-based access control (RBAC) roles and their scope
- Policy-based authorization policies
- Resource-based authorization patterns
- Which contexts enforce which authorization rules

---

## Step 7: Complexity and Risk Scoring

### 7a: Per-Service Complexity Score

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
| Framework migration needed | 2x | 1 (same framework), 3 (minor upgrade), 5 (.NET Framework → .NET Core) |

Total score interpretation:
- 15-25: Easy extraction
- 26-40: Medium complexity
- 41-55: Hard extraction
- 56+: Very hard — consider breaking into smaller steps

### 7b: Migration Order Algorithm

Determine extraction order using this algorithm:

1. Calculate complexity score for each proposed service
2. Calculate coupling score (sum of cross-boundary references)
3. Identify dependency chains (Service A must be extracted before Service B)
4. Sort by: lowest coupling first, then lowest complexity, respecting dependency chains
5. The first service to extract should be the most isolated, least coupled one

### 7c: Risk Register

For each proposed service, document risks:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Shared table X needs splitting | High | High | Create migration script, test with production data copy |
| Transaction spanning Order and Inventory | Medium | High | Implement saga pattern with compensation |
| Performance degradation from API calls replacing in-process calls | Medium | Medium | Add caching, optimize API contracts |
| Authentication flow disruption | Low | Critical | Extract auth service first, test thoroughly |

---

## Step 8: Generate Assessment Report

Present a comprehensive report to the user. The report must include ALL of the following sections:

```
## Monolith Assessment Report

### 1. Executive Summary
- One paragraph overview of the monolith
- Number of proposed microservices
- Overall complexity rating (Easy/Medium/Hard/Very Hard)
- Estimated effort range
- Key risks in 2-3 bullet points

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
