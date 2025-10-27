# JWT Auto-Injection для Next.js приложений

## Обзор

Django-CFG автоматически инжектирует JWT токены (`auth_token` и `refresh_token`) в `localStorage` для авторизованных пользователей при загрузке Next.js приложений через **NextJSStaticView**.

## Как это работает

### Автоматическая инжекция в Next.js apps (рекомендуется)

**NextJSStaticView** автоматически инжектирует JWT токены во все HTML ответы для авторизованных пользователей.

```python
# urls.py
from django_cfg.apps.frontend.views import AdminView

urlpatterns = [
    path('admin/', include('django_cfg.apps.frontend.urls')),  # JWT injection automatic
]
```

При загрузке **любой страницы Next.js приложения**, если пользователь авторизован:
1. View обслуживает статический файл Next.js
2. Генерируются JWT токены (access + refresh)
3. Токены автоматически инжектируются в `<head>` или `<body>` через `<script>` тег
4. Токены сохраняются в `localStorage`

**Преимущества:**
- Работает только для Next.js приложений (безопасный scope)
- Не нужно модифицировать templates
- Централизованная логика в базовом view
- Не влияет на другие HTML responses (Django admin, etc.)

### Template Tags (для кастомных шаблонов)

Если вы используете собственные Django шаблоны, можете использовать готовые template tags:

#### 1. Полная автоматическая инжекция

```django
{% load django_cfg %}

<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
    {% inject_jwt_tokens_script %}  {# Автоматически инжектит оба токена #}
</head>
<body>
    <!-- Your content -->
</body>
</html>
```

#### 2. Отдельные токены

```django
{% load django_cfg %}

<script>
    // Access token
    const accessToken = '{% user_jwt_token %}';

    // Refresh token
    const refreshToken = '{% user_jwt_refresh_token %}';

    // Manual storage
    localStorage.setItem('auth_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
</script>
```

## Использование в Next.js

После инжекции токены доступны в вашем Next.js приложении:

```typescript
// В любом Next.js компоненте или API клиенте
const accessToken = localStorage.getItem('auth_token');
const refreshToken = localStorage.getItem('refresh_token');

// Использование с API клиентом
import { API } from './generated/cfg';

const api = new API('http://localhost:8000', {
  storage: {
    getItem: (key) => localStorage.getItem(key),
    setItem: (key, value) => localStorage.setItem(key, value),
    removeItem: (key) => localStorage.removeItem(key),
  }
});
```

## Безопасность

### Что инжектируется
- `auth_token` - JWT access token (короткий срок жизни)
- `refresh_token` - JWT refresh token (длинный срок жизни)

### Когда инжектируется
Токены генерируются **только** если:
1. Пользователь **авторизован** через Django session
2. Загружается **HTML файл** (не JS, CSS и т.д.)
3. `rest_framework_simplejwt` установлен

### Безопасность токенов
- Токены генерируются **на лету** при каждом запросе
- Access token имеет короткий срок жизни (настраивается в `JWTConfig`)
- Refresh token позволяет получить новый access token без повторной авторизации
- Токены хранятся только в `localStorage` на клиенте

## Конфигурация JWT

Настройка времени жизни токенов в `django_cfg`:

```python
from django_cfg.models.api import JWTConfig

jwt_config = JWTConfig(
    access_token_lifetime_hours=24,      # Access token на 24 часа
    refresh_token_lifetime_days=30,      # Refresh token на 30 дней
    rotate_refresh_tokens=True,          # Ротация refresh токенов
    blacklist_after_rotation=True,       # Блэклист старых токенов
)
```

## Отладка

Проверьте в консоли браузера:

```javascript
// Проверить наличие токенов
console.log('Access Token:', localStorage.getItem('auth_token'));
console.log('Refresh Token:', localStorage.getItem('refresh_token'));

// Сообщение об успешной инжекции
// "JWT tokens injected successfully"
```

## Примеры

### Пример 1: Автоматическая инжекция в Next.js приложении (рекомендуется)

```python
# urls.py - JWT injection работает автоматически
urlpatterns = [
    path('cfg/admin/', include('django_cfg.apps.frontend.urls')),  # Admin Panel with JWT
]

# views.py - создайте свой Next.js app view
from django_cfg.apps.frontend.views import NextJSStaticView

class MyAppView(NextJSStaticView):
    """Custom Next.js app with automatic JWT injection."""
    app_name = 'my_app'  # Serves from static/frontend/my_app/
```

При переходе на **любую страницу** Next.js приложения авторизованный пользователь автоматически получит JWT токены в localStorage.

**⚠️ На /cfg/admin/auth токены НЕ инжектятся** - это страница логина, пользователь ещё не авторизован!

### Пример 2: Кастомный шаблон с инжекцией

```django
{% load django_cfg %}

<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Centrifugo Monitor</title>

    {# Автоматическая инжекция JWT токенов #}
    {% inject_jwt_tokens_script %}
</head>
<body>
    <div id="root"></div>
    <script src="/_next/static/chunks/main.js"></script>
</body>
</html>
```

## Требования

- Django с включенной аутентификацией
- `rest_framework_simplejwt` установлен
- Пользователь авторизован через Django session

## API Reference

### Template Tags

#### `{% user_jwt_token %}`
Возвращает JWT access token для текущего пользователя.

#### `{% user_jwt_refresh_token %}`
Возвращает JWT refresh token для текущего пользователя.

#### `{% inject_jwt_tokens_script %}`
Генерирует полный `<script>` тег с автоматической инжекцией обоих токенов в localStorage.

### View Classes

#### `NextJSStaticView`
Базовый view для обслуживания Next.js статических сборок с автоматической JWT инжекцией.

**Features:**
- Serves Next.js static export files
- Automatically injects JWT tokens for authenticated users
- Tokens injected into HTML responses only
- Handles Next.js client-side routing (.html fallback)

**Usage:**
```python
from django_cfg.apps.frontend.views import NextJSStaticView

class MyAppView(NextJSStaticView):
    app_name = 'my_app'  # Serves from static/frontend/my_app/
```

#### `AdminView`
Специализированный view для Admin Panel (наследует `NextJSStaticView`).

**Built-in JWT injection** - no additional configuration needed.
