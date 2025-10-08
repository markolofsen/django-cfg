# Dashboard Debug Tool

Инструмент для отладки рендеринга dashboard секций.

## Использование

### 1. Management Command

Запустить из командной строки для тестирования рендера:

```bash
# Рендер всех секций
python manage.py debug_dashboard

# Рендер конкретной секции
python manage.py debug_dashboard --section overview
python manage.py debug_dashboard --section stats

# Указать пользователя
python manage.py debug_dashboard --user admin
```

### 2. Автоматическое сохранение

При каждом рендере dashboard секции автоматически сохраняются в:
```
libs/django_cfg/src/django_cfg/debug/dashboard/
```

Файлы:
- `section_overview_YYYYMMDD_HHMMSS.html` - отрендеренный HTML
- `section_overview_YYYYMMDD_HHMMSS_context.json` - контекст шаблона
- `section_overview_YYYYMMDD_HHMMSS_meta.json` - метаданные

**Важно**: Директория `debug/` добавлена в `.gitignore` и не попадает в git.

### 3. Программное использование

```python
from django_cfg.modules.django_dashboard.debug import save_section_render

# В коде секции
html = section.render()
save_section_render('my_section', html, section_data={'key': 'value'})
```

## Структура

```
dashboard/
├── debug.py              # DashboardDebugger класс
├── sections/             # Секции dashboard
│   ├── overview.py       # Overview секция
│   ├── stats.py          # Stats секция
│   ├── system.py         # System секция
│   └── commands.py       # Commands секция
└── management/
    └── commands/
        └── debug_dashboard.py  # Management command
```

## Сравнение с архивом

```python
from django_cfg.modules.django_dashboard.debug import get_debugger
from pathlib import Path

debugger = get_debugger()
archive = Path('@archieves/now/dashboard.html')

comparison = debugger.compare_with_archive(current_html, archive)
print(comparison)
```

## Debugging workflow

1. Запустить `python manage.py debug_dashboard`
2. Проверить `@archieves/debug/renders/`
3. Сравнить с `@archieves/now/dashboard.html`
4. Проверить context.json для диагностики данных
5. Исправить проблемы в секциях/шаблонах
6. Повторить

## Примеры проблем

### Пустой вывод данных
Проверить в `_context.json`:
- Наличие ключа `data`
- Структуру данных (`data.stats`, `data.system_health`)
- Значения (не None, не пустые)

### Template не найден
```
TemplateDoesNotExist: admin/sections/overview_section.html
```
Проверить:
- Путь к шаблону в `section.template_name`
- Наличие файла в `templates/admin/sections/`
- Правильность extends/include

### Ошибки импорта
Проверить:
- Наличие всех зависимостей
- Правильность импортов в секциях
- Доступность моделей/конфигов
