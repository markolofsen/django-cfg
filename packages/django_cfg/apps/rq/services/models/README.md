# RQ Internal Pydantic Models

Внутренние Pydantic модели для бизнес-логики RQ.

**ВАЖНО:** Все модели имеют **плоскую структуру** (никаких nested JSON)!

---

## 📁 Структура

```
services/models/
├── __init__.py       # Экспорт всех моделей
├── job.py            # RQJobModel, JobStatus
├── worker.py         # RQWorkerModel, WorkerState
├── queue.py          # RQQueueModel
├── event.py          # Event models для Centrifugo
└── README.md         # Этот файл
```

---

## 🎯 Назначение

### Разделение ответственности:

**`/serializers/`** (DRF Serializers):
- Для API endpoints (views)
- OpenAPI schema generation
- HTTP request/response validation

**`/services/models/`** (Pydantic Models):
- Внутренняя бизнес-логика
- Type safety для сервисов
- Валидация данных из RQ
- Computed properties и методы

---

## 📝 Модели

### 1. RQJobModel - Job данные

```python
from django_cfg.apps.rq.services.models import RQJobModel, JobStatus

job = RQJobModel(
    id="abc123",
    func_name="myapp.tasks.send_email",
    queue="default",
    status=JobStatus.FINISHED,
    created_at="2025-01-15T10:00:00Z",
    started_at="2025-01-15T10:00:05Z",
    ended_at="2025-01-15T10:00:10Z",
    worker_name="worker1.12345",
    timeout=180,
    result_ttl=500,
    args_json='["user@example.com", "Hello"]',
    kwargs_json='{"priority": "high"}',
    result_json='{"sent": true}',
)

# Properties
print(job.is_success)  # True
print(job.get_duration_seconds())  # 5.0
```

**Поля (все плоские!):**
- Базовые: `id`, `func_name`, `queue`, `status`
- Timestamps: `created_at`, `enqueued_at`, `started_at`, `ended_at` (ISO strings)
- Worker: `worker_name`
- Config: `timeout`, `result_ttl`, `failure_ttl`
- Data: `args_json`, `kwargs_json`, `meta_json`, `result_json` (JSON strings)
- Dependencies: `dependency_ids` (comma-separated)

**Properties:**
- `is_success` - успешность
- `is_failed` - провал
- `is_running` - выполняется
- `get_duration_seconds()` - длительность

---

### 2. RQWorkerModel - Worker данные

```python
from django_cfg.apps.rq.services.models import RQWorkerModel, WorkerState

worker = RQWorkerModel(
    name="worker1.12345",
    state=WorkerState.BUSY,
    queues="default,high,low",  # Comma-separated!
    current_job_id="abc123",
    birth="2025-01-15T08:00:00Z",
    last_heartbeat="2025-01-15T10:30:00Z",
    successful_job_count=450,
    failed_job_count=5,
    total_working_time=12500.5,
)

# Properties
print(worker.is_alive)  # True if heartbeat < 60s ago
print(worker.is_busy)  # True
print(worker.get_uptime_seconds())  # 9000.0
print(worker.get_queue_list())  # ['default', 'high', 'low']
print(worker.success_rate)  # 98.9%
```

**Поля (все плоские!):**
- Базовые: `name`, `state`, `queues` (comma-separated!)
- Current: `current_job_id`
- Timestamps: `birth`, `last_heartbeat` (ISO strings)
- Stats: `successful_job_count`, `failed_job_count`, `total_working_time`

**Properties:**
- `is_alive` - жив ли worker (heartbeat < 60s)
- `is_busy` / `is_idle` - состояние
- `get_uptime_seconds()` - время работы
- `get_queue_list()` - список очередей
- `total_job_count` - всего задач
- `success_rate` - процент успеха

---

### 3. RQQueueModel - Queue статистика

```python
from django_cfg.apps.rq.services.models import RQQueueModel

queue = RQQueueModel(
    name="default",
    is_async=True,
    count=45,
    queued_jobs=45,
    started_jobs=2,
    finished_jobs=1250,
    failed_jobs=12,
    deferred_jobs=0,
    scheduled_jobs=5,
    workers=3,
    oldest_job_timestamp="2025-01-15T09:15:00Z",
    connection_host="localhost",
    connection_port=6379,
    connection_db=0,
)

# Properties
print(queue.total_jobs)  # 1314
print(queue.completed_jobs)  # 1262
print(queue.failure_rate)  # 0.95%
print(queue.is_empty)  # False
print(queue.has_workers)  # True
print(queue.is_healthy)  # True
```

**Поля (все плоские!):**
- Базовые: `name`, `is_async`, `count`
- Job counts: `queued_jobs`, `started_jobs`, `finished_jobs`, `failed_jobs`, `deferred_jobs`, `scheduled_jobs`
- Workers: `workers`
- Metadata: `oldest_job_timestamp` (ISO string)
- Connection: `connection_host`, `connection_port`, `connection_db` (flat!)

**Properties:**
- `total_jobs` - всего задач
- `completed_jobs` - завершенных
- `failure_rate` - процент провалов
- `is_empty` - пустая ли очередь
- `has_workers` - есть ли workers
- `is_healthy` - здорова ли очередь

---

### 4. Event Models - для Centrifugo

#### JobEventModel

```python
from django_cfg.apps.rq.services.models import JobEventModel, EventType

event = JobEventModel(
    event_type=EventType.JOB_FINISHED,
    timestamp="2025-01-15T10:00:10Z",
    job_id="abc123",
    queue="default",
    func_name="myapp.tasks.send_email",
    status="finished",
    worker_name="worker1.12345",
    result_json='{"sent": true}',
    duration_seconds=5.0,
)
```

**Channel:** `rq:jobs`

**Поля (все плоские!):**
- Event: `event_type`, `timestamp`
- Job: `job_id`, `queue`, `func_name`
- Status: `status`, `worker_name`
- Result: `result_json` (JSON string), `error`
- Timing: `duration_seconds`

#### QueueEventModel

```python
from django_cfg.apps.rq.services.models import QueueEventModel, EventType

event = QueueEventModel(
    event_type=EventType.QUEUE_PURGED,
    timestamp="2025-01-15T10:00:00Z",
    queue="default",
    purged_count=45,
    job_count=0,
)
```

**Channel:** `rq:queues`

**Поля (все плоские!):**
- Event: `event_type`, `timestamp`
- Queue: `queue`
- Data: `purged_count`, `job_count`

#### WorkerEventModel

```python
from django_cfg.apps.rq.services.models import WorkerEventModel, EventType

event = WorkerEventModel(
    event_type=EventType.WORKER_STARTED,
    timestamp="2025-01-15T08:00:00Z",
    worker_name="worker1.12345",
    queues="default,high,low",  # Comma-separated!
    state="idle",
    successful_job_count=0,
    failed_job_count=0,
    total_working_time=0.0,
)
```

**Channel:** `rq:workers`

**Поля (все плоские!):**
- Event: `event_type`, `timestamp`
- Worker: `worker_name`, `queues` (comma-separated!)
- State: `state`, `current_job_id`
- Stats: `successful_job_count`, `failed_job_count`, `total_working_time`

---

## 💡 Примеры использования

### Пример 1: Валидация Job данных

```python
from rq.job import Job
from django_cfg.apps.rq.services.models import RQJobModel

def validate_job(job: Job) -> RQJobModel:
    """Validate RQ job with Pydantic."""
    import json

    return RQJobModel(
        id=job.id,
        func_name=job.func_name,
        queue="default",  # or extract from job
        status=job.get_status(),
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        ended_at=job.ended_at.isoformat() if job.ended_at else None,
        worker_name=job.worker_name,
        timeout=job.timeout,
        result_ttl=job.result_ttl,
        failure_ttl=job.failure_ttl,
        args_json=json.dumps(list(job.args or [])),
        kwargs_json=json.dumps(job.kwargs or {}),
        meta_json=json.dumps(job.meta or {}),
        result_json=json.dumps(job.result) if job.result else None,
        exc_info=job.exc_info,
        dependency_ids=",".join(job._dependency_ids or []),
    )

# Usage
job = Job.fetch("abc123", connection=...)
validated_job = validate_job(job)
print(validated_job.is_success)
print(validated_job.get_duration_seconds())
```

### Пример 2: Публикация события в Centrifugo

```python
from datetime import datetime
from django_cfg.apps.rq.services.models import JobEventModel, EventType

def publish_job_completed(job_model: RQJobModel):
    """Publish job completion event."""
    from django_cfg.apps.rq.services.centrifugo_publisher import publish_to_channel

    event = JobEventModel(
        event_type=EventType.JOB_FINISHED,
        timestamp=datetime.now().isoformat(),
        job_id=job_model.id,
        queue=job_model.queue,
        func_name=job_model.func_name,
        status=job_model.status,
        worker_name=job_model.worker_name,
        result_json=job_model.result_json,
        duration_seconds=job_model.get_duration_seconds(),
    )

    # Pydantic validates and serializes to flat JSON
    publish_to_channel("rq:jobs", event.model_dump())
```

### Пример 3: Бизнес-логика с типизацией

```python
from typing import List
from django_cfg.apps.rq.services.models import RQJobModel

def calculate_avg_duration(jobs: List[RQJobModel]) -> float:
    """Calculate average job duration with type safety."""
    durations = [j.get_duration_seconds() for j in jobs if j.get_duration_seconds()]

    if not durations:
        return 0.0

    return sum(durations) / len(durations)

def get_failed_jobs(jobs: List[RQJobModel]) -> List[RQJobModel]:
    """Filter failed jobs with type safety."""
    return [j for j in jobs if j.is_failed]

def group_by_queue(jobs: List[RQJobModel]) -> dict[str, List[RQJobModel]]:
    """Group jobs by queue with type safety."""
    result = {}
    for job in jobs:
        if job.queue not in result:
            result[job.queue] = []
        result[job.queue].append(job)
    return result
```

---

## ⚠️ Важные правила

### 1. NO NESTED JSON!

❌ **НЕПРАВИЛЬНО:**
```python
class BadJobModel(BaseModel):
    id: str
    config: JobConfig  # NESTED!
    result: dict  # NESTED!
```

✅ **ПРАВИЛЬНО:**
```python
class GoodJobModel(BaseModel):
    id: str
    config_timeout: int
    config_ttl: int
    result_json: str  # JSON string!
```

### 2. JSON как строки

Для сложных данных используем JSON strings:
```python
args_json: str = '["arg1", "arg2"]'
kwargs_json: str = '{"key": "value"}'
result_json: str = '{"success": true}'
```

### 3. Списки как comma-separated строки

```python
queues: str = "default,high,low"
dependency_ids: str = "id1,id2,id3"

# Получение списка:
queue_list = queues.split(",")
```

### 4. Timestamps как ISO strings

```python
created_at: str = "2025-01-15T10:00:00Z"

# Преобразование:
dt = datetime.fromisoformat(created_at)
```

---

## 🎯 Когда использовать

**Используй Pydantic models когда:**
- Нужна валидация данных из RQ
- Нужна типизация для IDE/mypy
- Нужны computed properties
- Нужна бизнес-логика (расчеты, фильтры)
- Готовишь данные для Centrifugo

**НЕ используй Pydantic models для:**
- API endpoints (используй DRF Serializers)
- OpenAPI schema (используй DRF Serializers)
- HTTP request/response (используй DRF Serializers)

---

## 📚 См. также

- `/serializers/` - DRF Serializers для API
- `/services/centrifugo_publisher.py` - публикация событий
- `/services/config_helper.py` - работа с конфигом
