# Phase 2 & 3: Planning and Executing the Transformation

This steering file covers both the planning and execution phases. Complete planning first, get user approval, then execute.

---

## Phase 2: Transformation Planning

### Step 1: Define Service Boundaries and Contracts

For each microservice identified in the assessment, produce a complete service definition.

#### Service Identity Card

```
Service Name: {kebab-case, e.g., order-service}
Responsibility: {Single sentence — what this service owns}
Bounded Context: {Which bounded context from assessment}
Spring Boot Version: {Target version, default: 3.2.x}
Java Version: {Target version, default: 21}
```

#### Owned Domain

List every entity, value object, and enum this service is the source of truth for:
- Aggregate roots with their child entities
- Value objects (JPA @Embeddable types)
- Enums specific to this domain
- Domain events defined by this context

#### API Surface

```
## {service-name} API

### REST Endpoints
POST   /api/{resource}          - Create
GET    /api/{resource}          - List (with pagination, filtering, sorting)
GET    /api/{resource}/{id}     - Get by ID
PUT    /api/{resource}/{id}     - Full update
PATCH  /api/{resource}/{id}     - Partial update
DELETE /api/{resource}/{id}     - Delete

### Events Published
- {EntityName}CreatedEvent   { id, key properties, timestamp }
- {EntityName}UpdatedEvent   { id, changed properties, timestamp }
- {EntityName}DeletedEvent   { id, timestamp }

### Events Consumed
- From {other-service}: {EventName} → Handler action

### APIs Consumed
- From {other-service}: GET /api/{resource}/{id} → Used in {workflow}
```

#### Project Structure Per Service

Each service follows hexagonal/clean architecture:

```
{service-name}/
├── src/main/java/com/{org}/{service}/
│   ├── {ServiceName}Application.java
│   ├── domain/
│   │   ├── model/                    # Entities, value objects, enums
│   │   ├── repository/               # Repository interfaces
│   │   ├── service/                  # Domain services (pure business logic)
│   │   └── event/                    # Domain events
│   ├── application/
│   │   ├── dto/                      # Request/Response DTOs
│   │   ├── mapper/                   # MapStruct mappers
│   │   ├── service/                  # Application services (orchestration)
│   │   └── exception/                # Application exceptions
│   ├── infrastructure/
│   │   ├── persistence/
│   │   │   ├── entity/               # JPA entities (if separate from domain)
│   │   │   ├── repository/           # JPA repository implementations
│   │   │   └── config/               # DataSource, JPA config
│   │   ├── messaging/
│   │   │   ├── publisher/            # Event publishers
│   │   │   └── consumer/             # Event consumers
│   │   ├── client/                   # HTTP clients for other services
│   │   └── config/                   # Infrastructure config beans
│   └── api/
│       ├── controller/               # REST controllers
│       ├── advice/                   # @ControllerAdvice exception handlers
│       └── filter/                   # Servlet filters
├── src/main/resources/
│   ├── application.yml
│   ├── application-dev.yml
│   ├── application-prod.yml
│   ├── db/migration/                 # Flyway migrations
│   └── logback-spring.xml
├── src/test/java/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── Dockerfile
└── pom.xml (or build.gradle)
```

### Step 2: Shared Library Strategy

#### Shared Kernel (common-domain module)

Only include types that are truly universal across ALL services:

```java
// common-domain/
├── BaseEntity.java          // @MappedSuperclass with id, createdAt, updatedAt
├── AuditableEntity.java     // Adds createdBy, modifiedBy
├── DomainEvent.java         // Base class for domain events
├── ValueObject.java         // Abstract base with equals/hashCode
├── Result.java              // Result<T> for operation outcomes
├── PagedResult.java         // Pagination wrapper
├── Guard.java               // Precondition checks
└── exception/
    ├── DomainException.java
    ├── NotFoundException.java
    └── ConflictException.java
```

Rules for shared kernel:
- Must be stable — changes affect ALL services
- No business logic — only structural types
- No infrastructure dependencies — pure Java
- Publish as a Maven/Gradle artifact with semantic versioning

#### Common Infrastructure (common-infrastructure module)

Cross-cutting infrastructure shared via published artifact:

```
common-infrastructure/
├── security/
│   ├── JwtAuthenticationFilter.java
│   ├── SecurityConfig.java (base)
│   └── ClaimsExtractor.java
├── logging/
│   ├── CorrelationIdFilter.java
│   ├── RequestLoggingFilter.java
│   └── MDCUtils.java
├── exception/
│   ├── GlobalExceptionHandler.java (@ControllerAdvice)
│   └── ProblemDetailFactory.java (RFC 7807)
├── health/
│   └── CommonHealthIndicators.java
├── resilience/
│   ├── RetryConfig.java
│   └── CircuitBreakerConfig.java
├── observability/
│   └── MicrometerConfig.java
└── swagger/
    └── OpenApiConfig.java
```

#### What to Duplicate Per Service (NOT shared)

- Entity classes — each service defines its own
- DTOs — each service defines its own request/response models
- Validation rules — each service validates its own inputs
- Configuration classes — each service has its own @Configuration
- MapStruct mappers — each service maps its own entities
- JPA configuration — each service has its own persistence config
- Repository implementations — each service implements its own data access

### Step 3: Data Decomposition Plan

For each service, define the complete data strategy. Consult the database-migration steering file for detailed patterns.

```
## {service-name} Data Plan

### Owned Tables
- {table1} (full ownership, read-write)
- {table2} (full ownership, read-write)

### Tables to Split
- {shared_table} → Extract columns into {service_name}.{new_table}

### Foreign Key Resolution
- {table}.{other_service_entity_id} → Keep as simple ID column, remove FK constraint
  - Data fetched via Feign/WebClient call to {other-service}
  - Cache with Caffeine/Redis, TTL: {duration}

### Read Model / Denormalization
- Need {other-service}.{entity}.{property} for display
  - Strategy: Subscribe to {other-service}.{entity}UpdatedEvent
  - Store denormalized copy in local read table
  - Eventual consistency acceptable: {Yes/No}

### Database
- Separate database: {service_name}_db
- Migration tool: Flyway
- Connection pool: HikariCP (default Spring Boot)
```

### Step 4: Inter-Service Communication Design

#### Synchronous Communication (HTTP)

For each service-to-service API call:

```
Caller: {service-a}
Callee: {service-b}
Endpoint: GET /api/{resource}/{id}
Client: OpenFeign / WebClient
Frequency: {Estimated calls per minute}
Failure handling: Resilience4j circuit breaker + retry + fallback
Timeout: 5 seconds
```

```java
// Feign client definition
@FeignClient(name = "product-service", fallbackFactory = ProductClientFallback.class)
public interface ProductClient {
    @GetMapping("/api/products/{id}")
    ProductResponse getProduct(@PathVariable UUID id);
}
```

#### Asynchronous Communication (Events)

For each integration event:

```
Event: {EventName}
Publisher: {service-a}
Subscribers: {service-b, service-c}
Payload: { id: UUID, property1: String, property2: BigDecimal, timestamp: Instant }
Transport: Kafka / RabbitMQ / Spring Cloud Stream
Delivery guarantee: At-least-once
Idempotency: Consumer uses eventId for deduplication
```

#### Saga / Process Manager

For distributed transactions:

```
Saga: PlaceOrderSaga
Steps:
  1. order-service: Create order (status: PENDING) → Success: proceed → Failure: abort
  2. inventory-service: Reserve stock → Success: proceed → Failure: compensate step 1
  3. payment-service: Process payment → Success: proceed → Failure: compensate 1, 2
  4. order-service: Confirm order (status: CONFIRMED)
  5. notification-service: Send confirmation (fire-and-forget)

Compensation:
  - Step 1: Cancel order
  - Step 2: Release reserved stock
Timeout: 30 seconds before auto-compensation
```

### Step 5: Cross-Cutting Concerns Plan

#### Authentication & Authorization Strategy

```
Identity Service:
  - Owns: User accounts, roles, permissions, tokens
  - Provides: Token issuance (JWT), user management API
  - Technology: Spring Security + Spring Authorization Server / Keycloak / Auth0

Per-Service Auth:
  - JWT validation filter (from common-infrastructure)
  - @PreAuthorize / @Secured for method-level security
  - Service-to-service: Client credentials flow (OAuth2)

Token Flow:
  1. Client authenticates with Identity Service → receives JWT
  2. Client sends JWT in Authorization header to any service
  3. Each service validates JWT independently (shared signing key or JWKS endpoint)
  4. Service extracts claims for authorization decisions
  5. Service-to-service: forwards user JWT or uses client credentials
```

#### Observability Strategy

```
Logging:
  - Framework: SLF4J + Logback
  - Format: JSON structured logging (logstash-logback-encoder)
  - MDC: correlationId, serviceId, userId
  - Centralized: ELK Stack / Loki / CloudWatch

Distributed Tracing:
  - Framework: Micrometer Tracing (Spring Boot 3.x) or Spring Cloud Sleuth (2.x)
  - Exporters: Zipkin / Jaeger / AWS X-Ray / Tempo
  - Propagation: W3C TraceContext headers
  - Auto-instrumented: RestTemplate, WebClient, Feign, JPA, Kafka

Metrics:
  - Framework: Micrometer
  - Exporters: Prometheus / CloudWatch / Datadog
  - Per-service: request rate, error rate, latency (RED)
  - Business metrics: custom counters and gauges

Health Checks:
  - /actuator/health/liveness — is the process running
  - /actuator/health/readiness — can it serve traffic (DB connected, dependencies available)
  - Custom health indicators for critical dependencies
```

### Step 6: API Gateway Strategy

```
API Gateway (recommended if 3+ services):
  - Technology: Spring Cloud Gateway / Kong / AWS API Gateway
  - Responsibilities:
    - Request routing to appropriate service
    - JWT validation at gateway level
    - Rate limiting
    - CORS handling
    - Request/response transformation
    - API versioning
    - SSL termination

Spring Cloud Gateway route example:
  spring:
    cloud:
      gateway:
        routes:
          - id: order-service
            uri: lb://order-service
            predicates:
              - Path=/api/orders/**
          - id: product-service
            uri: lb://product-service
            predicates:
              - Path=/api/products/**
```

### Step 7: Infrastructure Plan

```
Containerization:
  - Dockerfile per service (multi-stage build with eclipse-temurin)
  - docker-compose.yml for local development
  - JVM tuning: -XX:+UseContainerSupport, memory limits

Service Discovery:
  - Spring Cloud Netflix Eureka (self-hosted)
  - Or: Kubernetes DNS-based discovery
  - Or: Spring Cloud Consul

Configuration:
  - Spring Cloud Config Server (Git-backed)
  - Or: Kubernetes ConfigMaps + Secrets
  - Or: AWS Parameter Store / Azure App Configuration
  - Per-service: application.yml + application-{profile}.yml

Database:
  - Per-service database (or schema)
  - Flyway for migrations
  - HikariCP connection pooling (Spring Boot default)

Message Broker:
  - Apache Kafka (docker container for dev)
  - Or: RabbitMQ
  - Or: cloud-managed (Amazon MSK, CloudAMQP)
```

### Step 8: Rollback Strategy

For each service extraction:

```
Service: {service-name}
Rollback Trigger: {error rate > 2x baseline, data inconsistency, etc.}
Rollback Steps:
  1. Disable feature flag / revert gateway routing
  2. Restore monolith endpoint handling
  3. Verify monolith functionality
Rollback Time Estimate: {minutes}
Data Considerations: {any data that needs sync back}
```

### Step 9: Test Coverage Strategy During Migration

#### 9a: Characterization Tests (Before Extraction)

Before extracting any service, capture current behavior:

```
For each service being extracted:
  1. Identify all API endpoints that will move
  2. Write integration tests against the MONOLITH exercising these endpoints
  3. Capture request/response pairs as golden files
  4. The new service must pass the same tests
```

```java
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class OrderEndpointCharacterizationTest {
    @Autowired TestRestTemplate restTemplate;

    @Test
    void createOrder_withValidRequest_returnsCreatedOrder() {
        var request = new CreateOrderRequest(/* ... */);
        var response = restTemplate.postForEntity("/api/orders", request, OrderResponse.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().getStatus()).isEqualTo("PENDING");
    }
}
```

#### 9b: Contract Tests (Between Services)

Use Pact for consumer-driven contract tests:

```java
// Consumer side (order-service tests)
@ExtendWith(PactConsumerTestExt.class)
@PactTestFor(providerName = "product-service")
class ProductClientContractTest {
    @Pact(consumer = "order-service")
    V4Pact getProductPact(PactDslWithProvider builder) {
        return builder
            .given("product 123 exists")
            .uponReceiving("get product by id")
            .path("/api/products/123")
            .method("GET")
            .willRespondWith()
            .status(200)
            .body(newJsonBody(o -> {
                o.uuid("id"); o.stringType("name"); o.decimalType("price");
            }).build())
            .toPact(V4Pact.class);
    }
}
```

#### 9c: Test Migration Checklist

```
Before extracting each service:
- [ ] Characterization tests written and passing against monolith
- [ ] Contract tests defined for all consumed APIs

During extraction:
- [ ] Unit tests for new service code
- [ ] Integration tests with Testcontainers
- [ ] Contract tests passing (consumer and provider)
- [ ] Monolith tests still pass

After extraction:
- [ ] Characterization tests pass against new service
- [ ] Remove stale monolith tests for extracted functionality
- [ ] End-to-end smoke tests pass in docker-compose
```

### Step 10: API Versioning During Migration

#### Versioning Strategy

| Strategy | When to Use | Implementation |
|----------|-------------|----------------|
| URL path (`/api/v1/orders`) | Simple, explicit | `@RequestMapping("/api/v1/orders")` |
| Header (`Api-Version: 2`) | Cleaner URLs | Custom `RequestMappingHandlerMapping` |
| Gateway routing (transparent) | Clients don't change | Spring Cloud Gateway routes by path |

#### Backward Compatibility Rules

```
DO: Add new fields to responses, add new optional request fields, support aliases
DON'T: Remove response fields, make optional fields required, change types, change URLs without routing
```

Consult the traffic-cutover steering file for detailed routing and canary deployment strategies.

### Step 11: Present the Complete Plan

Present to the user:
1. Complete service breakdown with project structures
2. Shared library strategy
3. Data decomposition plan per service
4. Inter-service communication design (sync + async)
5. Saga definitions for distributed workflows
6. Cross-cutting concerns strategy
7. API gateway recommendation
8. Infrastructure plan
9. Rollback strategy per extraction step
10. Test coverage strategy
11. API versioning and backward compatibility plan
12. Traffic cutover strategy
13. Migration order with dependencies and estimated effort

**Get explicit approval before executing.**

---

## Phase 3: Execution

### Step 1: Create Solution Structure

Create the complete project skeleton. For Maven:

```xml
<!-- parent pom.xml -->
<project>
    <groupId>com.{org}</groupId>
    <artifactId>{project}-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.5</version>
    </parent>

    <properties>
        <java.version>21</java.version>
        <spring-cloud.version>2023.0.1</spring-cloud.version>
        <mapstruct.version>1.5.5.Final</mapstruct.version>
    </properties>

    <modules>
        <module>common-domain</module>
        <module>common-infrastructure</module>
        <module>order-service</module>
        <module>product-service</module>
        <module>customer-service</module>
        <!-- ... -->
    </modules>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.cloud</groupId>
                <artifactId>spring-cloud-dependencies</artifactId>
                <version>${spring-cloud.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

Per-service pom.xml:
```xml
<project>
    <parent>
        <groupId>com.{org}</groupId>
        <artifactId>{project}-parent</artifactId>
        <version>1.0.0-SNAPSHOT</version>
    </parent>
    <artifactId>{service-name}</artifactId>

    <dependencies>
        <dependency>
            <groupId>com.{org}</groupId>
            <artifactId>common-domain</artifactId>
            <version>${project.version}</version>
        </dependency>
        <dependency>
            <groupId>com.{org}</groupId>
            <artifactId>common-infrastructure</artifactId>
            <version>${project.version}</version>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-data-jpa</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-validation</artifactId>
        </dependency>
        <dependency>
            <groupId>org.flywaydb</groupId>
            <artifactId>flyway-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springdoc</groupId>
            <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
            <version>2.5.0</version>
        </dependency>
    </dependencies>
</project>
```

### Step 2: Create Shared Libraries

#### Common Domain

```java
// common-domain/src/main/java/.../domain/BaseEntity.java
@MappedSuperclass
@EntityListeners(AuditingEntityListener.class)
public abstract class BaseEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @CreatedDate
    @Column(updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    private Instant updatedAt;
}
```

#### Common Infrastructure

Key components:

```java
// CorrelationIdFilter — extract/generate X-Correlation-ID, store in MDC
// GlobalExceptionHandler — @ControllerAdvice mapping exceptions to RFC 7807 ProblemDetail
// JwtAuthenticationFilter — validate JWT, set SecurityContext
```

### Step 3: Extract Domain Layer (per service, in migration order)

#### 3a: Create Entity Classes

1. Copy entity from monolith
2. Remove @ManyToOne/@OneToMany that reference entities in OTHER services
3. Replace cross-service foreign keys with simple ID fields (no JPA relationship)
4. Keep relationships for entities WITHIN this service
5. Ensure entity extends BaseEntity from common-domain

```java
// BEFORE (monolith): Order has @ManyToOne to Customer and Product
@Entity
public class Order {
    @Id private Long id;
    @ManyToOne @JoinColumn(name = "customer_id")
    private Customer customer;  // Cross-boundary
    @OneToMany(cascade = ALL, orphanRemoval = true)
    private List<OrderItem> items;
}

// AFTER (microservice): Order only references own entities
@Entity
@Table(name = "orders")
public class Order extends BaseEntity {
    @Column(nullable = false)
    private UUID customerId;  // Just an ID, no JPA relationship
    private String customerName;  // Denormalized for display

    @OneToMany(cascade = ALL, orphanRemoval = true, mappedBy = "order")
    private List<OrderItem> items = new ArrayList<>();

    public BigDecimal getTotalAmount() {
        return items.stream()
            .map(OrderItem::getSubtotal)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}
```

#### 3b: Create Repository Interfaces

```java
public interface OrderRepository extends JpaRepository<Order, UUID> {
    Page<Order> findByCustomerId(UUID customerId, Pageable pageable);
    List<Order> findByStatus(OrderStatus status);
    @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
    Optional<Order> findByIdWithItems(@Param("id") UUID id);
}
```

#### 3c: Create Application Services

```java
@Service
@Transactional
@RequiredArgsConstructor
public class OrderApplicationService {
    private final OrderRepository orderRepository;
    private final ProductClient productClient;
    private final OrderMapper orderMapper;
    private final ApplicationEventPublisher eventPublisher;

    public OrderResponse createOrder(CreateOrderRequest request) {
        // Validate products exist and have stock (via Feign client)
        // Create order entity
        // Save and publish event
        // Return response DTO
    }
}
```

### Step 4: Create API Layer

```java
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
@Tag(name = "Orders", description = "Order management")
public class OrderController {
    private final OrderApplicationService orderService;

    @GetMapping
    public Page<OrderResponse> list(Pageable pageable) {
        return orderService.findAll(pageable);
    }

    @GetMapping("/{id}")
    public OrderResponse getById(@PathVariable UUID id) {
        return orderService.findById(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public OrderResponse create(@Valid @RequestBody CreateOrderRequest request) {
        return orderService.createOrder(request);
    }
}
```

### Step 5: Configure Application

```yaml
# application.yml
spring:
  application:
    name: order-service
  datasource:
    url: jdbc:postgresql://localhost:5432/order_db
    username: ${DB_USERNAME:order_user}
    password: ${DB_PASSWORD:order_pass}
  jpa:
    hibernate:
      ddl-auto: validate
    open-in-view: false
  flyway:
    enabled: true

server:
  port: 8081

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true
```

### Step 6: Create Docker Support

```dockerfile
FROM eclipse-temurin:21-jre-alpine AS base
WORKDIR /app
EXPOSE 8080

FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /src
COPY pom.xml .
COPY common-domain/pom.xml common-domain/
COPY common-infrastructure/pom.xml common-infrastructure/
COPY {service-name}/pom.xml {service-name}/
RUN mvn dependency:go-offline -pl {service-name} -am
COPY . .
RUN mvn package -pl {service-name} -am -DskipTests

FROM base AS final
COPY --from=build /src/{service-name}/target/*.jar app.jar
RUN adduser --system --no-create-home appuser
USER appuser
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s \
    CMD wget -qO- http://localhost:8080/actuator/health/liveness || exit 1
ENTRYPOINT ["java", "-XX:+UseContainerSupport", "-XX:MaxRAMPercentage=75.0", "-jar", "app.jar"]
```

### Step 7: Validation Checklist

After extracting each service:

```
Compilation:
- [ ] mvn clean verify passes for each service independently
- [ ] No references to monolith packages remain
- [ ] All dependencies resolve

Architecture:
- [ ] No cross-service JPA relationships (@ManyToOne across boundaries)
- [ ] No cross-service repository usage
- [ ] Each service has its own DataSource configuration
- [ ] Domain layer has zero infrastructure imports

API:
- [ ] All endpoints return proper HTTP status codes
- [ ] All endpoints use DTOs (no entity exposure)
- [ ] OpenAPI docs generate correctly (/v3/api-docs)
- [ ] Authentication configured on non-public endpoints

Infrastructure:
- [ ] Actuator health endpoints respond
- [ ] Structured logging with correlation IDs
- [ ] Docker build succeeds
- [ ] docker-compose up starts all services
- [ ] Services can communicate

Data:
- [ ] Flyway migrations apply correctly
- [ ] No orphaned foreign keys to other service tables
```

### Step 8: Post-Transformation Summary

Present to the user:

```
## Transformation Complete

### Services Created
- {service-name}: {responsibility}, port {port}, {entity count} entities, {endpoint count} endpoints

### Architecture Diagram
(text-based showing services, APIs, events, databases)

### Inter-Service Dependencies
- service-a → service-b: GET /api/{resource}/{id}
- service-a → Kafka → service-c: {EventName}

### Next Steps
1. Run all services: docker-compose up
2. Test each service: http://localhost:{port}/swagger-ui.html
3. Test inter-service communication
4. Set up CI/CD pipelines per service
5. Plan production deployment
6. Set up monitoring and alerting
7. Execute data migration from monolith database
```
