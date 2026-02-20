# Entity Framework Patterns Reference

Patterns specific to Entity Framework 6 and Entity Framework Core during monolith-to-microservices decomposition.

---

## Single Large DbContext (God Context)
**Pattern:** One DbContext with 50+ DbSets covering the entire domain.
**Resolution:**
- Split into one DbContext per microservice
- Each context includes only its owned entities
- Remove navigation properties that cross service boundaries
- Cross-service relationships become ID-only references
- OnModelCreating configurations split by entity ownership
- Shared configurations (e.g., audit columns) → base configuration class

## Multiple DbContexts (Already Split)
**Pattern:** Monolith already uses multiple DbContexts for different areas.
**Resolution:**
- Existing context boundaries may align with service boundaries
- Validate that context boundaries match domain boundaries
- May need to further split or merge contexts
- Check for entities registered in multiple contexts (shared entities)

## EDMX (Database First)
**Pattern:** Entity Framework using .edmx visual designer files.
**Resolution:**
- Convert to Code First during migration
- Use EF Power Tools or `Scaffold-DbContext` to generate entity classes from database
- Create Fluent API configurations from EDMX mappings
- Each service gets Code First entities for its owned tables
- Complex EDMX mappings (table splitting, entity splitting) need manual conversion

## Table-Per-Hierarchy (TPH) Inheritance
**Pattern:** Multiple entity types stored in a single table with a discriminator column.
**Resolution:**
- If all types belong to one service → move the entire hierarchy
- If types span services → split the table (each service gets its own table for its types)
- Discriminator column may need to be replicated or removed
- Consider converting to Table-Per-Type (TPT) during migration for cleaner separation

## Table-Per-Type (TPT) Inheritance
**Pattern:** Each entity type in the hierarchy has its own table.
**Resolution:**
- Base table ownership must be assigned to one service
- Derived type tables move with their owning service
- Cross-service inheritance hierarchies need to be broken (use composition instead)

## Many-to-Many Relationships
**Pattern:** Join tables for many-to-many relationships (explicit or implicit in EF Core 5+).
**Resolution:**
- If both entities are in the same service → keep the join table
- If entities are in different services → the join table goes with the service that "owns" the relationship
- The other service queries via API to get related IDs
- Consider denormalizing if query performance is critical

## Owned Types and Value Objects
**Pattern:** EF Core Owned Types or DDD Value Objects mapped to database columns.
**Resolution:**
- Owned types stay with their owning entity
- If the parent entity moves to a service, owned types move with it
- Value objects shared across services → duplicate in each service or put in shared kernel
- Complex owned types with their own table → move with parent entity

## Global Query Filters
**Pattern:** HasQueryFilter() for soft delete, multi-tenancy, etc.
**Resolution:**
- Each service's DbContext replicates relevant filters
- Tenant filtering may need a shared approach (tenant ID from JWT claims)
- Soft delete filters move with their entities
- Be careful with IgnoreQueryFilters() calls — they need to move too

## Interceptors and SaveChanges Overrides
**Pattern:** Custom logic in SaveChanges or via EF interceptors (auditing, timestamps, etc.).
**Resolution:**
- Audit interceptors → shared infrastructure package (BuildingBlocks)
- Domain-specific interceptors → move with their service
- Cross-cutting interceptors → replicate per service
- SaveChanges overrides → convert to interceptors for better separation

## Compiled Queries
**Pattern:** EF.CompileQuery() or EF.CompileAsyncQuery() for performance.
**Resolution:**
- Move compiled queries with their owning service
- Queries that join across service boundaries need rewriting
- Consider if compiled queries are still needed (EF Core has better query caching)

## Raw SQL and FromSqlRaw
**Pattern:** Direct SQL execution via FromSqlRaw, ExecuteSqlRaw, or SqlQuery.
**Resolution:**
- Queries scoped to one service's tables → move with that service
- Cross-service SQL queries → split into multiple service calls
- Ensure SQL references correct schema/database after migration
- Parameterized queries must remain parameterized (security)
