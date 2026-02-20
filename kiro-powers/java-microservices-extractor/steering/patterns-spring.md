# Spring Framework Patterns Reference

Patterns specific to Spring MVC, Spring Boot, Spring Security, Spring Batch, Spring Integration, and Spring Cloud during monolith-to-microservices decomposition.

---

## Spring MVC Patterns

### Controllers with Mixed Responsibilities
**Pattern:** A single `@Controller` or `@RestController` handles multiple domain concerns (e.g., `OrderController` managing orders, inventory, and shipping).
**Resolution:**
- Split controller actions by bounded context
- Each microservice gets only the actions relevant to its domain
- Shared `@ControllerAdvice` → common-infrastructure library or duplicated per service
- If controller has 500+ lines, it almost certainly spans multiple contexts

### Request Mappings and URL Structure
**Pattern:** Centralized URL structure with `@RequestMapping` at class and method level.
**Resolution:**
- Each service defines its own URL namespace (`/api/orders/**`, `/api/products/**`)
- API Gateway handles routing to the correct service
- Legacy URL patterns may need rewriting at the gateway level
- `@RequestMapping` with multiple paths → split by domain

### Interceptors (HandlerInterceptor)
**Pattern:** `HandlerInterceptor` implementations for cross-cutting concerns (logging, auth, tenant resolution).
**Resolution:**
- Cross-cutting interceptors (logging, correlation ID) → common-infrastructure library
- Domain-specific interceptors → move with their service
- Auth interceptors → JWT validation filter (common) or per-service
- Interceptor ordering preserved within each service

### Exception Handlers (@ControllerAdvice)
**Pattern:** Global `@ControllerAdvice` with `@ExceptionHandler` methods.
**Resolution:**
- Generic exception handlers (404, 500, validation errors) → common-infrastructure
- Domain-specific exception handlers → move with their service
- Use RFC 7807 Problem Detail format (`ProblemDetail` in Spring 6+)
- Each service should have consistent error response format

### View Resolvers and Template Engines
**Pattern:** Thymeleaf, Freemarker, JSP view resolvers in MVC controllers.
**Resolution:**
- If services have their own UI → each gets its own template engine config
- If using a BFF (Backend for Frontend) → templates stay in BFF, services expose REST APIs
- JSP migration → convert to Thymeleaf or separate frontend (React/Angular/Vue)
- Shared layouts → micro-frontend pattern or shared template fragments

### Content Negotiation
**Pattern:** Controllers producing multiple content types (JSON, XML, HTML).
**Resolution:**
- API services → JSON only (simplify)
- If XML is required → configure per service
- HTML rendering → BFF or dedicated UI service
- `produces`/`consumes` attributes move with their controller

### Multipart File Upload
**Pattern:** `@RequestParam MultipartFile` for file uploads.
**Resolution:**
- File upload endpoint moves with the service that owns the file storage
- If multiple services handle files → dedicated file/media service
- Storage backend (S3, local filesystem) configuration per service
- Max file size configuration per service

---

## Spring Boot Patterns

### Auto-Configuration
**Pattern:** Spring Boot auto-configuration via `spring.factories` or `@AutoConfiguration`.
**Resolution:**
- Each service benefits from its own auto-configuration
- Custom auto-configuration classes → move with their service or shared library
- `@ConditionalOnProperty` / `@ConditionalOnClass` → review per service
- Remove auto-configurations for features not used by a service (`spring.autoconfigure.exclude`)

### Actuator Endpoints
**Pattern:** Spring Boot Actuator for health, metrics, info.
**Resolution:**
- Each service gets its own Actuator configuration
- Custom health indicators → move with their service
- Custom metrics → move with their service
- Actuator security configuration per service
- Standardize exposed endpoints across services (health, info, metrics, prometheus)

### Spring Profiles
**Pattern:** `@Profile` annotations and `application-{profile}.yml` files.
**Resolution:**
- Each service gets its own profile-specific configuration
- Shared profiles (dev, staging, prod) → consistent naming across services
- Feature-toggle profiles → consider replacing with proper feature flags
- Profile-specific beans → move with their service

### Application Events and Listeners
**Pattern:** Custom `ApplicationEvent` subclasses with `@EventListener` or `ApplicationListener`.
**Resolution:**
- Intra-service events → keep as Spring events
- Cross-service events → convert to integration events (Kafka/RabbitMQ)
- `@TransactionalEventListener` → use outbox pattern for reliable cross-service publishing
- `ApplicationStartedEvent` / `ApplicationReadyEvent` listeners → per-service initialization

### CommandLineRunner / ApplicationRunner
**Pattern:** `CommandLineRunner` or `ApplicationRunner` for startup tasks.
**Resolution:**
- Startup tasks scoped to one domain → move with that service
- Data seeding runners → per-service, only seed that service's data
- Migration runners → per-service Flyway/Liquibase
- Initialization order matters → `@Order` annotation per service

### Spring Boot Starters (Custom)
**Pattern:** Custom `spring-boot-starter-*` modules for shared functionality.
**Resolution:**
- Cross-cutting starters (logging, security, metrics) → keep as shared library
- Domain-specific starters → move with their service or dissolve
- Starter auto-configuration → review for per-service applicability

---

## Spring Security Patterns

### SecurityFilterChain Configuration
**Pattern:** `SecurityFilterChain` bean (Spring Security 5.7+) or `WebSecurityConfigurerAdapter` (deprecated).
**Resolution:**
- Each service gets its own `SecurityFilterChain`
- Common JWT validation → shared filter in common-infrastructure
- Service-specific authorization rules → per-service configuration
- CSRF configuration → typically disabled for stateless APIs
- CORS configuration → per-service or at API gateway level

### Method Security (@PreAuthorize, @Secured)
**Pattern:** Method-level security annotations on service methods.
**Resolution:**
- `@PreAuthorize` / `@Secured` annotations move with their service methods
- Role/authority names must be consistent across services
- Custom `PermissionEvaluator` → move with the resource-owning service
- `@EnableMethodSecurity` → per-service configuration

### OAuth2 Resource Server
**Pattern:** Service validates JWT tokens from an authorization server.
**Resolution:**
- Each service configured as OAuth2 resource server
- Shared JWT validation configuration → common-infrastructure
- `spring.security.oauth2.resourceserver.jwt.issuer-uri` → per-service config
- Custom `JwtAuthenticationConverter` → shared or per-service

### OAuth2 Client
**Pattern:** Service acts as OAuth2 client (authorization code flow, client credentials).
**Resolution:**
- Client credentials for service-to-service → per-service configuration
- Authorization code flow → BFF or gateway only
- `OAuth2AuthorizedClientManager` → per-service
- Token relay in gateway → Spring Cloud Gateway filter

### Custom Authentication Filters
**Pattern:** Custom `OncePerRequestFilter` or `AbstractAuthenticationProcessingFilter`.
**Resolution:**
- API key filters → move with the service that validates API keys
- Custom token filters → shared if all services use the same token format
- Multi-tenant filters → shared common-infrastructure
- Filter ordering critical → document and replicate per service

### Session Management
**Pattern:** `HttpSession` with Spring Session (Redis, JDBC).
**Resolution:**
- Stateless JWT preferred for microservices (no session needed)
- If session required → Spring Session with Redis (shared session store)
- Session-scoped beans → refactor to request-scoped or stateless
- `@SessionAttributes` in controllers → refactor to client-side state or Redis

---

## Spring Batch Patterns

### Job Configuration
**Pattern:** `@EnableBatchProcessing`, `Job`, `Step`, `ItemReader/Processor/Writer`.
**Resolution:**
- Batch jobs move with their domain's service
- Each service gets its own batch configuration and job repository
- Shared batch infrastructure (job repository tables) → per-service
- `JobLauncher` → per-service, triggered by scheduler or API

### Partitioned Steps
**Pattern:** `Partitioner` for parallel processing across data partitions.
**Resolution:**
- Partitioned steps stay within one service
- If partitions span service boundaries → split into per-service jobs coordinated by events
- Remote partitioning → consider if services need to coordinate batch work

### Chunk-Oriented Processing
**Pattern:** `ItemReader` → `ItemProcessor` → `ItemWriter` pipeline.
**Resolution:**
- Reader/Processor/Writer move with their domain service
- Readers that query across service boundaries → replace with API calls or pre-fetched data
- Writers that update multiple service databases → split into per-service writers

---

## Spring Integration Patterns

### Message Channels
**Pattern:** `DirectChannel`, `QueueChannel`, `PublishSubscribeChannel`.
**Resolution:**
- Intra-service channels → keep within the service
- Cross-service channels → replace with external message broker (Kafka/RabbitMQ)
- Channel adapters become service boundary points

### Integration Flows
**Pattern:** `IntegrationFlow` with transformers, routers, filters, service activators.
**Resolution:**
- Flows scoped to one domain → move with that service
- Flows spanning domains → split at domain boundaries
- Gateway interfaces (`@MessagingGateway`) → move with their consumer
- Consider simplifying to direct messaging during migration

### File Integration
**Pattern:** `FileReadingMessageSource`, `FileWritingMessageHandler` for file-based integration.
**Resolution:**
- File processing moves with the service that owns the file domain
- Shared file directories → dedicated file service or S3 with events
- FTP/SFTP adapters → move with their service

---

## Spring Cloud Patterns

### Eureka Service Discovery
**Pattern:** `@EnableEurekaClient` / `@EnableDiscoveryClient` with Eureka server.
**Resolution:**
- Each service registers with Eureka
- Feign clients use service names for discovery
- Consider Kubernetes DNS-based discovery as alternative
- Eureka server → deploy as infrastructure service

### Spring Cloud Config
**Pattern:** Centralized configuration via Spring Cloud Config Server.
**Resolution:**
- Config Server serves configuration for all services
- Each service has its own config file in the Git repo
- Shared configuration → `application.yml` (applies to all services)
- Service-specific → `{service-name}.yml`
- Profile-specific → `{service-name}-{profile}.yml`

### Spring Cloud Gateway
**Pattern:** API Gateway with route definitions, filters, predicates.
**Resolution:**
- Gateway routes traffic to individual services
- Path-based routing: `/api/orders/**` → order-service
- Rate limiting, authentication, CORS at gateway level
- Custom `GatewayFilter` for cross-cutting concerns
- See traffic-cutover steering file for migration routing strategies

### Resilience4j / Hystrix
**Pattern:** Circuit breakers, retry, rate limiting on service calls.
**Resolution:**
- Resilience patterns move with the calling service
- `@CircuitBreaker`, `@Retry`, `@RateLimiter` on Feign clients
- Fallback methods → per-service
- Hystrix (deprecated) → migrate to Resilience4j
- Bulkhead pattern for isolating service call thread pools

### Spring Cloud Stream
**Pattern:** Binder-based messaging abstraction over Kafka/RabbitMQ.
**Resolution:**
- Stream bindings move with their service
- `@StreamListener` (deprecated) → functional style (`Consumer<Message<T>>`)
- Each service defines its own bindings in `application.yml`
- Shared message types → published as Maven artifact or duplicated

### Feign Clients
**Pattern:** `@FeignClient` for declarative HTTP clients.
**Resolution:**
- Feign client interfaces defined in the consuming service
- Shared Feign client library → anti-pattern (creates coupling)
- Each service defines its own client interfaces for services it calls
- Error decoder, request interceptor → per-service or common-infrastructure


---

## Spring WebFlux / Reactive Patterns

### Reactive Controllers
**Pattern:** `@RestController` returning `Mono<T>` and `Flux<T>` with Spring WebFlux.
**Resolution:**
- Reactive controllers move with their domain service
- Each service can independently choose reactive or servlet stack
- Don't mix WebFlux and MVC in the same service (pick one)
- Reactive services work well for high-concurrency, I/O-bound workloads
- Consider keeping servlet stack for simpler CRUD services

### WebClient (Reactive HTTP Client)
**Pattern:** `WebClient` for non-blocking HTTP calls.
**Resolution:**
- `WebClient` instances → per-service configuration
- Prefer `WebClient` over `RestTemplate` for inter-service calls (even in servlet stack)
- `WebClient` with Resilience4j → per-service circuit breaker configuration
- Connection pool (`ConnectionProvider`) → per-service tuning

### R2DBC (Reactive Data Access)
**Pattern:** `spring-boot-starter-data-r2dbc` with reactive repositories.
**Resolution:**
- R2DBC repositories move with their entity's service
- Each service configures its own `ConnectionFactory`
- Cannot mix JPA and R2DBC in the same persistence unit
- Consider R2DBC for new services with high-concurrency data access
- Flyway/Liquibase still needed for schema migration (they use JDBC)

### Reactive Security
**Pattern:** `@EnableWebFluxSecurity` with `SecurityWebFilterChain`.
**Resolution:**
- Each reactive service gets its own `SecurityWebFilterChain`
- JWT validation → `ReactiveJwtDecoder` (from common-infrastructure)
- Method security → `@EnableReactiveMethodSecurity`
- `ReactiveSecurityContextHolder` instead of `SecurityContextHolder`

### Project Reactor Patterns
**Pattern:** Complex reactive chains with `flatMap`, `zip`, `switchIfEmpty`, error handling.
**Resolution:**
- Reactive chains scoped to one domain → move with that service
- Cross-service reactive calls → `WebClient` with proper error handling
- `Schedulers.boundedElastic()` for blocking calls within reactive pipeline
- Context propagation (tracing, security) → Micrometer Context Propagation library
