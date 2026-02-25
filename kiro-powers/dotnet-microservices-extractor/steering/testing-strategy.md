# Testing Strategy for Microservices Extraction

Testing is the safety net that makes incremental extraction possible. This steering file should be consulted before Phase 3 execution begins. The test strategy has three stages: before extraction (characterization), during extraction (contract + unit), and after extraction (validation).

---

## Pre-Extraction Checklist

Before extracting ANY service, verify these are in place:

- [ ] Characterization tests written for all endpoints being extracted
- [ ] Contract tests defined for all APIs the new service will consume
- [ ] Existing monolith test suite passes (baseline)
- [ ] Test infrastructure ready (Testcontainers, WireMock, or equivalent)
- [ ] CI pipeline can run the new service's tests independently

**Do not begin Phase 3 execution until this checklist is satisfied for the first service being extracted.**

---

## Stage 1: Characterization Tests (Before Extraction)

Characterization tests capture the current behavior of the monolith for the functionality being extracted. They serve as acceptance criteria for the new service.

### What to Test

For each service being extracted, write tests against the MONOLITH that cover:

1. Every public API endpoint that will move to the new service
2. Happy path for each endpoint (valid input, expected output)
3. Error cases (invalid input, not found, unauthorized)
4. Edge cases identified during assessment (null handling, empty collections, boundary values)
5. Response shape (field names, types, nesting) — the new service must match

### How to Write Them

```csharp
// Characterization tests run against the monolith first, then against the new service
// Use WebApplicationFactory or a running instance

public class OrderEndpointCharacterizationTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public OrderEndpointCharacterizationTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetOrders_ReturnsPagedList()
    {
        var response = await _client.GetAsync("/api/orders?page=1&pageSize=10");

        response.StatusCode.Should().Be(HttpStatusCode.OK);
        var body = await response.Content.ReadFromJsonAsync<PagedResult<OrderResponse>>();
        body.Should().NotBeNull();
        body.Items.Should().NotBeNull();
        body.Page.Should().Be(1);
        body.PageSize.Should().Be(10);
    }

    [Fact]
    public async Task CreateOrder_WithValidRequest_ReturnsCreated()
    {
        var request = new CreateOrderRequest
        {
            CustomerId = Guid.Parse("..."),  // Use seeded test data
            Items = new[] { new CreateOrderItemRequest { ProductId = Guid.Parse("..."), Quantity = 2 } }
        };

        var response = await _client.PostAsJsonAsync("/api/orders", request);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var order = await response.Content.ReadFromJsonAsync<OrderResponse>();
        order.Should().NotBeNull();
        order.Status.Should().Be("Pending");
        order.Items.Should().HaveCount(1);
    }

    [Fact]
    public async Task CreateOrder_WithEmptyItems_ReturnsBadRequest()
    {
        var request = new CreateOrderRequest
        {
            CustomerId = Guid.Parse("..."),
            Items = Array.Empty<CreateOrderItemRequest>()
        };

        var response = await _client.PostAsJsonAsync("/api/orders", request);

        response.StatusCode.Should().Be(HttpStatusCode.BadRequest);
    }

    [Fact]
    public async Task GetOrder_NotFound_Returns404()
    {
        var response = await _client.GetAsync($"/api/orders/{Guid.NewGuid()}");

        response.StatusCode.Should().Be(HttpStatusCode.NotFound);
    }
}
```

### Golden File Testing (Optional but Recommended)

For complex responses, capture the full response body as a golden file and compare:

```csharp
[Fact]
public async Task GetOrderDetails_MatchesGoldenFile()
{
    var response = await _client.GetAsync("/api/orders/known-test-order-id");
    var body = await response.Content.ReadAsStringAsync();

    // First run: save as golden file
    // Subsequent runs: compare against golden file
    // Ignore volatile fields (timestamps, generated IDs)
    body.Should().MatchSnapshot(options => options
        .IgnoreField("createdAt")
        .IgnoreField("updatedAt")
        .IgnoreField("id"));
}
```

---

## Stage 2: Contract Tests (During Extraction)

Contract tests verify that service-to-service API calls work correctly. They catch breaking changes before they reach production.

### Consumer-Driven Contract Tests with Pact

```csharp
// CONSUMER SIDE: OrderService defines what it expects from ProductService

public class OrderService_ProductServiceContractTests
{
    private readonly IPactBuilderV4 _pactBuilder;

    public OrderService_ProductServiceContractTests()
    {
        var pact = Pact.V4("OrderService", "ProductService", new PactConfig());
        _pactBuilder = pact.WithHttpInteractions();
    }

    [Fact]
    public async Task GetProduct_ReturnsExpectedShape()
    {
        _pactBuilder
            .UponReceiving("a request for product by ID")
            .WithRequest(HttpMethod.Get, "/api/products/550e8400-e29b-41d4-a716-446655440000")
            .WillRespond()
            .WithStatus(HttpStatusCode.OK)
            .WithJsonBody(new
            {
                id = "550e8400-e29b-41d4-a716-446655440000",
                name = Match.Type("Widget"),
                price = Match.Decimal(9.99m),
                inStock = Match.Type(true)
            });

        await _pactBuilder.VerifyAsync(async ctx =>
        {
            var client = new ProductServiceClient(new HttpClient { BaseAddress = ctx.MockServerUri });
            var product = await client.GetProductAsync(Guid.Parse("550e8400-e29b-41d4-a716-446655440000"));

            product.Should().NotBeNull();
            product.Name.Should().NotBeNullOrEmpty();
            product.Price.Should().BePositive();
        });
    }

    [Fact]
    public async Task GetProduct_NotFound_Returns404()
    {
        _pactBuilder
            .UponReceiving("a request for a non-existent product")
            .WithRequest(HttpMethod.Get, "/api/products/00000000-0000-0000-0000-000000000000")
            .WillRespond()
            .WithStatus(HttpStatusCode.NotFound);

        await _pactBuilder.VerifyAsync(async ctx =>
        {
            var client = new ProductServiceClient(new HttpClient { BaseAddress = ctx.MockServerUri });
            var product = await client.GetProductAsync(Guid.Empty);

            product.Should().BeNull();
        });
    }
}

// PROVIDER SIDE: ProductService verifies it can fulfill the contract

public class ProductService_PactVerificationTests
{
    [Fact]
    public void VerifyPactWithOrderService()
    {
        var verifier = new PactVerifier("ProductService", new PactVerifierConfig());

        verifier
            .WithHttpEndpoint(new Uri("http://localhost:5002"))
            .WithPactBrokerSource(new Uri("https://pact-broker.example.com"))
            .Verify();
    }
}
```

### When to Add Contract Tests

| Interaction | Contract Test Needed? |
|------------|----------------------|
| Service A calls Service B's REST API | Yes — consumer-driven contract test |
| Service A publishes event consumed by Service B | Yes — message contract test |
| Service A reads from shared cache | No — but document the cache key format |
| Service A calls external third-party API | No — use WireMock for integration tests instead |

---

## Stage 3: Service-Level Tests (During and After Extraction)

### Unit Tests

Each service gets its own unit tests covering domain logic:

```csharp
public class OrderTests
{
    [Fact]
    public void AddItem_IncreasesTotalAmount()
    {
        var order = Order.Create(Guid.NewGuid(), new List<OrderItemInput>());
        order.AddItem(Guid.NewGuid(), "Widget", 2, 9.99m);

        order.TotalAmount.Should().Be(19.98m);
        order.Items.Should().HaveCount(1);
    }

    [Fact]
    public void Cancel_SetsStatusToCancelled()
    {
        var order = Order.Create(Guid.NewGuid(), new List<OrderItemInput>());
        order.Cancel("Test reason");

        order.Status.Should().Be(OrderStatus.Cancelled);
    }
}
```

### Integration Tests with Testcontainers

Test the full stack (API → service → database) using real infrastructure:

```csharp
public class OrderApiIntegrationTests : IAsyncLifetime
{
    private MsSqlContainer _dbContainer;
    private WebApplicationFactory<Program> _factory;
    private HttpClient _client;

    public async Task InitializeAsync()
    {
        _dbContainer = new MsSqlBuilder()
            .WithImage("mcr.microsoft.com/mssql/server:2022-latest")
            .Build();
        await _dbContainer.StartAsync();

        _factory = new WebApplicationFactory<Program>()
            .WithWebHostBuilder(builder =>
            {
                builder.ConfigureServices(services =>
                {
                    // Replace DbContext with test container connection
                    services.RemoveAll<DbContextOptions<OrderDbContext>>();
                    services.AddDbContext<OrderDbContext>(options =>
                        options.UseSqlServer(_dbContainer.GetConnectionString()));

                    // Mock external service clients
                    services.RemoveAll<IProductServiceClient>();
                    services.AddSingleton<IProductServiceClient>(new FakeProductServiceClient());
                });
            });

        _client = _factory.CreateClient();

        // Apply migrations
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<OrderDbContext>();
        await db.Database.MigrateAsync();
    }

    [Fact]
    public async Task CreateAndRetrieveOrder_RoundTrip()
    {
        var createRequest = new CreateOrderRequest { /* ... */ };
        var createResponse = await _client.PostAsJsonAsync("/api/orders", createRequest);
        createResponse.StatusCode.Should().Be(HttpStatusCode.Created);

        var created = await createResponse.Content.ReadFromJsonAsync<OrderResponse>();
        var getResponse = await _client.GetAsync($"/api/orders/{created.Id}");
        getResponse.StatusCode.Should().Be(HttpStatusCode.OK);

        var retrieved = await getResponse.Content.ReadFromJsonAsync<OrderResponse>();
        retrieved.Id.Should().Be(created.Id);
    }

    public async Task DisposeAsync()
    {
        await _dbContainer.DisposeAsync();
        await _factory.DisposeAsync();
    }
}
```

---

## Test Migration Checklist (Per Service)

Use this checklist for each service extraction. Copy it into the transformation plan.

### Before Extraction
- [ ] Characterization tests written and passing against monolith
- [ ] Contract tests defined for all consumed APIs
- [ ] Test data seeding strategy defined
- [ ] Test infrastructure (Testcontainers, WireMock) set up

### During Extraction
- [ ] Unit tests written for domain logic in Core project
- [ ] Integration tests written with Testcontainers for database
- [ ] Contract tests passing (consumer and provider sides)
- [ ] Existing monolith tests still pass (monolith functionality unchanged)
- [ ] External service dependencies mocked in tests (WireMock or fakes)

### After Extraction
- [ ] Characterization tests pass against new service (with URL changes)
- [ ] Response shapes match between monolith and new service
- [ ] Remove or update monolith tests that covered extracted functionality
- [ ] End-to-end smoke tests pass in docker-compose environment
- [ ] Performance baseline established (response times, throughput)

---

## Handling Existing Tests During Migration

Existing monolith tests will be affected by extraction. Handle them as follows:

| Test Type | If Tests Touch Single Service | If Tests Span Services |
|-----------|------------------------------|----------------------|
| Unit tests | Move to new service's test project | Split by service, mock cross-service calls |
| Integration tests | Move to new service, update DB connection | Split into per-service integration tests + contract tests |
| End-to-end tests | Keep in a shared E2E test project | Keep, but run against docker-compose environment |
| UI tests | No change (they test through the API) | No change if API gateway handles routing |

### Tests That Must NOT Be Deleted

- Any test that covers business logic being extracted (move it, don't delete it)
- Integration tests that verify data integrity across what are now service boundaries (convert to contract tests)
- Performance/load tests (adapt to test the new service independently)

### Tests That Can Be Removed After Extraction

- Monolith integration tests that test functionality now fully owned by the new service (after characterization tests pass against the new service)
- Mock-heavy unit tests that were working around monolith coupling (the new service should have cleaner tests)
