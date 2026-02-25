# Phase 1a: Codebase Discovery

This steering file covers Steps 1-2 of the assessment phase: scanning the workspace and fingerprinting the technology stack. Complete this before moving to assessment-analysis.md.

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

After completing Steps 1-2, proceed to **assessment-analysis.md** for domain model analysis, dependency analysis, and coupling metrics.
