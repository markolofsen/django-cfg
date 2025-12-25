# Protocol Buffer Enum Naming Conflict Fix

## Problem

Protocol Buffers use C++ scoping rules for enum values. This means enum values are **siblings** of their type, not children. When multiple enums are defined within the same message, all enum values must be unique across ALL enums in that message scope.

### Error Example

```
"unknown" is already defined in "workspaces.v1.workspaces.Workspace".
Note that enum values use C++ scoping rules, meaning that enum values are
siblings of their type, not children of it. Therefore, "unknown" must be
unique within "workspaces.v1.workspaces.Workspace", not just within "Plan".
```

### Before Fix (Causes Compilation Error)

```protobuf
message Workspace {
  enum Plan {
    unknown = 0;      // ❌ First definition of "unknown"
    free = 1;
    pro = 2;
  }

  enum Type {
    unknown = 0;      // ❌ ERROR: "unknown" already defined!
    personal = 1;
    team = 2;
  }
}
```

## Solution

Prefix all "unknown" and "unspecified" enum values with the enum name in UPPER_SNAKE_CASE format. This ensures uniqueness while maintaining Protocol Buffer best practices.

### After Fix (Compiles Successfully)

```protobuf
message Workspace {
  enum Plan {
    PLAN_UNKNOWN = 0;     // ✅ Prefixed with enum name
    free = 1;
    pro = 2;
  }

  enum Type {
    TYPE_UNKNOWN = 0;     // ✅ Prefixed - no conflict!
    personal = 1;
    team = 2;
  }
}
```

## Implementation

### File
`django_cfg/modules/django_client/core/generator/proto/messages_generator.py`

### Method
`ProtoMessagesGenerator._generate_enum()`

### Changes

1. **Auto-generated "unknown" values**: Use `sanitize_enum_value()` with `json_compatible=False` to generate prefixed names like `PLAN_UNKNOWN`

2. **User-provided "unknown"/"unspecified" values**: Also prefix these to prevent conflicts

3. **Regular enum values**: Keep using `json_compatible=True` to preserve original casing for JSON serialization compatibility with Django

### Code

```python
# Auto-generated unknown value
if not has_unknown:
    unknown_value_name = sanitize_enum_value(
        "unknown", enum_name, json_compatible=False
    )
    lines.append(f"{indent_str}  {unknown_value_name} = 0;")

# User-provided values
for idx, value in enumerate(enum_values, start=start_index):
    value_str = str(value).lower()
    if value_str in ("unknown", "unspecified"):
        # Prefix to avoid conflicts
        enum_value_name = sanitize_enum_value(
            value, enum_name, json_compatible=False
        )
    else:
        # Preserve original casing for JSON compatibility
        enum_value_name = sanitize_enum_value(
            value, enum_name, json_compatible=True
        )
    lines.append(f"{indent_str}  {enum_value_name} = {idx};")
```

## Scenarios Handled

### 1. Multiple enums with auto-generated "unknown"
```protobuf
message Workspace {
  enum Plan {
    PLAN_UNKNOWN = 0;    // Auto-generated
    free = 1;
  }
  enum Type {
    TYPE_UNKNOWN = 0;    // Auto-generated
    personal = 1;
  }
}
```

### 2. Multiple enums with user-provided "unknown"
```protobuf
message Task {
  enum Status {
    STATUS_UNKNOWN = 0;  // User-provided "unknown"
    active = 1;
  }
  enum State {
    STATE_UNKNOWN = 0;   // User-provided "unknown"
    pending = 1;
  }
}
```

### 3. Regular values preserve JSON compatibility
```protobuf
message Notification {
  enum Channel {
    CHANNEL_UNKNOWN = 0;
    email = 1;           // Original casing preserved
    phone = 2;           // Original casing preserved
  }
}
```

## Benefits

1. **No C++ Scoping Conflicts**: All enum values are unique within message scope
2. **JSON Compatibility**: Regular enum values preserve original casing for Django serialization
3. **Best Practices**: Follows Protocol Buffer naming conventions for default/unknown values
4. **Backward Compatible**: Doesn't break existing proto files that don't have conflicts

## References

- [Protocol Buffers Language Guide - Enums](https://protobuf.dev/programming-guides/proto3/#enum)
- [Protocol Buffers Style Guide](https://protobuf.dev/programming-guides/style/)
