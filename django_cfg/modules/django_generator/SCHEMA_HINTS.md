# Schema Generation Hints

Common drf-spectacular gotchas and copy-paste fixes.

---

## 1. `swagger_fake_view` guard

When `get_queryset` reads `self.request.user.id` or `self.kwargs[...]`,
schema gen blows up with `AnonymousUser` / `KeyError` because drf-spectacular
calls the view without a real request.

```python
def get_queryset(self):
    if getattr(self, "swagger_fake_view", False):
        return MyModel.objects.none()
    return MyModel.objects.filter(user=self.request.user)
```

---

## 2. Plain Python data, not ORM

When the view sources a list that is not a `QuerySet` (Pydantic objects,
registry dicts, …), `paginate_queryset` works on plain lists, but schema gen
probes `queryset.model`. Return a `ContentType` placeholder:

```python
def get_queryset(self):
    if getattr(self, "swagger_fake_view", False):
        from django.contrib.contenttypes.models import ContentType
        return ContentType.objects.none()
    return list(my_service.iter_items())   # plain list, not QuerySet
```

---

## 3. Inline schema vs `$ref`

`ts_extras` ignores inline response schemas — no zod, no typed hooks.
Two fixes:

**A. Paginate** (wraps in `{count, next, previous, results}`):
```python
class MyViewSet(GenericViewSet):
    pagination_class = DefaultPagination
    serializer_class = MySerializer
```

**B. Named wrapper serializer** (for flat arrays / custom shapes):
```python
class MyListSerializer(serializers.Serializer):
    results = MySerializer(many=True)

# view:
@extend_schema(responses=MyListSerializer)
def list(self, request): ...
```

---

## 4. Tag convention

Use lowercase `snake_case`. The first tag becomes the slicer group.

```python
# Good — slicer produces "cfg" group
@extend_schema(tags=["cfg_dashboard_activity"])

# Bad — slicer warning + scattered groups
@extend_schema(tags=["Dashboard - Activity"])
```

---

## 5. `enum_name_overrides`

Only use when you cannot rename the source class. The better fix is to rename
the `TextChoices` class so its name is globally unique — drf-spectacular then
auto-derives the schema name without any override.

```python
# Before (collision-prone)
class Status(TextChoices): ...

# After (portable, no override needed)
class CRMTaskStatus(TextChoices): ...
```

---

## 6. `unable to guess serializer`

`APIView` without `serializer_class` → schema generator emits an Error.

Either annotate explicitly:
```python
class MyView(APIView):
    serializer_class = MySerializer   # class-level fallback
```

Or exclude from the schema entirely:
```python
@extend_schema(exclude=True)
class InternalWebhookView(APIView): ...
```
