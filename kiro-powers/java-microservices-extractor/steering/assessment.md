# Phase 1: Codebase Assessment

This steering file guides the assessment phase of a Java monolith-to-microservices transformation. Complete this entire phase and present findings to the user before proceeding to transformation. Do not skip any step — thoroughness here prevents costly mistakes during extraction.

---

## Step 1: Build System and Project Structure Discovery

Scan the workspace to build a complete picture of the codebase.

### 1a: Build System Identification

Determine the build system and scan all build files:

```
Search for: **/pom.xml, **/build.gradle, **/build.gradle.kts, **/settings.gradle, **/settings.gradle.kts
```

**For Maven projects**, extract from each pom.xml:
- GroupId, ArtifactId, Version (GAV coordinates)
- Parent POM (spring-boot-starter-parent version, custom parent)
- Packaging type: jar, war, ear, pom (aggregator)
- Java source/target version (maven-compiler-plugin configuration)
- All <dependency> elements with groupId, artifactId, version, scope
- All <module> elements (multi-module structure)
- Plugin configurations (spring-boot-maven-plugin, maven-war-plugin, shade plugin, etc.)
- Profiles and their activation conditions
- Dependency management (BOM imports, version properties)
- Repository declarations (custom Maven repos, Nexus, Artifactory)

**For Gradle projects**, extract from each build.gradle/build.gradle.kts:
- Group, name, version
- Applied plugins (org.springframework.boot, java, war, application)
- Java toolchain or sourceCompatibility/targetCompatibility
- All dependencies with configurations (implementation, compileOnly, runtimeOnly, testImplementation)
- Subproject declarations in settings.gradle
- Custom tasks and their dependencies
- Build script repositories
- Dependency management (Spring Boot BOM, platform dependencies)

### 1b: Multi-Module Structure Mapping

For multi-module projects, build the complete module dependency graph:

```
For each module:
  - Module name and path
  - Module type (web, library, domain, data, common, test)
  - Dependencies on other modules
  - External dependencies unique to this module
  - Packaging type
  - Estimated lines of code
```

Classify each module:
| Classification | Criteria | Implication |
|---------------|----------|-------------|
| Hub | Referenced by > 3 other modules | Shared library, needs careful splitting |
| God module | Depends on > 5 other modules | Too many responsibilities, extraction target |
| Leaf | No outbound module dependencies | Pure dependency, easy to package |
| Island | No inbound or outbound module deps | Isolated, may be dead code |
| Circular | Mutual module references | Must be broken before extraction |

### 1c: Deployment Model Detection

Determine how the application is deployed:

```
Search for: **/Dockerfile*, **/docker-compose*, **/*.war, **/WEB-INF/web.xml
Search for: **/application.yml, **/application.properties, **/application-*.yml
Search for: **/META-INF/application.xml (EAR), **/jboss-web.xml, **/weblogic.xml
Search for: main() methods with SpringApplication.run() or embedded server setup
```

Classify deployment model:
- **Embedded Spring Boot** — SpringApplication.run(), fat JAR, embedded Tomcat/Jetty/Undertow
- **WAR deployment** — extends SpringBootServletInitializer or has web.xml, deployed to external Tomcat/Jetty
- **EAR deployment** — application.xml, deployed to WildFly/WebSphere/WebLogic
- **Standalone** — plain main() with manual server setup
- **Serverless** — AWS Lambda handlers, Azure Functions, GCP Cloud Functions

The deployment model significantly impacts migration complexity. EAR/app-server deployments are the hardest.

### 1d: Configuration File Inventory

Search for and catalog all configuration:

```
Search for: **/application.yml, **/application.properties, **/application-*.yml, **/application-*.properties
Also: **/bootstrap.yml, **/logback*.xml, **/log4j2*.xml, **/ehcache*.xml
Also: **/persistence.xml, **/orm.xml, **/hibernate.cfg.xml
Also: **/*.env, **/config/**, **/META-INF/spring.factories
```

For each configuration file, note:
- DataSource configurations (how many databases? what drivers? MySQL, PostgreSQL, Oracle, SQL Server, H2?)
- JPA/Hibernate properties (dialect, DDL auto, show SQL, second-level cache)
- Spring profiles and their purpose
- Server configuration (port, context path, SSL)
- Security configuration (OAuth2 endpoints, JWT settings, LDAP URLs)
- Messaging configuration (Kafka brokers, RabbitMQ hosts, JMS connection factories)
- Cache configuration (Redis, Ehcache, Caffeine, Hazelcast)
- External service URLs and API keys
- Spring Cloud Config Server settings
- Actuator endpoint configuration
- Custom properties and their usage

### 1e: Infrastructure File Inventory

```
Search for: **/Dockerfile*, **/docker-compose*, **/.github/workflows/*, **/Jenkinsfile
Also: **/*.yaml, **/*.yml (Kubernetes), **/*.tf (Terraform), **/deploy/**
Also: **/ansible/**, **/helm/**, **/.gitlab-ci.yml, **/bitbucket-pipelines.yml
```

Catalog:
- Dockerfiles and their base images (openjdk, eclipse-temurin, amazoncorretto)
- Docker Compose configurations
- CI/CD pipeline definitions
- Infrastructure as Code files
- Kubernetes manifests
- Helm charts

### Output: Project Inventory Table

| Module | Type | Java Version | Spring Boot | Packaging | Module Deps | Key Libraries | LOC Estimate |
|--------|------|-------------|-------------|-----------|-------------|---------------|--------------|
| app-web | Spring MVC | 11 | 2.7.x | WAR | core, data, service | Thymeleaf, Spring Security | ~8000 |
| app-core | Library | 11 | — | JAR | — | Lombok, MapStruct | ~3000 |
| app-data | Library | 11 | — | JAR | core | Spring Data JPA, Hibernate | ~5000 |

---

## Step 2: Technology Stack Fingerprinting

Identify every framework, library, and pattern in use. Be exhaustive.

### 2a: Web Framework Detection

| Framework | Detection Method |
|-----------|-----------------|
| Spring MVC | `spring-boot-starter-web` or `spring-webmvc` dependency, `@Controller`, `@RestController` |
| Spring WebFlux | `spring-boot-starter-webflux`, `@RestController` with `Mono`/`Flux` return types |
| JAX-RS (Jersey) | `jersey-server` or `javax.ws.rs`/`jakarta.ws.rs` annotations (`@Path`, `@GET`) |
| JAX-RS (RESTEasy) | `resteasy-jaxrs` dependency |
| Servlet API | `javax.servlet`/`jakarta.servlet` imports, `HttpServlet` subclasses, `web.xml` |
| JSP | `.jsp` files in `WEB-INF/` or `webapp/` |
| Thymeleaf | `spring-boot-starter-thymeleaf`, `.html` templates with `th:` attributes |
| Freemarker | `spring-boot-starter-freemarker`, `.ftl` template files |
| Vaadin | `vaadin-spring-boot-starter`, `@Route` annotations |
| Struts | `struts2-core` dependency, `struts.xml` configuration |
| GWT | `gwt-user` dependency, `.gwt.xml` module files |
| gRPC | `grpc-spring-boot-starter` or `io.grpc` dependencies, `.proto` files |
| GraphQL | `graphql-spring-boot-starter` or `com.netflix.dgs` dependencies |
| Apache CXF | `cxf-spring-boot-starter-jaxws` or `cxf-rt-frontend-jaxrs` |

### 2b: Data Access Detection

| Technology | Detection Method |
|------------|-----------------|
| Spring Data JPA | `spring-boot-starter-data-jpa`, interfaces extending `JpaRepository`, `CrudRepository` |
| Hibernate (standalone) | `hibernate-core` without Spring Data, `SessionFactory`, `Session` usage |
| Hibernate XML mappings | `.hbm.xml` files, `<mapping>` elements in hibernate.cfg.xml |
| MyBatis | `mybatis-spring-boot-starter`, `@Mapper` annotations, `*Mapper.xml` files |
| Spring JDBC Template | `JdbcTemplate`, `NamedParameterJdbcTemplate` usage |
| Plain JDBC | `DriverManager.getConnection()`, `java.sql.Connection` direct usage |
| jOOQ | `jooq` dependency, generated `Tables` and `Records` classes |
| QueryDSL | `querydsl-jpa` dependency, `Q*` generated classes |
| Spring Data MongoDB | `spring-boot-starter-data-mongodb`, `MongoRepository` |
| Spring Data Redis | `spring-boot-starter-data-redis`, `RedisTemplate` |
| Spring Data Elasticsearch | `spring-boot-starter-data-elasticsearch` |
| R2DBC | `spring-boot-starter-data-r2dbc`, reactive repositories |
| JPA Criteria API | `CriteriaBuilder`, `CriteriaQuery` usage |
| Stored procedures | `@NamedStoredProcedureQuery`, `@Procedure`, `CallableStatement` |
| Native queries | `@Query(nativeQuery = true)`, `createNativeQuery()` |

### 2c: Dependency Injection Detection

| Container | Detection Method |
|-----------|-----------------|
| Spring IoC | `@Component`, `@Service`, `@Repository`, `@Configuration`, `@Bean` |
| Spring XML config | `applicationContext.xml`, `<bean>` definitions |
| CDI (Weld) | `@Inject`, `@Named`, `beans.xml`, `javax.enterprise.inject` |
| Google Guice | `com.google.inject` imports, `AbstractModule`, `@Inject` with Guice |
| Dagger 2 | `dagger` dependency, `@Component` (Dagger), `@Module`, `@Provides` |
| HK2 | `org.glassfish.hk2` imports (common with Jersey) |
| PicoContainer | `picocontainer` dependency |

### 2d: Messaging and Event Detection

| Framework | Detection Method |
|-----------|-----------------|
| Spring Events | `ApplicationEventPublisher`, `@EventListener`, `ApplicationEvent` subclasses |
| Spring Integration | `spring-integration-*` dependencies, `@MessagingGateway`, `IntegrationFlow` |
| Apache Camel | `camel-spring-boot-starter`, `RouteBuilder`, `from().to()` patterns |
| Spring Kafka | `spring-kafka`, `@KafkaListener`, `KafkaTemplate` |
| Spring AMQP (RabbitMQ) | `spring-boot-starter-amqp`, `@RabbitListener`, `RabbitTemplate` |
| JMS | `spring-boot-starter-activemq` or `spring-jms`, `@JmsListener`, `JmsTemplate` |
| Kafka Streams | `kafka-streams` dependency, `StreamsBuilder` |
| Axon Framework | `axon-spring-boot-starter`, `@CommandHandler`, `@EventHandler`, `@Aggregate` |
| EventBus (Guava) | `com.google.common.eventbus.EventBus`, `@Subscribe` |
| MediatR-like | Custom command/query bus implementations |

### 2e: Background Processing Detection

| Framework | Detection Method |
|-----------|-----------------|
| @Scheduled | `@Scheduled` annotation, `@EnableScheduling` |
| @Async | `@Async` annotation, `@EnableAsync` |
| Spring Batch | `spring-boot-starter-batch`, `@EnableBatchProcessing`, `Job`, `Step` |
| Quartz | `quartz` dependency, `Job` interface, `Trigger`, `Scheduler` |
| ExecutorService | `Executors.newFixedThreadPool()`, `CompletableFuture`, `ThreadPoolTaskExecutor` |
| Spring TaskExecutor | `TaskExecutor`, `ThreadPoolTaskExecutor` beans |
| Hangfire-like (Jobrunr) | `jobrunr-spring-boot-starter` |

### 2f: Cross-Cutting Concern Detection

Scan for cross-cutting libraries systematically:

| Category | Libraries to Detect | Detection Method |
|----------|-------------------|-----------------|
| Logging | SLF4J, Logback, Log4j2, java.util.logging, Commons Logging | `logback.xml`, `log4j2.xml`, `org.slf4j` imports |
| Object Mapping | MapStruct, ModelMapper, Dozer, Orika | `mapstruct` dependency, `@Mapper` (MapStruct), `ModelMapper` usage |
| Validation | Hibernate Validator (Bean Validation), custom validators | `@NotNull`, `@Size`, `@Valid`, `ConstraintValidator` implementations |
| HTTP Clients | RestTemplate, WebClient, Feign, OkHttp, Apache HttpClient, Retrofit | `RestTemplate` beans, `@FeignClient`, `OkHttpClient`, `CloseableHttpClient` |
| Resilience | Resilience4j, Hystrix, Spring Retry, Failsafe | `resilience4j` dependency, `@CircuitBreaker`, `@Retryable`, `@HystrixCommand` |
| Serialization | Jackson, Gson, Moshi, Protocol Buffers | `ObjectMapper`, `Gson`, `.proto` files |
| Caching | Spring Cache, Ehcache, Caffeine, Redis, Hazelcast | `@Cacheable`, `ehcache.xml`, `CaffeineCacheManager`, `RedisTemplate` |
| Utilities | Lombok, Guava, Apache Commons, Vavr | `lombok` dependency, `com.google.common` imports, `org.apache.commons` imports |
| API Documentation | Springfox Swagger, springdoc-openapi | `springfox` or `springdoc` dependencies, `@Api`, `@Tag` annotations |
| Monitoring | Micrometer, Prometheus, Dropwizard Metrics | `micrometer-core`, `MeterRegistry`, `@Timed` |

For each library found, note the specific artifact ID and version.

### 2g: Testing Framework Detection

| Framework | Detection Method |
|-----------|-----------------|
| JUnit 5 | `junit-jupiter` dependency, `@Test` from `org.junit.jupiter.api` |
| JUnit 4 | `junit:junit` dependency, `@Test` from `org.junit` |
| TestNG | `testng` dependency, `@Test` from `org.testng` |
| Mockito | `mockito-core` dependency, `@Mock`, `@InjectMocks`, `when().thenReturn()` |
| Spring Test | `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`, `MockMvc` |
| Testcontainers | `testcontainers` dependency, `@Container`, `@Testcontainers` |
| WireMock | `wiremock` dependency, `WireMockServer` |
| ArchUnit | `archunit` dependency, architecture rule tests |
| AssertJ | `assertj-core`, `assertThat()` fluent assertions |
| REST Assured | `rest-assured` dependency, `given().when().then()` |
| Pact | `pact-jvm-consumer-junit5`, contract tests |
| Cucumber | `cucumber-java`, `.feature` files |
| Awaitility | `awaitility` dependency, async test assertions |

### Output: Technology Stack Summary

```
## Technology Stack

### Web Layer
- Spring Boot 2.7.18 (Spring MVC)
- Thymeleaf 3.0 (server-side templates)
- Spring Security 5.7 (form login + OAuth2)

### Data Access
- Spring Data JPA 2.7 with Hibernate 5.6
- 3 native queries, 2 stored procedure calls
- Single DataSource (PostgreSQL 14)

### Dependency Injection
- Spring IoC (annotation-based, 0 XML configs)

### Messaging
- Spring Events (12 event classes, 8 listeners)
- Spring Kafka (3 consumers, 2 producers)

### Cross-Cutting
- SLF4J + Logback (structured logging)
- MapStruct 1.5 (14 mapper interfaces)
- Hibernate Validator (23 constraint annotations)
- RestTemplate (4 external API clients)
- Resilience4j (circuit breakers on 2 clients)

### Background Processing
- @Scheduled (5 cron jobs)
- @Async (3 async methods)
- Spring Batch (1 nightly import job)

### Testing
- JUnit 5, Mockito 4, Spring Test
- 280 unit tests, 45 integration tests
- Testcontainers for PostgreSQL

### Infrastructure
- Docker (1 Dockerfile, docker-compose with PostgreSQL + Kafka)
- GitHub Actions CI/CD
```

---

## Step 3: Domain Model Analysis

This is the most critical step. Identify natural domain boundaries using DDD principles.

### 3a: Entity Discovery

Scan for all domain entities systematically:

```
Search for: @Entity, @Table, @MappedSuperclass, @Embeddable, @EmbeddedId
Search in: **/entity/, **/entities/, **/domain/, **/model/, **/models/
Also: classes referenced in JpaRepository<EntityType, IdType> generics
Also: Hibernate XML mappings in *.hbm.xml files
Also: MyBatis result maps in *Mapper.xml files
```

For EACH entity discovered, create a detailed profile:

| Property | What to Record |
|----------|---------------|
| Name | Class name and full package |
| Location | File path and module |
| Fields | All fields with types (especially @ManyToOne, @OneToMany, @ManyToMany) |
| JPA annotations | @Entity, @Table, @Id, @GeneratedValue, @Column, @JoinColumn, etc. |
| Inheritance | @Inheritance strategy (SINGLE_TABLE, TABLE_PER_CLASS, JOINED) |
| Embedded types | @Embedded, @Embeddable value objects |
| Repository | Which Spring Data repository interface manages this entity |
| Used by services | Which @Service classes operate on this entity |
| Used by controllers | Which @Controller/@RestController classes expose this entity |
| Validation | Bean Validation annotations (@NotNull, @Size, @Valid, custom) |
| Mapping | MapStruct/ModelMapper mappers that convert this entity |
| Listeners | @EntityListeners, @PrePersist, @PostUpdate callbacks |

### 3b: Aggregate Root Identification

Identify aggregate boundaries:

- Look for entities that are always loaded/saved together (cascade = CascadeType.ALL)
- Entities with orphanRemoval = true form natural aggregates
- Entities saved in the same @Transactional method
- Parent-child relationships where the child has no independent repository

Example:
```
Aggregate: Order
  - Order (root) — has OrderRepository
  - OrderItem (child, cascade ALL, orphanRemoval) — no repository
  - OrderStatus (embedded value object)
  - ShippingAddress (embedded value object)

Aggregate: Product
  - Product (root) — has ProductRepository
  - ProductImage (child, cascade ALL)
  - ProductVariant (child, cascade ALL)
  - Money (embedded value object)
```

### 3c: Bounded Context Identification

Group aggregates into bounded contexts using multiple signals:

1. **Business capability alignment** — map to real business functions
2. **Linguistic boundaries** — where the same word means different things
3. **Data ownership** — which context is the source of truth for each entity
4. **Change frequency** — entities that change together belong together
5. **Team alignment** — if different teams own different features
6. **Package structure** — existing code organization often hints at boundaries
7. **Controller grouping** — controllers often naturally align with bounded contexts
8. **Spring profile usage** — profiles sometimes indicate feature boundaries
9. **Maven/Gradle module boundaries** — existing modules may align with contexts

### 3d: Entity Relationship Cross-Boundary Mapping

For each proposed bounded context boundary, create a detailed crossing map:

```
## Cross-Boundary Reference Map

### Order Context → Product Context
- OrderItem.product (@ManyToOne to Product entity)
- OrderService.calculateTotal() calls ProductRepository.findById()
- OrderController.create() reads Product.price and Product.stockLevel

### Order Context → Customer Context
- Order.customer (@ManyToOne to Customer entity)
- OrderService.placeOrder() reads Customer.shippingAddress
- OrderController.getOrders() filters by Customer

### Customer Context → Identity Context
- Customer.userId (FK reference to users table)
- CustomerService.register() creates Spring Security user
```

For each crossing, classify:
- **Read-only reference** — service only reads from the other context (can become API call)
- **Write dependency** — service writes to entities in another context (needs event or saga)
- **Transactional dependency** — both contexts must be updated atomically (hardest to break)
- **Query join** — data from both contexts is joined in a query (needs API composition or denormalization)
- **JPA navigation** — @ManyToOne/@OneToMany across boundaries (must be broken)

---

## Step 4: Dependency and Coupling Analysis

### 4a: Module/Project Reference Graph

Build a complete directed graph of module dependencies:

```
For each Maven module or Gradle subproject:
  List all module dependencies
  List all external dependencies
  Calculate fan-in (how many modules depend on this one)
  Calculate fan-out (how many modules this one depends on)
```

### 4b: Package-Level Dependency Analysis

Go deeper than module references — analyze package dependencies:

```
For each package in the codebase:
  Scan all import statements
  Map which packages depend on which other packages
  Identify package clusters that form natural modules
  Flag packages with high fan-out (> 10 imports from other packages)
```

This reveals hidden coupling that module references don't show.

### 4c: Class-Level Coupling Metrics

For each proposed bounded context, calculate:

| Metric | Formula | Meaning |
|--------|---------|---------|
| Afferent Coupling (Ca) | Count of external classes depending on this context | How much others depend on us |
| Efferent Coupling (Ce) | Count of external classes this context depends on | How much we depend on others |
| Instability (I) | Ce / (Ca + Ce) | 0 = stable (hard to extract), 1 = unstable (easy to extract) |
| Abstractness (A) | Abstract types / Total types | Higher = more abstract, easier to decouple |
| Distance from Main Sequence (D) | abs(A + I - 1) | 0 = ideal balance, higher = problematic |

### 4d: Shared State Analysis

Systematically scan for shared mutable state:

```
Search for: static final (mutable collections), static volatile, static AtomicReference
Search for: @Singleton, @ApplicationScoped (CDI)
Search for: ServletContext.setAttribute, HttpSession
Search for: ThreadLocal<, InheritableThreadLocal<
Search for: ConcurrentHashMap used as global state
Search for: @Scope("singleton") with mutable fields
Search for: Spring beans with mutable instance fields (prototype scope needed?)
Search for: Hazelcast/Ehcache shared maps
```

### 4e: Database Coupling Analysis

```
For each DataSource / EntityManagerFactory:
  List all @Entity classes it manages
  List all repositories and their entity types

For each @Service or @Repository class:
  List all entities it queries
  Identify cross-context joins (JPQL/HQL joins across proposed boundaries)
  Identify native SQL queries and which tables they touch
  Identify stored procedure calls

For each stored procedure/view/function:
  List all tables it reads from and writes to
  Identify cross-context data access
```

Produce a table ownership matrix:

| Table | Context A | Context B | Context C | Resolution |
|-------|-----------|-----------|-----------|------------|
| orders | Owner (RW) | — | Read | API call from C |
| products | Read | Owner (RW) | Read | API calls from A, C |
| customers | Read | — | Owner (RW) | API call from A |

### 4f: External Integration Analysis

```
Search for: RestTemplate, WebClient, FeignClient, @FeignClient
Search for: HttpClient (Apache, OkHttp, java.net.http)
Search for: JavaMailSender, SmtpClient
Search for: AmazonS3, S3Client, BlobServiceClient
Search for: connection strings/URLs in configuration pointing to external systems
```

### 4g: Transaction Boundary Analysis

```
Search for: @Transactional (class-level and method-level)
Search for: TransactionTemplate, PlatformTransactionManager
Search for: @TransactionalEventListener
Search for: JTA / XA transactions (javax.transaction, jakarta.transaction)
Search for: ChainedTransactionManager, JtaTransactionManager
```

For each @Transactional method:
- Which entities are modified within the transaction
- Do the entities span proposed service boundaries
- Can the transaction be replaced with eventual consistency (saga pattern)
- What is the business impact of eventual consistency for this operation

---

## Step 5: Communication Pattern Analysis

### 5a: Synchronous Call Chains

```
For each @Controller/@RestController action:
  Trace: Controller → Service(s) → Repository/EntityManager
  Note which bounded contexts are touched in a single request
  Identify the deepest call chain depth
  Flag chains that cross proposed service boundaries
```

### 5b: Event and Message Patterns

```
Search for: ApplicationEventPublisher.publishEvent()
Search for: @EventListener, @TransactionalEventListener
Search for: @KafkaListener, @RabbitListener, @JmsListener
Search for: KafkaTemplate.send(), RabbitTemplate.convertAndSend()
Search for: IntegrationFlow, @MessagingGateway
Search for: RouteBuilder (Apache Camel)
```

### 5c: Shared Resource Access

Identify shared resources beyond the database:
- File system paths accessed by multiple contexts
- Shared blob storage containers
- Shared Redis keys or cache regions
- Shared message queues or topics
- Shared external API connections (rate limits, connection pools)

---

## Step 6: Security and Identity Analysis

### 6a: Authentication Flow

```
Search for: @EnableWebSecurity, WebSecurityConfigurerAdapter, SecurityFilterChain
Search for: @EnableOAuth2Client, @EnableResourceServer, @EnableAuthorizationServer
Search for: UsernamePasswordAuthenticationFilter, JwtAuthenticationFilter
Search for: SecurityContextHolder, Authentication, Principal
Search for: @PreAuthorize, @Secured, @RolesAllowed
Search for: LDAP configuration (LdapAuthenticationProvider)
Search for: SAML configuration (spring-security-saml2)
Search for: Keycloak adapter configuration
```

Document:
- Authentication mechanism (form login, JWT, OAuth2, SAML, LDAP, Basic Auth)
- Identity provider (Spring Security UserDetailsService, Keycloak, Okta, Auth0, custom)
- Token issuance and validation flow
- Session management (HttpSession, stateless JWT, Spring Session + Redis)

### 6b: Authorization Model

```
Search for: @PreAuthorize, @PostAuthorize, @Secured, @RolesAllowed
Search for: hasRole(), hasAuthority(), hasPermission()
Search for: AccessDecisionManager, AccessDecisionVoter
Search for: PermissionEvaluator, MethodSecurityExpressionHandler
Search for: @EnableGlobalMethodSecurity, @EnableMethodSecurity
```

---

## Step 7: Team Structure and Conway's Law Analysis

This step is critical for large organizations. Service boundaries that don't align with team structure will fail in practice.

### 7a: Current Team Topology

```
For each team or developer group:
  - Which modules/packages do they primarily own?
  - Which areas of the codebase do they modify most frequently? (check git log)
  - What is the team size?
  - What is their deployment cadence?
  - Do they have on-call/operational responsibilities?
```

### 7b: Boundary Alignment Check

For each proposed bounded context, evaluate:

| Question | Impact |
|----------|--------|
| Can a single team own this service end-to-end? | If no, the boundary may be wrong |
| Does this boundary split code that one team currently owns? | Creates handoff overhead |
| Does this boundary merge code from multiple teams? | May cause ownership conflicts |
| Does the team have the skills to operate this service independently? | Training needed |
| Can the team handle the operational burden? | Capacity constraint |

### 7c: Viability Assessment

If proposed service boundaries cannot be cleanly mapped to teams, flag this as a high-severity risk. Options:
1. Adjust boundaries to match team structure
2. Reorganize teams to match proposed boundaries
3. Reduce the number of services to match available team capacity
4. Recommend modular monolith if team structure doesn't support microservices

---

## Step 8: Complexity and Risk Scoring

### 8a: Per-Service Complexity Score

For each proposed microservice, calculate:

| Factor | Weight | Score (1-5) |
|--------|--------|-------------|
| Entity count | 1x | 1 (1-3), 2 (4-7), 3 (8-12), 4 (13-20), 5 (21+) |
| Cross-boundary references | 2x | 1 (0-1), 2 (2-3), 3 (4-6), 4 (7-10), 5 (11+) |
| Shared tables | 3x | 1 (0), 2 (1), 3 (2-3), 4 (4-5), 5 (6+) |
| Stored procedures / native queries | 1x | 1 (0), 2 (1-2), 3 (3-5), 4 (6-10), 5 (11+) |
| External integrations | 1x | 1 (0), 2 (1), 3 (2), 4 (3-4), 5 (5+) |
| Transactional dependencies | 3x | 1 (0), 2 (1), 3 (2), 4 (3-4), 5 (5+) |
| Shared state instances | 2x | 1 (0), 2 (1), 3 (2-3), 4 (4-5), 5 (6+) |
| Framework migration needed | 2x | 1 (Spring Boot 3.x), 2 (Spring Boot 2.x), 3 (Spring Boot 1.x), 4 (Spring MVC no Boot), 5 (Java EE / app server) |

Total score interpretation:
- 15-25: Easy extraction
- 26-40: Medium complexity
- 41-55: Hard extraction
- 56+: Very hard — consider breaking into smaller steps

### 8b: Migration Viability Gate

Before calculating migration order, evaluate whether microservices extraction is justified. If any of the following conditions are true, recommend against decomposition:

**Recommend AGAINST microservices if:**

| Condition | Threshold | Rationale |
|-----------|-----------|-----------|
| Total module count | ≤ 3 | Too small to benefit from distribution overhead |
| Total entity count | ≤ 15 | Insufficient domain complexity |
| Proposed service count | ≤ 2 | Not enough distinct bounded contexts |
| All complexity scores | < 15 (Easy) | Monolith is manageable as-is |
| No team scaling problem | Single team, < 8 devs | Conway's Law doesn't demand splitting |
| No independent deployment need | Single release cadence | Key microservices benefit is absent |
| High cross-boundary coupling | > 60% of entities have cross-boundary refs | Will produce a distributed monolith |
| App server locked (WebSphere/WebLogic) | Vendor lock-in with no budget to change | Migration cost exceeds benefit |

**Recommend CAUTION (modular monolith instead) if:**
- 4-8 modules with moderate coupling — a modular monolith with clean boundaries may deliver 80% of the benefit at 20% of the cost
- Team is < 4 developers — operational overhead of microservices will exceed velocity gains
- No existing CI/CD, containerization, or observability — infrastructure prerequisites are missing
- Spring Boot 1.x or Java 8 — upgrade the monolith first before decomposing

**When recommending against decomposition, suggest alternatives:**
1. Modular monolith — enforce bounded contexts via Maven/Gradle modules and package-private visibility
2. Vertical slice architecture — organize by feature within the monolith
3. Strangler Fig for specific pain points — extract only the 1-2 components that genuinely need independent scaling
4. Do nothing — if the monolith is working and the team is productive, document that finding

Include the viability assessment in the Executive Summary. The recommendation field should be one of:
- **Proceed** — clear benefits, manageable complexity
- **Proceed with Caution** — benefits exist but significant risks; consider phased approach
- **Modular Monolith Recommended** — enforce boundaries without distribution
- **Do Not Decompose** — monolith is appropriate for this codebase and team

### 8c: Migration Order Algorithm

Determine extraction order using this formula:

```
Migration Priority Score =
  (100 / Complexity Score) × 30                    [Lower complexity = higher priority]
  + (1 / (Cross-Boundary References + 1)) × 25     [Fewer cross-refs = higher priority]
  + (1 / (Inbound Dependencies + 1)) × 20          [Fewer dependents = higher priority]
  + (Independent Deployability Factor × 15)         [0.0-1.0: can it run alone?]
  + (Business Value Factor × 10)                    [0 (low), 1 (medium), 2 (high)]
```

Ordering rules after scoring:
1. Services with zero inbound dependencies go first
2. Services depended upon by many others go last
3. Break ties using complexity score (lower first)
4. Never extract a service before its synchronous dependencies are available
5. Identity/Auth service should be extracted early if multiple services need token validation
6. Group related services that share transaction boundaries into the same migration phase

### 8d: Risk Register

For each proposed service, document risks:

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Shared table X needs splitting | High | High | Create migration script, test with production data copy |
| @Transactional spanning Order and Inventory | Medium | High | Implement saga pattern with compensation |
| Performance degradation from API calls replacing in-process calls | Medium | Medium | Add caching, optimize API contracts |
| Spring Security filter chain disruption | Low | Critical | Extract auth service first, test thoroughly |

---

## Step 9: Generate Assessment Report

Present a comprehensive report to the user. The report must include ALL of the following sections:

```
## Monolith Assessment Report

### 1. Executive Summary
- One paragraph overview of the monolith
- Migration viability recommendation (Proceed / Proceed with Caution / Modular Monolith Recommended / Do Not Decompose)
- If "Do Not Decompose" or "Modular Monolith Recommended", explain why and suggest alternatives
- Number of proposed microservices (if proceeding)
- Overall complexity rating (Easy/Medium/Hard/Very Hard)
- Estimated effort (see Effort Estimation below)
- Key risks in 2-3 bullet points

### Effort Estimation

Map the sum of all per-service complexity scores to an effort range:

| Total Complexity Score | Effort Estimate | Typical Duration (1 team) | Description |
|----------------------|-----------------|--------------------------|-------------|
| 15-50 | Small | 2-6 weeks | Few services, low coupling, straightforward extraction |
| 51-120 | Medium | 6-16 weeks | Multiple services, moderate coupling, some refactoring |
| 121-250 | Large | 4-8 months | Many services, significant coupling, database splitting |
| 251+ | Very Large | 8-18 months | Complex system, extensive refactoring, phased migration |

Adjustment multipliers:
- Java 8 or older: multiply by 1.4x (language migration + decomposition)
- Spring Boot 1.x or no Spring Boot: multiply by 1.5x (framework migration needed)
- App server deployment (WebSphere/WebLogic): multiply by 1.6x
- No existing test coverage: multiply by 1.3x (need characterization tests first)
- Stored procedure heavy (20+): multiply by 1.2x
- Team unfamiliar with microservices: multiply by 1.3x
- Multiple databases or database vendors: multiply by 1.2x

### 2. Codebase Overview
- Build system and module structure diagram
- Module inventory table (from Step 1)
- Technology stack summary (from Step 2)
- Lines of code estimates per module
- Test coverage summary
- Java version and Spring Boot version compatibility notes

### 3. Domain Model Map
- Complete entity inventory with relationships
- Aggregate boundaries identified
- Entity relationship diagram (text-based)

### 4. Identified Bounded Contexts
For EACH context: name, entities, controllers, services, data access, external integrations, background jobs

### 5. Dependency Analysis
- Module reference graph
- Hub modules and their role
- God modules and their responsibilities
- Circular dependencies (with resolution strategy)
- Package-level coupling hotspots

### 6. Data Layer Analysis
- DataSource inventory with entity sets
- Table ownership matrix
- Shared tables with resolution strategy
- Stored procedure / native query ownership
- Cross-context query inventory
- Transaction boundary analysis results

### 7. Coupling Metrics
- Per-context coupling scores (Ca, Ce, I, A, D)
- Cross-boundary reference inventory
- Shared state instances with resolution strategy

### 8. Security Analysis
- Authentication mechanism and flow
- Authorization model summary
- Identity data ownership

### 8.5. Team Structure Analysis
- Current team topology mapped to codebase ownership
- Proposed service-to-team mapping
- Boundary alignment assessment
- Capacity and skills gap analysis

### 9. Proposed Microservices
For EACH proposed service: name, responsibility, entities, APIs, events, dependencies, complexity score, risks

### 10. Recommended Migration Order
- Ordered list with priority scores
- Dependencies between migration steps
- Estimated relative effort per step

### 11. Risk Register
- Complete risk table with likelihood, impact, and mitigation

### 12. Recommendations
- Java version upgrade recommendations (if applicable)
- Spring Boot upgrade path
- Shared library strategy
- Inter-service communication patterns
- Infrastructure recommendations
```

### After Presenting the Report

Ask the user:
1. Does the bounded context identification look correct?
2. Would you like to adjust any service boundaries?
3. Are there business constraints that should influence the migration order?
4. Are there any entities or components I missed?
5. Do you agree with the risk assessment?
6. Are you ready to proceed to the transformation planning phase?

**Do not proceed to transformation until the user explicitly approves the assessment.**
