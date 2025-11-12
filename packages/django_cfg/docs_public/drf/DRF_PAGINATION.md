# DRF Pagination in ViewSet Actions

## Problem

When using `@action` decorators in DRF ViewSets that need pagination, forgetting to properly configure pagination leads to:
- Missing pagination parameters (`page`, `page_size`) in OpenAPI schema
- Wrong response type (single object instead of paginated list)
- Frontend receiving unpaginated data when expecting paginated response
- TypeScript client not including pagination parameters

## Symptoms

1. **OpenAPI Schema Issues**:
   ```yaml
   responses:
     '200':
       schema:
         $ref: '#/components/schemas/MySerializer'  # ❌ Should be paginated
   ```

2. **Missing Parameters**:
   - No `page` parameter in query
   - No `page_size` parameter in query

3. **Frontend Issues**:
   - `recentRequests` is `undefined` in React component
   - Hook doesn't return paginated data structure
   - Missing `results`, `count`, `page`, `pages` fields

## Root Cause

When using `@action` with pagination:
1. ViewSet needs explicit `pagination_class` set
2. Response schema must use `Serializer(many=True)`
3. Without these, drf-spectacular generates single-object schema instead of paginated schema

## Solution

### ✅ Correct Pattern for Paginated Actions

```python
from django_cfg.mixins import AdminAPIMixin
from django_cfg.middleware.pagination import DefaultPagination
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class MyMonitoringViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """ViewSet with paginated actions."""

    # 1. ✅ Set pagination_class on ViewSet
    pagination_class = DefaultPagination

    # 2. ✅ Required for GenericViewSet
    queryset = MyModel.objects.none()  # Placeholder
    serializer_class = MySerializer    # Default serializer

    @extend_schema(
        tags=["Monitoring"],
        summary="Get recent items",
        description="Returns paginated list of items",
        parameters=[
            OpenApiParameter(name="status", type=str, required=False),
            # Note: page, page_size added automatically by pagination_class
        ],
        responses={
            200: MySerializer(many=True),  # 3. ✅ Use many=True for list
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="recent")
    def recent(self, request):
        """Get recent items with pagination."""
        queryset = MyModel.objects.filter(...)

        # 4. ✅ Use paginate_queryset
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Serialize paginated data
            serializer = MySerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Fallback (no pagination)
        serializer = MySerializer(queryset, many=True)
        return Response(serializer.data)
```

### Key Points

1. **Set `pagination_class` on ViewSet**:
   ```python
   pagination_class = DefaultPagination
   ```

2. **Use `many=True` in response schema**:
   ```python
   responses={200: MySerializer(many=True)}
   ```

3. **Use `paginate_queryset()` and `get_paginated_response()`**:
   ```python
   page = self.paginate_queryset(queryset)
   if page is not None:
       return self.get_paginated_response(data)
   ```

4. **Set `queryset` and `serializer_class`**:
   Required for GenericViewSet to work with drf-spectacular

## Generated OpenAPI Schema

### ✅ Correct (With Pagination)

```yaml
/api/monitor/recent/:
  get:
    operationId: monitor_recent_list  # Note: "_list" suffix
    parameters:
      - name: status
        in: query
      - name: page          # ✅ Auto-added
        in: query
      - name: page_size     # ✅ Auto-added
        in: query
    responses:
      '200':
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/PaginatedMySerializerList'
```

### ❌ Wrong (Without Pagination)

```yaml
/api/monitor/recent/:
  get:
    operationId: monitor_recent_retrieve  # Note: "_retrieve" suffix
    parameters:
      - name: status
        in: query
      # ❌ Missing: page, page_size
    responses:
      '200':
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MySerializer'  # ❌ Single object
```

## Generated TypeScript Client

### ✅ Correct

```typescript
// Fetcher includes pagination params
export async function getMonitorRecentList(
  params?: {
    status?: string;
    page?: number;        // ✅
    page_size?: number;   // ✅
  },
  client?: any
): Promise<PaginatedMySerializerList> {
  const response = await api.monitor.recentList(...)
  return PaginatedMySerializerListSchema.parse(response)
}

// Hook with pagination
export function useMonitorRecentList(params?: {...}):
  ReturnType<typeof useSWR<PaginatedMySerializerList>>

// Schema with pagination
export const PaginatedMySerializerListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(MySerializerSchema),
})
```

### ❌ Wrong

```typescript
// Missing pagination params
export async function getMonitorRecentRetrieve(
  params?: { status?: string },  // ❌ No page, page_size
  client?: any
): Promise<MySerializer> {  // ❌ Single object
  ...
}
```

## Frontend Usage

### Context Setup

```typescript
import { useDRFPagination } from '@djangocfg/ui';
import { useMonitorRecentList } from '@/api/generated';

export function MonitoringProvider({ children }) {
  // 1. Setup pagination state
  const pagination = useDRFPagination(1, 10);

  // 2. Pass pagination params to hook
  const {
    data: recentItems,
    isLoading,
    mutate,
  } = useMonitorRecentList(
    {
      page: pagination.page,
      page_size: pagination.pageSize,
      // ... other filters
    },
    api
  );

  // 3. Extract results from paginated response
  const items = recentItems?.results || [];

  return (
    <MonitoringContext.Provider value={{
      items,
      isLoading,
      pagination
    }}>
      {children}
    </MonitoringContext.Provider>
  );
}
```

### Component with Pagination

```typescript
export function ItemsTable() {
  const { items, pagination } = useMonitoring();

  return (
    <div>
      <Table>
        {items.map(item => <TableRow key={item.id}>...</TableRow>)}
      </Table>

      {/* Pagination controls */}
      <StaticPagination
        data={recentItems}  // Pass full paginated response
        onPageChange={pagination.setPage}
        className="mt-4"
      />
    </div>
  );
}
```

## Common Mistakes

### ❌ Mistake 1: No pagination_class on ViewSet

```python
class MyViewSet(viewsets.GenericViewSet):
    # ❌ Missing: pagination_class = DefaultPagination

    @action(...)
    def recent(self, request):
        ...
```

**Result**: No pagination parameters in OpenAPI schema, single-object response type.

### ❌ Mistake 2: Missing many=True in response

```python
@extend_schema(
    responses={200: MySerializer}  # ❌ Should be: MySerializer(many=True)
)
@action(...)
def recent(self, request):
    ...
```

**Result**: drf-spectacular treats it as single object, not a list.

### ❌ Mistake 3: Not using paginate_queryset

```python
@action(...)
def recent(self, request):
    queryset = MyModel.objects.all()
    serializer = MySerializer(queryset, many=True)
    return Response(serializer.data)  # ❌ Returns raw list, not paginated
```

**Result**: Backend returns unpaginated list, frontend expects paginated response.

### ❌ Mistake 4: Using pagination_class=None on action

```python
@action(detail=False, pagination_class=None)  # ❌ Disables pagination
def recent(self, request):
    ...
```

**Result**: Action won't be paginated even if ViewSet has pagination_class.

**Use Case**: Only use `pagination_class=None` when you explicitly want a simple array response (not paginated).

## Actions Without Pagination

For actions that should return simple arrays (not paginated):

```python
class MyViewSet(viewsets.GenericViewSet):
    pagination_class = DefaultPagination  # Default for other actions

    @extend_schema(
        responses={200: MySerializer(many=True)}
    )
    @action(
        detail=False,
        methods=["get"],
        pagination_class=None  # ✅ Explicitly disable pagination
    )
    def simple_list(self, request):
        """Returns simple array without pagination."""
        items = MyModel.objects.all()[:100]
        serializer = MySerializer(items, many=True)
        return Response(serializer.data)  # Returns: [{...}, {...}]
```

Generated schema:
```yaml
responses:
  '200':
    schema:
      type: array  # ✅ Simple array
      items:
        $ref: '#/components/schemas/MySerializer'
```

## Verification Checklist

Before regenerating API clients:

- [ ] ViewSet has `pagination_class = DefaultPagination`
- [ ] Response schema uses `Serializer(many=True)`
- [ ] Action uses `self.paginate_queryset()` and `self.get_paginated_response()`
- [ ] ViewSet has `queryset` and `serializer_class` defined
- [ ] Decorator order: `@extend_schema` BEFORE `@action`

After regenerating:

- [ ] OpenAPI schema has `page` and `page_size` parameters
- [ ] Response references `PaginatedXxxList` schema
- [ ] OperationId ends with `_list` (not `_retrieve`)
- [ ] TypeScript fetcher includes pagination params
- [ ] Zod schema includes pagination fields

## Real-World Example

See: `django_cfg/apps/integrations/grpc/views/monitoring.py`

The `requests()` action was fixed from returning single object to paginated list:

**Before Fix**:
```python
@extend_schema(responses={200: RecentRequestSerializer})  # ❌
@action(detail=False, methods=["get"])
def requests(self, request):
    queryset = get_requests()
    serializer = RecentRequestSerializer(queryset, many=True)
    return Response(serializer.data)  # ❌ Unpaginated
```

**After Fix**:
```python
class GRPCMonitorViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    pagination_class = DefaultPagination  # ✅

    @extend_schema(responses={200: RecentRequestSerializer(many=True)})  # ✅
    @action(detail=False, methods=["get"])
    def requests(self, request):
        queryset = get_requests()
        page = self.paginate_queryset(queryset)  # ✅
        if page is not None:
            serializer = RecentRequestSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)  # ✅
        ...
```

## References

- DRF Pagination: https://www.django-rest-framework.org/api-guide/pagination/
- drf-spectacular: https://drf-spectacular.readthedocs.io/
- DefaultPagination: `django_cfg/middleware/pagination.py`
