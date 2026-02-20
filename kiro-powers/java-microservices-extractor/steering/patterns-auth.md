# Authentication & Authorization Patterns Reference

Patterns for handling identity, authentication, and authorization during Java monolith-to-microservices decomposition.

---

## Spring Security (Form Login)
**Pattern:** `formLogin()` configuration with `UserDetailsService`, session-based authentication, CSRF protection.
**Resolution:**
- Extract into a dedicated Identity/Auth microservice
- Identity service owns: users, roles, permissions, password encoding
- Migrate from session-based auth to JWT for service-to-service communication
- Keep form login at the BFF/gateway level for browser clients
- CSRF → typically disabled for stateless REST APIs, keep at BFF if server-rendered UI

## Spring Security (JWT / Stateless)
**Pattern:** Custom `OncePerRequestFilter` validating JWT tokens, `SecurityContextHolder` populated from token claims.
**Resolution:**
- JWT validation filter → common-infrastructure library (shared across all services)
- Each service configured as OAuth2 resource server
- Token issuance → Identity service or external IdP (Keycloak, Auth0, Okta)
- `SecurityContextHolder` populated per-request in each service
- Service-to-service → client credentials flow or token relay

## Spring Authorization Server
**Pattern:** Spring Authorization Server (replacement for Spring Security OAuth2 Authorization Server).
**Resolution:**
- Authorization Server becomes the Identity microservice
- Issues access tokens (JWT) and refresh tokens
- All other services validate tokens via JWKS endpoint
- Client registrations managed by Identity service
- Supports authorization code, client credentials, device authorization flows

## Keycloak Integration
**Pattern:** Keycloak adapter (`keycloak-spring-boot-starter`) or Spring Security OAuth2 with Keycloak as IdP.
**Resolution:**
- Keycloak remains as external Identity Provider
- Remove Keycloak adapter dependency (deprecated) → use standard Spring Security OAuth2
- Each service validates JWT from Keycloak via JWKS endpoint
- Realm roles and client roles → map to Spring Security authorities
- Keycloak admin API → used by Identity service for user management
```yaml
# Per-service configuration
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://keycloak.example.com/realms/myapp
          jwk-set-uri: https://keycloak.example.com/realms/myapp/protocol/openid-connect/certs
```

## OAuth2 Resource Server
**Pattern:** Service validates JWT tokens from an authorization server using `spring-boot-starter-oauth2-resource-server`.
**Resolution:**
- Each service independently validates JWT tokens
- Shared JWT configuration → common-infrastructure auto-configuration
- Custom `JwtAuthenticationConverter` for mapping claims to authorities
- Token introspection (opaque tokens) → each service calls the introspection endpoint
- Prefer JWT over opaque tokens for microservices (no network call needed for validation)

## OAuth2 Client (Service-to-Service)
**Pattern:** Service acts as OAuth2 client using client credentials flow for calling other services.
**Resolution:**
- Each service configured with its own client credentials
- `OAuth2AuthorizedClientManager` → per-service
- Token caching → per-service (avoid redundant token requests)
- Spring Cloud Gateway → token relay filter for forwarding user tokens
```java
// Feign client with OAuth2 client credentials
@FeignClient(name = "inventory-service", configuration = OAuth2FeignConfig.class)
public interface InventoryClient {
    @GetMapping("/api/inventory/{productId}")
    InventoryResponse getStock(@PathVariable UUID productId);
}

@Configuration
public class OAuth2FeignConfig {
    @Bean
    public RequestInterceptor oauth2Interceptor(OAuth2AuthorizedClientManager clientManager) {
        return template -> {
            var client = clientManager.authorize(
                OAuth2AuthorizeRequest.withClientRegistrationId("inventory-service").build()
            );
            template.header("Authorization", "Bearer " + client.getAccessToken().getTokenValue());
        };
    }
}
```

## SAML 2.0 Authentication
**Pattern:** Spring Security SAML (`spring-security-saml2-service-provider`) with enterprise IdP (ADFS, Okta, PingFederate).
**Resolution:**
- SAML authentication handled at gateway/BFF level only
- Gateway authenticates via SAML, issues internal JWT for downstream services
- Microservices never handle SAML directly (too complex, session-based)
- SAML assertion attributes → mapped to JWT claims at the gateway
- Single Logout (SLO) → handled at gateway level

## LDAP Authentication
**Pattern:** `LdapAuthenticationProvider`, `LdapTemplate` for authenticating against Active Directory or OpenLDAP.
**Resolution:**
- LDAP authentication → Identity service only
- Identity service authenticates against LDAP, issues JWT
- Other services validate JWT (no LDAP dependency)
- LDAP group membership → mapped to JWT roles/authorities
- LDAP user attributes → included in JWT claims or fetched via Identity API
```java
// Identity service LDAP configuration
@Configuration
public class LdapSecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/login").permitAll()
                .anyRequest().authenticated())
            .ldapAuthentication(ldap -> ldap
                .userDnPatterns("uid={0},ou=users")
                .groupSearchBase("ou=groups")
                .contextSource(ctx -> ctx
                    .url("ldap://ldap.example.com:389/dc=example,dc=com")))
            .build();
    }
}
```

## Custom Authentication Filters
**Pattern:** Custom `OncePerRequestFilter` or `AbstractAuthenticationProcessingFilter` for API keys, custom tokens, multi-factor auth.
**Resolution:**
- API key validation filter → move with the service that manages API keys (or shared if all services accept API keys)
- Custom token filters → shared if all services use the same token format
- Multi-factor auth → Identity service handles MFA, issues JWT after successful MFA
- Filter ordering is critical → document and replicate per service

## Method-Level Security (@PreAuthorize)
**Pattern:** `@PreAuthorize("hasRole('ADMIN')")`, `@Secured`, `@RolesAllowed` on service methods.
**Resolution:**
- Annotations move with their service methods
- Role/authority names must be consistent across services (define in shared constants)
- Custom `PermissionEvaluator` → move with the resource-owning service
- `@EnableMethodSecurity` → per-service configuration
- SpEL expressions referencing custom beans → ensure beans exist in the service

## Resource-Based Authorization
**Pattern:** Authorization decisions based on the resource being accessed (e.g., "user can only edit their own orders").
**Resolution:**
- Resource-based auth stays with the resource-owning service
- Each service enforces its own resource-level permissions
- Custom `PermissionEvaluator` implementations → per-service
- Avoid centralized authorization service for resource-level checks (creates coupling)
```java
@PreAuthorize("@orderSecurity.isOwner(#orderId, authentication)")
@GetMapping("/api/orders/{orderId}")
public OrderResponse getOrder(@PathVariable UUID orderId) {
    return orderService.findById(orderId);
}
```

## ACL (Access Control Lists)
**Pattern:** Spring Security ACL module for fine-grained object-level permissions.
**Resolution:**
- ACL tables move with the resource-owning service
- Each service manages ACLs for its own resources
- ACL evaluation → per-service `AclService` configuration
- Cross-service ACL checks → anti-pattern, avoid
- Consider simplifying to role-based or attribute-based access control during migration

## Security Context Propagation
**Pattern:** `SecurityContextHolder` used throughout the codebase to access current user.
**Resolution:**
- Each service populates its own `SecurityContextHolder` from JWT
- `SecurityContext` does not propagate across service boundaries automatically
- User identity propagated via JWT in `Authorization` header
- `@AuthenticationPrincipal` → works per-service after JWT validation
- Async processing (`@Async`, `CompletableFuture`) → configure `SecurityContextHolder.MODE_INHERITABLETHREADLOCAL` or propagate manually

## Session Management
**Pattern:** `HttpSession` with Spring Session (Redis, JDBC, Hazelcast).
**Resolution:**
- Stateless JWT preferred for microservices (no session needed)
- If session required for UI → Spring Session with Redis at BFF/gateway only
- Session-scoped beans → refactor to request-scoped or stateless
- `@SessionAttributes` → refactor to client-side state or Redis cache
- Shopping cart in session → dedicated Cart service with its own persistence

## CORS Configuration
**Pattern:** `@CrossOrigin` annotations or global CORS configuration.
**Resolution:**
- CORS handled at API Gateway level (single point of configuration)
- Per-service CORS → only if services are directly exposed (not recommended)
- Gateway CORS configuration covers all services
- Allowed origins, methods, headers → centralized at gateway
