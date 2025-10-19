---
title: Background Tasks Commands
description: Django-CFG CLI background tasks commands. Command-line interface for background tasks commands with examples, options, and production workflows.
sidebar_label: Background Tasks
sidebar_position: 7
keywords:
  - django-cfg background tasks
  - django-cfg command background tasks
  - cli background tasks
---

# Background Tasks Commands

Commands for managing Dramatiq background task workers, queues, and task monitoring.

## Worker Management

### `rundramatiq`

Run Dramatiq background task workers with Django settings integration.

```bash
python manage.py rundramatiq [OPTIONS]
```

**Options:**
- `--processes, -p INTEGER` - Number of worker processes (default: 2)
- `--threads, -t INTEGER` - Threads per process (default: 4)
- `--queues, -q TEXT` - Comma-separated list of queues to process
- `--watch` - Auto-restart on code changes (development only)

**Examples:**

```bash
# Start workers with default settings
python manage.py rundramatiq

# Start with specific number of processes and threads
python manage.py rundramatiq --processes 4 --threads 8

# Start workers for specific queues
python manage.py rundramatiq --queues default,high,low

# Development mode with auto-restart
python manage.py rundramatiq --watch

# Production: high capacity
python manage.py rundramatiq --processes 8 --threads 16

# Priority queue only
python manage.py rundramatiq --queues high --processes 2
```

---

## Task Monitoring

### `task_status`

Show Dramatiq task status and queue information.

```bash
python manage.py task_status [OPTIONS]
```

**Options:**
- `--queue TEXT` - Show status for specific queue
- `--verbose, -v` - Show detailed task information
- `--format [json|yaml|table]` - Output format (default: table)

**Examples:**

```bash
# Show status for all queues
python manage.py task_status

# Show status for specific queue
python manage.py task_status --queue high

# Show detailed task information
python manage.py task_status --verbose

# Export status as JSON
python manage.py task_status --format json
```

**Output:**
```
📊 Dramatiq Task Status
==================================================
Queues:
  default:  123 pending, 5 processing
  high:     45 pending, 3 processing
  low:      234 pending, 2 processing

Workers:
  Process 1: 4 tasks completed
  Process 2: 3 tasks completed

Recent Tasks:
  ✅ process_document (completed in 2.3s)
  ⏳ generate_report (processing...)
  ✅ send_email (completed in 0.5s)
```

---

## Queue Management

### `task_clear`

Clear Dramatiq task queues.

```bash
python manage.py task_clear [OPTIONS]
```

**Options:**
- `--all` - Clear all queues
- `--queue TEXT` - Clear specific queue
- `--failed-only` - Clear failed tasks only

**Examples:**

```bash
# Clear all queues
python manage.py task_clear --all

# Clear specific queue
python manage.py task_clear --queue default

# Clear failed tasks only
python manage.py task_clear --failed-only

# Clear specific queue failed tasks
python manage.py task_clear --queue high --failed-only
```

---

## Task Testing

### `test_tasks`

Test Dramatiq task processing pipeline.

```bash
python manage.py test_tasks [OPTIONS]
```

**Options:**
- `--document-id INTEGER` - Test with specific document ID
- `--queue TEXT` - Test specific queue

**Examples:**

```bash
# Test basic task processing
python manage.py test_tasks

# Test with specific document ID
python manage.py test_tasks --document-id 123

# Test specific queue
python manage.py test_tasks --queue knowledge
```

---

## Production Deployment

### Systemd Service

Create `/etc/systemd/system/dramatiq.service`:

```ini
[Unit]
Description=Dramatiq Workers
After=network.target redis.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/project/.venv/bin"
ExecStart=/path/to/project/.venv/bin/python manage.py rundramatiq --processes 4 --threads 8
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Commands:**
```bash
# Start service
sudo systemctl start dramatiq

# Enable on boot
sudo systemctl enable dramatiq

# Check status
sudo systemctl status dramatiq

# View logs
sudo journalctl -u dramatiq -f
```

---

### Docker Compose

Add to `docker-compose.yml`:

```yaml
services:
  dramatiq:
    build: .
    command: python manage.py rundramatiq --processes 4
    depends_on:
      - redis
      - postgres
    environment:
      - REDIS_URL=redis://redis:6379/0
    restart: unless-stopped
```

---

### Supervisor Configuration

Create `/etc/supervisor/conf.d/dramatiq.conf`:

```ini
[program:dramatiq]
command=/path/to/project/.venv/bin/python manage.py rundramatiq --processes 4
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/dramatiq/worker.log
```

**Commands:**
```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start workers
sudo supervisorctl start dramatiq

# Check status
sudo supervisorctl status dramatiq
```

---

## Queue Configuration

### Creating Custom Queues

```python
# tasks.py
import dramatiq

# Default queue
@dramatiq.actor
def process_data(data):
    pass

# High priority queue
@dramatiq.actor(queue_name="high")
def urgent_task(data):
    pass

# Low priority queue
@dramatiq.actor(queue_name="low")
def background_cleanup():
    pass

# Knowledge base queue
@dramatiq.actor(queue_name="knowledge")
def process_document(doc_id):
    pass
```

### Running Specific Queues

```bash
# Run only high priority
python manage.py rundramatiq --queues high --processes 4

# Run multiple queues
python manage.py rundramatiq --queues default,high,low

# Separate processes for different queues
# Terminal 1: High priority
python manage.py rundramatiq --queues high --processes 4

# Terminal 2: Default
python manage.py rundramatiq --queues default --processes 2

# Terminal 3: Low priority
python manage.py rundramatiq --queues low --processes 1
```

---

## Monitoring & Debugging

### Real-time Monitoring

```bash
# Watch task status in real-time
watch -n 2 'python manage.py task_status'

# Monitor specific queue
watch -n 1 'python manage.py task_status --queue high'
```

### Check Worker Health

```bash
# Check if workers are running
ps aux | grep rundramatiq

# Check Redis connection
redis-cli ping

# Check queue sizes
redis-cli llen dramatiq:default
redis-cli llen dramatiq:high
redis-cli llen dramatiq:low
```

### Debug Task Failures

```bash
# Show verbose status
python manage.py task_status --verbose

# Check failed tasks
python manage.py task_clear --failed-only --dry-run

# Clear and retry
python manage.py task_clear --failed-only
```

---

## Performance Tuning

### Optimal Worker Configuration

```bash
# Light workload (development)
python manage.py rundramatiq --processes 1 --threads 2

# Medium workload
python manage.py rundramatiq --processes 2 --threads 4

# Heavy workload
python manage.py rundramatiq --processes 4 --threads 8

# Very heavy workload
python manage.py rundramatiq --processes 8 --threads 16
```

### Queue Priority Strategy

```bash
# Dedicated high-priority workers
python manage.py rundramatiq --queues high --processes 4 &

# Shared workers for default and low
python manage.py rundramatiq --queues default,low --processes 2 &
```

---

## Common Workflows

### Development Setup

```bash
# 1. Start Redis
docker run -d -p 6379:6379 redis:alpine

# 2. Start workers with auto-reload
python manage.py rundramatiq --watch

# 3. Monitor tasks
python manage.py task_status
```

### Production Deployment

```bash
# 1. Start workers as systemd service
sudo systemctl start dramatiq

# 2. Monitor status
python manage.py task_status

# 3. Check logs
sudo journalctl -u dramatiq -f
```

### Task Queue Maintenance

```bash
# 1. Check queue sizes
python manage.py task_status

# 2. Clear old failed tasks
python manage.py task_clear --failed-only

# 3. Restart workers
sudo systemctl restart dramatiq
```

---

## Best Practices

### 1. Use Appropriate Queue Names

```python
# ✅ GOOD - Descriptive queue names
@dramatiq.actor(queue_name="email")
@dramatiq.actor(queue_name="reports")
@dramatiq.actor(queue_name="notifications")

# ❌ BAD - Generic names
@dramatiq.actor(queue_name="queue1")
@dramatiq.actor(queue_name="q")
```

### 2. Set Worker Count Based on Workload

```bash
# CPU-intensive tasks: fewer processes, more threads
python manage.py rundramatiq --processes 2 --threads 8

# I/O-intensive tasks: more processes, fewer threads
python manage.py rundramatiq --processes 8 --threads 2
```

### 3. Monitor Queue Sizes

```bash
# Alert if queue too large
QUEUE_SIZE=$(redis-cli llen dramatiq:default)
if [ $QUEUE_SIZE -gt 1000 ]; then
  echo "Alert: Queue size is $QUEUE_SIZE"
fi
```

### 4. Regular Queue Cleanup

```bash
# Weekly cleanup
0 3 * * 0 python manage.py task_clear --failed-only
```

### 5. Use Development Mode Wisely

```bash
# ✅ GOOD - Development only
python manage.py rundramatiq --watch

# ❌ BAD - Never in production
# --watch causes unnecessary restarts
```

---

## Troubleshooting

### Workers Not Starting

```bash
# Check Redis connection
redis-cli ping

# Check for port conflicts
lsof -i :6379

# Check worker logs
sudo journalctl -u dramatiq -n 50
```

### Tasks Not Processing

```bash
# Check worker status
python manage.py task_status

# Restart workers
sudo systemctl restart dramatiq

# Clear stuck tasks
python manage.py task_clear --queue default
```

### High Memory Usage

```bash
# Reduce threads per process
python manage.py rundramatiq --processes 4 --threads 2

# Or reduce processes
python manage.py rundramatiq --processes 2 --threads 4
```

---

## Related Documentation

- **[Quick Reference](./quick-reference)** - Fast command lookup
- **[Dramatiq Integration](/features/integrations/dramatiq/overview)** - Complete documentation
- **[Core Commands](./core-commands)** - Project setup

---

**Background tasks made easy!** 🔄
