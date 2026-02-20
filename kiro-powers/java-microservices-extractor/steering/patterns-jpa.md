# JPA / Hibernate Patterns Reference

Patterns specific to JPA and Hibernate during monolith-to-microservices decomposition. Covers entity splitting, relationship handling, inheritance strategies, second-level cache, native queries, and multi-tenancy.

---

## Single Large Persistence Unit (God Context)
**Pattern:** One `persistence.xml` or Spring Boot auto-configuration managing 50+ entities in a single `EntityManagerFactory`.
**Resolution:**
- Split into one persistence configuration per microservice
- Each service includes only its owned entities via `@EntityScan` and `@EnableJpaRepositories` with specific base packages
- Remove `@ManyToOne` / `@OneToMany` that cross service boundaries
- Cross-service relationships become ID-only columns (no JPA mapping)
- Shared `@MappedSuperclass` (audit fields, base entity) → common-domain library

## Multiple Persistence Units (Already Split)
**Pattern:** Monolith already uses multiple `EntityManagerFactory` beans for different databases or schemas.
**Resolution:**
- Existing persistence unit boundaries may align with service boundaries
- Validate that boundaries match domain boundaries
- May need to further split or merge
- Check for entities registered in multiple persistence units

## Hibernate XML Mappings (.hbm.xml)
**Pattern:** Entity mappings defined in `.hbm.xml` files instead of annotations.
**Resolution:**
- Convert to JPA annotations during migration
- Each service gets annotation-based entities for its owned tables
- Complex XML mappings (formula, subselect, custom types) need manual conversion
- `hibernate.cfg.xml` → Spring Boot `spring.jpa.*` properties

---

## Inheritance Strategies

### Single Table (TABLE_PER_CLASS Discriminator)
**Pattern:** `@Inheritance(strategy = InheritanceType.SINGLE_TABLE)` with `@DiscriminatorColumn`.
**Resolution:**
- If all subtypes belong to one service → move the entire hierarchy
- If subtypes span services → split the table:
  - Each service gets its own table for its subtypes
  - Remove inheritance, use composition instead
  - Discriminator column may be dropped or kept for backward compatibility
- Consider converting to separate tables during migration for cleaner separation

### Joined Table
**Pattern:** `@Inheritance(strategy = InheritanceType.JOINED)` with each subtype in its own table.
**Resolution:**
- Base table ownership assigned to one service
- Subtype tables move with their owning service
- Cross-service inheritance hierarchies must be broken (use composition)
- Joins across service databases not possible → denormalize or API calls

### Table Per Class
**Pattern:** `@Inheritance(strategy = InheritanceType.TABLE_PER_CLASS)` with each concrete class in its own table.
**Resolution:**
- Each concrete entity table moves with its owning service
- Polymorphic queries (`SELECT FROM BaseType`) → not possible across services
- Replace polymorphic queries with per-service queries + API composition
- Cleanest inheritance strategy for service splitting

---

## Relationship Patterns

### @ManyToOne Across Service Boundaries
**Pattern:** Entity in Service A has `@ManyToOne` to entity in Service B.
**Resolution:**
```java
// BEFORE (monolith)
@Entity
public class OrderItem {
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    private Product product;  // Product is in another service
}

// AFTER (microservice)
@Entity
public class OrderItem {
    @Column(name = "product_id", nullable = false)
    private UUID productId;  // Just the ID, no JPA relationship

    private String productName;   // Denormalized for display
    private BigDecimal unitPrice; // Snapshot at time of order
}
```
- Remove the `@ManyToOne` annotation
- Keep the FK column as a simple typed field
- Denormalize frequently needed fields (name, price snapshot)
- Fetch full details via Feign/WebClient when needed

### @OneToMany Across Service Boundaries
**Pattern:** Entity in Service A has `@OneToMany` to entities in Service B.
**Resolution:**
- Remove the `@OneToMany` collection
- The "many" side service provides an API to query by the parent ID
- Example: `OrderService` calls `GET /api/order-items?orderId={id}` if items are in another service
- Usually the `@OneToMany` and its children belong in the same service (aggregate pattern)

### @ManyToMany Across Service Boundaries
**Pattern:** Join table connecting entities from different services.
**Resolution:**
- Join table ownership goes to the service that "owns" the relationship
- The other service queries via API to get related IDs
- Consider which service is the source of truth for the association
- Example: `UserRole` join table → Identity service owns it
```java
// Identity service owns the user-role relationship
// Other services call Identity API to check roles
```

### @OneToOne Across Service Boundaries
**Pattern:** Two entities with `@OneToOne` in different services.
**Resolution:**
- Remove the `@OneToOne` mapping
- Keep the FK column as a simple ID field
- Fetch related entity via API call when needed
- Consider if the two entities should actually be in the same service

### Cascade Operations Across Boundaries
**Pattern:** `cascade = CascadeType.ALL` or `CascadeType.REMOVE` on cross-boundary relationships.
**Resolution:**
- Cascades cannot cross service boundaries
- Replace with explicit service calls or events
- `CascadeType.REMOVE` → publish deletion event, consuming service handles cleanup
- `CascadeType.PERSIST` → orchestrate creation via saga or sequential API calls

---

## Embedded Types and Value Objects

### @Embeddable / @Embedded
**Pattern:** Value objects embedded in entities (`@Embeddable` classes).
**Resolution:**
- Embedded types move with their owning entity
- If the same `@Embeddable` is used across services → duplicate in each service
- Shared value objects (Money, Address) → common-domain library
- `@AttributeOverride` configurations move with the entity

### @ElementCollection
**Pattern:** Collections of embeddable types or basic types stored in a separate table.
**Resolution:**
- Element collection table moves with the owning entity's service
- The collection table is part of the aggregate → same service
- No cross-service element collections

---

## Query Patterns

### JPQL / HQL Queries
**Pattern:** `@Query` annotations or `createQuery()` with JPQL/HQL.
**Resolution:**
- Queries referencing only service-owned entities → move as-is
- Queries joining across service boundaries → split into multiple queries + in-memory composition
- Named queries (`@NamedQuery`) → move with their entity
- Dynamic queries (Criteria API) → move with their service

### Native SQL Queries
**Pattern:** `@Query(nativeQuery = true)`, `createNativeQuery()`, `@SqlResultSetMapping`.
**Resolution:**
- Native queries referencing service-owned tables → move as-is, update schema/table names if needed
- Cross-service native queries → rewrite as service calls
- Result set mappings → move with their service
- Database-specific SQL → may need adjustment if services use different databases

### JPA Criteria API
**Pattern:** `CriteriaBuilder`, `CriteriaQuery`, `Predicate` for dynamic queries.
**Resolution:**
- Criteria queries move with their entity's service
- Cross-entity criteria joins → split into per-service queries
- `Specification<T>` pattern → move with entity's service
- Metamodel classes (`*_`) → regenerated per service

### QueryDSL
**Pattern:** `Q*` generated classes with type-safe queries.
**Resolution:**
- QueryDSL generated classes regenerated per service database
- Queries scoped to one service → move as-is
- Cross-service joins → split into service calls
- QueryDSL configuration (APT plugin) → per-service build config

### Stored Procedure Calls
**Pattern:** `@NamedStoredProcedureQuery`, `@Procedure`, `StoredProcedureQuery`.
**Resolution:**
- Procedures touching single-service tables → move with that service
- Cross-service procedures → rewrite (see database-migration steering file)
- `@Procedure` annotations → move with their repository
- `CallableStatement` usage → move with the calling service

---

## Caching Patterns

### Second-Level Cache (Ehcache / Caffeine / Hazelcast)
**Pattern:** `@Cacheable` on entities, `@Cache` (Hibernate), `hibernate.cache.region.factory_class`.
**Resolution:**
- Each service configures its own second-level cache
- Cache regions scoped to service entities
- Shared cache regions → not possible across services
- Cache invalidation across services → event-driven
- Hibernate cache configuration → per-service `application.yml`

### Query Cache
**Pattern:** `hibernate.cache.use_query_cache = true`, `@QueryHint(name = "org.hibernate.cacheable", value = "true")`.
**Resolution:**
- Query cache per service (scoped to service's queries)
- Cross-service query results → not cacheable at JPA level, use application-level caching
- Query cache invalidation → automatic within service, event-driven across services

---

## Multi-Tenancy Patterns

### Schema-Per-Tenant
**Pattern:** `MultiTenantConnectionProvider` with schema-based isolation.
**Resolution:**
- Each service implements its own multi-tenancy
- Tenant resolution (from JWT, header, subdomain) → shared filter in common-infrastructure
- Schema routing → per-service `MultiTenantConnectionProvider`
- Flyway migrations → per-tenant schema migration

### Database-Per-Tenant
**Pattern:** Separate database per tenant with dynamic DataSource routing.
**Resolution:**
- Each service manages its own tenant database routing
- `AbstractRoutingDataSource` → per-service configuration
- Tenant context propagation → via HTTP header or JWT claim
- Connection pool per tenant → HikariCP configuration per service

### Discriminator Column
**Pattern:** `@TenantId` column or `@Filter` for row-level tenant isolation.
**Resolution:**
- Tenant filter moves with the entity's service
- `@Filter` / `@FilterDef` → per-service Hibernate configuration
- Global filter enabling → per-service request filter
- Ensure tenant ID is always set (security critical)

---

## Transaction Patterns

### @Transactional Spanning Multiple Repositories
**Pattern:** Single `@Transactional` method updating entities from multiple bounded contexts.
**Resolution:**
- If entities are in the same service → keep the transaction
- If entities span services → replace with saga pattern or eventual consistency
- Evaluate business impact of eventual consistency for each case
- Document which transactions can tolerate eventual consistency

### JTA / XA Distributed Transactions
**Pattern:** `JtaTransactionManager`, `@TransactionAttribute`, XA DataSources.
**Resolution:**
- Remove JTA/XA transactions during migration
- Replace with local transactions per service (`PlatformTransactionManager`)
- Cross-service consistency → saga pattern with compensation
- XA DataSources → standard HikariCP DataSources
- Two-phase commit → eventual consistency with outbox pattern

### Programmatic Transaction Management
**Pattern:** `TransactionTemplate`, `PlatformTransactionManager.getTransaction()`.
**Resolution:**
- Programmatic transactions move with their service
- Ensure `TransactionManager` is service-specific
- Cross-service programmatic transactions → saga pattern

### @TransactionalEventListener
**Pattern:** Event listeners that execute after transaction commit.
**Resolution:**
- Intra-service → keep as `@TransactionalEventListener`
- Cross-service → use outbox pattern:
  1. Save entity + outbox message in same transaction
  2. Background worker publishes outbox messages to broker
  3. Guarantees at-least-once delivery
- `TransactionPhase.AFTER_COMMIT` → outbox pattern equivalent

---

## Performance Patterns

### Fetch Strategies (LAZY vs EAGER)
**Pattern:** `FetchType.LAZY` / `FetchType.EAGER` on relationships.
**Resolution:**
- Cross-service relationships removed → fetch strategy irrelevant
- Intra-service relationships → prefer LAZY, use `JOIN FETCH` in queries
- `@EntityGraph` → move with entity's service
- N+1 query problems → address during extraction with proper fetch joins

### Batch Fetching
**Pattern:** `@BatchSize`, `hibernate.default_batch_fetch_size`.
**Resolution:**
- Batch fetch configuration → per-service Hibernate properties
- Batch size tuning → per-service based on entity access patterns

### Read-Only Transactions
**Pattern:** `@Transactional(readOnly = true)` for query optimization.
**Resolution:**
- Read-only transactions move with their service
- Hibernate flush mode optimization preserved
- Connection routing to read replicas → per-service DataSource configuration

### Connection Pooling
**Pattern:** HikariCP, C3P0, or DBCP connection pool configuration.
**Resolution:**
- Each service gets its own connection pool
- Pool sizing based on service load (not monolith sizing)
- HikariCP (Spring Boot default) → per-service `spring.datasource.hikari.*` properties
- Monitor pool usage per service (Actuator + Micrometer)
