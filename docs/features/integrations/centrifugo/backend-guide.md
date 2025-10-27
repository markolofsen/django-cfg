# Backend Developer Guide

Learn how to create type-safe RPC handlers using Pydantic models and the `@websocket_rpc` decorator.

## Creating Your First Handler

### 1. Define Pydantic Models

Create request and response models using Pydantic v2:

```python
# core/centrifugo_handlers.py
from pydantic import BaseModel, Field
from typing import List, Optional

class TaskStatsParams(BaseModel):
    """Request parameters for task statistics."""
    user_id: str = Field(..., description="User ID to fetch stats for")
    include_completed: bool = Field(True, description="Include completed tasks")

class TaskStatsResult(BaseModel):
    """Task statistics response."""
    total: int = Field(..., description="Total number of tasks")
    completed: int = Field(..., description="Number of completed tasks")
    pending: int = Field(..., description="Number of pending tasks")
    user_id: str = Field(..., description="User ID")
```

### 2. Create RPC Handler

Use the `@websocket_rpc` decorator to register your handler:

```python
from django_cfg.apps.centrifugo.decorators import websocket_rpc

@websocket_rpc("tasks.get_stats")
async def get_task_stats(conn, params: TaskStatsParams) -> TaskStatsResult:
    """
    Get task statistics for a user.

    This handler retrieves comprehensive task statistics including
    total, completed, and pending task counts.
    """
    from apps.tasks.models import Task

    # Use params as Pydantic model
    user_id = params.user_id

    # Query database
    total = Task.objects.filter(user_id=user_id).count()
    completed = Task.objects.filter(user_id=user_id, status='completed').count()
    pending = total - completed

    # Return Pydantic model
    return TaskStatsResult(
        total=total,
        completed=completed,
        pending=pending,
        user_id=user_id
    )
```

### 3. Register Handlers

Import handlers in your `AppConfig.ready()`:

```python
# core/apps.py
from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = "core"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Import handlers to register them with the router."""
        from . import centrifugo_handlers
```

## Handler Best Practices

### Use Type Hints

Type hints are **required** - they drive code generation:

```python
# ✅ GOOD - Pydantic models with type hints
@websocket_rpc("user.get")
async def get_user(conn, params: GetUserParams) -> UserResult:
    ...

# ❌ BAD - No type hints
@websocket_rpc("user.get")
async def get_user(conn, params):
    ...
```

### Add Field Descriptions

Descriptions appear in generated client documentation:

```python
class UserParams(BaseModel):
    user_id: str = Field(..., description="Unique user identifier")
    include_profile: bool = Field(
        True,
        description="Include full profile data in response"
    )
```

Generates TypeScript documentation:

```typescript
interface UserParams {
  /** Unique user identifier */
  user_id: string;
  /** Include full profile data in response */
  include_profile?: boolean;
}
```

### Write Handler Docstrings

Docstrings appear in README files:

```python
@websocket_rpc("tasks.create")
async def create_task(conn, params: CreateTaskParams) -> TaskResult:
    """
    Create a new task.

    Creates a task for the specified user with the given title and description.
    Automatically sets created_at timestamp and initializes status to 'pending'.

    Returns the created task with its generated ID.
    """
    ...
```

### Use Async Handlers

All handlers **must** be async:

```python
# ✅ GOOD
@websocket_rpc("tasks.list")
async def list_tasks(conn, params: ListParams) -> ListResult:
    tasks = await Task.objects.filter(user_id=params.user_id).alist()
    return ListResult(tasks=[...])

# ❌ BAD - sync handler
@websocket_rpc("tasks.list")
def list_tasks(conn, params: ListParams) -> ListResult:
    ...
```

## Naming Conventions

### Method Names

Use dot notation for namespacing:

```python
@websocket_rpc("tasks.list")       # List tasks
@websocket_rpc("tasks.create")     # Create task
@websocket_rpc("tasks.update")     # Update task
@websocket_rpc("tasks.delete")     # Delete task

@websocket_rpc("users.get")        # Get user
@websocket_rpc("users.profile")    # Get user profile

@websocket_rpc("system.health")    # System health check
@websocket_rpc("system.stats")     # System statistics
```

This generates organized client methods:

```python
# Python
api.tasks_list(...)
api.tasks_create(...)
api.users_get(...)
api.system_health(...)
```

```typescript
// TypeScript
api.tasksList(...)
api.tasksCreate(...)
api.usersGet(...)
api.systemHealth(...)
```

```go
// Go
api.TasksList(ctx, ...)
api.TasksCreate(ctx, ...)
api.UsersGet(ctx, ...)
api.SystemHealth(ctx, ...)
```

### Model Names

Follow these conventions:

```python
# Request models: <Action><Entity>Params
class CreateTaskParams(BaseModel): ...
class UpdateUserParams(BaseModel): ...
class ListTasksParams(BaseModel): ...

# Response models: <Entity>Result or <Action><Entity>Result
class TaskResult(BaseModel): ...
class UserResult(BaseModel): ...
class TaskListResult(BaseModel): ...
```

## Advanced Patterns

### Optional Parameters

Use `Optional` for optional fields:

```python
from typing import Optional

class SearchParams(BaseModel):
    query: str = Field(..., description="Search query")
    limit: Optional[int] = Field(None, description="Max results")
    offset: Optional[int] = Field(None, description="Result offset")
```

Generates:

```typescript
interface SearchParams {
  query: string;
  limit?: number | null;
  offset?: number | null;
}
```

### Lists and Nested Models

Use `List` for arrays and nest models:

```python
from typing import List

class Tag(BaseModel):
    name: str
    color: str

class Task(BaseModel):
    id: int
    title: str
    tags: List[Tag]

class TaskListResult(BaseModel):
    tasks: List[Task]
    total: int
```

Generates:

```typescript
interface Tag {
  name: string;
  color: string;
}

interface Task {
  id: number;
  title: string;
  tags: Tag[];
}

interface TaskListResult {
  tasks: Task[];
  total: number;
}
```

### Using Connection Object

The `conn` parameter provides access to connection metadata:

```python
@websocket_rpc("user.profile")
async def get_profile(conn, params: ProfileParams) -> ProfileResult:
    # Access user from connection
    user_id = conn.user_id  # From JWT token

    # Use in business logic
    profile = await UserProfile.objects.get(user_id=user_id)

    return ProfileResult(
        username=profile.username,
        email=profile.email
    )
```

### Error Handling

Raise exceptions for error cases:

```python
from django.core.exceptions import ObjectDoesNotExist

@websocket_rpc("tasks.get")
async def get_task(conn, params: GetTaskParams) -> TaskResult:
    try:
        task = await Task.objects.aget(id=params.task_id)
        return TaskResult(...)
    except ObjectDoesNotExist:
        raise ValueError(f"Task {params.task_id} not found")
```

Clients receive error responses:

```python
try:
    result = await api.tasks_get(GetTaskParams(task_id=999))
except Exception as e:
    print(f"Error: {e}")  # "Task 999 not found"
```

### Database Queries

Use Django ORM async methods:

```python
@websocket_rpc("tasks.list")
async def list_tasks(conn, params: ListParams) -> ListResult:
    # Async query
    tasks = await Task.objects.filter(
        user_id=params.user_id
    ).order_by('-created_at').alist()

    # Transform to Pydantic
    task_list = [
        TaskItem(id=t.id, title=t.title, status=t.status)
        for t in tasks
    ]

    return ListResult(tasks=task_list, total=len(task_list))
```

## Testing Handlers

### Unit Tests

Test handlers directly:

```python
# core/tests/test_centrifugo_handlers.py
import pytest
from core.centrifugo_handlers import get_task_stats, TaskStatsParams

@pytest.mark.asyncio
async def test_get_task_stats():
    # Create test data
    user = await User.objects.acreate(username="test")
    await Task.objects.acreate(user=user, status="completed")
    await Task.objects.acreate(user=user, status="pending")

    # Call handler
    result = await get_task_stats(
        conn=None,  # Mock connection
        params=TaskStatsParams(user_id=user.id)
    )

    # Assert results
    assert result.total == 2
    assert result.completed == 1
    assert result.pending == 1
```

### Integration Tests

Test with generated clients:

```python
@pytest.mark.asyncio
async def test_rpc_client_integration():
    from opensdk.python import CentrifugoRPCClient, APIClient

    # Setup client
    rpc = CentrifugoRPCClient(
        url=settings.CENTRIFUGO_URL,
        token=generate_test_token(),
        user_id="test-user"
    )
    await rpc.connect()

    api = APIClient(rpc)

    # Call RPC method
    result = await api.tasks_get_stats(TaskStatsParams(user_id="test-user"))

    # Verify
    assert result.total >= 0
    assert result.completed >= 0
```

## Complete Example

Here's a complete CRUD example for a Todo app:

```python
# core/centrifugo_handlers.py
from pydantic import BaseModel, Field
from typing import List, Optional
from django_cfg.apps.centrifugo.decorators import websocket_rpc
from apps.todos.models import Todo

# ========================================
# Models
# ========================================

class TodoItem(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: str

class CreateTodoParams(BaseModel):
    title: str = Field(..., description="Todo title")

class UpdateTodoParams(BaseModel):
    id: int = Field(..., description="Todo ID")
    title: Optional[str] = Field(None, description="New title")
    completed: Optional[bool] = Field(None, description="Completion status")

class DeleteTodoParams(BaseModel):
    id: int = Field(..., description="Todo ID to delete")

class ListTodosParams(BaseModel):
    completed: Optional[bool] = Field(None, description="Filter by completion")
    limit: Optional[int] = Field(10, description="Max results")

class TodoResult(BaseModel):
    todo: TodoItem

class TodoListResult(BaseModel):
    todos: List[TodoItem]
    total: int

class SuccessResult(BaseModel):
    success: bool
    message: str

# ========================================
# Handlers
# ========================================

@websocket_rpc("todos.create")
async def create_todo(conn, params: CreateTodoParams) -> TodoResult:
    """Create a new todo item."""
    todo = await Todo.objects.acreate(
        user_id=conn.user_id,
        title=params.title,
        completed=False
    )

    return TodoResult(
        todo=TodoItem(
            id=todo.id,
            title=todo.title,
            completed=todo.completed,
            created_at=todo.created_at.isoformat()
        )
    )

@websocket_rpc("todos.update")
async def update_todo(conn, params: UpdateTodoParams) -> TodoResult:
    """Update an existing todo item."""
    todo = await Todo.objects.aget(id=params.id, user_id=conn.user_id)

    if params.title is not None:
        todo.title = params.title
    if params.completed is not None:
        todo.completed = params.completed

    await todo.asave()

    return TodoResult(
        todo=TodoItem(
            id=todo.id,
            title=todo.title,
            completed=todo.completed,
            created_at=todo.created_at.isoformat()
        )
    )

@websocket_rpc("todos.delete")
async def delete_todo(conn, params: DeleteTodoParams) -> SuccessResult:
    """Delete a todo item."""
    await Todo.objects.filter(id=params.id, user_id=conn.user_id).adelete()

    return SuccessResult(
        success=True,
        message=f"Todo {params.id} deleted"
    )

@websocket_rpc("todos.list")
async def list_todos(conn, params: ListTodosParams) -> TodoListResult:
    """List todos with optional filtering."""
    query = Todo.objects.filter(user_id=conn.user_id)

    if params.completed is not None:
        query = query.filter(completed=params.completed)

    query = query.order_by('-created_at')[:params.limit]
    todos = await query.alist()

    todo_items = [
        TodoItem(
            id=t.id,
            title=t.title,
            completed=t.completed,
            created_at=t.created_at.isoformat()
        )
        for t in todos
    ]

    return TodoListResult(
        todos=todo_items,
        total=len(todo_items)
    )
```

## Next Steps

- **[Client Generation](./client-generation.md)** - Generate type-safe clients
- **[Frontend Guide](./frontend-guide.md)** - Use clients in your frontend
- **[API Reference](./api-reference.md)** - Complete API documentation

---

:::tip[Handler Checklist]
Before generating clients:
- ✅ All handlers use Pydantic models
- ✅ Type hints on all parameters and returns
- ✅ Descriptive field descriptions
- ✅ Handler docstrings written
- ✅ Handlers are async
- ✅ Handlers registered in apps.py
:::
