# Frontend Build Guide

## Static Build Configuration

Настроена статическая сборка Next.js Admin для отдачи через Django.

### Конфигурация

**next.config.ts:**
```typescript
output: "export"        // Статическая сборка
distDir: "out"          // Директория для сборки
images: {
  unoptimized: true     // Отключена оптимизация (для static export)
}
```

### Команды

#### 1. Генерация API клиентов

```bash
cd /path/to/django_admin
make generate-api
```

Или вручную:
```bash
cd ../../../../solution/projects/django
poetry run python manage.py generate_clients --typescript --no-python
cp -r openapi/clients/typescript/cfg/* django_admin/packages/api/src/cfg/generated/
cd django_admin/packages/api && pnpm build
```

#### 2. Сборка статики

```bash
cd /path/to/django_admin
make build-admin
```

Или вручную:
```bash
cd apps/admin
pnpm build:static
```

Статические файлы появятся в `apps/admin/out/`

### Структура после сборки

```
django_admin/
├── apps/admin/out/          # ← Статические файлы Next.js
│   ├── _next/
│   ├── index.html
│   └── ...
└── packages/api/
    └── src/cfg/generated/   # ← Сгенерированные TypeScript клиенты
```

### Интеграция с Django

Статические файлы из `apps/admin/out/` нужно отдавать через Django:

```python
# В Django settings
STATICFILES_DIRS = [
    BASE_DIR / "django_admin/apps/admin/out",
]
```

### Troubleshooting

**Ошибка: Cannot find module**
- Запустите `pnpm install` в корне django_admin

**Ошибка при сборке API**
- Убедитесь что Django проект собран и запущен
- Проверьте пути в Makefile

**Ошибка: Image Optimization requires `unoptimized`**
- Уже настроено в next.config.ts
- Если возникает - добавьте `unoptimized: true` в images

