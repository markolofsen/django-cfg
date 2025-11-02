# PostgreSQL Transaction Error Fix

## Problem

Error: **"current transaction is aborted, commands ignored until end of transaction block"**

### Root Causes:
1. Using `.extra()` for raw SQL queries in PostgreSQL
2. Calling `.count()` on models whose tables don't exist in the database

## Solution

### 1. Replaced `.extra()` with `TruncDate()` in `charts_service.py`

**Before:**
```python
.extra({'date': "date(date_joined)"})  # ❌ Raw SQL
```

**After:**
```python
from django.db.models.functions import TruncDate
.annotate(date=TruncDate('date_joined'))  # ✅ Django ORM
```

### 2. Added table existence check in `statistics_service.py`

**Problem:** `model.objects.count()` was called on ALL models, including those without database tables (e.g., migrations not run).

**Solution:** Check if table exists before querying:

```python
def _get_model_stats(self, model) -> Optional[Dict[str, Any]]:
    try:
        from django.db import connection, OperationalError, ProgrammingError

        # Check if table exists before querying
        table_name = model._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {connection.ops.quote_name(table_name)} LIMIT 1")

        # Now safe to call model.objects.count()
        model_stats = {
            "count": model.objects.count(),
            ...
        }
        return model_stats

    except (OperationalError, ProgrammingError):
        # Table doesn't exist - skip this model
        return None
```

## Modified Files

- ✅ `services/charts_service.py` - replaced all `.extra()` with `TruncDate()`
- ✅ `services/statistics_service.py` - added table existence check
- ✅ `views/overview_views.py` - simplified, removed complex transaction logic

## Key Lessons

1. **Don't use `.extra()`** - always use Django ORM functions
2. **Check table existence** before querying models
3. **Don't overcomplicate** - let Django handle transactions
4. **Catch specific exceptions** - `OperationalError`, `ProgrammingError` for DB issues

## Conclusion

Keep it simple! The issue was two simple bugs:
- Using raw SQL (`.extra()`)
- Querying non-existent tables

Fixed by using proper Django ORM and checking table existence.
