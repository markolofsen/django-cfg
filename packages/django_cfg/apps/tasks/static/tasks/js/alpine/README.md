# Alpine.js Dashboard Modules

Модульная архитектура для Tasks Dashboard.

## Структура

```
alpine/
├── state.js              # Начальное состояние компонента
├── loaders/              # Загрузка данных из API
│   ├── overview.js       # Загрузка статистики
│   ├── queues.js         # Загрузка очередей
│   ├── workers.js        # Загрузка воркеров
│   ├── tasks.js          # Загрузка задач
│   └── index.js          # Экспорт всех loaders
├── actions/              # Действия пользователя
│   ├── management.js     # Управление (clear, purge, simulate)
│   ├── workers.js        # Управление воркерами
│   ├── tasks.js          # Управление задачами
│   ├── pagination.js     # Пагинация
│   └── index.js          # Экспорт всех actions
├── utils/                # Утилиты
│   ├── formatters.js     # Форматирование дат, времени
│   └── helpers.js        # Вспомогательные функции
└── index.js              # Главный файл, собирает все вместе
```

## Использование

```js
// Вместо:
<script src="{% static 'tasks/js/dashboard-alpine.js' %}"></script>

// Использовать:
<script type="module" src="{% static 'tasks/js/alpine/index.js' %}"></script>
```

## Статус

🚧 В РАЗРАБОТКЕ - пока используется монолитный `dashboard-alpine.js` (716 строк)

TODO:
- [ ] Создать все action модули
- [ ] Создать utils модули
- [ ] Протестировать модульную версию
- [ ] Переключить dashboard.html на модульную версию
- [ ] Удалить старый dashboard-alpine.js
