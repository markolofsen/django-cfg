# DRF-Spectacular: Array Responses in ViewSet @action Methods

## Problem

When using `@action` decorators in DRF viewsets with `many=True` serializers, drf-spectacular fails to generate correct OpenAPI schemas showing array responses. Instead, it generates single object references.

## Symptoms

1. **OpenAPI Schema Issue**:
   ```yaml
   responses:
     '200':
       schema:
         $ref: '#/components/schemas/MySerializer'  # ❌ Wrong - should be array
   ```

2. **TypeScript Client Issue**:
   - Generated hooks return single objects instead of arrays
   - Type errors: `Type 'MyModel' is missing properties: length, pop, push, concat...`
   - Missing fetchers/hooks for array endpoints

## Root Cause

DRF-Spectacular inherits `pagination_class` from the ViewSet for list-like responses. When `responses=Serializer(many=True)` is detected, it automatically assumes pagination is needed and generates a paginated response schema instead of a simple array.

## Solution

### ✅ Correct Pattern

```python
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework import viewsets

class MyViewSet(viewsets.GenericViewSet):
    serializer_class = DefaultSerializer  # Required for drf-spectacular

    # IMPORTANT: @extend_schema MUST come BEFORE @action
    @extend_schema(
        summary="Get list of items",
        responses={200: MySerializer(many=True)},  # ← Use dict format with status code
        tags=["MyTag"]
    )
    @action(
        detail=False,
        methods=['get'],
        url_path='my-list',
        pagination_class=None  # ← KEY: Disable pagination for simple arrays
    )
    def my_list_action(self, request):
        items = MyModel.objects.all()
        serializer = MySerializer(items, many=True)
        return Response(serializer.data)
```

### Key Points

1. **Decorator Order**: `@extend_schema` MUST come **before** `@action`
2. **Disable Pagination**: Add `pagination_class=None` to `@action` decorator
3. **Responses Format**: Use `responses={200: Serializer(many=True)}` (dict format with status code)
4. **Serializer Class**: ViewSet must have `serializer_class` defined

## ❌ Common Mistakes

### Mistake 1: Wrong Decorator Order

```python
# ❌ Wrong - @action before @extend_schema
@action(detail=False, methods=['get'], pagination_class=None)
@extend_schema(responses={200: MySerializer(many=True)})
def my_action(self, request):
    pass
```

**Result**: OpenAPI schema uses wrong tag (default "app" instead of custom tag), wrong operationId, or references wrong serializer (ViewSet's default instead of action's).

### Mistake 2: Direct Serializer Format (without dict)

```python
# ❌ Wrong - not using dict with status codes
@extend_schema(
    responses=MySerializer(many=True)  # Should be {200: MySerializer(many=True)}
)
@action(detail=False, methods=['get'], pagination_class=None)
def my_action(self, request):
    pass
```

**Result**: TypeScript generator creates `Promise<any>` instead of properly typed array. Schema generation might work but client types will be wrong.

### Mistake 3: Missing pagination_class=None

```python
# ❌ Wrong - pagination_class inherited from ViewSet
@extend_schema(
    responses={200: MySerializer(many=True)}
)
@action(detail=False, methods=['get'])  # Missing pagination_class=None
def my_action(self, request):
    pass
```

**Result**: Generates paginated response schema instead of simple array.

### Mistake 4: No serializer_class in ViewSet

```python
# ❌ Wrong - no serializer_class defined
class MyViewSet(viewsets.GenericViewSet):
    # Missing: serializer_class = DefaultSerializer

    @action(...)
    @extend_schema(...)
    def my_action(self, request):
        pass
```

**Result**: Error: `'MyViewSet' should either include a 'serializer_class' attribute...`

## Verification

### 1. Check OpenAPI Schema

```bash
python manage.py spectacular --file schema.yaml --validate
```

Look for correct array format:

```yaml
responses:
  '200':
    content:
      application/json:
        schema:
          type: array  # ✅ Correct
          items:
            $ref: '#/components/schemas/MySerializer'
```

### 2. Check Generated TypeScript

```typescript
// ✅ Correct - returns array
export async function getMyList(client?: API): Promise<MyModel[]> {
  const response = await api.my_endpoint.myListAction()
  return MyModelSchema.array().parse(response)
}

// Hook returns array type
export function useMyList(): ReturnType<typeof useSWR<MyModel[]>> {
  return useSWR<MyModel[]>('my-list', () => Fetchers.getMyList())
}
```

### 3. Test API Response

```bash
curl http://localhost:8000/api/my-endpoint/my-list/
```

Should return array:
```json
[
  {"id": 1, "name": "Item 1"},
  {"id": 2, "name": "Item 2"}
]
```

## Related Issues

- [drf-spectacular #692](https://github.com/tfranzel/drf-spectacular/issues/692) - Document endpoint supporting both many=True and many=False
- [drf-spectacular FAQ](https://drf-spectacular.readthedocs.io/en/latest/faq.html#my-action-is-erroneously-paginated-or-has-filter-parameters-that-i-do-not-want)

## Tag Grouping in Generated Clients

### Problem: Endpoints Split Across Multiple Files

When ViewSet actions use different OpenAPI tags, the TypeScript generator creates separate client files for each tag, causing import issues and missing endpoints.

**Example - Wrong Approach**:
```python
class DashboardViewSet(viewsets.GenericViewSet):
    @extend_schema(tags=["Statistics"])  # ❌ Wrong - different tag
    @action(...)
    def stat_cards(self, request):
        pass

    @extend_schema(tags=["System Health"])  # ❌ Wrong - different tag
    @action(...)
    def system_health(self, request):
        pass
```

**Result**: Generated files split across multiple locations:
- `_utils/fetchers/cfg__dashboard__statistics.ts` (stat_cards)
- `_utils/fetchers/cfg__dashboard__system_health.ts` (system_health)
- `_utils/hooks/cfg__dashboard__statistics.ts`
- `_utils/hooks/cfg__dashboard__system_health.ts`

### Solution: Use Consistent Tag

**Correct Approach**:
```python
class DashboardViewSet(viewsets.GenericViewSet):
    @extend_schema(tags=["dashboard"])  # ✅ Correct - consistent tag
    @action(...)
    def stat_cards(self, request):
        pass

    @extend_schema(tags=["dashboard"])  # ✅ Correct - consistent tag
    @action(...)
    def system_health(self, request):
        pass
```

**Result**: All endpoints in one file:
- `_utils/fetchers/cfg__dashboard.ts` (all endpoints)
- `_utils/hooks/cfg__dashboard.ts` (all hooks)

### Multiple Tags (Alternative)

You can use multiple tags where the **first tag** determines grouping:

```python
@extend_schema(
    tags=["dashboard", "Statistics"],  # First tag used for grouping
    responses=StatCardSerializer(many=True)
)
```

This generates files under `cfg__dashboard/` while maintaining additional tag metadata for documentation.

### Best Practices

1. **Single ViewSet = Single Tag**: All actions in one ViewSet should use the same primary tag
2. **Tag Naming**: Use lowercase, underscores allowed (e.g., `dashboard`, `user_management`)
3. **Consistency**: Keep tags consistent across related endpoints to avoid file fragmentation

## Real-World Example: Admin Panel Commands

This example shows a complete working implementation from the StockAPIS admin panel.

### Problem
Frontend received error: `"expected object, received array"` when calling `/api/adminpanel/commands/available/`.

**Cause**: API returned simple array `[{...}, {...}]` but TypeScript client expected paginated object `{results: [...], count: N, ...}`.

### Solution

```python
# apps/adminpanel/views/command_execution.py

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from ..models import CommandExecution
from ..serializers import (
    CommandExecutionSerializer,
    CommandExecutionListSerializer,
    CommandAvailableSerializer,
)

@extend_schema_view(
    list=extend_schema(
        summary="List command executions",
        description="Get paginated list of command execution history",
        tags=["Admin Panel - Commands"],
    ),
    retrieve=extend_schema(
        summary="Get command execution details",
        description="Retrieve detailed information about a command execution",
        tags=["Admin Panel - Commands"],
    ),
)
class CommandExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Django management command executions."""

    queryset = CommandExecution.objects.all().select_related("user")
    serializer_class = CommandExecutionSerializer  # ← Required!
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return CommandExecutionListSerializer
        return CommandExecutionSerializer

    # ✅ CORRECT: @extend_schema BEFORE @action
    @extend_schema(
        summary="List available commands",
        description="Get list of Django management commands available for execution",
        tags=["Admin Panel - Commands"],
        responses={200: CommandAvailableSerializer(many=True)},  # ← Dict format!
    )
    @action(detail=False, methods=["get"], pagination_class=None)  # ← Disable pagination
    def available(self, request):
        """Get list of available Django management commands."""
        commands = [
            {
                "name": "migrate",
                "title": "Database Migration",
                "description": "Apply database migrations",
                "icon": "database",
                "color": "blue",
                "actions": [...]
            },
            # ... more commands
        ]
        serializer = CommandAvailableSerializer(commands, many=True)
        return Response(serializer.data)
```

### Generated OpenAPI Schema

```yaml
/api/adminpanel/commands/available/:
  get:
    operationId: adminpanel_commands_available_list  # ✅ Correct operationId
    summary: List available commands
    tags:
      - Admin Panel - Commands  # ✅ Correct tag
    responses:
      '200':
        content:
          application/json:
            schema:
              type: array  # ✅ Simple array!
              items:
                $ref: '#/components/schemas/CommandAvailable'
```

### Frontend Usage

```typescript
// contexts/adminpanel/AdminPanelContext.tsx
import { useAdminpanelCommandsAvailableList } from '@/api/generated/adminpanel/_utils/hooks';
import type { CommandAvailable } from '@/api/generated/adminpanel/_utils/schemas';

export function AdminPanelProvider({ children }: AdminPanelProviderProps) {
  // Hook returns simple array (no pagination)
  const {
    data: commandsData,
    error: commandsError,
    isLoading: commandsLoading,
  } = useAdminpanelCommandsAvailableList(adminpanelApi);

  // Cast to array type (generator returns `any` for now)
  const availableCommands = (commandsData as CommandAvailable[] | undefined) || [];

  return (
    <AdminPanelContext.Provider value={{ availableCommands, commandsLoading, commandsError }}>
      {children}
    </AdminPanelContext.Provider>
  );
}
```

### Key Takeaways

1. **Decorator order matters**: `@extend_schema` must come **before** `@action`
2. **Use dict format**: `responses={200: Serializer(many=True)}` not `responses=Serializer(many=True)`
3. **Disable pagination**: Add `pagination_class=None` to `@action` for simple arrays
4. **Set serializer_class**: Required on ViewSet for drf-spectacular to work correctly
5. **TypeScript generator limitation**: Currently generates `Promise<any>` for arrays - cast to proper type in frontend

## References

- [drf-spectacular Documentation](https://drf-spectacular.readthedocs.io/)
- [DRF @action Decorator](https://www.django-rest-framework.org/api-guide/viewsets/#marking-extra-actions-for-routing)
- [OpenAPI 3.0 Schema](https://spec.openapis.org/oas/v3.0.3)
