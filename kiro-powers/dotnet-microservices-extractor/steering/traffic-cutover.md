# Traffic Cutover and Incremental Migration Guide

This steering file covers the riskiest part of a production migration: incrementally routing traffic from the monolith to new microservices without downtime or data loss. Consult this during Phase 2 planning and Phase 3 execution.

---

## Strangler Fig Pattern — Detailed Implementation

The Strangler Fig pattern is the primary strategy for incremental migration. New microservices gradually take over functionality from the monolith.

### Architecture

```
                    ┌─────────────────┐
                    │   API Gateway   │
                    │  (routing layer) │
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

1. Place an API Gateway or reverse proxy in front of the monolith
2. All traffic initially routes to the monolith (no behavior change)
3. Deploy new microservice alongside the monolith
4. Route specific endpoints from monolith to new service
5. Monitor, validate, expand routing
6. Repeat for each service extraction
7. Monolith shrinks until decommissioned

---

## API Gateway Routing Strategies

### Path-Based Routing

Route specific URL paths to the new service:

```yaml
# YARP (Yet Another Reverse Proxy) configuration
routes:
  # New service handles order endpoints
  - routeId: orders-service
    match:
      path: /api/orders/{**catch-all}
    destination: http://order-service:8080

  # Everything else goes to monolith
  - routeId: monolith-fallback
    match:
      path: /{**catch-all}
    destination: http://monolith:5000
```

```csharp
// YARP configuration in API Gateway Program.cs
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));
```

### Header-Based Routing (Canary)

Route a percentage of traffic or specific users to the new service:

```yaml
routes:
  - routeId: orders-canary
    match:
      path: /api/orders/{**catch-all}
      headers:
        - name: X-Canary
          values: ["true"]
    destination: http://order-service:8080

  - routeId: orders-monolith
    match:
      path: /api/orders/{**catch-all}
    destination: http://monolith:5000
```

### Weighted Routing (Gradual Rollout)

Shift traffic percentage over time:

```
Day 1:   1% → new service, 99% → monolith   (smoke test)
Day 3:   10% → new service, 90% → monolith   (validate at scale)
Day 7:   50% → new service, 50% → monolith   (parallel run)
Day 14:  100% → new service, 0% → monolith   (full cutover)
```

---

## Feature Flags

Use feature flags to control which code path executes — monolith or microservice — without redeployment.

### Feature Flag Implementation

```csharp
// In the monolith or BFF layer
public class OrderController : ControllerBase
{
    private readonly IFeatureManager _featureManager;
    private readonly IOrderService _localOrderService;      // monolith
    private readonly IOrderServiceClient _remoteOrderClient; // microservice

    [HttpPost("api/orders")]
    public async Task<IActionResult> CreateOrder([FromBody] CreateOrderRequest request)
    {
        if (await _featureManager.IsEnabledAsync("UseOrderMicroservice"))
        {
            // Route to new microservice
            var result = await _remoteOrderClient.CreateOrderAsync(request);
            return CreatedAtAction(nameof(GetOrder), new { id = result.Id }, result);
        }
        else
        {
            // Use existing monolith code
            var result = await _localOrderService.CreateOrderAsync(request);
            return CreatedAtAction(nameof(GetOrder), new { id = result.Id }, result);
        }
    }
}
```

### Feature Flag Providers

| Provider | Use Case |
|----------|----------|
| Microsoft.FeatureManagement | Simple on/off flags, percentage rollout |
| LaunchDarkly | Advanced targeting, A/B testing, audit trail |
| Azure App Configuration | Azure-native, integrates with .NET config |
| Unleash | Open-source, self-hosted |
| appsettings.json | Simplest option for dev/test |

### Feature Flag Best Practices

- Name flags descriptively: `UseOrderMicroservice`, `RouteInventoryToNewService`
- Always have a kill switch — ability to route back to monolith instantly
- Remove flags after migration is complete (flag debt is real)
- Log which path was taken for every request (aids debugging)
- Test both paths in CI/CD

---

## Parallel Run Validation

Run both the monolith and microservice simultaneously, compare results, and alert on discrepancies. This is the safest approach for critical business logic.

### Shadow Traffic Pattern

Send a copy of production traffic to the new service without affecting the response:

```csharp
// In API Gateway or middleware
public class ShadowTrafficMiddleware
{
    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        // Forward to monolith (primary — this response goes to the client)
        await next(context);

        // Asynchronously forward to new service (shadow — response is discarded)
        if (ShouldShadow(context.Request))
        {
            _ = Task.Run(async () =>
            {
                try
                {
                    var shadowResponse = await _shadowClient.ForwardAsync(context.Request);
                    await CompareResponses(context.Response, shadowResponse);
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Shadow request failed — not affecting production");
                }
            });
        }
    }
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
  - Route via user ID or email domain
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

```csharp
// Automated rollback via health check
public class CutoverHealthCheck : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(HealthCheckContext context, CancellationToken ct)
    {
        var errorRate = await _metrics.GetErrorRateAsync("order-service", TimeSpan.FromMinutes(5));
        var baselineErrorRate = await _metrics.GetBaselineErrorRateAsync("orders");

        if (errorRate > baselineErrorRate * 2)
        {
            // Trigger automatic rollback
            await _featureManager.DisableAsync("UseOrderMicroservice");
            return HealthCheckResult.Unhealthy($"Error rate {errorRate:P} exceeds 2x baseline {baselineErrorRate:P}. Rolled back.");
        }

        return HealthCheckResult.Healthy();
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
- [ ] Monitoring dashboards are set up for the new service
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
- [ ] Update API documentation
- [ ] Archive monolith code for this feature (don't delete yet)
- [ ] Update runbooks and incident response procedures
- [ ] Celebrate the successful extraction 🎉
```

---

## Common Cutover Failures and Mitigations

| Failure Mode | Detection | Mitigation |
|-------------|-----------|------------|
| Data inconsistency after split | Comparison queries, checksums | Parallel run validation before cutover |
| Latency spike from network hops | P99 latency monitoring | Caching, connection pooling, gRPC instead of REST |
| Cascading failure from service dependency | Circuit breaker tripping | Bulkhead pattern, fallback responses, async where possible |
| Authentication token not propagated | 401 errors in new service | Test token forwarding in staging, verify JWT validation config |
| Missing data in denormalized read model | Stale or missing data in responses | Backfill script, event replay capability |
| Connection pool exhaustion | Database connection errors | Per-service connection limits, connection pooling config |
