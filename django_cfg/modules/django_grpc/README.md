# django_grpc

Async gRPC server module for [django-cfg](../../../../../../README.md).

Runs a production-ready `grpc.aio` server alongside your Django ASGI application.
All request state is persisted to **Cloudflare D1** — no PostgreSQL dependency.
Authentication is handled via **simplejwt Bearer tokens** — no extra round-trips on the hot path.

---

## Features

- **Async gRPC server** — `grpc.aio` with interceptor chain, health check, and server reflection
- **JWT authentication** — validates simplejwt tokens locally using `SECRET_KEY` (zero network requests)
- **Observability interceptor** — structured logging, in-memory metrics, Centrifugo publish, Telegram alerts
- **D1 persistence** — request logs, server status, connection states and metrics stored in Cloudflare D1
- **Async log worker** — producer-consumer queue batches D1 writes (50 rows / 5 s), never blocks requests
- **Connection state tracking** — optimistic CAS locking with exponential jitter retry
- **Bidirectional streaming** — full support for all four gRPC call types
- **Streamlit admin pages** — Overview, Connections, and Request Logs dashboards auto-registered on startup
- **Service auto-discovery** — discovers and registers gRPC services from `handlers_hook` or `enabled_apps`

---

## Quick Start

### 1. Add to your config

```python
# djangoconfig.py
from django_cfg import DjangoConfig
from django_cfg.modules.django_grpc import DjangoGrpcModuleConfig

class MyConfig(DjangoConfig):
    grpc_module: DjangoGrpcModuleConfig = DjangoGrpcModuleConfig(
        enabled=True,
        host="[::]",
        port=50051,
        public_url="grpc.example.com:443",
        handlers_hook="myapp.grpc.register_handlers",
    )
```

### 2. Implement your handlers hook

```python
# myapp/grpc.py
def register_handlers(server) -> list[str]:
    from myapp.proto import myservice_pb2_grpc, MyServiceServicer
    myservice_pb2_grpc.add_MyServiceServicer_to_server(MyServiceServicer(), server)
    return ["myapp.MyService"]
```

### 3. Run the server

```bash
uv run manage.py rungrpc
uv run manage.py rungrpc --host 0.0.0.0 --port 50051
uv run manage.py rungrpc --noreload   # disable hot-reload in staging
uv run manage.py rungrpc --http3      # add a Hypercorn[h3] frontend on :50052
```

---

## HTTP/3 (QUIC) Frontend (optional)

`django_grpc` can run a Hypercorn[h3] reverse proxy alongside the gRPC server.
Clients see HTTP/3 over QUIC, and traffic is forwarded transparently to the
existing `grpc.aio.server()` on the upstream HTTP/2 origin. The gRPC
interceptor chain (auth, error handling, observability) is unchanged — it all
runs on the upstream server.

### Install

The H3 dependencies are isolated in an opt-in extras group so projects that
don't need QUIC don't pay the dep cost:

```bash
pip install 'django-cfg[grpc-h3]'
```

This pulls in `hypercorn[h3]>=0.14.0` and `aioquic>=0.9.21`.

### Enable

Three independent paths set H3 on (priority: CLI > env > config field):

1. **CLI flag**

   ```bash
   uv run manage.py rungrpc --http3
   uv run manage.py rungrpc --http3 --http3-host 0.0.0.0 --http3-port 50052
   ```

2. **Environment variables** (useful for Docker / Kubernetes)

   ```bash
   export DJANGO_GRPC_ENABLE_H3=1
   export DJANGO_GRPC_H3_HOST=0.0.0.0
   export DJANGO_GRPC_H3_PORT=50052
   uv run manage.py rungrpc
   ```

3. **Config field** (per-project default)

   ```python
   from django_cfg.modules.django_grpc import (
       DjangoGrpcModuleConfig,
       GrpcServerConfig,
   )

   grpc_module = DjangoGrpcModuleConfig(
       server=GrpcServerConfig(
           port=50051,
           enable_h3=True,
           h3_host="0.0.0.0",
           h3_port=50052,
       ),
   )
   ```

### TLS

HTTP/3 mandates TLS. When `GrpcServerConfig.tls.enabled=True` with valid
`cert_path` / `key_path`, the H3 listener reuses those certs and clients
negotiate real QUIC. Without certs, Hypercorn falls back to HTTP/1.1 + HTTP/2
cleartext on the H3 port (a warning is logged) — useful in dev only.

### Behaviour

| Setting | Result |
|---|---|
| `enable_h3=False` (default) | No Hypercorn process spawned; rungrpc behaves exactly as before. |
| `enable_h3=True`, hypercorn installed | gRPC server on `:50051` + Hypercorn[h3] on `:50052`. Both shut down together on SIGINT. |
| `enable_h3=True`, hypercorn missing | A loud warning is logged, the gRPC server starts normally on HTTP/2 only — never crashes. |

### Limitations

- The proxy adds one localhost hop (~negligible latency).
- Per the audit, this is the recommended path until `grpcio` ships native
  HTTP/3 (no concrete ETA from upstream as of 2026).
- The H3 listener is server-side only — agents and other gRPC clients keep
  using their existing HTTP/2 transport unchanged.

See `services/h3.py` and `@plans/plan24-transport/reports2/11-djangocfg-h3-integration-audit.md`
for the design rationale.

---

## Configuration

All settings live in `DjangoGrpcModuleConfig` (Pydantic v2, frozen).

### Server

| Field | Default | Description |
|-------|---------|-------------|
| `host` | `"[::]"` | Listen address (IPv4/IPv6) |
| `port` | `50051` | Listen port |
| `max_workers` | `10` | Thread pool workers |
| `enable_reflection` | `True` | gRPC server reflection (grpcurl support) |
| `enable_health_check` | `True` | `/grpc.health.v1.Health/Check` endpoint |
| `max_send_message_length` | `4 MiB` | Max outbound message size |
| `max_receive_message_length` | `4 MiB` | Max inbound message size |
| `public_url` | `None` | Advertised external address |
| `internal_url` | `None` | Internal container-to-container address |

### Service Registration

| Field | Default | Description |
|-------|---------|-------------|
| `handlers_hook` | `""` | Import path(s) to a `register_handlers(server)` function |
| `enabled_apps` | `[]` | Django apps whose gRPC handlers are auto-registered |
| `package_prefix` | `"api"` | Proto package prefix for codegen |

### Authentication

JWT authentication is **opt-in**. When enabled, the `JWTAuthInterceptor` validates simplejwt
Bearer tokens from `authorization: Bearer <token>` request metadata.

| Field | Default | Description |
|-------|---------|-------------|
| `require_auth` | `False` | Reject requests without a valid JWT |
| `public_methods` | `[]` | Full method paths always allowed without auth |

Health check (`/grpc.health.v1.Health/Check`, `/Watch`) and reflection
(`/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo`) are **always** exempt
regardless of this setting.

**Token format** (simplejwt defaults, HS256 + `SECRET_KEY`):

```json
{
  "token_type": "access",
  "exp": 1234567890,
  "user_id": 42,
  "email": "user@example.com",
  "roles": ["admin"]
}
```

After successful validation, `get_current_grpc_user()` returns a `GrpcUserContext` for the
duration of the request:

```python
from django_cfg.modules.django_grpc.services.auth.context import get_current_grpc_user

def MyHandler(request, context):
    user = get_current_grpc_user()   # GrpcUserContext | None
    if user:
        print(user["user_id"], user["roles"])
```

### D1 Persistence

| Field | Default | Description |
|-------|---------|-------------|
| `log_requests` | `True` | Write request logs to D1 |
| `retention_request_days` | `90` | Request log TTL |
| `retention_event_days` | `90` | Connection event TTL |
| `retention_metric_days` | `30` | Connection metric TTL |
| `optimistic_lock_retries` | `3` | CAS retry attempts for connection state updates |

### Async Log Worker

| Field | Default | Description |
|-------|---------|-------------|
| `log_worker_batch_size` | `50` | Rows flushed per D1 batch call |
| `log_worker_flush_interval` | `5.0 s` | Max time between flushes |
| `log_worker_queue_size` | `2000` | In-memory queue cap (drops on overflow) |

---

## Architecture

```
grpc.aio server
    │
    ├─ ErrorHandlingInterceptor      — catches unhandled exceptions, returns INTERNAL
    ├─ JWTAuthInterceptor (optional) — validates Bearer token, sets GrpcUserContext
    └─ ObservabilityInterceptor      — metrics, structured logs, D1 request logging
           │
           └─ enqueue_log() ──► asyncio.Queue ──► D1LogWorker ──► Cloudflare D1
                                                  (batch 50 rows / 5s)
```

### Interceptor chain

The order is fixed and asserted at startup:

1. `ErrorHandlingInterceptor` — never wraps `request_iterator`, safe as first
2. `JWTAuthInterceptor` — sets `_grpc_user_var` ContextVar
3. `ObservabilityInterceptor` — reads `_grpc_user_var` for D1 log entries

### D1 tables

| Table | Purpose |
|-------|---------|
| `grpc_request_logs` | Per-request audit log (append-only, 2-row pattern) |
| `grpc_server_status` | Running server heartbeat (upsert) |
| `grpc_connection_states` | Machine connection state (CAS, optimistic locking) |
| `grpc_connection_events` | Connection event audit log (append-only) |
| `grpc_connection_metrics` | RTT / packet-loss time-series (append-only) |

Initialize tables with:

```bash
uv run manage.py create_grpc_d1_schema
```

---

## Connection State Management

The `connection_state` manager handles machine connect/disconnect/error transitions with
**optimistic CAS locking** (no SELECT FOR UPDATE — D1 does not support it).

```python
from django_cfg.modules.django_grpc.services.connection_state.manager import (
    amark_connected_safe,
    amark_disconnected_safe,
    amark_error_safe,
)

# In your streaming handler:
await amark_connected_safe(machine_id="bot-001", ip_address="1.2.3.4")
await amark_disconnected_safe(machine_id="bot-001")
await amark_error_safe(machine_id="bot-001", error_message="keepalive timeout")
```

First connection is auto-created (upsert). Retries use exponential backoff with
full jitter to avoid thundering-herd on mass reconnects.

---

## Streamlit Admin

When `streamlit_admin` is active, three pages are auto-registered under the **gRPC** group:

| Page | Content |
|------|---------|
| **gRPC Overview** | Request rate chart, KPI cards (total / success / error / avg latency), server status |
| **gRPC Connections** | Connection state table with status badges, event timeline per machine |
| **gRPC Request Logs** | Paginated log viewer with service / status filters |

Register in your Streamlit entry point:

```python
from django_cfg.modules.django_grpc.streamlit import auto_register
auto_register()
```

---

## Management Commands

| Command | Description |
|---------|-------------|
| `rungrpc` | Start the async gRPC server |
| `create_grpc_d1_schema` | Create / migrate D1 tables (idempotent) |
| `compile_proto` | Compile `.proto` files to Python |
| `generate_protos` | Generate `.proto` files from Django apps |
| `d1_logs` *(cross-module)* | Query `grpc_request_logs` / `grpc_server_status` — see [d1-logs guide](../django_cf/@docs/d1-logs.md) |

---

## Dependencies

**Required:**

- `grpcio` — gRPC core
- `grpcio-tools` — proto compilation
- `djangorestframework-simplejwt` — JWT token format
- `PyJWT` — token decoding (installed by simplejwt)
- `django-cf` module — Cloudflare D1 client

**Optional:**

- `grpcio-health-checking` — health check endpoint
- `grpcio-reflection` — server reflection / grpcurl support
- `betterproto` — alternative proto codegen
- `django_centrifugo` module — real-time event publishing
- `django_telegram` module — error alert notifications

---

## Go Client Example

```go
// OAuth 2.0 Device Flow → simplejwt access token → gRPC metadata
conn, _ := grpc.Dial(addr, grpc.WithPerRPCCredentials(tokenAuth{token: accessToken}))

type tokenAuth struct{ token string }
func (t tokenAuth) GetRequestMetadata(_ context.Context, _ ...string) (map[string]string, error) {
    return map[string]string{"authorization": "Bearer " + t.token}, nil
}
func (t tokenAuth) RequireTransportSecurity() bool { return false }
```
