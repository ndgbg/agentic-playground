# Policy Controls

Cedar policy engine for fine-grained access control and compliance enforcement. Define who can do what with your agents using declarative policies.

## Overview

Implement role-based access control (RBAC) and attribute-based access control (ABAC) for your agents using Cedar policies. Enforce security, compliance, and governance rules declaratively.

## Quick Start

```bash
cd advanced-patterns/policy-controls
pip install -r requirements.txt
python policy_agent.py
```

**Output:**
```
Policy Control Agent
============================================================

Action: read_data
Principal: user::alice
Resource: database::customers
Result: ✅ ALLOWED - User has read permission

Action: write_data
Principal: user::bob
Resource: database::customers
Result: ❌ DENIED - User lacks write permission

Action: delete_data
Principal: user::admin
Resource: database::customers
Result: ✅ ALLOWED - Admin has full access

Action: read_data
Principal: user::contractor
Resource: database::financial
Result: ❌ DENIED - Contractors cannot access financial data
============================================================
```

## Cedar Policy Language

### Basic Policy Structure

```cedar
permit(
    principal == User::"alice",
    action == Action::"read",
    resource == Database::"customers"
);
```

### Role-Based Policies

```cedar
// Admins can do everything
permit(
    principal in Role::"admin",
    action,
    resource
);

// Users can read
permit(
    principal in Role::"user",
    action == Action::"read",
    resource
);

// Deny contractors from financial data
forbid(
    principal in Role::"contractor",
    action,
    resource in Database::"financial"
);
```

### Attribute-Based Policies

```cedar
// Allow if same department
permit(
    principal,
    action == Action::"read",
    resource
)
when {
    principal.department == resource.department
};

// Allow during business hours
permit(
    principal,
    action,
    resource
)
when {
    context.time >= "09:00" && context.time <= "17:00"
};
```

## Available Tools

### check_permission()
Check if action is allowed:
```python
check_permission(
    principal="user::alice",
    action="read_data",
    resource="database::customers"
)
# Returns: {"allowed": True, "reason": "User has read permission"}
```

### add_policy()
Add new policy:
```python
add_policy(
    policy_id="allow-read",
    policy="""
    permit(
        principal in Role::"user",
        action == Action::"read",
        resource
    );
    """
)
```

### list_policies()
List all active policies:
```python
list_policies()
# Returns: [{"id": "policy1", "effect": "permit", ...}]
```

### audit_log()
Log access attempts:
```python
audit_log(
    principal="user::alice",
    action="read_data",
    resource="database::customers",
    result="allowed"
)
```

## Example Policies

### Multi-Tenant Isolation

```cedar
// Users can only access their own tenant's data
permit(
    principal,
    action,
    resource
)
when {
    principal.tenant_id == resource.tenant_id
};
```

### Time-Based Access

```cedar
// Allow access only during business hours
permit(
    principal,
    action,
    resource
)
when {
    context.hour >= 9 && context.hour <= 17 &&
    context.day_of_week in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
};
```

### Data Classification

```cedar
// Only admins can access sensitive data
forbid(
    principal,
    action,
    resource
)
when {
    resource.classification == "sensitive"
}
unless {
    principal in Role::"admin"
};
```

### Approval Workflow

```cedar
// High-value actions require approval
permit(
    principal,
    action == Action::"transfer_funds",
    resource
)
when {
    resource.amount < 10000 ||
    context.has_approval == true
};
```

## Customization

### Add Custom Attributes

```python
@tool
def check_permission_with_context(
    principal: str,
    action: str,
    resource: str,
    context: dict
) -> dict:
    """Check permission with additional context"""
    
    # Add custom attributes
    principal_attrs = {
        "department": get_user_department(principal),
        "clearance_level": get_clearance_level(principal),
        "tenant_id": get_tenant_id(principal)
    }
    
    resource_attrs = {
        "classification": get_data_classification(resource),
        "owner": get_resource_owner(resource),
        "tenant_id": get_resource_tenant(resource)
    }
    
    # Evaluate policy
    return evaluate_policy(principal_attrs, action, resource_attrs, context)
```

### Add Dynamic Policies

```python
@tool
def add_temporary_policy(
    principal: str,
    resource: str,
    duration_hours: int
) -> str:
    """Grant temporary access"""
    
    expiry = datetime.now() + timedelta(hours=duration_hours)
    
    policy = f"""
    permit(
        principal == User::"{principal}",
        action,
        resource == Resource::"{resource}"
    )
    when {{
        context.time < "{expiry.isoformat()}"
    }};
    """
    
    policy_id = add_policy(policy)
    schedule_policy_deletion(policy_id, expiry)
    
    return policy_id
```

### Add Policy Validation

```python
@tool
def validate_policy(policy: str) -> dict:
    """Validate policy syntax"""
    try:
        parse_cedar_policy(policy)
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}
```

## Integration Examples

### API Gateway Integration

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.before_request
def check_access():
    user = request.headers.get('X-User-ID')
    resource = request.path
    action = request.method.lower()
    
    result = check_permission(user, action, resource)
    
    if not result["allowed"]:
        return jsonify({"error": "Access denied"}), 403
```

### Database Access Control

```python
import psycopg2

def query_with_policy(user: str, query: str):
    # Check permission
    result = check_permission(
        principal=user,
        action="query_database",
        resource="database::main"
    )
    
    if not result["allowed"]:
        raise PermissionError("Access denied")
    
    # Execute query
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.execute(query)
    return cursor.fetchall()
```

### S3 Access Control

```python
import boto3

def download_s3_file(user: str, bucket: str, key: str):
    # Check permission
    result = check_permission(
        principal=user,
        action="read",
        resource=f"s3://{bucket}/{key}"
    )
    
    if not result["allowed"]:
        raise PermissionError("Access denied")
    
    # Download file
    s3 = boto3.client('s3')
    s3.download_file(bucket, key, '/tmp/file')
```

## Deploy to Production

### Store Policies in S3

```python
import boto3
import json

s3 = boto3.client('s3')

def load_policies_from_s3(bucket: str, key: str):
    response = s3.get_object(Bucket=bucket, Key=key)
    policies = json.loads(response['Body'].read())
    
    for policy in policies:
        add_policy(policy['id'], policy['policy'])
```

### Use AWS Verified Permissions

```python
import boto3

verifiedpermissions = boto3.client('verifiedpermissions')

def check_permission_aws(principal: str, action: str, resource: str):
    response = verifiedpermissions.is_authorized(
        policyStoreId='ps-123456',
        principal={'entityType': 'User', 'entityId': principal},
        action={'actionType': 'Action', 'actionId': action},
        resource={'entityType': 'Resource', 'entityId': resource}
    )
    
    return response['decision'] == 'ALLOW'
```

## Use Cases

### Multi-Tenant SaaS
Isolate customer data with tenant-based policies.

### Healthcare Compliance
Enforce HIPAA rules with role and attribute-based access.

### Financial Services
Implement SOX compliance with approval workflows.

### Enterprise Security
Control access to sensitive data based on clearance levels.

## Best Practices

### Principle of Least Privilege
```cedar
// Default deny, explicit allow
forbid(principal, action, resource);

permit(
    principal in Role::"user",
    action == Action::"read",
    resource in Database::"public"
);
```

### Separation of Duties
```cedar
// Users cannot approve their own requests
forbid(
    principal,
    action == Action::"approve",
    resource
)
when {
    principal == resource.requester
};
```

### Audit Everything
```python
@app.after_request
def log_access(response):
    audit_log(
        principal=request.user,
        action=request.method,
        resource=request.path,
        result="allowed" if response.status_code < 400 else "denied"
    )
    return response
```

## Troubleshooting

**Policy Not Working**
- Validate policy syntax
- Check attribute names match
- Verify policy order (forbid overrides permit)

**Performance Issues**
- Cache policy evaluations
- Index policies by resource type
- Use policy sets for organization

**Debugging Access Denials**
- Enable detailed logging
- Review audit logs
- Test policies in isolation

## Next Steps

1. Define your roles and resources
2. Write policies for your use cases
3. Test policies thoroughly
4. Integrate with your application
5. Monitor and audit access
