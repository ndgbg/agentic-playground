# Distributed Transaction Patterns

When a monolith is decomposed into microservices, operations that previously ran in a single database transaction may now span multiple services. This steering file covers the patterns for handling cross-service data consistency. Consult this during Phase 2 planning whenever the assessment identifies transactional dependencies crossing service boundaries.

---

## When You Need This

The assessment phase (Step 4g: Transaction Boundary Analysis) identifies transactions that span proposed service boundaries. For each such transaction, you must choose a consistency strategy from this file.

**Key question for each cross-boundary transaction:** What is the business impact if the operation is eventually consistent (seconds of delay) vs. immediately consistent?

| Business Impact | Strategy |
|----------------|----------|
| Unacceptable (financial, legal) | Saga with strict compensation |
| Tolerable for seconds | Event-driven eventual consistency |
| Tolerable for minutes | Async event with retry |
| Display-only (read path) | Denormalized read model via events |

---

## Pattern 1: Saga (Orchestration)

A central orchestrator coordinates the steps across services and handles compensation (rollback) on failure. Best when the workflow has a clear owner and the steps must happen in order.

### When to Use
- Business operations that span 2-4 services with ordered steps
- Operations where compensation logic is well-defined
- When you need visibility into the overall workflow state

### Implementation

```csharp
// Saga orchestrator lives in the service that owns the workflow
// Example: PlaceOrderSaga in OrderService

public class PlaceOrderSaga
{
    private readonly IOrderRepository _orders;
    private readonly IInventoryServiceClient _inventory;
    private readonly IPaymentServiceClient _payment;
    private readonly ILogger<PlaceOrderSaga> _logger;

    public async Task<Result<OrderConfirmation>> ExecuteAsync(PlaceOrderCommand command, CancellationToken ct)
    {
        // Step 1: Create order in Pending state
        var order = Order.Create(command.CustomerId, command.Items);
        await _orders.AddAsync(order, ct);

        // Step 2: Reserve inventory
        var reserveResult = await _inventory.ReserveStockAsync(
            new ReserveStockRequest(order.Id, command.Items), ct);

        if (!reserveResult.IsSuccess)
        {
            // Compensate step 1
            order.Cancel("Insufficient stock");
            await _orders.UpdateAsync(order, ct);
            return Result<OrderConfirmation>.Failure("Insufficient stock");
        }

        // Step 3: Process payment
        var paymentResult = await _payment.ProcessPaymentAsync(
            new ProcessPaymentRequest(order.Id, order.TotalAmount), ct);

        if (!paymentResult.IsSuccess)
        {
            // Compensate step 2, then step 1
            await _inventory.ReleaseStockAsync(new ReleaseStockRequest(order.Id), ct);
            order.Cancel("Payment failed");
            await _orders.UpdateAsync(order, ct);
            return Result<OrderConfirmation>.Failure("Payment failed");
        }

        // Step 4: Confirm order
        order.Confirm(paymentResult.Value.TransactionId);
        await _orders.UpdateAsync(order, ct);

        return Result<OrderConfirmation>.Success(new OrderConfirmation(order.Id));
    }
}
```

### Saga State Machine (for complex workflows)

For sagas with many steps or conditional branches, use a state machine:

```csharp
public enum OrderSagaState
{
    Started,
    InventoryReserved,
    PaymentProcessed,
    Confirmed,
    // Compensation states
    PaymentFailed_ReleasingInventory,
    InventoryFailed_CancellingOrder,
    Compensated,
    Failed
}

public class OrderSagaStateMachine
{
    // Store saga state in a SagaState table in the orchestrator's database
    // Each transition is idempotent
    // Timeout handling: if a step doesn't complete within N seconds, trigger compensation
    // Retry handling: transient failures retry before compensating
}
```

### Compensation Design Rules

1. Every forward step must have a defined compensation step
2. Compensation must be idempotent (safe to retry)
3. Compensation should be "best effort" — log and alert if compensation itself fails
4. Order of compensation is reverse of execution
5. Some steps may not need compensation (e.g., sending a notification — send a correction instead)

---

## Pattern 2: Saga (Choreography)

Each service reacts to events from other services. No central orchestrator. Best when services are loosely coupled and the workflow is simple.

### When to Use
- Simple 2-3 step workflows
- Services are independently developed by different teams
- No single service "owns" the workflow
- You want maximum decoupling

### Implementation

```
Flow: Order Placed → Inventory Reserved → Payment Processed → Order Confirmed

1. OrderService publishes OrderPlacedEvent
2. InventoryService consumes OrderPlacedEvent
   → Reserves stock
   → Publishes StockReservedEvent (or StockReservationFailedEvent)
3. PaymentService consumes StockReservedEvent
   → Processes payment
   → Publishes PaymentProcessedEvent (or PaymentFailedEvent)
4. OrderService consumes PaymentProcessedEvent
   → Confirms order

Compensation flow:
- PaymentFailedEvent → InventoryService releases stock → OrderService cancels order
- StockReservationFailedEvent → OrderService cancels order
```

```csharp
// In InventoryService — event handler
public class OrderPlacedEventHandler : IIntegrationEventHandler<OrderPlacedEvent>
{
    public async Task HandleAsync(OrderPlacedEvent @event, CancellationToken ct)
    {
        var result = await _inventoryService.TryReserveAsync(@event.OrderId, @event.Items, ct);

        if (result.IsSuccess)
            await _eventBus.PublishAsync(new StockReservedEvent(@event.OrderId), ct);
        else
            await _eventBus.PublishAsync(new StockReservationFailedEvent(@event.OrderId, result.Error), ct);
    }
}
```

### Choreography Pitfalls
- Hard to understand the full workflow (no single place to see all steps)
- Difficult to add new steps or change order
- Debugging failures requires correlating events across services
- Cyclic event chains can cause infinite loops
- Use choreography only for simple flows; switch to orchestration when complexity grows

---

## Pattern 3: Outbox Pattern

Guarantees that domain changes and integration events are published atomically. Solves the "dual write" problem where saving to the database succeeds but publishing the event fails (or vice versa).

### When to Use
- Always, when publishing integration events after a state change
- Critical for saga reliability (both orchestration and choreography)
- Any time you need "at-least-once" event delivery

### Implementation

```csharp
// 1. Define the outbox table (in each service's database)
public class OutboxMessage
{
    public Guid Id { get; set; }
    public string EventType { get; set; }        // e.g., "OrderPlacedEvent"
    public string Payload { get; set; }           // JSON-serialized event
    public DateTime CreatedAt { get; set; }
    public DateTime? ProcessedAt { get; set; }
    public int RetryCount { get; set; }
    public string? Error { get; set; }
}

// 2. Save entity + outbox message in the same transaction
public class OrderService
{
    public async Task<Order> PlaceOrderAsync(PlaceOrderCommand command, CancellationToken ct)
    {
        var order = Order.Create(command.CustomerId, command.Items);

        await using var transaction = await _context.Database.BeginTransactionAsync(ct);

        _context.Orders.Add(order);
        _context.OutboxMessages.Add(new OutboxMessage
        {
            Id = Guid.NewGuid(),
            EventType = nameof(OrderPlacedEvent),
            Payload = JsonSerializer.Serialize(new OrderPlacedEvent(order.Id, order.CustomerId, order.TotalAmount)),
            CreatedAt = DateTime.UtcNow
        });

        await _context.SaveChangesAsync(ct);
        await transaction.CommitAsync(ct);

        return order;
    }
}

// 3. Background worker polls and publishes
public class OutboxProcessor : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var messages = await _context.OutboxMessages
                .Where(m => m.ProcessedAt == null && m.RetryCount < 5)
                .OrderBy(m => m.CreatedAt)
                .Take(50)
                .ToListAsync(ct);

            foreach (var message in messages)
            {
                try
                {
                    await _eventBus.PublishAsync(message.EventType, message.Payload, ct);
                    message.ProcessedAt = DateTime.UtcNow;
                }
                catch (Exception ex)
                {
                    message.RetryCount++;
                    message.Error = ex.Message;
                }
            }

            await _context.SaveChangesAsync(ct);
            await Task.Delay(TimeSpan.FromSeconds(1), ct);
        }
    }
}
```

### Outbox with MassTransit

MassTransit has built-in outbox support:

```csharp
// In Program.cs
builder.Services.AddMassTransit(x =>
{
    x.AddEntityFrameworkOutbox<OrderDbContext>(o =>
    {
        o.UseSqlServer();
        o.UseBusOutbox();
    });
});
```

### Outbox Cleanup

Processed messages should be cleaned up periodically:

```sql
-- Run daily or weekly
DELETE FROM OutboxMessages WHERE ProcessedAt IS NOT NULL AND ProcessedAt < DATEADD(DAY, -7, GETUTCDATE());
```

---

## Pattern 4: Inbox Pattern (Idempotent Consumers)

The counterpart to the outbox. Ensures that duplicate event deliveries (which are inevitable with at-least-once delivery) don't cause duplicate side effects.

### Implementation

```csharp
public class InboxMessage
{
    public Guid EventId { get; set; }       // From the event's unique ID
    public string EventType { get; set; }
    public DateTime ProcessedAt { get; set; }
}

public class StockReservedEventHandler : IIntegrationEventHandler<StockReservedEvent>
{
    public async Task HandleAsync(StockReservedEvent @event, CancellationToken ct)
    {
        // Check inbox — have we already processed this event?
        var alreadyProcessed = await _context.InboxMessages
            .AnyAsync(m => m.EventId == @event.EventId, ct);

        if (alreadyProcessed)
            return; // Idempotent — skip duplicate

        // Process the event
        await _orderService.ConfirmStockReservationAsync(@event.OrderId, ct);

        // Record in inbox
        _context.InboxMessages.Add(new InboxMessage
        {
            EventId = @event.EventId,
            EventType = nameof(StockReservedEvent),
            ProcessedAt = DateTime.UtcNow
        });

        await _context.SaveChangesAsync(ct);
    }
}
```

---

## Pattern 5: Event-Driven Denormalization

For read-path consistency: a service subscribes to events from another service and maintains a local read-only copy of the data it needs.

### When to Use
- Service A frequently needs to display data owned by Service B
- The data doesn't need to be real-time (seconds of lag is acceptable)
- You want to avoid synchronous API calls on the read path

### Implementation

```csharp
// ProductService publishes ProductUpdatedEvent
// OrderService subscribes and maintains a local ProductReadModel

public class ProductReadModel
{
    public Guid ProductId { get; set; }
    public string Name { get; set; }
    public decimal Price { get; set; }
    public DateTime LastUpdated { get; set; }
}

public class ProductUpdatedEventHandler : IIntegrationEventHandler<ProductUpdatedEvent>
{
    public async Task HandleAsync(ProductUpdatedEvent @event, CancellationToken ct)
    {
        var existing = await _context.ProductReadModels.FindAsync(@event.ProductId);
        if (existing == null)
        {
            _context.ProductReadModels.Add(new ProductReadModel
            {
                ProductId = @event.ProductId,
                Name = @event.Name,
                Price = @event.Price,
                LastUpdated = DateTime.UtcNow
            });
        }
        else
        {
            existing.Name = @event.Name;
            existing.Price = @event.Price;
            existing.LastUpdated = DateTime.UtcNow;
        }
        await _context.SaveChangesAsync(ct);
    }
}
```

### Backfill Strategy

When a new service starts up or a new read model is added, historical data needs to be backfilled:

1. Service B exposes a bulk export API: `GET /api/products?modifiedSince=...`
2. Service A calls this on startup to populate its read model
3. After backfill, Service A switches to event-driven updates
4. Include a `LastUpdated` timestamp to handle ordering

---

## Choosing the Right Pattern

| Scenario | Recommended Pattern |
|----------|-------------------|
| Order placement spanning inventory + payment | Orchestration saga with outbox |
| Updating a product and notifying catalog consumers | Outbox + event-driven denormalization |
| Displaying customer name on order details | Event-driven denormalization (or sync API with cache) |
| Transferring money between accounts | Orchestration saga with strict compensation |
| Sending email after order confirmation | Simple async event (fire-and-forget, retry on failure) |
| Audit logging across services | Choreography (each service publishes, audit service consumes) |
| Reserving a seat/ticket (time-sensitive) | Sync API call with timeout + saga for confirmation |

---

## Anti-Patterns to Avoid

### Two-Phase Commit (2PC) Across Services
Don't try to implement distributed transactions with 2PC across microservices. It creates tight coupling, requires all participants to be available, and doesn't scale. Use sagas instead.

### Shared Database as Transaction Coordinator
Don't keep services writing to the same database "just for transactions." This defeats the purpose of decomposition and creates a hidden coupling point.

### Fire-and-Forget Without Outbox
Don't publish events directly after saving without an outbox. If the event publish fails after the database commit, you have an inconsistent state with no recovery path.

### Synchronous Saga Steps Without Timeout
Every synchronous call in a saga must have a timeout. Without it, a hung downstream service blocks the entire workflow indefinitely.

### Compensation Without Idempotency
Compensation steps will be retried on failure. If they're not idempotent, retries can cause double-reversals or other inconsistencies.
