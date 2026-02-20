# Database Decomposition and Migration Guide

This steering file provides detailed guidance for splitting a monolithic database into per-service databases during Java microservices extraction. Consult this during Phase 2 planning and Phase 3 execution.

---

## Database Splitting Strategies

### Strategy 1: Database-Per-Service (Target State)

Each microservice owns its own database instance. This is the ideal end state.

```
Monolith DB (before):
┌─────────────────────────────────────────┐
│ orders, order_items, products,          │
│ customers, inventory, payments,         │
│ users, roles, audit_log, ...            │
└─────────────────────────────────────────┘

Per-Service DBs (after):
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ order_db │ │product_db│ │customer_db│ │identity_db│
│ orders   │ │ products │ │ customers │ │ users     │
│order_items│ │categories│ │ addresses │ │ roles     │
└──────────┘ └──────────┘ └──────────┘ └──────────┘
```

Pros: Full autonomy, independent scaling, technology freedom
Cons: Most complex migration, no cross-service joins

### Strategy 2: Schema-Per-Service (Interim Step)

Each service gets its own schema within the same database. Good as a transitional step.

```sql
-- PostgreSQL
CREATE SCHEMA order_schema;
CREATE SCHEMA product_schema;
CREATE SCHEMA customer_schema;

-- Move tables
ALTER TABLE orders SET SCHEMA order_schema;
ALTER TABLE order_items SET SCHEMA order_schema;
ALTER TABLE products SET SCHEMA product_schema;

-- Create service-specific users with schema-level permissions
CREATE USER order_service_user WITH PASSWORD '...';
GRANT USAGE ON SCHEMA order_schema TO order_service_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA order_schema TO order_service_user;
-- Each service can ONLY access its own schema
```

```sql
-- MySQL (no true schemas, use separate databases on same server)
CREATE DATABASE order_db;
CREATE DATABASE product_db;
CREATE USER 'order_svc'@'%' IDENTIFIED BY '...';
GRANT ALL PRIVILEGES ON order_db.* TO 'order_svc'@'%';
```

```sql
-- Oracle
CREATE USER order_schema IDENTIFIED BY "...";
GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE TO order_schema;
-- Move tables via CREATE TABLE AS SELECT or Data Pump
```

Pros: Simpler migration, still enforces boundaries, easy to split later
Cons: Shared database instance, can still be tempted to cross-schema query

### Strategy 3: Shared Database with Logical Boundaries (Simplest Start)

Keep one database but enforce boundaries through code and conventions only. Use this only as a very first step if the team isn't ready for physical separation.

---

## Table Ownership Resolution

### Pattern A: Exclusive Ownership (Easy)

Table is used by only one bounded context → assign to that service.

```
Table: orders → OrderService (exclusive owner)
Table: order_items → OrderService (exclusive owner)
Action: Move to order_db, no changes needed
```

### Pattern B: Primary Owner with Readers (Medium)

One context writes, others only read.

```
Table: products
  - ProductService: READ + WRITE (owner)
  - OrderService: READ (needs product name and price when creating orders)
  - InventoryService: READ (needs product SKU)

Resolution Options:

Option 1: API Call (simplest)
  - OrderService calls ProductService API to get product details
  - Add caching (Caffeine local cache, 5-minute TTL) to reduce API calls
  - Acceptable if read frequency is moderate

Option 2: Event-Driven Denormalization (best for high-read)
  - ProductService publishes ProductUpdatedEvent to Kafka
  - OrderService stores a local read-only copy of needed fields (productId, name, price)
  - InventoryService stores a local copy of (productId, sku)
  - Each consumer maintains its own projection table
  - Eventually consistent (typically < 1 second lag)

Option 3: Shared Read Replica (interim)
  - Create a read replica of the product table
  - Consumers query the replica
  - Owner service manages the source table
  - Transition to Option 1 or 2 later
```

### Pattern C: Multiple Writers (Hard)

Multiple contexts write to the same table.

```
Table: audit_log
  - OrderService: WRITE (logs order events)
  - CustomerService: WRITE (logs customer events)
  - InventoryService: WRITE (logs inventory events)

Resolution Options:

Option 1: Per-Service Audit Table
  - Each service has its own audit_log table
  - Aggregation done at query time (API composition or reporting service)

Option 2: Dedicated Audit Service
  - Create an AuditService that owns the audit_log table
  - Other services publish audit events to Kafka
  - AuditService consumes events and writes to its table

Option 3: Event Store Pattern
  - All services publish events to an event store (Kafka, EventStoreDB)
  - Audit log is a projection of the event stream
```

### Pattern D: Shared Reference Data (Medium)

Tables like countries, currencies, status_codes used by many services.

```
Resolution Options:

Option 1: Duplicate Per Service (recommended for small, stable data)
  - Each service has its own copy of reference data
  - Seed during Flyway migration
  - Rarely changes, so sync is not a concern

Option 2: Shared Reference Data Service
  - Dedicated service for reference data
  - Other services call API or cache locally
  - Good for large or frequently changing reference data

Option 3: Configuration (for very small datasets)
  - Store in application.yml or environment variables
  - No database needed
```

---

## Foreign Key Resolution Patterns

### Cross-Service Foreign Keys

When a table has a foreign key to a table in another service, the FK constraint must be removed.

```sql
-- BEFORE: orders table has FK to customers table
ALTER TABLE orders
    ADD CONSTRAINT fk_orders_customers
    FOREIGN KEY (customer_id) REFERENCES customers(id);

-- AFTER: Remove FK constraint, keep the column
ALTER TABLE orders DROP CONSTRAINT fk_orders_customers;

-- The customer_id column remains as a simple UUID/BIGINT
-- Data integrity is now enforced at the application level
-- OrderService validates customer_id by calling CustomerService API
```

### ID Type Considerations

When splitting, consider standardizing on UUIDs for cross-service IDs:

```sql
-- If monolith uses BIGINT SERIAL/AUTO_INCREMENT:
-- Option 1: Keep BIGINT internally, use UUID for cross-service references
-- Option 2: Migrate to UUID (recommended for new services)

-- PostgreSQL: Add UUID column alongside BIGINT
ALTER TABLE orders ADD COLUMN global_id UUID NOT NULL DEFAULT gen_random_uuid();
CREATE UNIQUE INDEX ix_orders_global_id ON orders (global_id);

-- MySQL: Add UUID column
ALTER TABLE orders ADD COLUMN global_id CHAR(36) NOT NULL DEFAULT (UUID());
CREATE UNIQUE INDEX ix_orders_global_id ON orders (global_id);

-- Update all cross-service references to use global_id
-- Then drop the BIGINT FK columns
```

---

## Data Migration with Flyway

### Flyway Setup Per Service

Each service manages its own database migrations:

```yaml
# application.yml per service
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true
    baseline-version: 0
```

```
service-name/
└── src/main/resources/
    └── db/migration/
        ├── V1__create_orders_table.sql
        ├── V2__create_order_items_table.sql
        ├── V3__add_customer_id_index.sql
        └── V4__add_denormalized_columns.sql
```

### Initial Migration Script Template

```sql
-- V1__initial_schema.sql
-- Service: {service-name}
-- Migrated from monolith database

CREATE TABLE IF NOT EXISTS {table_name} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- columns from monolith table
    -- REMOVE: foreign key columns to other services (keep as simple ID)
    -- ADD: denormalized columns for display data
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX ix_{table}_{column} ON {table_name} ({column});

-- Seed reference data if needed
INSERT INTO {table_name} (...) VALUES (...) ON CONFLICT DO NOTHING;
```

### Data Migration Script Template

```sql
-- V2__migrate_data_from_monolith.sql
-- One-time migration: copy data from monolith database
-- Run this ONCE during initial migration, then remove or skip

-- Option 1: Direct insert (if databases are on same server)
INSERT INTO {service_db}.{table} (id, col1, col2, ...)
SELECT id, col1, col2, ...
FROM {monolith_db}.{table};

-- Option 2: Use pg_dump/pg_restore or mysqldump for large datasets
-- Option 3: Application-level migration with batch processing (for transformations)
```

### Liquibase Alternative

If the monolith uses Liquibase instead of Flyway:

```yaml
# application.yml
spring:
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.yaml
```

```yaml
# db/changelog/db.changelog-master.yaml
databaseChangeLog:
  - include:
      file: db/changelog/001-create-orders.yaml
  - include:
      file: db/changelog/002-create-order-items.yaml
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
| Does it use cursors or temp tables? | Yes/No | Complexity indicator |
| Can it be replaced with JPA query? | Yes/No | Simplification opportunity |

### Migration Strategies for Stored Procedures

#### Strategy A: Move As-Is (single service tables only)
```sql
-- Procedure only touches order_service tables → move to order_db
-- Recreate in the new database, no changes needed
```

#### Strategy B: Rewrite as Application Code
```java
// Replace simple stored procedure with Spring Data JPA query
// BEFORE: CALL sp_get_orders_by_customer(?)
// AFTER:
public interface OrderRepository extends JpaRepository<Order, UUID> {
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.customerId = :customerId ORDER BY o.createdAt DESC")
    List<Order> findByCustomerIdWithItems(@Param("customerId") UUID customerId);
}
```

#### Strategy C: Split into Multiple Queries
```
-- Procedure joins orders and products tables (different services)
-- Split into:
-- 1. OrderService repository: Get order data
-- 2. Application service: Call ProductService API for product data
-- 3. Application service: Combine results in memory (Java Streams)
```

#### Strategy D: Convert to Domain Service
```java
// Complex stored procedure with business logic → domain service
@Service
@Transactional
public class OrderPricingService {
    // Business rules that were in the stored procedure
    // now live in Java code in the owning service
    public BigDecimal calculateOrderTotal(Order order) {
        return order.getItems().stream()
            .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
```

---

## Database-Specific Migration Notes

### PostgreSQL
- Schema-per-service works natively (`CREATE SCHEMA`)
- `gen_random_uuid()` for UUID generation (requires `pgcrypto` extension on older versions)
- `pg_dump --schema=order_schema` for per-schema export
- Foreign Data Wrappers (FDW) as interim cross-database query solution (remove later)
- Logical replication for zero-downtime data migration

### MySQL
- No true schema separation (database = schema in MySQL)
- Use separate databases on same server as interim step
- `UUID()` function for UUID generation (stored as `CHAR(36)` or `BINARY(16)`)
- `mysqldump --databases order_db` for per-database export
- MySQL replication for zero-downtime migration

### Oracle
- Schema = User in Oracle
- Use separate schemas with grants for interim step
- `SYS_GUID()` for UUID generation (stored as `RAW(16)`)
- Data Pump (`expdp`/`impdp`) for data migration
- Oracle GoldenGate for zero-downtime replication
- PL/SQL packages → convert to Java domain services
- Database links as interim cross-schema solution (remove later)

### SQL Server
- Schema-per-service works natively (`CREATE SCHEMA`)
- `NEWID()` for UUID generation (`UNIQUEIDENTIFIER` type)
- Cross-database queries possible on same server (interim)
- SQL Server replication or Change Data Capture (CDC) for migration

### H2 (Development/Testing)
- Each service uses its own H2 instance in tests
- `MODE=PostgreSQL` or `MODE=MySQL` for compatibility
- Flyway migrations run against H2 in tests
- Testcontainers preferred for integration tests (real database)

---

## Eventual Consistency Patterns

### Pattern: Event-Driven Data Sync

When Service B needs data owned by Service A:

```
1. Service A modifies its data
2. Service A publishes an integration event to Kafka (e.g., ProductPriceChangedEvent)
3. Kafka delivers event to Service B's consumer group
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

Step 1: OrderService → Create order (status: PENDING)
Step 2: InventoryService → Reserve stock
  - Success → proceed to Step 3
  - Failure → Compensate: OrderService → Cancel order
Step 3: PaymentService → Process payment
  - Success → proceed to Step 4
  - Failure → Compensate: InventoryService → Release stock, OrderService → Cancel order
Step 4: OrderService → Confirm order (status: CONFIRMED)
Step 5: NotificationService → Send confirmation email (fire-and-forget)
```

Implementation options:
- **Choreography** — services react to events (simpler, harder to trace)
- **Orchestration** — central saga coordinator (more complex, easier to trace)
- **Axon Framework** — built-in saga support for Java
- **Temporal** — workflow engine for complex sagas

### Pattern: Outbox Pattern for Reliable Event Publishing

Ensure events are published reliably even if the message broker is temporarily unavailable:

```java
// 1. Save entity changes AND outbox message in the same database transaction
@Transactional
public OrderResponse createOrder(CreateOrderRequest request) {
    Order order = orderMapper.toEntity(request);
    orderRepository.save(order);

    outboxRepository.save(OutboxMessage.builder()
        .id(UUID.randomUUID())
        .aggregateType("Order")
        .aggregateId(order.getId().toString())
        .eventType("OrderCreatedEvent")
        .payload(objectMapper.writeValueAsString(new OrderCreatedEvent(order)))
        .createdAt(Instant.now())
        .build());

    return orderMapper.toResponse(order);
}

// 2. Background worker polls outbox table
@Scheduled(fixedDelay = 1000)
@Transactional
public void publishOutboxMessages() {
    List<OutboxMessage> messages = outboxRepository.findUnpublished();
    for (OutboxMessage msg : messages) {
        kafkaTemplate.send(msg.getAggregateType(), msg.getAggregateId(), msg.getPayload());
        msg.markPublished();
    }
}

// 3. Guarantees at-least-once delivery
// 4. Consumers must be idempotent (use eventId for deduplication)
```

Alternative: Use Debezium CDC (Change Data Capture) to stream outbox table changes to Kafka automatically — no polling needed.

---

## Database Migration Execution Order

### Change Data Capture (CDC) with Debezium

Debezium is the recommended tool for zero-downtime data synchronization during migration. It captures row-level changes from the source database and streams them to Kafka.

```
Monolith DB → Debezium Connector → Kafka → New Service DB
```

**Setup:**
1. Deploy Debezium connector for your database (PostgreSQL, MySQL, Oracle, SQL Server)
2. Configure connector to capture changes from monolith tables
3. New service consumes change events and applies to its database
4. Supports initial snapshot + ongoing CDC (no data loss)

**Advantages over application-level dual-write:**
- No monolith code changes required
- Captures all changes (including direct SQL, batch jobs, stored procedures)
- Exactly-once semantics with Kafka Connect
- Can also power the outbox pattern (capture outbox table changes automatically)

```json
// Debezium connector configuration (PostgreSQL example)
{
  "name": "monolith-orders-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "monolith-db",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "${DB_PASSWORD}",
    "database.dbname": "monolith_db",
    "table.include.list": "public.orders,public.order_items",
    "topic.prefix": "monolith",
    "plugin.name": "pgoutput"
  }
}
```

### Recommended Approach: Parallel Run

1. Create new service database
2. Set up data sync (CDC, triggers, or application-level dual-write)
3. Migrate historical data (batch job or pg_dump/restore)
4. Run both databases in parallel
5. Verify data consistency (row counts, checksums, spot checks)
6. Switch service to new database (feature flag)
7. Monitor for issues (48+ hours)
8. Decommission sync mechanism
9. (Eventually) Remove tables from monolith database

### Rollback Plan

For each database migration step:
- Keep monolith database intact until cutover is verified
- Maintain reverse sync capability during parallel run
- Document exact rollback steps
- Test rollback procedure before production cutover
- Define rollback triggers (error rate threshold, data inconsistency detection)

### Zero-Downtime Migration Checklist

```
- [ ] New database created and accessible from service
- [ ] Flyway migrations applied successfully
- [ ] Historical data migrated and verified
- [ ] Data sync mechanism running (CDC or dual-write)
- [ ] Service tested against new database in staging
- [ ] Feature flag ready to switch database connection
- [ ] Monitoring dashboards for new database
- [ ] Rollback procedure documented and tested
- [ ] On-call team briefed
- [ ] Cutover window scheduled (low-traffic period)
```
