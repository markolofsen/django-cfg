# API Reference

Complete API documentation for Centrifugo WebSocket RPC integration.

## Python API

### Decorator

#### `@websocket_rpc(method_name: str)`

Registers an async function as an RPC handler.

**Parameters:**
- `method_name` (str): RPC method name (e.g., `"tasks.get_stats"`)

**Example:**
```python
@websocket_rpc("tasks.get_stats")
async def get_task_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
    return TaskStatsResult(total=100)
```

**Handler Signature:**
```python
async def handler_name(
    conn: ConnectionContext,
    params: ParamsModel
) -> ResultModel:
    ...
```

### Client Classes

#### `CentrifugoRPCClient`

Base RPC client handling WebSocket and correlation IDs.

**Constructor:**
```python
CentrifugoRPCClient(
    url: str,
    token: str,
    user_id: str
)
```

**Methods:**

##### `async connect() -> None`

Establishes WebSocket connection and subscribes to user channel.

**Example:**
```python
await rpc.connect()
```

##### `async disconnect() -> None`

Closes WebSocket connection.

**Example:**
```python
await rpc.disconnect()
```

##### `async call(method: str, params: dict) -> dict`

Calls an RPC method with correlation ID pattern.

**Parameters:**
- `method` (str): RPC method name
- `params` (dict): Request parameters

**Returns:**
- `dict`: Response data

**Example:**
```python
result = await rpc.call("tasks.get_stats", {"user_id": "123"})
```

#### `APIClient`

Type-safe wrapper with generated methods.

**Constructor:**
```python
APIClient(rpc_client: CentrifugoRPCClient)
```

**Generated Methods:**

Each RPC handler generates a typed method:

```python
async def <method_name>(
    self,
    params: <ParamsModel>
) -> <ResultModel>
```

**Example:**
```python
api = APIClient(rpc)
result = await api.tasks_get_stats(TaskStatsParams(user_id="123"))
```

### Configuration

#### `DjangoCfgCentrifugoConfig`

Configuration model for Centrifugo integration.

**Parameters:**
- `enabled` (bool): Enable Centrifugo integration
- `wrapper_url` (str): Django wrapper service URL
- `wrapper_api_key` (str): Wrapper API key
- `centrifugo_url` (str): Centrifugo WebSocket URL
- `centrifugo_api_url` (str): Centrifugo HTTP API URL
- `centrifugo_api_key` (str): Centrifugo API key
- `centrifugo_token_hmac_secret` (str): HMAC secret for JWT
- `ack_timeout` (int, optional): RPC timeout in seconds (default: 30)
- `log_level` (str, optional): Logging level (default: "INFO")
- `log_all_calls` (bool, optional): Log all RPC calls (default: True)
- `log_only_with_ack` (bool, optional): Log only ack calls (default: False)

**Example:**
```python
centrifugo: DjangoCfgCentrifugoConfig = DjangoCfgCentrifugoConfig(
    enabled=True,
    wrapper_url="http://localhost:8001",
    wrapper_api_key="secret-key",
    centrifugo_url="ws://localhost:8000/connection/websocket",
    centrifugo_api_url="http://localhost:8000/api",
    centrifugo_api_key="api-key",
    centrifugo_token_hmac_secret="hmac-secret",
    ack_timeout=60,
    log_level="DEBUG"
)
```

---

## TypeScript API

### Client Classes

#### `CentrifugoRPCClient`

Base RPC client.

**Constructor:**
```typescript
constructor(
    url: string,
    token: string,
    userId: string
)
```

**Methods:**

##### `async connect(): Promise<void>`

Connects to Centrifugo.

**Example:**
```typescript
await rpc.connect();
```

##### `disconnect(): void`

Disconnects from Centrifugo.

**Example:**
```typescript
rpc.disconnect();
```

##### `async call(method: string, params: any): Promise<any>`

Calls RPC method.

**Parameters:**
- `method` (string): RPC method name
- `params` (any): Request parameters

**Returns:**
- `Promise<any>`: Response data

**Example:**
```typescript
const result = await rpc.call('tasks.get_stats', { user_id: '123' });
```

#### `APIClient`

Type-safe API wrapper.

**Constructor:**
```typescript
constructor(rpc: CentrifugoRPCClient)
```

**Generated Methods:**

```typescript
async <methodName>(params: <ParamsType>): Promise<ResultType>
```

**Example:**
```typescript
const api = new APIClient(rpc);
const result = await api.tasksGetStats({ user_id: '123' });
```

### Type Interfaces

Generated TypeScript interfaces from Pydantic models:

```typescript
interface TaskStatsParams {
  user_id: string;
  include_completed?: boolean;
}

interface TaskStatsResult {
  total: number;
  completed: number;
  pending: number;
}
```

---

## Go API

### Client Struct

#### `APIClient`

Combined RPC and API client.

**Constructor:**
```go
func NewAPIClient(url, token, userID string) *APIClient
```

**Methods:**

##### `func (c *APIClient) Connect(ctx context.Context) error`

Connects to Centrifugo.

**Example:**
```go
err := client.Connect(ctx)
```

##### `func (c *APIClient) Disconnect()`

Disconnects from Centrifugo.

**Example:**
```go
defer client.Disconnect()
```

##### `func (c *APIClient) Call(ctx context.Context, method string, params interface{}) ([]byte, error)`

Calls RPC method.

**Parameters:**
- `ctx` (context.Context): Context for timeout/cancellation
- `method` (string): RPC method name
- `params` (interface{}): Request parameters

**Returns:**
- `[]byte`: Response JSON
- `error`: Error if any

**Example:**
```go
result, err := client.Call(ctx, "tasks.get_stats", params)
```

### Generated Methods

Each handler generates a typed method:

```go
func (api *APIClient) <MethodName>(
    ctx context.Context,
    params <ParamsStruct>
) (*<ResultStruct>, error)
```

**Example:**
```go
result, err := api.TasksGetStats(ctx, TaskStatsParams{
    UserId: "123",
    IncludeCompleted: true,
})
```

### Type Structs

Generated Go structs from Pydantic models:

```go
type TaskStatsParams struct {
    UserId           string `json:"user_id"`
    IncludeCompleted bool   `json:"include_completed"`
}

type TaskStatsResult struct {
    Total     int64 `json:"total"`
    Completed int64 `json:"completed"`
    Pending   int64 `json:"pending"`
}
```

---

## Management Commands

### `generate_centrifugo_clients`

Generates type-safe clients from RPC handlers.

**Usage:**
```bash
python manage.py generate_centrifugo_clients [OPTIONS]
```

**Options:**
- `--output DIR`: Output directory (required)
- `--all`: Generate all clients (Python, TypeScript, Go)
- `--python`: Generate Python client
- `--typescript`: Generate TypeScript client
- `--go`: Generate Go client
- `--verbose`: Verbose output

**Examples:**
```bash
# All clients
python manage.py generate_centrifugo_clients --output ./opensdk --all

# Specific languages
python manage.py generate_centrifugo_clients --output ./opensdk --python --typescript

# With verbose output
python manage.py generate_centrifugo_clients --output ./opensdk --all --verbose
```

---

## Error Handling

### Python Exceptions

```python
# Validation errors
from pydantic import ValidationError

try:
    params = TaskStatsParams(user_id=123)  # Wrong type
except ValidationError as e:
    print(e)

# Connection errors
try:
    await rpc.connect()
except ConnectionError as e:
    print(f"Failed to connect: {e}")

# RPC errors
try:
    result = await api.tasks_get_stats(params)
except ValueError as e:
    print(f"RPC error: {e}")
```

### TypeScript Errors

```typescript
// Connection errors
try {
  await rpc.connect();
} catch (error) {
  console.error('Connection failed:', error);
}

// RPC errors
try {
  const result = await api.tasksGetStats(params);
} catch (error) {
  if (error.code) {
    console.error(`RPC error ${error.code}: ${error.message}`);
  }
}
```

### Go Errors

```go
// Connection errors
if err := client.Connect(ctx); err != nil {
    log.Fatalf("Connection failed: %v", err)
}

// RPC errors
result, err := api.TasksGetStats(ctx, params)
if err != nil {
    if rpcErr, ok := err.(*RPCError); ok {
        log.Printf("RPC error %d: %s", rpcErr.Code, rpcErr.Message)
    } else {
        log.Printf("Error: %v", err)
    }
}
```

---

## Environment Variables

Recommended environment variable names:

```bash
# Centrifugo server
CENTRIFUGO_URL=ws://localhost:8000/connection/websocket
CENTRIFUGO_API_URL=http://localhost:8000/api
CENTRIFUGO_API_KEY=your-api-key
CENTRIFUGO_TOKEN_HMAC_SECRET=your-hmac-secret

# Django wrapper
CENTRIFUGO_WRAPPER_URL=http://localhost:8001
CENTRIFUGO_WRAPPER_API_KEY=your-wrapper-key

# Behavior
CENTRIFUGO_ACK_TIMEOUT=30
CENTRIFUGO_LOG_LEVEL=INFO
CENTRIFUGO_LOG_ALL_CALLS=true
```

---

## Next Steps

- **[Setup Guide](./setup.md)** - Installation and configuration
- **[Backend Guide](./backend-guide.md)** - Create RPC handlers
- **[Frontend Guide](./frontend-guide.md)** - Use clients in your app
