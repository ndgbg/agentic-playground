# Traffic Cutover and Incremental Migration Guide

This steering file covers the riskiest part of a production migration: incrementally routing traffic from the monolith to new microservices without downtime or data loss. Consult this during Phase 2 planning and Phase 3 execution.

---

## Strangler Fig Pattern — Detailed Implementation

The Strangler Fig pattern is the primary strategy for incremental migration. New microservices gradually take over functionality from the monolith.

### Architecture

```
                    ┌─────────────────┐
                    │   API Gateway   │
                    │ (Spring Cloud   │
                    │  Gateway / Kong)│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │  Monolith  │  │ Service A  │  │ Service B  │
     │ (shrinking)│  │   (new)    │  │   (new)    │
     └────────────┘  └────────────┘  └────────────┘
```

### Implementation Steps

1. Place an API Gateway (Spring Cloud Gateway, Kong, or Nginx) in front of the monolith
2. All traffic initially routes to the monolith (no behavior change)
3. Deploy new microservice alongside the monolith
4. Route specific endpoints from monolith to new service
5. Monitor, validate, expand routing
6. Repeat for each service extraction
7. Monolith shrinks until decommissioned

---

## API Gateway Routing Strategies

### Spring Cloud Gateway (Recommended for Spring Ecosystem)

```yaml
# application.yml for Spring Cloud Gateway
spring:
  cloud:
    gateway:
      routes:
        # New service handles order endpoints
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
          filters:
            - StripPrefix=0

        # New service handles product endpoints
        - id: product-service
          uri: lb://product-service
          predicates:
            - Path=/api/products/**

        # Everything else goes to monolith (catch-all, must be last)
        - id: monolith-fallback
          uri: http://monolith:8080
          predicates:
            - Path=/**
```

### Header-Based Routing (Canary)

Route specific users or a percentage of traffic to the new service:

```yaml
spring:
  cloud:
    gateway:
      routes:
        # Canary: requests with X-Canary header go to new service
        - id: orders-canary
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
            - Header=X-Canary, true
          metadata:
            response-timeout: 5000

        # Default: all other order requests go to monolith
        - id: orders-monolith
          uri: http://monolith:8080
          predicates:
            - Path=/api/orders/**
```

### Weighted Routing (Gradual Rollout)

```java
// Custom RoutePredicateFactory for weighted routing
@Component
public class WeightedRoutePredicateFactory extends AbstractRoutePredicateFactory<WeightedRoutePredicateFactory.Config> {
    @Override
    public Predicate<ServerWebExchange> apply(Config config) {
        return exchange -> {
            // Consistent hashing on user ID for sticky routing
            String userId = exchange.getRequest().getHeaders().getFirst("X-User-Id");
            if (userId != null) {
                int hash = Math.abs(userId.hashCode() % 100);
                return hash < config.getWeight();
            }
            // Random for anonymous traffic
            return ThreadLocalRandom.current().nextInt(100) < config.getWeight();
        };
    }
}
```

Shift traffic percentage over time:

```
Day 1:   1% → new service, 99% → monolith   (smoke test)
Day 3:   10% → new service, 90% → monolith   (validate at scale)
Day 7:   50% → new service, 50% → monolith   (parallel run)
Day 14:  100% → new service, 0% → monolith   (full cutover)
```

### Kong Gateway Alternative

```yaml
# Kong declarative configuration
services:
  - name: order-service
    url: http://order-service:8080
    routes:
      - name: order-routes
        paths:
          - /api/orders
        strip_path: false
    plugins:
      - name: canary
        config:
          percentage: 10
          upstream_fallback: monolith

  - name: monolith
    url: http://monolith:8080
    routes:
      - name: monolith-fallback
        paths:
          - /
```

---

## Feature Flags

Use feature flags to control which code path executes — monolith or microservice — without redeployment.

### Feature Flag Implementation (In Monolith or BFF)

```java
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {
    private final FeatureManager featureManager;
    private final OrderService localOrderService;        // monolith
    private final OrderServiceClient remoteOrderClient;  // microservice Feign client

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(@Valid @RequestBody CreateOrderRequest request) {
        if (featureManager.isActive("use-order-microservice")) {
            // Route to new microservice
            OrderResponse result = remoteOrderClient.createOrder(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(result);
        } else {
            // Use existing monolith code
            OrderResponse result = localOrderService.createOrder(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(result);
        }
    }
}
```

### Feature Flag Libraries for Java

| Library | Use Case | Configuration |
|---------|----------|---------------|
| Togglz | Java-native, Spring Boot starter, admin console | `togglz-spring-boot-starter` |
| FF4J | Feature flags + monitoring, Spring integration | `ff4j-spring-boot-starter` |
| LaunchDarkly | SaaS, advanced targeting, A/B testing, audit trail | `launchdarkly-java-server-sdk` |
| Unleash | Open-source, self-hosted, Spring Boot client | `unleash-client-java` |
| Spring Cloud Config | Simple on/off via config properties | `@ConditionalOnProperty` |
| application.yml | Simplest option for dev/test | `@Value("${feature.use-order-service:false}")` |

### Togglz Example

```java
// Define features
public enum MigrationFeatures implements Feature {
    @Label("Route orders to microservice")
    USE_ORDER_MICROSERVICE,

    @Label("Route products to microservice")
    USE_PRODUCT_MICROSERVICE,

    @Label("Route customers to microservice")
    USE_CUSTOMER_MICROSERVICE;
}

// Configuration
@Configuration
public class TogglzConfig {
    @Bean
    public FeatureProvider featureProvider() {
        return new EnumBasedFeatureProvider(MigrationFeatures.class);
    }

    @Bean
    public StateRepository stateRepository(DataSource dataSource) {
        // Store feature state in database (survives restarts)
        return new JDBCStateRepository(dataSource);
    }
}

// Usage
if (FeatureContext.getFeatureManager().isActive(MigrationFeatures.USE_ORDER_MICROSERVICE)) {
    return remoteOrderClient.createOrder(request);
}
```

### Feature Flag Best Practices

- Name flags descriptively: `use-order-microservice`, `route-inventory-to-new-service`
- Always have a kill switch — ability to route back to monolith instantly
- Remove flags after migration is complete (flag debt is real)
- Log which path was taken for every request (aids debugging)
- Test both paths in CI/CD
- Use percentage rollout for gradual migration
- Consistent user routing (same user always hits same backend during rollout)

---

## Parallel Run Validation

Run both the monolith and microservice simultaneously, compare results, and alert on discrepancies. This is the safest approach for critical business logic.

### Shadow Traffic Pattern

Send a copy of production traffic to the new service without affecting the response:

```java
// Spring Cloud Gateway filter for shadow traffic
@Component
public class ShadowTrafficGatewayFilter implements GlobalFilter, Ordered {
    private final WebClient shadowClient;
    private final MeterRegistry meterRegistry;

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        if (shouldShadow(exchange.getRequest())) {
            // Fire-and-forget shadow request to new service
            shadowClient.method(exchange.getRequest().getMethod())
                .uri(buildShadowUri(exchange.getRequest()))
                .headers(h -> h.addAll(exchange.getRequest().getHeaders()))
                .exchangeToMono(response -> {
                    compareResponses(exchange, response);
                    return Mono.empty();
                })
                .onErrorResume(ex -> {
                    log.warn("Shadow request failed — not affecting production", ex);
                    meterRegistry.counter("shadow.failures").increment();
                    return Mono.empty();
                })
                .subscribe();
        }
        // Primary request continues to monolith
        return chain.filter(exchange);
    }

    @Override
    public int getOrder() { return -1; }
}
```

### Dual-Write Verification

For write operations, compare the outcome of both paths:

```
1. Client sends POST /api/orders
2. Gateway forwards to BOTH monolith and microservice
3. Monolith response is returned to client (primary)
4. Microservice response is logged and compared
5. If responses differ → alert, log discrepancy, investigate
6. If responses match consistently → safe to cut over
```

**Caution:** Dual-write for mutations requires careful handling:
- The microservice write may need to be rolled back if it's not the primary
- Use a "dry run" mode where the microservice validates but doesn't persist
- Or use an event-sourced approach where both systems process the same events

### Comparison Metrics

Track these during parallel run:

| Metric | Threshold for Cutover |
|--------|----------------------|
| Response match rate | > 99.9% for reads, > 99.99% for writes |
| Latency difference | New service within 20% of monolith |
| Error rate | New service error rate ≤ monolith error rate |
| Data consistency | Zero discrepancies in business-critical fields |

---

## Canary Deployment

Deploy the new service to a small subset of users/traffic first.

### Canary Strategy

```
Phase 1: Internal users only (employees, QA team)
  - Route via user ID or email domain in JWT claims
  - Duration: 1-3 days
  - Success criteria: zero errors, correct behavior

Phase 2: 1-5% of production traffic
  - Route via consistent hashing on user ID
  - Duration: 3-7 days
  - Success criteria: error rate ≤ baseline, latency ≤ baseline + 10%

Phase 3: 25% of production traffic
  - Duration: 3-7 days
  - Success criteria: same as Phase 2

Phase 4: 50% of production traffic
  - Duration: 3-7 days
  - Monitor for capacity issues

Phase 5: 100% of production traffic
  - Remove monolith routing
  - Keep monolith running for 2 weeks as rollback target
  - Decommission monolith endpoint after confidence period
```

### Rollback Triggers

Automatically roll back to monolith if:
- Error rate exceeds 2x baseline for 5 minutes
- P99 latency exceeds 3x baseline for 10 minutes
- Any 5xx error rate > 1% for 2 minutes
- Data inconsistency detected between monolith and service databases
- Manual rollback triggered by on-call engineer

```java
// Automated rollback via Spring Boot Actuator health check
@Component
public class CutoverHealthIndicator implements HealthIndicator {
    private final MeterRegistry meterRegistry;
    private final FeatureManager featureManager;

    @Override
    public Health health() {
        double errorRate = getErrorRate("order-service", Duration.ofMinutes(5));
        double baselineRate = getBaselineErrorRate("orders");

        if (errorRate > baselineRate * 2) {
            // Trigger automatic rollback
            featureManager.disable("use-order-microservice");
            log.error("Auto-rollback: error rate {}% exceeds 2x baseline {}%", errorRate, baselineRate);
            return Health.down()
                .withDetail("reason", "Error rate exceeded threshold, rolled back")
                .withDetail("errorRate", errorRate)
                .withDetail("baseline", baselineRate)
                .build();
        }

        return Health.up()
            .withDetail("errorRate", errorRate)
            .withDetail("baseline", baselineRate)
            .build();
    }
}
```

---

## API Coexistence During Migration

During migration, both old (monolith) and new (microservice) endpoints may coexist.

### URL Strategy

Option 1: Gateway handles routing transparently (recommended)
- Clients don't know which backend serves the request
- Same URL, different backend based on routing rules
- Cleanest for clients, most complex for infrastructure

Option 2: Version prefix
- Monolith: `/api/v1/orders`
- Microservice: `/api/v2/orders`
- Clients migrate to v2 at their own pace
- Both versions coexist until all clients migrate

Option 3: Subdomain
- Monolith: `api.example.com/orders`
- Microservice: `orders.api.example.com/orders`
- Clear separation, requires DNS changes

### Client Migration

For each API consumer (frontend, mobile app, third-party):
1. Document which endpoints they use
2. Provide migration guide (URL changes, payload changes, new auth requirements)
3. Set deprecation timeline for old endpoints
4. Monitor old endpoint usage — don't decommission until traffic drops to zero
5. Provide backward-compatible responses where possible (add fields, don't remove)

---

## Cutover Checklist

Before cutting over each service:

```
Pre-Cutover:
- [ ] New service passes all integration tests
- [ ] Parallel run shows > 99.9% response match rate
- [ ] Latency is within acceptable range
- [ ] Error rate is at or below baseline
- [ ] Database migration is complete and verified
- [ ] Feature flag is tested (both on and off)
- [ ] Rollback procedure is documented and tested
- [ ] On-call team is briefed on the cutover
- [ ] Monitoring dashboards are set up (Grafana/Prometheus/CloudWatch)
- [ ] Alerting rules are configured

During Cutover:
- [ ] Enable feature flag for canary percentage
- [ ] Monitor error rates and latency for 30 minutes
- [ ] Gradually increase traffic percentage
- [ ] Verify data consistency between old and new databases
- [ ] Check all dependent services are functioning

Post-Cutover:
- [ ] 100% traffic on new service for 48+ hours with no issues
- [ ] Remove feature flag code from monolith
- [ ] Remove old endpoint from monolith (or mark deprecated)
- [ ] Update API documentation (Swagger/OpenAPI)
- [ ] Archive monolith code for this feature (don't delete yet)
- [ ] Update runbooks and incident response procedures
- [ ] Celebrate the successful extraction 🎉
```

---

## Common Cutover Failures and Mitigations

| Failure Mode | Detection | Mitigation |
|-------------|-----------|------------|
| Data inconsistency after split | Comparison queries, checksums | Parallel run validation before cutover |
| Latency spike from network hops | P99 latency monitoring (Micrometer) | Caching (Caffeine/Redis), connection pooling, gRPC instead of REST |
| Cascading failure from service dependency | Resilience4j circuit breaker tripping | Bulkhead pattern, fallback responses, async where possible |
| Authentication token not propagated | 401 errors in new service | Test token forwarding in staging, verify JWT validation config |
| Missing data in denormalized read model | Stale or missing data in responses | Backfill script, Kafka event replay capability |
| Connection pool exhaustion | HikariCP connection timeout errors | Per-service pool sizing, connection limit monitoring |
| Kafka consumer lag | Consumer lag metrics in Grafana | Scale consumers, increase partitions, optimize processing |
| Thread pool saturation | Rejected execution exceptions | Per-service thread pool tuning, bulkhead isolation |
