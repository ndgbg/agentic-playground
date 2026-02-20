# Authentication & Authorization Patterns Reference

Patterns for handling identity, authentication, and authorization during monolith-to-microservices decomposition.

---

## ASP.NET Identity (Full Framework)
**Pattern:** ASP.NET Identity with IdentityDbContext, UserManager, SignInManager.
**Resolution:**
- Extract into a dedicated Identity/Auth microservice
- Other services validate JWT tokens (no direct Identity dependency)
- Identity service owns: AspNetUsers, AspNetRoles, AspNetUserRoles, AspNetUserClaims, etc.
- Migrate from cookie auth to JWT for service-to-service communication
- Keep cookie auth at the gateway/BFF level for browser clients

## ASP.NET Core Identity
**Pattern:** ASP.NET Core Identity with modern configuration.
**Resolution:**
- Same as above but easier migration (already uses modern patterns)
- Identity service can use IdentityServer/Duende for token issuance
- Other services only need JWT validation middleware

## IdentityServer / Duende IdentityServer
**Pattern:** OAuth2/OpenID Connect server for token issuance.
**Resolution:**
- IdentityServer becomes the Identity microservice (or stays as a standalone service)
- All other services validate tokens against IdentityServer's JWKS endpoint
- Client credentials flow for service-to-service authentication
- Authorization code flow for user-facing applications

## Custom Authorization Attributes
**Pattern:** Custom [Authorize] attributes with business logic.
**Resolution:**
- Simple role/policy checks → replicate per service
- Complex authorization with data access → move to the owning service
- Consider a centralized authorization service for complex policies (e.g., OPA, Casbin)
- Resource-based authorization → stays with the resource-owning service

## Windows Authentication
**Pattern:** Integrated Windows Authentication (IWA) in intranet apps.
**Resolution:**
- May need to convert to token-based auth for microservices
- Use a gateway that handles Windows Auth and issues JWT tokens
- Services validate JWT tokens internally
- Kerberos delegation → replace with token forwarding

## Claims Transformation
**Pattern:** Custom IClaimsTransformation that enriches claims from database.
**Resolution:**
- Claims transformation moves to the Identity service
- Or: each service enriches claims from its own data as needed
- Avoid cross-service claims enrichment (adds coupling)
