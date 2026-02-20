# Java Patterns Reference Guide

Comprehensive reference for handling specific Java patterns during monolith-to-microservices decomposition. This file covers the most commonly needed patterns during transformation. For specialized topics, consult the targeted sub-files:

- **patterns-spring.md** — Spring MVC, Spring Boot, Spring Security, Spring Batch, Spring Integration, Spring Cloud patterns
- **patterns-jpa.md** — JPA/Hibernate patterns (entity splitting, relationship handling, inheritance, second-level cache, native queries)
- **patterns-auth.md** — Authentication and authorization (Spring Security, OAuth2, SAML, LDAP, Keycloak, custom filters)

---

## Dependency Injection Patterns

### Spring IoC (Annotation-Based)
**Pattern:** `@Component`, `@Service`, `@Repository`, `@Controller` with `@Autowired` or constructor injection.
**Resolution:**
- Each service gets its own Spring context with only its beans
- Remove `@ComponentScan` packages that reference other services' packages
- Constructor injection preferred over field injection during migration
- `@Qualifier` annotations may need updating if bean names change

### Spring XML Configuration
**Pattern:** `applicationContext.xml` with `<bean>` definitions, `<import>` of other XML files.
**Resolution:**
- Convert to `@Configuration` classes during extraction
- Each service gets its own configuration classes
- XML imports that cross service boundaries → remove, replace with API calls
- Property placeholders (`${...}`) → `application.yml` properties
- If XML config is deeply embedded, migrate incrementally (Java config alongside XML)

### CDI / Weld (Jakarta EE)
**Pattern:** `@Inject`, `@Named`, `@ApplicationScoped`, `@RequestScoped` with `beans.xml`.
**Resolution:**
- Convert to Spring DI during migration to Spring Boot
- `@Inject` → `@Autowired` (or keep `@Inject`, Spring supports it)
- `@Named` → `@Component` / `@Service` / `@Repository`
- `@ApplicationScoped` → `@Singleton` (Spring) or default singleton scope
- `@RequestScoped` → `@Scope("request")`
- CDI producers (`@Produces`) → `@Bean` methods in `@Configuration`
- CDI interceptors → Spring AOP `@Aspect`
- CDI events → Spring `ApplicationEventPublisher`

### Google Guice
**Pattern:** `AbstractModule` with `bind()` calls, `@Inject` (Guice), `Provider<T>`.
**Resolution:**
- Convert to Spring DI during migration
- `bind(Interface.class).to(Implementation.class)` → `@Bean` or `@Component`
- `@Provides` methods → `@Bean` methods
- Guice `Provider<T>` → Spring `ObjectProvider<T>` or `@Lazy`
- Guice scopes → Spring scopes
- Guice AOP (`bindInterceptor`) → Spring AOP `@Aspect`

### Dagger 2
**Pattern:** `@Component` (Dagger), `@Module`, `@Provides`, compile-time DI.
**Resolution:**
- Convert to Spring DI (runtime DI)
- Dagger `@Module` → Spring `@Configuration`
- Dagger `@Provides` → Spring `@Bean`
- Dagger `@Component` → Spring application context
- Dagger `@Singleton` → Spring singleton scope (default)
- Compile-time validation lost — add integration tests to compensate

### Service Locator Anti-Pattern
**Pattern:** Using `ApplicationContext.getBean()` or static service locator throughout code.
**Resolution:**
- Refactor to constructor injection during extraction
- Each service should use proper DI
- Remove static `ApplicationContext` holders
- If deeply embedded, refactor incrementally per service

### Factory Patterns
**Pattern:** Abstract factories or factory methods registered as Spring beans.
**Resolution:**
- Factories that create entities for one service → move with that service
- Factories that create cross-cutting infrastructure → shared library
- Factory registrations move with their consumers
- `FactoryBean<T>` → move with the bean it creates

---

## Data Access Patterns

### Repository Pattern (Spring Data)
**Pattern:** Interfaces extending `JpaRepository`, `CrudRepository`, `PagingAndSortingRepository`.
**Resolution:**
- Each service gets its own repository interfaces for its owned entities
- Custom query methods move with their entity's service
- `@Query` annotations referencing other service entities → rewrite
- Custom repository implementations (`*RepositoryImpl`) → move with service

### Generic DAO Pattern
**Pattern:** Custom generic DAO base class wrapping `EntityManager`.
**Resolution:**
- Replace with Spring Data JPA repositories during migration
- If keeping custom DAO, each service gets its own DAO implementations
- Generic DAO base class → shared infrastructure library
- Entity-specific DAOs → move with their service

### Unit of Work (JPA EntityManager)
**Pattern:** `EntityManager` managing persistence context as unit of work.
**Resolution:**
- Each service gets its own `EntityManager` / `EntityManagerFactory`
- Cross-service transactions → replace with saga pattern
- `@PersistenceContext` injection scoped to service-specific persistence unit
- `persistence.xml` split per service (or use Spring Boot auto-configuration)

### CQRS Pattern
**Pattern:** Separate command and query models, often with Axon Framework or custom implementation.
**Resolution:**
- Commands and queries split by service ownership
- Each service gets its own command/query handlers
- Read models may need to aggregate data from multiple services → API composition
- Axon aggregates → move with their bounded context
- Event store → per-service or shared (Axon Server)

### Specification Pattern
**Pattern:** JPA Criteria API specifications or Spring Data `Specification<T>`.
**Resolution:**
- Specifications move with their entity's owning service
- Shared specification base class → shared kernel
- Cross-entity specifications → split or move to primary entity's service
- `Specification<T>` composability preserved within service boundaries

### MyBatis Mappers
**Pattern:** `@Mapper` interfaces with XML mapper files or annotation-based SQL.
**Resolution:**
- Mapper interfaces move with their entity's owning service
- XML mapper files (`*Mapper.xml`) move with the mapper interface
- Cross-service joins in mapper XML → split into multiple service calls
- Result maps referencing other service entities → simplify to ID references
- MyBatis configuration (`mybatis-config.xml`) → per-service configuration

### Plain JDBC / JdbcTemplate
**Pattern:** Direct `JdbcTemplate`, `NamedParameterJdbcTemplate`, or raw JDBC usage.
**Resolution:**
- Queries scoped to one service's tables → move with that service
- Cross-service joins → split into multiple service calls + in-memory composition
- Connection strings → service-specific DataSource configuration
- `RowMapper` implementations → move with their service

### jOOQ
**Pattern:** Type-safe SQL with jOOQ generated classes.
**Resolution:**
- Generated classes regenerated per service database schema
- Queries scoped to one service → move with that service
- Cross-schema joins → split into service calls
- jOOQ code generation configuration → per-service

### Stored Procedures and Native Queries
**Pattern:** `@NamedStoredProcedureQuery`, `@Procedure`, `@Query(nativeQuery = true)`, `CallableStatement`.
**Resolution:**
- Procedures touching single-service tables → move with that service
- Procedures joining across boundaries → rewrite as service calls + in-memory joins
- Simple procedures → replace with Spring Data JPA queries
- Complex procedures → convert to domain services
- See database-migration steering file for detailed strategies

---

## Communication Patterns

### Direct Service Calls (In-Process)
**Pattern:** Service A directly calls Service B's methods (both in same JVM).
**Resolution:**
- Replace with HTTP (Feign/WebClient) or gRPC calls between services
- Define API contracts as DTOs in each service
- Add resilience (Resilience4j: retry, circuit breaker, bulkhead)
- Performance impact: ~1-10ms in-process → ~10-100ms HTTP (plan accordingly)
- Consider async messaging for non-time-sensitive operations

### Spring Application Events
**Pattern:** `ApplicationEventPublisher.publishEvent()` with `@EventListener`.
**Resolution:**
- Intra-service events → keep as Spring events within the service
- Cross-service events → convert to integration events via Kafka/RabbitMQ
- `@TransactionalEventListener` → use outbox pattern for reliable publishing
- Ensure handlers are idempotent when converting to distributed events

### Apache Camel Routes
**Pattern:** `RouteBuilder` with `from().to()` integration patterns.
**Resolution:**
- Routes scoped to one domain → move with that service
- Routes that integrate multiple domains → split at domain boundaries
- Camel endpoints become inter-service communication points
- Consider replacing simple routes with Spring Integration or direct HTTP/messaging

### Spring Integration Flows
**Pattern:** `IntegrationFlow` with channels, transformers, routers, service activators.
**Resolution:**
- Flows scoped to one domain → move with that service
- Flows spanning domains → split at domain boundaries
- Channel adapters become inter-service messaging endpoints
- Consider simplifying to direct Kafka/RabbitMQ usage during migration

### Background Jobs (Quartz / @Scheduled)
**Pattern:** Quartz `Job` implementations, `@Scheduled` cron methods, `@Async` methods.
**Resolution:**
- Jobs scoped to one domain → move with that service
- Jobs spanning domains → split into service-specific jobs with event coordination
- Each service gets its own Quartz scheduler / job store
- `@Scheduled` methods → move with their service, ensure only one instance runs (use `@SchedulerLock` from ShedLock)
- `@Async` methods → move with their service, configure per-service thread pools
- Spring Batch jobs → move with their domain, each service gets its own batch configuration

### gRPC Services
**Pattern:** `.proto` files with gRPC service definitions.
**Resolution:**
- Each `.proto` file typically maps to one service
- Shared `.proto` definitions → published as Maven artifact
- gRPC excellent for internal service-to-service (faster than REST)
- Consider gRPC for internal, REST for external APIs

### WebSocket / STOMP
**Pattern:** Spring WebSocket with STOMP messaging.
**Resolution:**
- WebSocket endpoints stay with the service owning the real-time feature
- If multiple services push to clients → dedicated notification service
- Consider message broker (RabbitMQ) as STOMP relay for scaling
- Client connections managed by gateway or dedicated WebSocket service

---

## Configuration Patterns

### Static Configuration Classes
**Pattern:** Static final fields or singleton configuration holders loaded at startup.
**Resolution:**
- Replace with `@ConfigurationProperties` per service
- Each service defines its own strongly-typed configuration classes
- Remove static configuration holders

### Properties Files
**Pattern:** `application.properties` / `application.yml` with all configuration in one file.
**Resolution:**
- Split into per-service `application.yml` files
- Shared configuration → Spring Cloud Config Server or environment variables
- Profile-specific configuration → `application-{profile}.yml` per service
- Secrets → externalize to vault (HashiCorp Vault, AWS Secrets Manager)

### JNDI Lookups
**Pattern:** `InitialContext.lookup()` for DataSources, JMS ConnectionFactories in app server.
**Resolution:**
- Replace with Spring Boot auto-configuration
- DataSource → `spring.datasource.*` properties
- JMS → `spring.activemq.*` or `spring.rabbitmq.*` properties
- Remove all JNDI dependencies during migration to embedded containers

### System Properties / Environment Variables
**Pattern:** `System.getProperty()` or `System.getenv()` scattered through code.
**Resolution:**
- Centralize into `@ConfigurationProperties` classes
- Inject via `@Value("${property.name}")` or typed config beans
- Each service defines its own required properties

---

## Caching Patterns

### Ehcache / Caffeine (Local Cache)
**Pattern:** `@Cacheable`, `@CacheEvict` with local cache provider.
**Resolution:**
- Each service gets its own cache configuration
- Cache names scoped to service (avoid collisions)
- Cross-service cache invalidation → event-driven invalidation
- Consider Redis for shared cache needs

### Hazelcast (Distributed Cache)
**Pattern:** Hazelcast `IMap`, `IQueue` for distributed data structures.
**Resolution:**
- Each service gets its own Hazelcast instance or cluster
- Shared Hazelcast maps → replace with per-service caches + events
- Hazelcast for session clustering → replace with Redis or JWT (stateless)

### Spring Cache Abstraction
**Pattern:** `@Cacheable`, `@CachePut`, `@CacheEvict` with `CacheManager`.
**Resolution:**
- Cache annotations move with their service
- Each service configures its own `CacheManager`
- Cross-service cache dependencies → event-driven invalidation

---

## Anti-Patterns to Watch For

### God Classes
**Pattern:** Large classes with many responsibilities (e.g., 2000-line `OrderService`).
**Resolution:** Split by responsibility during extraction. Each microservice gets only the methods relevant to its domain.

### Circular Dependencies
**Pattern:** Package A imports Package B which imports Package A.
**Resolution:** Must be broken before extraction. Extract shared interfaces into a separate module. Use dependency inversion.

### Tight Database Coupling
**Pattern:** Services directly querying each other's tables via joins or views.
**Resolution:** Replace with API calls between services. Create materialized views or read models for query-heavy scenarios. See database-migration steering file.

### Shared Mutable State
**Pattern:** Static variables, singletons, `ThreadLocal`, `ConcurrentHashMap` used as global state.
**Resolution:** Each service gets its own state. Shared state → distributed cache (Redis) or dedicated state service.

### Distributed Monolith
**Warning:** Splitting a monolith into services that are still tightly coupled creates a distributed monolith — worse than the original.
**Prevention:**
- Each service must be independently deployable
- Minimize synchronous inter-service calls
- Prefer events over direct API calls where possible
- Each service owns its data completely
- No shared databases in the final state
- Test: can you deploy Service A without deploying Service B? If not, boundaries are wrong

### Anemic Domain Model
**Pattern:** Entity classes with only getters/setters (no behavior), all logic in service classes.
**Resolution:** During extraction, consider enriching entities with domain behavior. This is optional but improves the domain model.

### Leaky Abstractions
**Pattern:** Repository interfaces returning `Page<T>` or JPA-specific types in domain layer.
**Resolution:** Domain layer should not depend on infrastructure. Repository interfaces in domain, implementations in infrastructure.

### Over-Engineering
**Warning:** Don't add patterns that aren't needed.
**Guidance:**
- Not every service needs CQRS or event sourcing
- Not every service needs a message broker (start with HTTP, add messaging when needed)
- Keep it simple — complexity should be justified by requirements

---

## Build System Patterns

### Maven Multi-Module
**Pattern:** Parent POM with `<modules>` aggregating child modules.
**Resolution:**
- Each microservice becomes its own Maven project (or module in a new parent)
- Shared libraries published as Maven artifacts to a repository (Nexus, Artifactory, GitHub Packages)
- Parent POM for shared dependency management (BOM pattern)
- Remove inter-service module dependencies
- Each service must build independently: `mvn clean verify -pl service-name -am`

### Gradle Multi-Project
**Pattern:** `settings.gradle` with `include` for subprojects.
**Resolution:**
- Each microservice becomes its own Gradle project (or subproject in new root)
- Shared libraries published as Gradle artifacts
- Use `platform()` dependencies for version alignment (Spring Boot BOM)
- Remove inter-service project dependencies
- Each service must build independently

### Shade / Fat JAR Plugins
**Pattern:** `maven-shade-plugin` or `spring-boot-maven-plugin` creating uber JARs.
**Resolution:**
- Each service uses `spring-boot-maven-plugin` for its own fat JAR
- Shade plugin conflicts (duplicate classes) → resolve per service
- Ensure no class name collisions in fat JARs

### WAR Packaging
**Pattern:** `maven-war-plugin` producing WAR files for external Tomcat/Jetty.
**Resolution:**
- Convert to Spring Boot fat JAR with embedded Tomcat
- Remove `extends SpringBootServletInitializer` (or keep for backward compatibility)
- Remove `web.xml` → use Spring Boot auto-configuration
- Servlet filters → Spring `@Component` filters or `FilterRegistrationBean`
- Servlet listeners → Spring `@EventListener` or `ApplicationListener`

### EAR Packaging
**Pattern:** `maven-ear-plugin` producing EAR files for WildFly/WebSphere/WebLogic.
**Resolution:**
- Most complex migration path
- Each EJB module → Spring Boot service
- EJB `@Stateless`, `@Stateful` → Spring `@Service`
- EJB `@Remote` → REST API or gRPC
- EJB `@Local` → direct Spring bean injection (within same service)
- JPA `persistence.xml` → Spring Boot auto-configuration
- JTA transactions → Spring `@Transactional` (local transactions per service)
- JNDI lookups → Spring DI
- MDB (Message-Driven Beans) → `@KafkaListener` or `@RabbitListener`
- Timer service → `@Scheduled` or Quartz

---

## Modular Java (JPMS) Patterns

### module-info.java
**Pattern:** Java Platform Module System with `module-info.java` defining exports, requires, opens.
**Resolution:**
- JPMS module boundaries may align with service boundaries
- Each service can be a single module or drop JPMS (Spring Boot doesn't require it)
- `exports` directives → map to service API surface
- `requires` directives → map to service dependencies
- `opens` for reflection (JPA, Jackson) → per-service module-info
- If JPMS adds complexity without benefit for microservices, consider removing it

### Automatic Modules
**Pattern:** Libraries on the module path without `module-info.java`.
**Resolution:**
- Most Spring Boot starters work as automatic modules
- Check library compatibility with JPMS before migration
- If problematic, drop JPMS for the service and use classpath

---

## Alternative Target Frameworks

While this power primarily targets Spring Boot, some services may benefit from alternative frameworks:

### Micronaut
**When to consider:** Services needing fast startup (serverless), low memory footprint, GraalVM native image.
**Key differences:** Compile-time DI (no reflection), `@Singleton`/`@Controller` annotations similar to Spring.
**Migration notes:** Most Spring patterns have Micronaut equivalents. Data access via Micronaut Data (similar to Spring Data).

### Quarkus
**When to consider:** Services targeting GraalVM native image, Kubernetes-native, CDI-based codebase.
**Key differences:** CDI-based DI, Hibernate with Panache, RESTEasy for JAX-RS.
**Migration notes:** Good fit if monolith already uses CDI/JAX-RS. Quarkus Spring compatibility extensions ease migration.

### General Guidance
- Don't mix frameworks unless there's a strong reason (operational complexity)
- Spring Boot is the safest default for most Java microservices
- Consider alternatives only for specific services with unique requirements (e.g., serverless function)

---

## Framework Migration: Java EE / Jakarta EE → Spring Boot

When the monolith is on Java EE and services target Spring Boot:

### Step 1: Identify Compatibility
- Check all dependencies for Spring Boot equivalents
- Identify Java EE APIs in use (EJB, JPA, JMS, JAX-RS, CDI, JSF, Servlet)
- Check for vendor-specific APIs (WebSphere, WebLogic, JBoss)
- Assess Java version compatibility (Java 8 → 17/21 may be needed)

### Step 2: API Mapping

| Java EE API | Spring Boot Equivalent |
|-------------|----------------------|
| EJB `@Stateless` | `@Service` |
| EJB `@Stateful` | `@Service` + `@Scope("session")` |
| EJB `@Singleton` | `@Service` (default singleton) |
| EJB `@Remote` | REST controller or gRPC |
| EJB `@Local` | Direct bean injection |
| CDI `@Inject` | `@Autowired` or constructor injection |
| CDI `@Named` | `@Component` / `@Service` |
| CDI `@Produces` | `@Bean` in `@Configuration` |
| CDI `@Observes` | `@EventListener` |
| JPA `persistence.xml` | `spring.jpa.*` properties |
| JMS `@MessageDriven` | `@KafkaListener` / `@RabbitListener` |
| JAX-RS `@Path` | `@RequestMapping` / `@RestController` |
| JAX-RS `@GET` / `@POST` | `@GetMapping` / `@PostMapping` |
| JSF managed beans | Spring MVC controllers + Thymeleaf |
| Servlet `@WebServlet` | `@RestController` or `ServletRegistrationBean` |
| Servlet `@WebFilter` | `@Component` filter or `FilterRegistrationBean` |
| Timer `@Schedule` | `@Scheduled` |
| JTA `@TransactionAttribute` | `@Transactional` |

### Step 3: Strangler Fig Pattern
- New microservices built on Spring Boot 3.x
- Monolith stays on Java EE during transition
- API Gateway routes requests to new services or monolith
- Gradually move functionality from monolith to services
- Monolith shrinks over time until decommissioned
- See traffic-cutover steering file for detailed implementation
