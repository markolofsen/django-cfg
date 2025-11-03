---
title: Dynamic gRPC Invocation
description: Test and invoke gRPC methods dynamically via REST API using reflection
sidebar_label: Dynamic Invocation
sidebar_position: 5
keywords:
  - grpc reflection
  - grpc testing
  - grpc rest api
  - grpc dynamic invocation
---

# Dynamic gRPC Invocation (Phase 4)

:::tip[Production-Ready Feature]
**Phase 4** is complete! Test and invoke any gRPC method dynamically via REST API without writing client code.
:::

## 🎯 What is Dynamic Invocation?

Dynamic gRPC Invocation allows you to:

- ✅ **Discover Services** - List all available gRPC services via REST API
- ✅ **Introspect Methods** - View method signatures and message schemas
- ✅ **Test Methods** - Invoke gRPC methods via HTTP/REST without gRPC client
- ✅ **Generate Messages** - Automatically create request messages from JSON
- ✅ **Use Reflection** - Built on gRPC Server Reflection protocol
- ✅ **No Proto Files** - Test services without .proto files

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Client (Web/HTTP)"
        Browser["Web Browser"]
        Postman["Postman/Insomnia"]
        CURL["curl/HTTPie"]
    end

    subgraph "REST API Layer"
        TestingViewSet["/cfg/integrations/grpc/test/"]
        ServicesViewSet["/cfg/integrations/grpc/services/"]
    end

    subgraph "Dynamic Invocation Layer"
        DynamicClient["DynamicGRPCClient"]
        MessageFactory["Message Factory"]
        Reflection["gRPC Reflection Client"]
    end

    subgraph "gRPC Server"
        Server["gRPC Server"]
        Services["Your gRPC Services"]
        ReflectionService["Server Reflection"]
    end

    Browser --> TestingViewSet
    Postman --> TestingViewSet
    CURL --> ServicesViewSet

    TestingViewSet --> DynamicClient
    ServicesViewSet --> Reflection

    DynamicClient --> MessageFactory
    MessageFactory --> Server
    Reflection --> ReflectionService

    Server --> Services

    style TestingViewSet fill:#e3f2fd
    style DynamicClient fill:#f3e5f5
    style MessageFactory fill:#e8f5e9
```

## 🎯 Core Capabilities

### Service Discovery via Reflection

Use gRPC Server Reflection to discover services dynamically:

```python
from django_cfg.apps.integrations.grpc.services.grpc_client import DynamicGRPCClient

# Create client with reflection enabled
client = DynamicGRPCClient(host="localhost", port=50051)

# List all available services
services = client.list_services()
# ['api.users.UserService', 'api.products.ProductService', ...]

# Get service descriptor
service_desc = client.get_service_descriptor("api.users.UserService")

# Inspect methods
for method in service_desc.methods:
    print(f"Method: {method.name}")
    print(f"  Input: {method.input_type}")
    print(f"  Output: {method.output_type}")
```

### Message Factory

Automatically create protobuf messages from JSON/dict:

```python
# Create request message dynamically
request_data = {
    "user_id": 1,
    "filters": {
        "active": True,
        "role": "admin"
    }
}

# Message factory handles conversion
response = client.invoke_method(
    service="api.users.UserService",
    method="GetUser",
    request_data=request_data
)
```

## 🔧 DynamicGRPCClient

The `DynamicGRPCClient` class enables dynamic invocation without protobuf files.

### Basic Usage

```python
from django_cfg.apps.integrations.grpc.services.grpc_client import DynamicGRPCClient

# Create client
client = DynamicGRPCClient(host="localhost", port=50051)

# List services
services = client.list_services()
print(f"Available services: {services}")

# Get service descriptor
service_desc = client.get_service_descriptor("api.users.UserService")
print(f"Methods: {service_desc.methods}")

# Invoke method
response = client.invoke_method(
    service="api.users.UserService",
    method="GetUser",
    request_data={"user_id": 1}
)
print(f"Response: {response}")
```

### With Authentication

```python
# Create metadata with JWT token
metadata = {
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# Invoke authenticated method
response = client.invoke_method(
    service="api.users.UserService",
    method="UpdateProfile",
    request_data={
        "first_name": "John",
        "last_name": "Doe"
    },
    metadata=metadata
)
```

### Error Handling

```python
try:
    response = client.invoke_method(
        service="api.users.UserService",
        method="GetUser",
        request_data={"user_id": 9999}
    )
except grpc.RpcError as e:
    if e.code() == grpc.StatusCode.NOT_FOUND:
        print("User not found")
    elif e.code() == grpc.StatusCode.UNAUTHENTICATED:
        print("Authentication required")
    elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
        print("Permission denied")
    else:
        print(f"Error: {e.details()}")
```

## 🎨 Python Integration Examples

### Testing with grpcurl

```bash
# List all services using reflection
grpcurl -plaintext localhost:50051 list

# Describe a service
grpcurl -plaintext localhost:50051 describe api.users.UserService

# Call a method
grpcurl -plaintext -d '{"user_id": 1}' \
  localhost:50051 api.users.UserService/GetUser
```

### Dynamic Client in Python Scripts

```python
from django_cfg.apps.integrations.grpc.services.grpc_client import DynamicGRPCClient

# Create reusable client
client = DynamicGRPCClient(host="localhost", port=50051)

# Test different methods
test_cases = [
    ("api.users.UserService", "GetUser", {"user_id": 1}),
    ("api.products.ProductService", "GetProduct", {"product_id": 100}),
    ("api.orders.OrderService", "ListOrders", {"user_id": 1}),
]

for service, method, request_data in test_cases:
    try:
        response = client.invoke_method(service, method, request_data)
        print(f"✅ {service}.{method}: {response}")
    except Exception as e:
        print(f"❌ {service}.{method}: {e}")
```

## 🎯 Use Cases

### 1. API Testing

Test your gRPC APIs without writing client code:
- Rapid prototyping
- Integration testing
- Manual QA testing
- API exploration

### 2. Documentation

Generate API documentation dynamically:
- Interactive API explorer
- Auto-generated examples
- Live playground

### 3. Debugging

Debug gRPC services in real-time:
- Test edge cases
- Reproduce bugs
- Verify fixes

### 4. Monitoring

Monitor service health:
- Health checks
- Service discovery
- Method availability

## 📊 Performance

### Caching

The DynamicGRPCClient caches service descriptors for performance:

```python
client = DynamicGRPCClient(
    host="localhost",
    port=50051,
    cache_descriptors=True,  # Cache service descriptors
    cache_ttl=300,           # Cache for 5 minutes
)
```

### Connection Pooling

Reuse connections for better performance:

```python
# Create a singleton client
client = DynamicGRPCClient(host="localhost", port=50051)

# Reuse for multiple invocations
for user_id in range(1, 100):
    response = client.invoke_method(
        service="api.users.UserService",
        method="GetUser",
        request_data={"user_id": user_id}
    )
```

## 📚 Related Documentation

- **[Getting Started](./getting-started.md)** - Configure gRPC in your project
- **[Configuration](./configuration.md)** - gRPC configuration options
- **[Architecture](./architecture.md)** - gRPC system architecture
- **[Concepts](./concepts.md)** - Core gRPC concepts

---

**Next:** Learn about [gRPC concepts](./concepts.md) and best practices.
