# Centrifugo Client Code Generation - Usage Guide

## Overview

Автоматическая генерация type-safe клиентов для Centrifugo WebSocket RPC из Python обработчиков.

**Архитектура:**
- Используется Pydantic как единый источник правды
- Декоратор `@websocket_rpc` регистрирует обработчики
- Discovery извлекает типы из сигнатур функций
- Генераторы создают тонкие обёртки над базовыми RPC клиентами

## Quick Start

### 1. Создайте RPC Handler

```python
# myapp/handlers.py
from pydantic import BaseModel, Field
from django_cfg.apps.centrifugo.decorators import websocket_rpc

class TaskStatsParams(BaseModel):
    user_id: str = Field(..., description="User ID")
    limit: int = Field(10, description="Max results")

class TaskStatsResult(BaseModel):
    total: int = Field(..., description="Total tasks")
    completed: int = Field(..., description="Completed tasks")

@websocket_rpc("tasks.get_stats")
async def get_task_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
    """Get task statistics for user."""
    # Ваша бизнес-логика
    return TaskStatsResult(total=100, completed=75)
```

### 2. Импортируйте Handlers в AppConfig

```python
# myapp/apps.py
class MyAppConfig(AppConfig):
    def ready(self):
        # Импортируйте handlers чтобы декораторы сработали
        from . import handlers
```

### 3. Сгенерируйте Клиенты

```bash
# Все языки
python manage.py generate_centrifugo_clients --output ./clients --all

# Только Python
python manage.py generate_centrifugo_clients --output ./clients --python

# Только TypeScript
python manage.py generate_centrifugo_clients --output ./clients --typescript

# Только Go
python manage.py generate_centrifugo_clients --output ./clients --go

# С verbose выводом
python manage.py generate_centrifugo_clients --output ./clients --all --verbose
```

### 4. Используйте Сгенерированные Клиенты

**Python:**
```python
from clients.python import CentrifugoRPCClient, APIClient
from clients.python.models import TaskStatsParams

async def main():
    rpc = CentrifugoRPCClient(
        url='ws://localhost:8000/connection/websocket',
        token='jwt-token',
        user_id='user-123'
    )
    await rpc.connect()

    api = APIClient(rpc)
    result = await api.tasks_get_stats(
        TaskStatsParams(user_id='user-123', limit=10)
    )
    print(f"Total: {result.total}, Completed: {result.completed}")

    await rpc.disconnect()
```

**TypeScript:**
```typescript
import { CentrifugoRPCClient, APIClient } from './clients/typescript';
import type { TaskStatsParams } from './clients/typescript';

const rpc = new CentrifugoRPCClient(
  'ws://localhost:8000/connection/websocket',
  'jwt-token',
  'user-123'
);
await rpc.connect();

const api = new APIClient(rpc);
const result = await api.tasksGetStats({
  user_id: 'user-123',
  limit: 10
});
console.log(`Total: ${result.total}, Completed: ${result.completed}`);

await rpc.disconnect();
```

**Go:**
```go
import (
    "context"
    client "path/to/clients/go"
)

func main() {
    ctx := context.Background()
    api := client.NewAPIClient(
        "ws://localhost:8000/connection/websocket",
        "jwt-token",
        "user-123",
    )

    if err := api.Connect(ctx); err != nil {
        log.Fatal(err)
    }
    defer api.Disconnect()

    result, err := api.TasksGetStats(ctx, client.TaskStatsParams{
        UserId: "user-123",
        Limit:  10,
    })
    if err != nil {
        log.Fatal(err)
    }

    fmt.Printf("Total: %d, Completed: %d\n", result.Total, result.Completed)
}
```

## Декоратор @websocket_rpc

### Базовое Использование

```python
from django_cfg.apps.centrifugo.decorators import websocket_rpc
from pydantic import BaseModel

class MyParams(BaseModel):
    name: str

class MyResult(BaseModel):
    message: str

@websocket_rpc("my.method")
async def my_handler(conn, params: MyParams) -> MyResult:
    """Handler docstring (будет в генерируемых клиентах)."""
    return MyResult(message=f"Hello {params.name}")
```

### Регистрация

Декоратор автоматически регистрирует обработчик в:
1. **MessageRouter** - для runtime обработки сообщений
2. **RPCRegistry** - для code generation (discovery)

### Type Hints

Обязательно указывайте типы:
- `params: YourParamsModel` - Pydantic модель параметров
- `-> YourResultModel` - Pydantic модель результата

Discovery извлекает эти типы для генерации клиентов.

## Архитектура Генераторов

### Thin Wrapper Pattern

Генерируется 2 слоя:

1. **Base RPC Client** (`rpc_client.py/ts/go`)
   - Управляет WebSocket соединением
   - Реализует correlation ID pattern
   - Отправляет запросы на канал `rpc.requests`
   - Получает ответы на канал `user#{user_id}`
   - Мэтчит ответы по correlation_id

2. **Typed API Client** (`client.py/ts/go`)
   - Тонкая обёртка над base client
   - Type-safe методы для каждого RPC endpoint
   - Автоматическая сериализация/десериализация
   - IDE autocomplete, type checking

### Correlation ID Pattern

```
Client                           Centrifugo                    Server
  |                                   |                           |
  |-- publish('rpc.requests') ------->|                           |
  |   {                               |                           |
  |     method: 'tasks.get_stats',    |                           |
  |     params: {...},                |                           |
  |     correlation_id: 'uuid-123',   |                           |
  |     reply_to: 'user#123'          |                           |
  |   }                               |                           |
  |                                   |-- subscribe to channel -->|
  |                                   |                           |
  |                                   |<-- publish to user#123 ---|
  |<-- receive on user#123 -----------|   {                       |
  |    {                              |     correlation_id: ...   |
  |      correlation_id: 'uuid-123',  |     result: {...}         |
  |      result: {...}                |   }                       |
  |    }                              |                           |
```

## Структура Сгенерированных Файлов

### Python Client

```
clients/python/
├── __init__.py          # Exports: CentrifugoRPCClient, APIClient, models
├── models.py            # Pydantic models
├── rpc_client.py        # CentrifugoRPCClient (base)
├── client.py            # APIClient (thin wrapper)
├── requirements.txt     # Dependencies: centrifuge, pydantic
└── README.md            # Usage documentation
```

### TypeScript Client

```
clients/typescript/
├── index.ts             # Exports: CentrifugoRPCClient, APIClient, types
├── types.ts             # TypeScript interfaces
├── rpc-client.ts        # CentrifugoRPCClient (base)
├── client.ts            # APIClient (thin wrapper)
├── package.json         # Dependencies: centrifuge
├── tsconfig.json        # TypeScript config
└── README.md            # Usage documentation
```

### Go Client

```
clients/go/
├── types.go             # Go structs
├── rpc_client.go        # CentrifugoRPCClient (base)
├── client.go            # APIClient (thin wrapper)
├── go.mod               # Dependencies: centrifuge-go
└── README.md            # Usage documentation
```

## Management Command

### Опции

```bash
python manage.py generate_centrifugo_clients \
  --output ./clients \          # Директория для клиентов (обязательно)
  --python \                    # Генерировать Python клиент
  --typescript \                # Генерировать TypeScript клиент
  --go \                        # Генерировать Go клиент
  --all \                       # Генерировать все клиенты
  --router-path myapp.router \  # Кастомный router (опционально)
  --verbose                     # Verbose вывод
```

### Примеры

```bash
# Все языки с verbose
python manage.py generate_centrifugo_clients -o ./sdk --all --verbose

# Только Python и TypeScript
python manage.py generate_centrifugo_clients -o ./sdk --python --typescript

# Кастомный router
python manage.py generate_centrifugo_clients \
  -o ./sdk \
  --all \
  --router-path myapp.custom_router.router
```

### Вывод

```
Centrifugo Client Code Generation
============================================================
Using global MessageRouter

Discovering RPC methods...
Found 3 RPC methods
  - tasks.get_stats: TaskStatsParams -> TaskStats
  - users.get_profile: UserProfileParams -> UserProfile
  - notifications.send: NotificationParams -> NotificationResult

Output directory: ./clients

Generating Python client...
  ✓ Generated at: ./clients/python

Generating TypeScript client...
  ✓ Generated at: ./clients/typescript

Generating Go client...
  ✓ Generated at: ./clients/go

============================================================
Successfully generated 3 client(s): Python, TypeScript, Go

Next steps:
  cd ./clients/python && pip install -r requirements.txt
  cd ./clients/typescript && npm install
  cd ./clients/go && go mod tidy
```

## Advanced Usage

### Кастомный Router

```python
# myapp/routers.py
from django_cfg.apps.centrifugo.router import MessageRouter

custom_router = MessageRouter()

@custom_router.register("custom.method")
async def custom_handler(conn, params):
    return {"result": "custom"}
```

Затем:
```bash
python manage.py generate_centrifugo_clients \
  --output ./clients \
  --all \
  --router-path myapp.routers.custom_router
```

### Optional Fields

Pydantic опциональные поля → nullable в клиентах:

```python
class Params(BaseModel):
    required: str
    optional: Optional[str] = None
```

TypeScript:
```typescript
interface Params {
  required: string;
  optional?: string | null;
}
```

Go:
```go
type Params struct {
    Required string  `json:"required"`
    Optional *string `json:"optional"`
}
```

### Nested Models

```python
class Address(BaseModel):
    city: str
    country: str

class User(BaseModel):
    name: str
    address: Address
```

Автоматически генерируются все nested модели.

### List/Dict Fields

```python
class Data(BaseModel):
    tags: List[str]
    metadata: Dict[str, Any]
```

TypeScript:
```typescript
interface Data {
  tags: string[];
  metadata: { [key: string]: any };
}
```

Go:
```go
type Data struct {
    Tags     []string               `json:"tags"`
    Metadata map[string]interface{} `json:"metadata"`
}
```

## Type Conversion

### Python → TypeScript

| Python                | TypeScript              |
|-----------------------|-------------------------|
| `str`                 | `string`                |
| `int`, `float`        | `number`                |
| `bool`                | `boolean`               |
| `List[T]`             | `T[]`                   |
| `Dict[str, T]`        | `{ [key: string]: T }`  |
| `Optional[T]`         | `T \| null`             |
| `datetime`            | `string` (ISO 8601)     |
| `BaseModel`           | `interface`             |

### Python → Go

| Python                | Go                      |
|-----------------------|-------------------------|
| `str`                 | `string`                |
| `int`                 | `int64`                 |
| `float`               | `float64`               |
| `bool`                | `bool`                  |
| `List[T]`             | `[]T`                   |
| `Dict[str, T]`        | `map[string]T`          |
| `Optional[T]`         | `*T`                    |
| `datetime`            | `time.Time`             |
| `BaseModel`           | `struct`                |

## Best Practices

### 1. Используйте Field с description

```python
class Params(BaseModel):
    user_id: str = Field(..., description="User ID to fetch")
    limit: int = Field(10, description="Maximum results")
```

Генерирует комментарии в клиентах:
```typescript
interface Params {
  /** User ID to fetch */
  user_id: string;
  /** Maximum results */
  limit?: number;
}
```

### 2. Добавляйте Docstrings

```python
@websocket_rpc("users.get")
async def get_user(conn, params: GetUserParams) -> User:
    """
    Get user by ID.

    Retrieves full user profile including permissions and settings.
    """
    ...
```

Docstring попадает в README клиентов.

### 3. Версионирование API

```python
@websocket_rpc("users.v2.get")
async def get_user_v2(conn, params: GetUserParamsV2) -> UserV2:
    """Get user (API v2)."""
    ...
```

### 4. Namespace Methods

```python
@websocket_rpc("tasks.list")
@websocket_rpc("tasks.create")
@websocket_rpc("tasks.update")
@websocket_rpc("tasks.delete")
```

Генерирует:
```python
api.tasks_list(...)
api.tasks_create(...)
api.tasks_update(...)
api.tasks_delete(...)
```

### 5. Error Handling

```python
class ErrorResult(BaseModel):
    error: str
    code: str

@websocket_rpc("tasks.get")
async def get_task(conn, params: GetTaskParams) -> TaskResult:
    if not task_exists(params.task_id):
        raise ValueError("Task not found")
    return TaskResult(...)
```

Клиент получит exception:
```python
try:
    result = await api.tasks_get(params)
except Exception as e:
    print(f"Error: {e}")
```

## Troubleshooting

### No RPC methods found

Проблема: `Found 0 RPC methods`

Решение:
1. Проверьте что handlers импортированы в `AppConfig.ready()`
2. Проверьте что используется `@websocket_rpc` декоратор
3. Проверьте type hints на параметрах и return

### Type conversion errors

Проблема: Неправильная конвертация типов

Решение:
- Используйте только Pydantic BaseModel для params/result
- Избегайте Union types (кроме Optional)
- Используйте стандартные типы (str, int, float, bool, List, Dict)

### Import errors in generated code

Проблема: Generated code не импортирует правильно

Решение:
- Убедитесь что все Pydantic модели имеют уникальные имена
- Проверьте что nested модели тоже BaseModel
- Regenerate clients после изменения моделей

## Примеры

### Real-Time Notifications

```python
# Handler
@websocket_rpc("notifications.subscribe")
async def subscribe_notifications(conn, params: SubscribeParams) -> SubscriptionResult:
    """Subscribe to user notifications."""
    # Subscribe logic
    return SubscriptionResult(subscription_id="sub-123")

# Python client
result = await api.notifications_subscribe(
    SubscribeParams(user_id="user-123", topics=["orders", "messages"])
)
print(f"Subscribed: {result.subscription_id}")
```

### Batch Operations

```python
# Handler
class BatchTaskParams(BaseModel):
    task_ids: List[str]

class BatchTaskResult(BaseModel):
    results: List[TaskStatus]

@websocket_rpc("tasks.batch_status")
async def batch_task_status(conn, params: BatchTaskParams) -> BatchTaskResult:
    """Get status for multiple tasks."""
    statuses = [get_task_status(tid) for tid in params.task_ids]
    return BatchTaskResult(results=statuses)

# TypeScript client
const result = await api.tasksBatchStatus({
  task_ids: ['task-1', 'task-2', 'task-3']
});
result.results.forEach(status => console.log(status));
```

### Streaming Data

```python
# Handler
@websocket_rpc("data.stream")
async def stream_data(conn, params: StreamParams) -> StreamResult:
    """Start data stream."""
    # Initialize stream
    return StreamResult(stream_id="stream-123", channel="data.stream.123")

# Go client
result, err := api.DataStream(ctx, StreamParams{
    Source: "sensors",
    Limit:  1000,
})
if err != nil {
    log.Fatal(err)
}
fmt.Printf("Stream ID: %s, Channel: %s\n", result.StreamId, result.Channel)
```

## См. также

- [Centrifugo Documentation](https://centrifugal.dev/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [django-ipc (original inspiration)](../../../django-ipc/)
