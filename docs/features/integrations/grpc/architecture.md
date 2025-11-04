---
title: Architecture & Design
description: Django-CFG gRPC architecture, design patterns, and implementation details
sidebar_label: Architecture
sidebar_position: 2
keywords:
  - grpc architecture
  - django grpc design
  - grpc patterns
  - grpc interceptors
---

# gRPC Architecture & Design

This document explains the architecture and design patterns behind Django-CFG's gRPC integration.

## 🏗️ System Architecture

### High-Level Overview

```mermaid
graph TB
    subgraph "External Clients"
        PythonClient([Python Client])
        GoClient([Go Client])
        JSClient([JavaScript Client])
        MobileClient([Mobile App])
    end

    subgraph "Django-CFG Application"
        subgraph "gRPC Server Layer"
            Server["🚀 gRPC Server<br/>(asyncio/threading)"]
            Reflection["Server Reflection<br/>(grpcurl support)"]
            Health["Health Check Service"]
        end

        subgraph "Interceptors Pipeline"
            direction LR
            I1["Request Logger"]
            I2["Console Logger"]
            I3["JWT Auth"]
            I4["Error Handler"]
            I5["Metrics"]

            I1 --> I2 --> I3 --> I4 --> I5
        end

        subgraph "Service Layer"
            Discovery["Service Discovery<br/>(Auto-registration)"]
            BaseClasses["Base Service Classes<br/>(BaseService, ReadOnlyService, AuthRequiredService)"]
        end

        subgraph "Business Services"
            UserService["UserService"]
            ProductService["ProductService"]
            OrderService["OrderService"]
            CustomServices["Custom Services..."]
        end

        subgraph "Django Integration"
            ORM[("💾 Django ORM")]
            Auth["Django Auth<br/>(User, Permissions)"]
            Signals["Django Signals"]
            Cache{{Redis Cache}}
        end

        subgraph "Data Layer"
            DB[("PostgreSQL / MySQL / SQLite")]
            Redis[("Redis")]
        end

        subgraph "Monitoring Layer"
            LogModel["GRPCRequestLog<br/>Model"]
            AdminUI["Django Admin<br/>Interface"]
            RestAPI["REST Monitoring<br/>API"]
        end
    end

    PythonClient -->|gRPC| Server
    GoClient -->|gRPC| Server
    JSClient -->|gRPC| Server
    MobileClient -->|gRPC| Server

    Server --> Reflection
    Server --> Health
    Server --> I1

    I5 --> Discovery
    Discovery --> BaseClasses
    BaseClasses --> UserService
    BaseClasses --> ProductService
    BaseClasses --> OrderService
    BaseClasses --> CustomServices

    UserService --> ORM
    ProductService --> ORM
    OrderService --> ORM

    ORM --> DB
    Auth --> DB
    Cache --> Redis

    I1 -.->|Log| LogModel
    LogModel --> DB
    LogModel --> AdminUI
    LogModel --> RestAPI

    style Server fill:#1e40af
    style BaseClasses fill:#15803d
    style LogModel fill:#7e22ce
    style Discovery fill:#be185d
```

## 🔄 Request Flow Architecture

### Complete Request Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant Server as gRPC Server
    participant Pipeline as Interceptors Pipeline
    participant Logger as Request Logger
    participant Auth as JWT Auth
    participant Error as Error Handler
    participant Service as Business Service
    participant ORM as Django ORM
    participant DB as Database
    participant Admin as Admin Interface

    Note over Client,Admin: 1. Request Initiation
    Client->>Server: gRPC Call (method + metadata + payload)

    Note over Server,Pipeline: 2. Interceptors Pipeline (Pre-Processing)
    Server->>Pipeline: Enter pipeline
    Pipeline->>Logger: Interceptor #1: Request Logger

    Logger->>DB: INSERT GRPCRequestLog<br/>(request_id, service, method, status=PENDING)
    Note over Logger: Generate UUID<br/>Parse metadata<br/>Extract client info

    Pipeline->>Auth: Interceptor #2: JWT Auth
    Auth->>Auth: Extract token from metadata
    Auth->>DB: SELECT User WHERE id=<token.user_id>
    DB-->>Auth: User object
    Auth->>Pipeline: Set user in context

    Pipeline->>Error: Interceptor #3: Error Handler
    Note over Error: Wrap service call<br/>in try-catch

    Note over Service,ORM: 3. Service Execution
    Pipeline->>Service: Call service method
    Service->>Service: Validate request
    Service->>ORM: Query data<br/>(e.g., User.objects.get())
    ORM->>DB: SELECT query
    DB-->>ORM: Query result
    ORM-->>Service: Django model instance
    Service->>Service: Build protobuf response

    Note over Service,Error: 4. Response Path
    Service-->>Error: Return response
    Error->>Error: No exceptions - pass through

    Note over Logger,DB: 5. Post-Processing
    Error-->>Logger: Response ready
    Logger->>Logger: Calculate duration<br/>Measure sizes
    Logger->>DB: UPDATE GRPCRequestLog<br/>(status=SUCCESS, duration_ms, response_size)

    Logger-->>Server: Final response
    Server-->>Client: gRPC Response

    Note over Admin: 6. Monitoring
    Admin->>DB: Query GRPCRequestLog
    DB-->>Admin: Display metrics, logs, timeline
```

### Error Flow

```mermaid
sequenceDiagram
    participant Client
    participant Server as gRPC Server
    participant Pipeline as Interceptors
    participant Error as Error Handler
    participant Service
    participant Logger as Request Logger
    participant DB

    Client->>Server: gRPC Call

    Server->>Pipeline: Process request
    Pipeline->>Service: Call method

    Service->>Service: Business logic
    Service->>Service: ❌ Exception raised<br/>(e.g., User.DoesNotExist)

    Service-->>Error: Raise exception

    Note over Error: Map Django exception<br/>to gRPC status
    Error->>Error: User.DoesNotExist<br/>→ StatusCode.NOT_FOUND

    Error->>Logger: Log error details
    Logger->>DB: UPDATE GRPCRequestLog<br/>(status=ERROR, error_message, grpc_status_code)

    Error-->>Server: gRPC RpcError
    Server-->>Client: Error response<br/>(status_code, details)

    Note over Client: Handle error<br/>based on status code
```

## 🧩 Component Architecture

### 1. Interceptors Pipeline

The interceptors execute in a specific order to ensure proper request handling:

```mermaid
graph TB
    Request["Incoming<br/>Request"] --> I1

    subgraph "Interceptors (Execution Order)"
        I1["1️⃣ Request Logger<br/>━━━━━━━━━━━<br/>• Generate request ID<br/>• Create log entry<br/>• Extract metadata"]
        I2["2️⃣ Console Logger<br/>━━━━━━━━━━━<br/>• Structured logging<br/>• Request/response size<br/>• Duration tracking"]
        I3["3️⃣ JWT Auth<br/>━━━━━━━━━━━<br/>• Extract token<br/>• Verify signature<br/>• Load Django user<br/>• Set user context"]
        I4["4️⃣ Error Handler<br/>━━━━━━━━━━━<br/>• Wrap service call<br/>• Catch exceptions<br/>• Map to gRPC status<br/>• Format error details"]
        I5["5️⃣ Metrics<br/>━━━━━━━━━━━<br/>• Collect metrics<br/>• Performance data<br/>• Success/error rates"]
    end

    Service["Business<br/>Service"]
    Response["Outgoing<br/>Response"]

    I1 --> I2 --> I3 --> I4 --> I5 --> Service
    Service --> I5 --> I4 --> I3 --> I2 --> I1 --> Response

    style I1 fill:#1e40af
    style I3 fill:#ea580c
    style I4 fill:#dc2626
    style Service fill:#15803d
```

**Key Design Decisions:**

1. **Request Logger First** - Creates log entry before any processing
2. **Auth Before Error Handler** - User context available for error logging
3. **Error Handler Wraps Service** - Catches all service exceptions
4. **Bidirectional Flow** - Interceptors process both request and response

### 2. Service Discovery System

```mermaid
graph TB
    Config["GRPCConfig<br/>━━━━━━━━━━━<br/>auto_register_apps=True<br/>enabled_apps=[...]"]

    Discovery["ServiceDiscovery<br/>━━━━━━━━━━━"]

    subgraph "Discovery Process"
        Apps["Load Django Apps"]
        Scan["Scan for Service Modules"]
        Import["Import Service Classes"]
        Register["Register with gRPC Server"]
    end

    subgraph "Service Module Patterns"
        P1["app/grpc_services.py"]
        P2["app/grpc_handlers.py"]
        P3["app/services/grpc.py"]
        P4["app/handlers/grpc.py"]
        P5["app/api/grpc.py"]
    end

    subgraph "Service Registration"
        Server["gRPC Server"]
        Servicer["Add Servicer"]
        Reflection["Update Reflection"]
    end

    Config --> Discovery
    Discovery --> Apps --> Scan

    Scan --> P1
    Scan --> P2
    Scan --> P3
    Scan --> P4
    Scan --> P5

    P1 --> Import
    P2 --> Import
    P3 --> Import
    P4 --> Import
    P5 --> Import

    Import --> Register
    Register --> Servicer
    Register --> Reflection
    Servicer --> Server

    style Discovery fill:#be185d
    style Server fill:#1e40af
```

### 3. Base Service Classes Hierarchy

```mermaid
classDiagram
    class BaseService {
        +get_user(context) User | None
        +require_user(context) User
        +check_permission(context, perm)
        +require_staff(context)
        +require_superuser(context)
        +abort_not_found(context, msg)
        +abort_permission_denied(context, msg)
        +abort_invalid_argument(context, msg)
        +abort_unauthenticated(context, msg)
        +abort_already_exists(context, msg)
        +abort_internal(context, msg)
    }

    class ReadOnlyService {
        <<Read-Only Operations>>
        +list_items(request, context)
        +get_item(request, context)
        +search_items(request, context)
    }

    class AuthRequiredService {
        <<Authentication Required>>
        +user: User
        +check_access(context)
    }

    class UserService {
        +GetUser(request, context)
        +UpdateProfile(request, context)
        +ListUsers(request, context)
    }

    class ProductService {
        +GetProduct(request, context)
        +SearchProducts(request, context)
    }

    class OrderService {
        +CreateOrder(request, context)
        +GetOrder(request, context)
        +CancelOrder(request, context)
    }

    BaseService <|-- ReadOnlyService
    BaseService <|-- AuthRequiredService
    BaseService <|-- UserService
    ReadOnlyService <|-- ProductService
    AuthRequiredService <|-- OrderService

    note for BaseService "Provides Django integration:\n- User authentication\n- Permission checking\n- Helper abort methods\n- ORM access"

    note for ReadOnlyService "Only read operations allowed.\nNo write access to database."

    note for AuthRequiredService "All methods require\nauthenticated user.\nuser property always set."
```

## 🔐 Authentication Architecture

### JWT Token Flow

```mermaid
sequenceDiagram
    participant Client
    participant Django as Django API
    participant JWT as JWT Service
    participant gRPC as gRPC Server
    participant Auth as JWT Auth Interceptor
    participant DB

    Note over Client,DB: 1. Obtain JWT Token
    Client->>Django: POST /api/auth/login<br/>{username, password}
    Django->>DB: Verify credentials
    DB-->>Django: User valid
    Django->>JWT: Generate JWT token<br/>{user_id, exp, ...}
    JWT-->>Django: Signed token
    Django-->>Client: {access_token, refresh_token}

    Note over Client,DB: 2. gRPC Call with JWT
    Client->>gRPC: gRPC Call<br/>metadata: Authorization=Bearer <token>

    gRPC->>Auth: Extract token from metadata
    Auth->>Auth: Parse JWT token
    Auth->>Auth: Verify signature<br/>(using SECRET_KEY)
    Auth->>Auth: Check expiration

    Auth->>DB: SELECT User WHERE id=<token.user_id>
    DB-->>Auth: User object

    Auth->>gRPC: Set user in context
    Note over gRPC: context.user = User instance

    gRPC->>gRPC: Execute service method<br/>(user available via self.get_user())

    gRPC-->>Client: Response
```

### Public vs Protected Methods

```mermaid
graph TB
    Request["gRPC Request"]
    AuthInterceptor["JWT Auth Interceptor"]

    Decision{Has JWT<br/>Token?}

    Public{Method<br/>Requires<br/>Auth?}

    LoadUser["Load User from Token"]
    SetContext["Set user in context"]
    AllowPublic["Allow request<br/>(user=None)"]
    Deny["❌ Deny<br/>UNAUTHENTICATED"]

    Service["Execute Service Method"]

    Request --> AuthInterceptor
    AuthInterceptor --> Decision

    Decision -->|Yes| LoadUser
    Decision -->|No| Public

    Public -->|No| AllowPublic
    Public -->|Yes| Deny

    LoadUser --> SetContext
    SetContext --> Service
    AllowPublic --> Service

    Deny -.->|Error| Request

    style LoadUser fill:#047857
    style AllowPublic fill:#ea580c
    style Deny fill:#dc2626
    style Service fill:#1e40af
```

## 📊 Monitoring Architecture

### Request Logging System

```mermaid
graph TB
    subgraph "Request Processing"
        Request["gRPC Request"]
        Interceptor["Request Logger Interceptor"]
        Service["Service Execution"]
        Response["gRPC Response"]
    end

    subgraph "Logging Pipeline"
        Create["Create Log Entry<br/>━━━━━━━━━━━<br/>• request_id (UUID)<br/>• service_name<br/>• method_name<br/>• status = PENDING<br/>• timestamp"]

        Update["Update Log Entry<br/>━━━━━━━━━━━<br/>• status = SUCCESS/ERROR<br/>• duration_ms<br/>• response_size<br/>• grpc_status_code<br/>• error_message"]
    end

    subgraph "Database"
        LogTable["GRPCRequestLog Table<br/>━━━━━━━━━━━<br/>• All request metadata<br/>• Indexed by service/method<br/>• Indexed by status<br/>• Indexed by user"]
    end

    subgraph "Monitoring Interfaces"
        Admin["Django Admin<br/>━━━━━━━━━━━<br/>• Beautiful UI<br/>• Color-coded badges<br/>• Filtering & search<br/>• Export to CSV"]

        RestAPI["REST Monitoring API<br/>━━━━━━━━━━━<br/>/cfg/integrations/grpc/monitor/overview<br/>/cfg/integrations/grpc/monitor/requests<br/>/cfg/integrations/grpc/monitor/services<br/>/cfg/integrations/grpc/monitor/timeline"]

        Metrics["Metrics & Stats<br/>━━━━━━━━━━━<br/>• Total requests<br/>• Success rate<br/>• Avg duration<br/>• P95 latency"]
    end

    Request --> Interceptor
    Interceptor --> Create
    Create --> LogTable

    Interceptor --> Service
    Service --> Response

    Response --> Interceptor
    Interceptor --> Update
    Update --> LogTable

    LogTable --> Admin
    LogTable --> RestAPI
    LogTable --> Metrics

    style Create fill:#047857
    style Update fill:#1e40af
    style LogTable fill:#7e22ce
```

### Statistics & Metrics

```mermaid
graph TB
    subgraph "Data Collection"
        Logs["GRPCRequestLog<br/>Records"]
    end

    subgraph "Aggregation (ORM)"
        Manager["GRPCRequestLogManager<br/>━━━━━━━━━━━"]

        Stats["get_statistics(hours=24)<br/>━━━━━━━━━━━<br/>• total requests<br/>• successful requests<br/>• error count<br/>• success_rate %<br/>• avg_duration_ms<br/>• p95_duration_ms"]

        Filters["Filter Methods<br/>━━━━━━━━━━━<br/>• recent(hours)<br/>• successful()<br/>• error()<br/>• by_service(name)<br/>• by_method(name)<br/>• by_user(user)"]
    end

    subgraph "Presentation"
        Overview["Overview Dashboard<br/>━━━━━━━━━━━<br/>📊 Total Requests<br/>✅ Success Rate<br/>⚡ Avg Duration<br/>🔥 Top Services"]

        Timeline["Timeline View<br/>━━━━━━━━━━━<br/>📈 Requests over time<br/>🕐 Hourly breakdown<br/>📉 Error trends"]

        Services["Services View<br/>━━━━━━━━━━━<br/>📋 Service list<br/>🎯 Per-service stats<br/>🔍 Method breakdown"]
    end

    Logs --> Manager
    Manager --> Stats
    Manager --> Filters

    Stats --> Overview
    Filters --> Timeline
    Filters --> Services

    style Manager fill:#be185d
    style Overview fill:#047857
    style Timeline fill:#1e40af
```

## 🔄 Phase 4: Dynamic Invocation

### Dynamic gRPC Client Architecture

```mermaid
graph TB
    subgraph "Phase 4 Components"
        DynamicClient["DynamicGRPCClient"]
        ReflectionClient["Reflection Client"]
        MessageFactory["Message Factory"]
        DescriptorPool["Descriptor Pool"]
    end

    subgraph "gRPC Server"
        ReflectionService["Server Reflection Service"]
        Services["Your gRPC Services"]
    end

    DynamicClient --> ReflectionClient
    ReflectionClient --> ReflectionService
    ReflectionService --> DescriptorPool

    DynamicClient --> MessageFactory
    MessageFactory --> DescriptorPool
    MessageFactory --> Services

    style DynamicClient fill:#1e40af
    style MessageFactory fill:#15803d
    style ReflectionService fill:#ea580c
```

**Key Features:**
1. **Service Discovery** - Automatically discover all available services
2. **Method Introspection** - Get method signatures and schemas
3. **Dynamic Message Creation** - Create protobuf messages from JSON/dict
4. **No Proto Files Required** - Use reflection to understand service contracts

Learn more: [Dynamic Invocation Guide](./dynamic-invocation.md)

---

## 🎯 Design Patterns

### 1. Interceptor Pattern

**Purpose:** Cross-cutting concerns (logging, auth, metrics) without modifying service code.

**Implementation:**
```python
class MyInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        # Pre-processing
        # ...

        # Call next interceptor/service
        response = continuation(handler_call_details)

        # Post-processing
        # ...

        return response
```

### 2. Service Discovery Pattern

**Purpose:** Automatic registration of gRPC services from Django apps.

**Key Components:**
- Module scanning (grpc_services.py, grpc_handlers.py)
- Lazy loading support
- Convention over configuration

### 3. Django Integration Pattern

**Purpose:** Seamless access to Django features in gRPC services.

**Integration Points:**
- ORM via models
- User authentication via JWT
- Permissions via Django auth
- Admin interface for monitoring
- Signals for events

### 4. Error Mapping Pattern

**Purpose:** Convert Django exceptions to appropriate gRPC status codes.

**Mapping:**
```
Django Exception          → gRPC Status Code
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ValidationError           → INVALID_ARGUMENT
ObjectDoesNotExist        → NOT_FOUND
PermissionDenied          → PERMISSION_DENIED
NotImplementedError       → UNIMPLEMENTED
TimeoutError              → DEADLINE_EXCEEDED
Exception                 → INTERNAL
```

## 🚀 Performance Considerations

### Threading Model

```mermaid
graph TB
    Server["gRPC Server"]
    Pool["Thread Pool<br/>(max_workers=10)"]

    subgraph "Request Threads"
        T1["Thread 1<br/>Request A"]
        T2["Thread 2<br/>Request B"]
        T3["Thread 3<br/>Request C"]
        TN["Thread N<br/>Request N"]
    end

    Django["Django<br/>(Thread-safe ORM)"]
    DB[(Database<br/>Connection Pool)]

    Server --> Pool
    Pool --> T1
    Pool --> T2
    Pool --> T3
    Pool --> TN

    T1 --> Django
    T2 --> Django
    T3 --> Django
    TN --> Django

    Django --> DB

    style Pool fill:#1e40af
    style Django fill:#7e22ce
```

**Configuration:**
```python
GRPCServerConfig(
    max_workers=10,  # Thread pool size
    # More workers = more concurrent requests
    # But higher memory usage
)
```

### Database Optimization

- **Connection Pooling** - Reuse database connections
- **Select Related / Prefetch Related** - Reduce N+1 queries
- **Indexed Fields** - Fast lookups on service/method/status
- **Async Logging** - Non-blocking request logging

## 📚 Related Documentation

- **[Getting Started](./getting-started.md)** - Configure gRPC in your project
- **[Configuration](./configuration.md)** - Configure gRPC settings
- **[Concepts](./concepts.md)** - Core gRPC concepts
- **[FAQ](./faq.md)** - Common questions and answers

---

**Next:** Learn how to [get started with gRPC](./getting-started.md) in your Django-CFG project.
