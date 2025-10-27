# Client Code Generation

Automatically generate type-safe clients for Python, TypeScript, and Go from your RPC handlers.

## Quick Start

### Generate All Clients

```bash
# From your Django project root
python manage.py generate_centrifugo_clients --output ./opensdk --all
```

Output:
```
Found 10 RPC methods
  - tasks.list: ListTasksParams -> TaskListResult
  - tasks.create: CreateTaskParams -> TaskResult
  - tasks.update: UpdateTaskParams -> TaskResult
  - tasks.delete: DeleteTaskParams -> SuccessResult
  ...

✓ Generated Python client
✓ Generated TypeScript client
✓ Generated Go client

Successfully generated 3 client(s)
```

### Generate Specific Languages

```bash
# Only Python
python manage.py generate_centrifugo_clients --output ./opensdk --python

# Only TypeScript
python manage.py generate_centrifugo_clients --output ./opensdk --typescript

# Only Go
python manage.py generate_centrifugo_clients --output ./opensdk --go

# Python + TypeScript
python manage.py generate_centrifugo_clients --output ./opensdk --python --typescript
```

## Integration with Workflow

### Using make api

The recommended way is to use the integrated `make api` command:

```bash
make api
```

This automatically:
1. Generates OpenAPI clients (HTTP REST)
2. **Generates Centrifugo clients (WebSocket RPC)**
3. Copies clients to frontend packages
4. Builds @api package

### Manual Integration

Add to your `generate_api.py`:

```python
# core/management/commands/generate_api.py
from django.core.management import call_command

def handle(self, *args, **options):
    # Step 1: OpenAPI clients
    call_command('generate_clients')

    # Step 2: Centrifugo clients
    call_command('generate_centrifugo_clients',
                output='./opensdk',
                all=True)

    # Step 3: Copy to frontend
    ...
```

## Generated File Structure

### Python Client

```
opensdk/python/
├── __init__.py          # Exports
├── models.py            # Pydantic models (generated)
├── rpc_client.py        # Base RPC client
├── client.py            # Typed API wrapper
├── requirements.txt     # centrifuge, pydantic
└── README.md            # Usage docs
```

**Dependencies:**
- `centrifuge` - Official Centrifugo Python client
- `pydantic>=2.0` - Type validation

### TypeScript Client

```
opensdk/typescript/
├── index.ts             # Exports
├── types.ts             # TypeScript interfaces
├── rpc-client.ts        # Base RPC client
├── client.ts            # Typed API wrapper
├── package.json         # centrifuge dependency
├── tsconfig.json        # TS config
└── README.md            # Usage docs
```

**Dependencies:**
- `centrifuge` - Official Centrifugo JS client

### Go Client

```
opensdk/go/
├── types.go             # Go structs
├── rpc_client.go        # Base RPC client
├── client.go            # Typed API wrapper
├── go.mod               # nhooyr.io/websocket v1.8.10
└── README.md            # Usage docs
```

**Dependencies:**
- `nhooyr.io/websocket v1.8.10` - **NO GitHub dependencies!**

## Type Conversion

### Python → TypeScript

| Python Type | TypeScript Type |
|-------------|-----------------|
| `str` | `string` |
| `int`, `float` | `number` |
| `bool` | `boolean` |
| `List[T]` | `T[]` |
| `Dict[str, T]` | `{ [key: string]: T }` |
| `Optional[T]` | `T \| null` |
| `BaseModel` | `interface` |

### Python → Go

| Python Type | Go Type |
|-------------|---------|
| `str` | `string` |
| `int` | `int64` |
| `float` | `float64` |
| `bool` | `bool` |
| `List[T]` | `[]T` |
| `Dict[str, T]` | `map[string]T` |
| `Optional[T]` | `*T` |
| `BaseModel` | `struct` |

## Naming Conventions

### Method Names

RPC method `tasks.get_stats` generates:

- **Python**: `api.tasks_get_stats(...)`
- **TypeScript**: `api.tasksGetStats(...)`
- **Go**: `api.TasksGetStats(ctx, ...)`

### Model Names

Python model `TaskStatsParams` generates:

- **Python**: `TaskStatsParams` (unchanged)
- **TypeScript**: `TaskStatsParams` (interface)
- **Go**: `TaskStatsParams` (struct)

## Generated Client Architecture

### Two-Layer Design

**Layer 1: Base RPC Client**
- Handles WebSocket connection
- Implements correlation ID pattern
- Publishes to `rpc.requests`
- Subscribes to `user#{user_id}`
- Matches responses by correlation_id

**Layer 2: Typed API Client**
- Thin wrapper over base client
- One type-safe method per RPC endpoint
- Automatic serialization/deserialization
- Full type checking

### Example Generated Code

**Python Client (`client.py`):**
```python
class APIClient:
    def __init__(self, rpc_client: CentrifugoRPCClient):
        self.rpc = rpc_client

    async def tasks_get_stats(
        self,
        params: TaskStatsParams
    ) -> TaskStatsResult:
        """Get task statistics for a user."""
        result = await self.rpc.call("tasks.get_stats", params.model_dump())
        return TaskStatsResult(**result)
```

**TypeScript Client (`client.ts`):**
```typescript
export class APIClient {
  constructor(private rpc: CentrifugoRPCClient) {}

  async tasksGetStats(params: TaskStatsParams): Promise<TaskStatsResult> {
    const result = await this.rpc.call('tasks.get_stats', params);
    return result as TaskStatsResult;
  }
}
```

**Go Client (`client.go`):**
```go
func (api *APIClient) TasksGetStats(
    ctx context.Context,
    params TaskStatsParams,
) (*TaskStatsResult, error) {
    result, err := api.rpc.Call(ctx, "tasks.get_stats", params)
    if err != nil {
        return nil, err
    }

    var response TaskStatsResult
    if err := json.Unmarshal(result, &response); err != nil {
        return nil, err
    }

    return &response, nil
}
```

## Special Features

### Go Client: No GitHub Dependencies

The Go client uses `nhooyr.io/websocket` instead of GitHub-hosted libraries:

**Why?**
- ✅ Better for enterprise proxies
- ✅ Air-gapped environment support
- ✅ Clean module path
- ✅ Minimal dependencies

**go.mod:**
```go
module example.com/centrifugo_client

require (
    nhooyr.io/websocket v1.8.10
)
```

**UUID Generation:**
Uses `crypto/rand` from stdlib (no external UUID library):

```go
func generateUUID() string {
    b := make([]byte, 16)
    rand.Read(b)
    b[6] = (b[6] & 0x0f) | 0x40 // Version 4
    b[8] = (b[8] & 0x3f) | 0x80 // Variant is 10
    return fmt.Sprintf("%x-%x-%x-%x-%x",
        b[0:4], b[4:6], b[6:8], b[8:10], b[10:16])
}
```

### TypeScript: Full Type Safety

Generated TypeScript clients have complete type safety:

```typescript
// Type checking at compile time
const params: TaskStatsParams = {
  user_id: "123",
  include_completed: true
};

const result: TaskStatsResult = await api.tasksGetStats(params);
//    ^-- TypeScript knows the exact type

console.log(result.total);      // ✅ OK
console.log(result.completed);  // ✅ OK
console.log(result.invalid);    // ❌ Compile error
```

### Python: Runtime Validation

Python clients use Pydantic for runtime validation:

```python
# Valid params
params = TaskStatsParams(user_id="123", include_completed=True)
result = await api.tasks_get_stats(params)

# Invalid params - raises ValidationError
params = TaskStatsParams(user_id=123)  # ❌ Wrong type
```

## Testing Generated Clients

### Python

```bash
cd opensdk/python
pip install -r requirements.txt
python -c "from client import APIClient; print('✓ Import OK')"
```

### TypeScript

```bash
cd opensdk/typescript
npm install
npx tsc --noEmit  # Check types
```

### Go

```bash
cd opensdk/go
go mod tidy
go build .        # Compile
go vet .          # Static analysis
```

## Continuous Integration

### GitHub Actions

```yaml
name: Generate Clients

on:
  push:
    paths:
      - 'core/centrifugo_handlers.py'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Generate Clients
        run: |
          python manage.py generate_centrifugo_clients --output ./opensdk --all

      - name: Test Go Client
        run: |
          cd opensdk/go
          go build .

      - name: Test TS Client
        run: |
          cd opensdk/typescript
          npm install
          npx tsc --noEmit

      - name: Commit Generated Clients
        run: |
          git add opensdk/
          git commit -m "chore: regenerate clients"
          git push
```

## Troubleshooting

### No Handlers Found

**Problem**: `Found 0 RPC methods`

**Solution**:
1. Verify handlers use `@websocket_rpc` decorator
2. Check handlers are imported in `apps.py`
3. Run Django shell:
   ```python
   from django_cfg.apps.centrifugo.router import get_message_router
   router = get_message_router()
   print(router._handlers.keys())
   ```

### Go Build Fails

**Problem**: `package nhooyr.io/websocket is not in GOROOT`

**Solution**:
```bash
cd opensdk/go
go mod tidy  # Download dependencies
```

### TypeScript Type Errors

**Problem**: `Property 'foo' does not exist`

**Solution**:
Regenerate clients after model changes:
```bash
python manage.py generate_centrifugo_clients --output ./opensdk --typescript
```

## Next Steps

- **[Frontend Guide](./frontend-guide.md)** - Use generated clients in your app
- **[Architecture](./architecture.md)** - Understand client internals
- **[API Reference](./api-reference.md)** - Complete API docs

---

:::tip[Generation Best Practices]
- ✅ Regenerate after handler changes
- ✅ Commit generated clients to git
- ✅ Test clients before deployment
- ✅ Version generated clients with your app
- ✅ Use CI/CD to auto-generate
:::
