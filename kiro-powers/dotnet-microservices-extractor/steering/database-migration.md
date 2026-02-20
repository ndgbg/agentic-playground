# Database Decomposition and Migration Guide

This steering file provides detailed guidance for splitting a monolithic database into per-service databases during microservices extraction. Consult this during Phase 2 planning and Phase 3 execution.

---

## Database Splitting Strategies

### Strategy 1: Database-Per-Service (Target State)

Each microservice owns its own database instance. This is the ideal end state.

```
Monolith DB (before):
┌─────────────────────────────────┐
│ Orders, OrderItems, Products,   │
│ Customers, Inventory, Payments, │
│ Users, Roles, AuditLog, ...    │
└─────────────────────────────────┘

Per-Service DBs (after):
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ OrderDb  │ │ProductDb │ │CustomerDb│ │IdentityDb│
│ Orders   │ │ Products │ │Customers │ │ Users    │
│OrderItems│ │Categories│ │Addresses │ │ Roles    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

Pros: Full autonomy, independent scaling, technology freedom
Cons: Most complex migration, no cross-service joins

### Strategy 2: Schema-Per-Service (Interim Step)

Each service gets its own schema within the same database. Good as a transitional step.

```sql
-- Create schemas
CREATE SCHEMA [Order];
CREATE SCHEMA [Product];
CREATE SCHEMA [Customer];
CREATE SCHEMA [Identity];

-- Move tables to schemas
ALTER SCHEMA [Order] TRANSFER [dbo].[Orders];
ALTER SCHEMA [Order] TRANSFER [dbo].[OrderItems];
ALTER SCHEMA [Product] TRANSFER [dbo].[Products];
-- etc.

-- Create service-specific users with schema-level permissions
CREATE USER [OrderServiceUser] WITH PASSWORD = '...';
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::[Order] TO [OrderServiceUser];
-- Each service can ONLY access its own schema
```

Pros: Simpler migration, still enforces boundaries, easy to split later
Cons: Shared database instance, can still be tempted to cross-schema query

### Strategy 3: Shared Database with Logical Boundaries (Simplest Start)

Keep one database but enforce boundaries through code and conventions only.

Use this only as a very first step if the team isn't ready for physical separation.

---

## Table Ownership Resolution

### Pattern A: Exclusive Ownership (Easy)

Table is used by only one bounded context → assign to that service.

```
Table: Orders → OrderService (exclusive owner)
Table: OrderItems → OrderService (exclusive owner)
Action: Move to OrderService database, no changes needed
```

### Pattern B: Primary Owner with Readers (Medium)

One context writes, others only read.

```
Table: Products
  - ProductService: READ + WRITE (owner)
  - OrderService: READ (needs product name and price when creating orders)
  - InventoryService: READ (needs product SKU)

Resolution Options:

Option 1: API Call (simplest)
  - OrderService calls ProductService API to get product details
  - Add caching (Redis, 5-minute TTL) to reduce API calls
  - Acceptable if read frequency is moderate

Option 2: Event-Driven Denormalization (best for high-read)
  - ProductService publishes ProductUpdated events
  - OrderService stores a local read-only copy of needed fields (ProductId, Name, Price)
  - InventoryService stores a local copy of (ProductId, SKU)
  - Each consumer maintains its own projection table
  - Eventually consistent (typically < 1 second lag)

Option 3: Shared Read Model (interim)
  - Create a read-only view or materialized view
  - Consumers query the view
  - Owner service manages the source table
  - Transition to Option 1 or 2 later
```

### Pattern C: Multiple Writers (Hard)

Multiple contexts write to the same table.

```
Table: AuditLog
  - OrderService: WRITE (logs order events)
  - CustomerService: WRITE (logs customer events)
  - InventoryService: WRITE (logs inventory events)

Resolution Options:

Option 1: Per-Service Audit Table
  - Each service has its own AuditLog table
  - Aggregation done at query time (API composition or reporting service)

Option 2: Dedicated Audit Service
  - Create an AuditService that owns the AuditLog table
  - Other services publish audit events
  - AuditService consumes events and writes to its table

Option 3: Event Store Pattern
  - All services publish events to an event store
  - Audit log is a projection of the event stream
```

### Pattern D: Shared Reference Data (Medium)

Tables like Countries, Currencies, StatusCodes used by many services.

```
Resolution Options:

Option 1: Duplicate Per Service (recommended for small, stable data)
  - Each service has its own copy of reference data
  - Seed during database migration
  - Rarely changes, so sync is not a concern

Option 2: Shared Reference Data Service
  - Dedicated service for reference data
  - Other services call API or cache locally
  - Good for large or frequently changing reference data

Option 3: Configuration (for very small datasets)
  - Store in appsettings.json or environment variables
  - No database needed
```

---

## Foreign Key Resolution Patterns

### Cross-Service Foreign Keys

When a table has a foreign key to a table in another service, the FK constraint must be removed.

```sql
-- BEFORE: Orders table has FK to Customers table
ALTER TABLE [dbo].[Orders]
    ADD CONSTRAINT FK_Orders_Customers
    FOREIGN KEY (CustomerId) REFERENCES [dbo].[Customers](Id);

-- AFTER: Remove FK constraint, keep the column
ALTER TABLE [Order].[Orders]
    DROP CONSTRAINT FK_Orders_Customers;

-- The CustomerId column remains as a simple UNIQUEIDENTIFIER
-- Data integrity is now enforced at the application level
-- OrderService validates CustomerId by calling CustomerService API
```

### ID Type Considerations

When splitting, consider standardizing on GUIDs for cross-service IDs:

```sql
-- If monolith uses INT identity columns:
-- Option 1: Keep INT internally, use GUID for cross-service references
-- Option 2: Migrate to GUID (recommended for new services)

-- Migration script: Add GUID column alongside INT
ALTER TABLE [dbo].[Orders] ADD [GlobalId] UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID();
CREATE UNIQUE INDEX IX_Orders_GlobalId ON [dbo].[Orders] (GlobalId);

-- Update all cross-service references to use GlobalId
-- Then drop the INT FK columns
```

---

## Data Migration Scripts

### Template: Table Migration Script

```sql
-- ============================================
-- Migration: Move {TableName} to {ServiceName}Db
-- Date: {Date}
-- Author: {Author}
-- ============================================

-- Step 1: Create target table in service database
USE [{ServiceName}Db];
GO

CREATE TABLE [{Schema}].[{TableName}] (
    -- Column definitions matching source
    -- Adjust types if needed (e.g., INT → UNIQUEIDENTIFIER)
    -- Remove FK columns that reference other services
    -- Add denormalized columns if needed
);
GO

-- Step 2: Migrate data
INSERT INTO [{ServiceName}Db].[{Schema}].[{TableName}] (columns...)
SELECT columns...
FROM [{MonolithDb}].[dbo].[{TableName}]
-- Add JOINs for denormalized data
-- Add WHERE clause if filtering
;
GO

-- Step 3: Create indexes
CREATE INDEX IX_{TableName}_{Column} ON [{Schema}].[{TableName}] ({Column});
GO

-- Step 4: Verify row counts
DECLARE @source INT, @target INT;
SELECT @source = COUNT(*) FROM [{MonolithDb}].[dbo].[{TableName}];
SELECT @target = COUNT(*) FROM [{ServiceName}Db].[{Schema}].[{TableName}];

IF @source <> @target
    RAISERROR('Row count mismatch: Source=%d, Target=%d', 16, 1, @source, @target);
ELSE
    PRINT 'Migration verified: ' + CAST(@target AS VARCHAR) + ' rows migrated';
GO

-- Step 5: (After cutover) Drop source table or mark as deprecated
-- ALTER TABLE [{MonolithDb}].[dbo].[{TableName}] ADD [_Deprecated] BIT DEFAULT 1;
```

### Template: Table Splitting Script

When a table needs to be split between services:

```sql
-- ============================================
-- Migration: Split {TableName} between {ServiceA} and {ServiceB}
-- ============================================

-- ServiceA gets columns: Id, Col1, Col2, Col3
USE [{ServiceA}Db];
GO

CREATE TABLE [{Schema}].[{TableName}] (
    [Id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    [Col1] NVARCHAR(200) NOT NULL,
    [Col2] DECIMAL(18,2) NOT NULL,
    [Col3] DATETIME2 NOT NULL
);
GO

INSERT INTO [{ServiceA}Db].[{Schema}].[{TableName}] (Id, Col1, Col2, Col3)
SELECT Id, Col1, Col2, Col3
FROM [{MonolithDb}].[dbo].[{TableName}];
GO

-- ServiceB gets columns: Id, Col4, Col5, Col6
USE [{ServiceB}Db];
GO

CREATE TABLE [{Schema}].[{TableName}] (
    [Id] UNIQUEIDENTIFIER NOT NULL PRIMARY KEY,
    [Col4] INT NOT NULL,
    [Col5] NVARCHAR(MAX) NULL,
    [Col6] BIT NOT NULL DEFAULT 0
);
GO

INSERT INTO [{ServiceB}Db].[{Schema}].[{TableName}] (Id, Col4, Col5, Col6)
SELECT Id, Col4, Col5, Col6
FROM [{MonolithDb}].[dbo].[{TableName}];
GO
```

---

## Stored Procedure Migration

### Assessment Checklist for Each Stored Procedure

| Question | Answer | Implication |
|----------|--------|-------------|
| Which tables does it read from? | List tables | Determines which service(s) are involved |
| Which tables does it write to? | List tables | Determines ownership |
| Does it join across service boundaries? | Yes/No | If yes, needs rewriting |
| Does it use transactions? | Yes/No | If cross-service, needs saga |
| Is it called from application code? | Yes/No | If yes, needs migration |
| Is it called by other procedures? | Yes/No | Dependency chain |
| Does it use temp tables or cursors? | Yes/No | Complexity indicator |
| Can it be replaced with EF query? | Yes/No | Simplification opportunity |

### Migration Strategies for Stored Procedures

#### Strategy A: Move As-Is (single service tables only)
```sql
-- Procedure only touches OrderService tables → move to OrderService database
-- No changes needed, just recreate in the new database
```

#### Strategy B: Rewrite as Application Code
```csharp
// Replace simple stored procedure with EF Core query
// BEFORE: EXEC sp_GetOrdersByCustomer @CustomerId
// AFTER:
public async Task<List<Order>> GetByCustomerIdAsync(Guid customerId)
{
    return await _context.Orders
        .Include(o => o.Items)
        .Where(o => o.CustomerId == customerId)
        .OrderByDescending(o => o.CreatedAt)
        .ToListAsync();
}
```

#### Strategy C: Split into Multiple Procedures
```
-- Procedure joins Orders and Products tables (different services)
-- Split into:
-- 1. OrderService procedure: Get order data
-- 2. Application code: Call ProductService API for product data
-- 3. Application code: Combine results in memory
```

#### Strategy D: Convert to Domain Service
```csharp
// Complex stored procedure with business logic → domain service
// The business rules move to C# code in the owning service
// Data access uses repository pattern
```

---

## Eventual Consistency Patterns

### Pattern: Event-Driven Data Sync

When Service B needs data owned by Service A:

```
1. Service A modifies its data
2. Service A publishes an integration event (e.g., ProductPriceChanged)
3. Message broker delivers event to Service B
4. Service B updates its local read model/cache
5. Service B uses local data for queries (no API call needed)

Consistency window: typically < 1 second
Acceptable for: product catalogs, customer profiles, inventory levels (display)
Not acceptable for: financial transactions, stock reservations (use sync API)
```

### Pattern: Saga for Distributed Transactions

When a business operation spans multiple services:

```
Example: Place Order Saga

Step 1: OrderService → Create order (status: Pending)
Step 2: InventoryService → Reserve stock
  - Success → proceed to Step 3
  - Failure → Compensate: OrderService → Cancel order
Step 3: PaymentService → Process payment
  - Success → proceed to Step 4
  - Failure → Compensate: InventoryService → Release stock, OrderService → Cancel order
Step 4: OrderService → Confirm order (status: Confirmed)
Step 5: NotificationService → Send confirmation email (fire-and-forget)
```

### Pattern: Outbox Pattern for Reliable Event Publishing

Ensure events are published reliably even if the message broker is temporarily unavailable:

```csharp
// 1. Save entity changes AND outbox message in the same database transaction
await using var transaction = await _context.Database.BeginTransactionAsync();

_context.Orders.Add(order);
_context.OutboxMessages.Add(new OutboxMessage
{
    Id = Guid.NewGuid(),
    Type = nameof(OrderPlacedEvent),
    Payload = JsonSerializer.Serialize(orderPlacedEvent),
    CreatedAt = DateTime.UtcNow,
    ProcessedAt = null
});

await _context.SaveChangesAsync();
await transaction.CommitAsync();

// 2. Background worker polls OutboxMessages table
// 3. Publishes unprocessed messages to message broker
// 4. Marks messages as processed
// 5. Guarantees at-least-once delivery
```

---

## Database Migration Execution Order

### Recommended Approach: Parallel Run

1. Create new service database
2. Set up data sync (CDC, triggers, or application-level dual-write)
3. Migrate historical data
4. Run both databases in parallel
5. Verify data consistency
6. Switch service to new database
7. Monitor for issues
8. Decommission sync mechanism
9. (Eventually) Remove tables from monolith database

### Rollback Plan

For each database migration step:
- Keep monolith database intact until cutover is verified
- Maintain reverse sync capability during parallel run
- Document exact rollback SQL scripts
- Test rollback procedure before production cutover
- Define rollback triggers (error rate threshold, data inconsistency detection)
