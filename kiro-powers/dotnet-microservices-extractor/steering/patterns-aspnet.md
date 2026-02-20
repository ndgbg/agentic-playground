# ASP.NET Web Framework Patterns Reference

Patterns for handling ASP.NET MVC, Web API, Core, Razor Pages, Blazor, and Minimal APIs during monolith-to-microservices decomposition.

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
