# Phase 1b: Domain and Dependency Analysis

This steering file covers Steps 3-6 of the assessment phase: domain model analysis, dependency/coupling analysis, communication patterns, and security analysis. Run this after completing assessment-discovery.md.

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

After completing Steps 3-6, proceed to **assessment-scoring.md** for team analysis, complexity scoring, viability gate, and report generation.
