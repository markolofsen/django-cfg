# Centrifugo Client Code Generation

Автоматическая генерация type-safe клиентов (Python, TypeScript, Go) для Centrifugo WebSocket RPC из Python обработчиков с Pydantic моделями.

## Quick Start

### 1. Создайте RPC Handler

```python
from pydantic import BaseModel, Field
from django_cfg.apps.centrifugo.decorators import websocket_rpc

class TaskStatsParams(BaseModel):
    user_id: str = Field(..., description="User ID")

class TaskStatsResult(BaseModel):
    total: int = Field(..., description="Total tasks")

@websocket_rpc("tasks.get_stats")
async def get_task_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
    """Get task statistics."""
    return TaskStatsResult(total=100)
```

### 2. Сгенерируйте Клиенты

```bash
python manage.py generate_centrifugo_clients --output ./clients --all
```

### 3. Используйте

**Python:**
```python
from clients.python import CentrifugoRPCClient, APIClient

rpc = CentrifugoRPCClient('ws://localhost:8000/connection/websocket', 'token', 'user-123')
await rpc.connect()

api = APIClient(rpc)
result = await api.tasks_get_stats(TaskStatsParams(user_id='user-123'))
```

**TypeScript:**
```typescript
import { CentrifugoRPCClient, APIClient } from './clients/typescript';

const rpc = new CentrifugoRPCClient('ws://...', 'token', 'user-123');
await rpc.connect();

const api = new APIClient(rpc);
const result = await api.tasksGetStats({ user_id: 'user-123' });
```

**Go:**
```go
api := NewAPIClient("ws://...", "token", "user-123")
api.Connect(ctx)

result, err := api.TasksGetStats(ctx, TaskStatsParams{UserId: "user-123"})
```

## Архитектура

```
@websocket_rpc Decorator
         ↓
    MessageRouter (runtime)
         +
    RPCRegistry (codegen)
         ↓
    Discovery (type extraction)
         ↓
    Generators (Python/TS/Go)
         ↓
Generated Clients (thin wrappers)
```

### Thin Wrapper Pattern

- **Base RPC Client**: WebSocket + correlation ID pattern
- **Typed API Client**: Thin wrapper с type-safe методами

### Correlation ID Pattern

```
Client → publish('rpc.requests', {method, params, correlation_id, reply_to})
       ← receive on user channel by correlation_id
```

## Структура

```
codegen/
├── README.md                           # Этот файл
├── USAGE.md                            # Полная документация
│
├── discovery.py                        # Type discovery из handlers
├── registry.py                         # RPCRegistry для metadata
├── router.py                           # MessageRouter
├── decorators.py                       # @websocket_rpc
│
├── utils/
│   ├── naming.py                       # Naming conventions
│   └── type_converter.py               # Pydantic → TS/Go types
│
└── generators/
    ├── python_thin/                    # Python generator
    │   ├── generator.py
    │   └── templates/
    │       ├── models.py.j2
    │       ├── rpc_client.py.j2
    │       ├── client.py.j2
    │       └── ...
    │
    ├── typescript_thin/                # TypeScript generator
    │   ├── generator.py
    │   └── templates/
    │       ├── types.ts.j2
    │       ├── rpc-client.ts.j2
    │       ├── client.ts.j2
    │       └── ...
    │
    └── go_thin/                        # Go generator
        ├── generator.py
        └── templates/
            ├── types.go.j2
            ├── rpc_client.go.j2
            ├── client.go.j2
            └── ...
```

## Features

✅ **Type Safety**: End-to-end type checking from Pydantic
✅ **Multi-Language**: Python, TypeScript, Go
✅ **Thin Wrappers**: Minimal boilerplate, легко кастомизировать
✅ **IDE Support**: Полный autocomplete и type hints
✅ **Async/Await**: Во всех языках
✅ **Error Handling**: Timeout, exceptions, context cancellation
✅ **Documentation**: Auto-generated README для каждого клиента

## Management Command

```bash
# Все языки
python manage.py generate_centrifugo_clients --output ./clients --all

# Конкретные языки
python manage.py generate_centrifugo_clients -o ./sdk --python --typescript

# С verbose
python manage.py generate_centrifugo_clients -o ./sdk --all --verbose

# Кастомный router
python manage.py generate_centrifugo_clients \
  -o ./sdk --all --router-path myapp.router.custom_router
```

### Опции

- `-o, --output` - Директория для клиентов (required)
- `--python` - Генерировать Python клиент
- `--typescript` - Генерировать TypeScript клиент
- `--go` - Генерировать Go клиент
- `--all` - Все языки
- `--router-path` - Кастомный MessageRouter (optional)
- `--verbose` - Verbose вывод

## Dependencies

### Core
- Django
- Pydantic 2.x
- Jinja2

### Generated Clients
- **Python**: `centrifuge` (официальная библиотека)
- **TypeScript**: `centrifuge` (npm package)
- **Go**: `github.com/centrifugal/centrifuge-go`

## Type Conversion

### Python → TypeScript
- `str` → `string`
- `int`, `float` → `number`
- `bool` → `boolean`
- `List[T]` → `T[]`
- `Dict[str, T]` → `{ [key: string]: T }`
- `Optional[T]` → `T | null`
- `BaseModel` → `interface`

### Python → Go
- `str` → `string`
- `int` → `int64`
- `float` → `float64`
- `bool` → `bool`
- `List[T]` → `[]T`
- `Dict[str, T]` → `map[string]T`
- `Optional[T]` → `*T`
- `BaseModel` → `struct`

## Examples

См. [USAGE.md](./USAGE.md) для:
- Полной документации
- Advanced usage
- Best practices
- Troubleshooting
- Real-world примеры

## Сравнение с django-ipc

| Feature                  | django-ipc              | centrifugo codegen      |
|--------------------------|-------------------------|-------------------------|
| Transport                | Direct WebSocket        | Centrifugo pub/sub      |
| Scale                    | Limited                 | 1M+ connections         |
| Architecture             | Bidirectional           | Correlation ID pattern  |
| Code reuse               | 90% reused              | 10% custom templates    |
| Type source              | Pydantic                | Pydantic                |
| Languages                | Python, TS, Go          | Python, TS, Go          |
| Pattern                  | Full client             | Thin wrapper            |

## Credits

Основано на архитектуре из `django-ipc/codegen`:
- Discovery механизм
- Naming conventions
- Type converters
- Generator базы

Адаптировано для Centrifugo с:
- Correlation ID pattern
- Pub/sub каналы
- Thin wrapper подход
- Новые templates

---

**Generated by django_cfg.apps.centrifugo.codegen**

Pydantic as Single Source of Truth ™️
