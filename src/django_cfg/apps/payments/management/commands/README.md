# Currency Management Commands

Management команды для работы с валютами в Universal Payments System.

## Команды

### 🪙 `populate_currencies` - Первоначальное заполнение

Заполняет пустую базу данных валютами из внешних API (CoinGecko, YFinance).

```bash
# Быстрое заполнение (50 криптовалют + 20 фиатных)
python manage.py populate_currencies --quick

# Стандартное заполнение (200 криптовалют + 30 фиатных)
python manage.py populate_currencies

# Только криптовалюты
python manage.py populate_currencies --crypto-only

# Только фиатные валюты
python manage.py populate_currencies --fiat-only

# Пропустить существующие валюты
python manage.py populate_currencies --skip-existing
```

### 🔄 `update_currencies` - Обновление курсов

Обновляет курсы валют с внешних API.

```bash
# Обновить устаревшие курсы (старше 6 часов)
python manage.py update_currencies

# Принудительно обновить все валюты
python manage.py update_currencies --force-update

# Сухой прогон (показать что будет обновлено)
python manage.py update_currencies --dry-run

# Кастомные лимиты
python manage.py update_currencies --max-crypto 100 --max-fiat 30

# Исключить стейблкоины
python manage.py update_currencies --exclude-stablecoins

# Подробный вывод
python manage.py update_currencies --verbose
```

### 📊 `currency_stats` - Статистика валют

Показывает статистику базы данных валют.

```bash
# Базовая статистика
python manage.py currency_stats

# Детальная статистика
python manage.py currency_stats --detailed

# Показать топ-10 валют
python manage.py currency_stats --top 10

# Проверить устаревшие курсы
python manage.py currency_stats --check-rates

# Экспортировать в CSV
python manage.py currency_stats --export-csv currencies.csv
```

## Автоматизация

### Cron для регулярного обновления

```bash
# Обновлять курсы каждые 6 часов
0 */6 * * * cd /path/to/project && poetry run python manage.py update_currencies

# Ежедневная проверка статистики
0 9 * * * cd /path/to/project && poetry run python manage.py currency_stats --check-rates
```

### Docker

```bash
# В Docker контейнере
docker exec -it container_name poetry run python manage.py populate_currencies --quick
docker exec -it container_name poetry run python manage.py update_currencies
```

## Примеры использования

### Первоначальная настройка

```bash
# 1. Заполнить базу данных валютами
python manage.py populate_currencies --quick

# 2. Проверить результат
python manage.py currency_stats
```

### Регулярное обслуживание

```bash
# 1. Обновить курсы
python manage.py update_currencies --verbose

# 2. Проверить устаревшие курсы
python manage.py currency_stats --check-rates

# 3. При необходимости - принудительное обновление
python manage.py update_currencies --force-update
```

### Production обслуживание

```bash
# Обновление с минимальными API запросами
python manage.py update_currencies --max-crypto 50 --max-fiat 20

# Мониторинг состояния
python manage.py currency_stats --detailed --export-csv daily_report.csv
```

## Интеграция с django_currency

Команды используют модуль `django_currency.database.database_loader` для:

- ✅ Получения списка валют с CoinGecko
- ✅ Загрузки курсов фиатных валют с YFinance  
- ✅ Rate limiting для защиты от API throttling
- ✅ Кэширования для оптимизации производительности
- ✅ Pydantic валидации для типобезопасности

## Конфигурация

Настройки в `DatabaseLoaderConfig`:

```python
config = DatabaseLoaderConfig(
    max_cryptocurrencies=500,        # Максимум криптовалют
    max_fiat_currencies=50,          # Максимум фиатных валют  
    min_market_cap_usd=1_000_000,    # Минимальная капитализация
    coingecko_delay=1.5,             # Задержка между запросами
    yfinance_delay=0.5,              # Задержка для YFinance
    exclude_stablecoins=False,       # Исключить стейблкоины
    cache_ttl_hours=24               # TTL кэша в часах
)
```

## Мониторинг

### Логи

Команды логируют в `django_cfg.apps.payments.management.commands`:

```python
import logging
logger = logging.getLogger('django_cfg.apps.payments.management.commands')
```

### Метрики

- Количество созданных/обновленных валют
- Время выполнения API запросов
- Ошибки валидации и API
- Статистика курсов валют

## Безопасность

- ✅ Rate limiting для API запросов
- ✅ Atomic транзакции для консистентности
- ✅ Graceful handling ошибок API
- ✅ Валидация данных с Pydantic
- ✅ Rollback при критических ошибках
