# Django CFG Endpoints API

Модуль для работы с Django URL endpoints.

## Структура

```
endpoints/
├── endpoints_status/     # Проверка статуса всех endpoints
│   ├── checker.py        # Логика проверки endpoints
│   ├── drf_views.py      # DRF views
│   ├── serializers.py    # Serializers
│   ├── tests.py          # Tests
│   └── views.py          # Plain Django views
├── urls_list/            # Список всех URL в Django
│   ├── views.py          # DRF views для вывода URLs
│   └── serializers.py    # Serializers
└── urls.py               # URL routing
```

## Endpoints

### Endpoints Status

Проверяет здоровье всех зарегистрированных endpoints в Django.

- **DRF (Browsable)**: `/cfg/endpoints/drf/`
- **JSON**: `/cfg/endpoints/`

**Query параметры:**
- `include_unnamed` (bool): Включить endpoints без имени (default: false)
- `timeout` (int): Timeout запроса в секундах (default: 5)
- `auto_auth` (bool): Автоматически повторить с JWT при 401/403 (default: true)

### URLs List

Выводит список всех зарегистрированных URL patterns в Django.

- **Full details**: `/cfg/endpoints/urls/`
- **Compact**: `/cfg/endpoints/urls/compact/`

**Compact** возвращает только pattern + name для каждого URL.

**Full details** возвращает:
- Pattern (regex или typed)
- Name
- Full name (с namespace)
- Namespace
- View name
- View class
- HTTP methods
- Module path

## Примеры

### URLs List (Full)

```bash
curl http://localhost:8000/cfg/endpoints/urls/
```

```json
{
  "status": "success",
  "service": "Django CFG",
  "version": "2.0.0",
  "base_url": "http://localhost:8000",
  "total_urls": 150,
  "urls": [
    {
      "pattern": "/api/accounts/profile/",
      "name": "account_profile",
      "full_name": "api:account_profile",
      "namespace": "api",
      "view": "ProfileViewSet",
      "view_class": "ProfileViewSet",
      "methods": ["get", "post", "put", "patch", "delete"],
      "module": "apps.accounts.views"
    },
    ...
  ]
}
```

### URLs List (Compact)

```bash
curl http://localhost:8000/cfg/endpoints/urls/compact/
```

```json
{
  "status": "success",
  "total": 150,
  "urls": [
    {
      "pattern": "/api/accounts/profile/",
      "name": "account_profile"
    },
    ...
  ]
}
```

### Endpoints Status

```bash
curl http://localhost:8000/cfg/endpoints/drf/
```

```json
{
  "status": "healthy",
  "timestamp": "2025-10-26T10:30:00Z",
  "total_endpoints": 100,
  "healthy": 95,
  "unhealthy": 0,
  "warnings": 3,
  "errors": 0,
  "skipped": 2,
  "endpoints": [...]
}
```

## Health Check Integration

URLs list endpoint доступен из health check:

```bash
curl http://localhost:8000/cfg/health/drf/
```

```json
{
  "status": "healthy",
  ...
  "links": {
    "urls_list": "http://localhost:8000/cfg/endpoints/urls/",
    "urls_list_compact": "http://localhost:8000/cfg/endpoints/urls/compact/",
    "endpoints_status": "http://localhost:8000/cfg/endpoints/drf/",
    "quick_health": "http://localhost:8000/cfg/health/drf/quick/"
  }
}
```
