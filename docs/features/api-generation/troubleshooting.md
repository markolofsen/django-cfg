# Troubleshooting API Generation

Common issues and solutions when generating API clients with Django-CFG API Client Generation.

## TypeScript Generation Issues

### Cannot find name 'TypeName' errors

**Problem:**

TypeScript build fails with errors like:
```
error TS2304: Cannot find name 'ApiKeyDetail'
```

This happens when `@hey-api/openapi-ts` splits types with mixed readonly/writable fields into `Readable`/`Writable` versions (e.g., `ApiKeyDetailReadable`, `ApiKeyDetailWritable`), but references inside other types still use the base name.

**Root Cause:**

The TypeScript generator automatically splits schemas that have both:
- Readonly fields (`readOnly: true`)
- Writable fields (no `readOnly` flag)

It creates `TypeNameReadable` and `TypeNameWritable`, but doesn't create the base `TypeName`. However, references in other schemas still point to the base name.

**Solution:**

Make all fields in detail serializers read-only:

```python
class APIKeyDetailSerializer(serializers.ModelSerializer):
    # ... field definitions ...

    class Meta:
        model = APIKey
        fields = [
            'id',
            'name',
            'is_active',
            # ... other fields
        ]
        read_only_fields = fields  # All fields read-only prevents TS split
```

This prevents the TypeScript generator from splitting the type.

**Alternative Solution (if you need writable fields):**

Use separate serializers for read and write operations:

```python
# Read-only serializer (all fields readonly)
class APIKeyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = fields

# Write-only serializer (for updates)
class APIKeyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'is_active']  # Only writable fields
```

## Schema Generation Issues

### ModuleNotFoundError: No module named 'django_cfg'

**Problem:**

Schema generation fails with import errors when running `manage.py generate_api`.

**Root Cause:**

Django-CFG API Client Generation spawns subprocess calls to `manage.py spectacular` using the wrong Python interpreter (system Python instead of virtualenv Python).

**Solution:**

Fixed in Django-CFG Client Generator v1.4+ by using `sys.executable` instead of hardcoded `"python"` in subprocess calls.

If using older version, ensure you're running commands with the virtualenv Python:

```bash
.venv/bin/python manage.py generate_api
```

### COMPONENT_SPLIT creates missing type references

**Problem:**

DRF Spectacular with `COMPONENT_SPLIT_REQUEST: True` creates only `Readable`/`Writable` versions, but some references still point to base types.

**Root Cause:**

DRF Spectacular's COMPONENT_SPLIT doesn't create base types when splitting.

**Solution:**

Django-CFG API Client Generation includes a `SchemaPostprocessor` that automatically fixes missing references by replacing them with `Readable`/`Writable` versions. This runs automatically after schema generation.

The postprocessor:
1. Scans for `$ref` to non-existent components
2. Replaces with `ComponentNameReadable` or `ComponentNameWritable`
3. Handles `allOf` patterns used by Spectacular

## Python Client Generation Issues

### openapi-python-client not found

**Problem:**

Python client generation fails with command not found.

**Solution:**

Install openapi-python-client:

```bash
pip install openapi-python-client
```

Or add to your project dependencies:

```toml
[tool.poetry.dependencies]
openapi-python-client = "^0.15.0"
```

## General Tips

### Enable debug logging

Add to your Django settings:

```python
LOGGING = {
    'loggers': {
        'django_cfg.client': {
            'level': 'DEBUG',
        },
    },
}
```

### Check generated schemas

Schemas are saved to `openapi/schemas/{zone_name}.yaml`. Inspect them to verify:
- All required components exist
- References are correct
- No duplicate definitions

### Regenerate from scratch

If you encounter persistent issues:

```bash
# Clean output directories
rm -rf openapi/clients openapi/schemas

# Regenerate
python manage.py generate_api
```

### Verify TypeScript build

After generation, always test the TypeScript build:

```bash
cd frontend/packages/api
pnpm build
```

## Getting Help

If you encounter issues not covered here:

1. Check Django-CFG API Client Generation logs in `logs/djangocfg/`
2. Review the generated OpenAPI schemas
3. Report issues at [django-cfg issues](https://github.com/your-repo/issues)
