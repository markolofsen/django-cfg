# Django-Q2 Module

Автоматическая синхронизация расписаний Django-Q2 из конфига в базу данных.

## Зачем это нужно?

Django-Q2 хранит расписания в базе данных, но **не создаёт их автоматически** из конфига.
Этот модуль решает эту проблему - синхронизирует расписания после каждой миграции.

## Использование

### 1. Включи Django-Q2 в конфиге

```python
# config.py
from django_cfg.models.django import DjangoQ2Config

django_q2 = DjangoQ2Config(
    enabled=True,  # ← Автоматически добавит django_q и django_cfg.modules.django_q2 в INSTALLED_APPS
    schedules=[...]
)
```

**Модуль подключается автоматически!** Не нужно вручную добавлять в INSTALLED_APPS.

### 2. Определи расписания в конфиге

```python
from django_cfg.models.django import DjangoQ2Config, DjangoQ2ScheduleConfig

django_q2 = DjangoQ2Config(
    enabled=True,
    schedules=[
        DjangoQ2ScheduleConfig(
            name="Sync balances hourly",
            schedule_type="hourly",
            command="sync_account_balances",
            command_args=["--verbose"],
        ),
        DjangoQ2ScheduleConfig(
            name="Cleanup daily",
            schedule_type="cron",
            cron="0 2 * * *",  # 2 AM каждый день
            command="cleanup_old_data",
            command_kwargs={"days": 30},
        ),
    ],
)
```

### 3. Запусти миграции

```bash
python manage.py migrate
```

**Вывод:**
```
Running migrations:
  ...
  Syncing 2 Django-Q2 schedule(s)...
    ✓ Created schedule: Sync balances hourly
    ✓ Created schedule: Cleanup daily
  ✅ Django-Q2 schedules synced: 2 created, 0 updated
```

### 4. Запусти qcluster

```bash
python manage.py qcluster
```

Готово! Расписания автоматически синхронизированы и работают.

## Как это работает?

1. **Модуль подключается** к сигналу `post_migrate`
2. **После миграций** автоматически:
   - Читает расписания из конфига
   - Создаёт/обновляет их в базе данных (Schedule model)
3. **Django-Q2 читает** расписания из базы и выполняет задачи

## Ручная синхронизация (опционально)

Если нужно синхронизировать без миграций:

```bash
python manage.py sync_django_q_schedules

# Или с --dry-run для проверки:
python manage.py sync_django_q_schedules --dry-run
```

## Безопасность

- ✅ **Идемпотентность**: можно запускать много раз, не создаст дубликаты
- ✅ **Без race conditions**: синхронизация происходит один раз за цикл миграций
- ✅ **Graceful degradation**: если Django-Q2 не установлен, модуль просто молча пропустит синхронизацию
- ✅ **Logging**: все операции логируются для отладки

## Преимущества перед ручной синхронизацией

| Аспект | Ручная синхронизация | Модуль |
|--------|---------------------|--------|
| Автоматизация | Нужно помнить запускать | Автоматически |
| Деплой | Легко забыть | Всегда синхронизировано |
| CI/CD | Нужно добавлять в скрипты | Работает из коробки |
| Ошибки | Легко пропустить | Логи миграций |

## Troubleshooting

### Расписания не создаются

Проверь:
1. Модуль добавлен в INSTALLED_APPS
2. `django_q2.enabled = True` в конфиге
3. В конфиге есть расписания
4. Миграции запущены: `python manage.py migrate`

### Расписания не обновляются

Запусти миграции повторно или используй ручную синхронизацию:
```bash
python manage.py migrate --run-syncdb
# или
python manage.py sync_django_q_schedules
```

### Логи синхронизации

Включи DEBUG логи:
```python
LOGGING = {
    'loggers': {
        'django_cfg.modules.django_q2': {
            'level': 'DEBUG',
        },
    },
}
```
