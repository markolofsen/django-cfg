---
title: Task Management Dashboard
description: Django-CFG tasks feature guide. Production-ready task management dashboard with built-in validation, type safety, and seamless Django integration.
sidebar_label: Tasks
sidebar_position: 5
keywords:
  - django-cfg tasks
  - django tasks
  - tasks django-cfg
---

# Task Management Dashboard

Django-CFG includes a **comprehensive task management dashboard** for monitoring and managing background task queues, workers, and job processing.

## Overview

The Tasks app provides:
- **Real-time task monitoring** with live dashboard
- **Queue management** (pause, resume, clear queues)
- **Worker management** (start, stop, restart workers)
- **Task statistics** and performance metrics
- **Interactive web interface** with modern UI
- **REST API** for programmatic access
- **Background task processing** with Dramatiq integration

## Quick Start

### Enable Tasks in Configuration

```python
# config.py
from django_cfg import DjangoConfig, TaskConfig

class MyConfig(DjangoConfig):
    # Enable task management dashboard
    tasks: TaskConfig | None = TaskConfig(
        redis_url="redis://localhost:6379/2",
        processes=4,
        threads=8,
        queues=["default", "high", "low"],
        max_retries=3,
    )
```

### Access Task Dashboard

```bash
# Start Django server
python manage.py runserver

# Access dashboard at:
http://localhost:8000/admin/tasks/dashboard/
```

## Dashboard Features

### Real-time Monitoring

The task dashboard provides:
- **Live queue status** with real-time updates
- **Worker monitoring** with process information
- **Task statistics** and performance metrics
- **Queue management** controls
- **Task history** and execution logs

### Dashboard Interface

```html
<!-- Task Dashboard Layout -->
<div class="task-dashboard">
    <!-- Navigation Tabs -->
    <nav class="dashboard-tabs">
        <button class="tab-btn active" data-tab="overview">Overview</button>
        <button class="tab-btn" data-tab="queues">Queues</button>
        <button class="tab-btn" data-tab="workers">Workers</button>
        <button class="tab-btn" data-tab="tasks">Tasks</button>
    </nav>
    
    <!-- Overview Tab -->
    <div id="overview-tab" class="tab-content active">
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Tasks</h3>
                <span class="stat-value">1,234</span>
            </div>
            <div class="stat-card">
                <h3>Active Workers</h3>
                <span class="stat-value">4</span>
            </div>
            <div class="stat-card">
                <h3>Queue Length</h3>
                <span class="stat-value">56</span>
            </div>
        </div>
    </div>
    
    <!-- Queue Management -->
    <div id="queues-tab" class="tab-content">
        <div class="queue-controls">
            <button class="btn btn-success" onclick="pauseQueue('default')">Pause</button>
            <button class="btn btn-warning" onclick="resumeQueue('default')">Resume</button>
            <button class="btn btn-danger" onclick="clearQueue('default')">Clear</button>
        </div>
    </div>
</div>
```

## API Usage

### Task Management API

```python
# Get queue status
GET /api/tasks/queue-status/
{
    "queues": [
        {
            "name": "default",
            "size": 42,
            "is_paused": false,
            "workers": 2
        },
        {
            "name": "high",
            "size": 8,
            "is_paused": false,
            "workers": 1
        }
    ]
}

# Get task statistics
GET /api/tasks/task-statistics/
{
    "total_tasks": 1234,
    "completed_tasks": 1180,
    "failed_tasks": 12,
    "pending_tasks": 42,
    "success_rate": 95.6
}

# Manage queues
POST /api/tasks/queue-manage/
{
    "action": "pause",
    "queue_name": "default"
}

# Manage workers
POST /api/tasks/worker-manage/
{
    "action": "restart",
    "worker_id": "worker-1"
}
```

### Task Monitoring

```python
from django_cfg.apps.tasks.views import TaskManagementViewSet

# Get real-time task status
def get_task_dashboard_data():
    """Get comprehensive task dashboard data"""
    
    # Queue information
    queues = get_queue_status()
    
    # Worker information
    workers = get_worker_status()
    
    # Task statistics
    stats = get_task_statistics()
    
    return {
        'queues': queues,
        'workers': workers,
        'statistics': stats,
        'timestamp': timezone.now().isoformat()
    }

def get_queue_status():
    """Get status of all task queues"""
    from ...modules.django_tasks import DjangoTasks
    
    task_manager = DjangoTasks()
    return task_manager.get_queue_status()

def get_worker_status():
    """Get status of all workers"""
    from ...modules.django_tasks import DjangoTasks
    
    task_manager = DjangoTasks()
    return task_manager.get_worker_status()
```

## Queue Management

### Queue Operations

```python
from django_cfg.modules.django_tasks import DjangoTasks

class QueueManager:
    def __init__(self):
        self.task_manager = DjangoTasks()
    
    def pause_queue(self, queue_name: str):
        """Pause a specific queue"""
        return self.task_manager.pause_queue(queue_name)
    
    def resume_queue(self, queue_name: str):
        """Resume a paused queue"""
        return self.task_manager.resume_queue(queue_name)
    
    def clear_queue(self, queue_name: str):
        """Clear all tasks from a queue"""
        return self.task_manager.clear_queue(queue_name)
    
    def get_queue_info(self, queue_name: str):
        """Get detailed information about a queue"""
        return {
            'name': queue_name,
            'size': self.task_manager.get_queue_size(queue_name),
            'is_paused': self.task_manager.is_queue_paused(queue_name),
            'workers': self.task_manager.get_queue_workers(queue_name)
        }
```

### Worker Management

```python
class WorkerManager:
    def __init__(self):
        self.task_manager = DjangoTasks()
    
    def start_worker(self, queue_names: list = None):
        """Start a new worker"""
        return self.task_manager.start_worker(queue_names or ['default'])
    
    def stop_worker(self, worker_id: str):
        """Stop a specific worker"""
        return self.task_manager.stop_worker(worker_id)
    
    def restart_worker(self, worker_id: str):
        """Restart a specific worker"""
        self.stop_worker(worker_id)
        return self.start_worker()
    
    def get_worker_info(self):
        """Get information about all workers"""
        return self.task_manager.get_workers_info()
```

## Task Statistics

### Performance Metrics

```python
from django_cfg.apps.tasks.serializers import TaskStatisticsSerializer

class TaskAnalytics:
    def get_task_statistics(self, days: int = 7):
        """Get comprehensive task statistics"""
        
        stats = {
            # Basic counts
            'total_tasks': self.get_total_tasks(days),
            'completed_tasks': self.get_completed_tasks(days),
            'failed_tasks': self.get_failed_tasks(days),
            'pending_tasks': self.get_pending_tasks(),
            
            # Performance metrics
            'success_rate': self.calculate_success_rate(days),
            'avg_execution_time': self.get_avg_execution_time(days),
            'throughput': self.get_task_throughput(days),
            
            # Queue metrics
            'queue_lengths': self.get_queue_lengths(),
            'worker_utilization': self.get_worker_utilization(),
            
            # Trends
            'hourly_trends': self.get_hourly_trends(days),
            'daily_trends': self.get_daily_trends(days)
        }
        
        return stats
    
    def calculate_success_rate(self, days: int):
        """Calculate task success rate"""
        total = self.get_total_tasks(days)
        completed = self.get_completed_tasks(days)
        
        if total == 0:
            return 0.0
        
        return (completed / total) * 100
    
    def get_task_throughput(self, days: int):
        """Calculate tasks per hour"""
        total_tasks = self.get_total_tasks(days)
        hours = days * 24
        
        return total_tasks / hours if hours > 0 else 0
```

### Real-time Updates

```javascript
// Dashboard JavaScript for real-time updates
class TaskDashboard {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.initializeDashboard();
    }
    
    initializeDashboard() {
        this.startRealTimeUpdates();
        this.bindEventHandlers();
    }
    
    startRealTimeUpdates() {
        setInterval(() => {
            this.updateDashboardData();
        }, this.updateInterval);
    }
    
    async updateDashboardData() {
        try {
            // Fetch queue status
            const queueResponse = await fetch('/api/tasks/queue-status/');
            const queueData = await queueResponse.json();
            this.updateQueueDisplay(queueData);
            
            // Fetch task statistics
            const statsResponse = await fetch('/api/tasks/task-statistics/');
            const statsData = await statsResponse.json();
            this.updateStatistics(statsData);
            
        } catch (error) {
            console.error('Failed to update dashboard:', error);
        }
    }
    
    updateQueueDisplay(data) {
        data.queues.forEach(queue => {
            const queueElement = document.getElementById(`queue-${queue.name}`);
            if (queueElement) {
                queueElement.querySelector('.queue-size').textContent = queue.size;
                queueElement.querySelector('.worker-count').textContent = queue.workers;
                queueElement.classList.toggle('paused', queue.is_paused);
            }
        });
    }
    
    async manageQueue(action, queueName) {
        try {
            const response = await fetch('/api/tasks/queue-manage/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    action: action,
                    queue_name: queueName
                })
            });
            
            if (response.ok) {
                this.updateDashboardData(); // Refresh data
                this.showNotification(`Queue ${queueName} ${action}d successfully`);
            }
        } catch (error) {
            this.showError(`Failed to ${action} queue ${queueName}`);
        }
    }
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    new TaskDashboard();
});
```

## Dashboard Styling

### Modern UI Components

```css
/* Task Dashboard Styles */
.task-dashboard {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.dashboard-tabs {
    display: flex;
    border-bottom: 2px solid #e1e5e9;
    margin-bottom: 30px;
}

.tab-btn {
    padding: 12px 24px;
    border: none;
    background: none;
    cursor: pointer;
    font-weight: 500;
    color: #6c757d;
    border-bottom: 3px solid transparent;
    transition: all 0.3s ease;
}

.tab-btn.active {
    color: #007bff;
    border-bottom-color: #007bff;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.stat-card {
    background: white;
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-value {
    font-size: 2.5rem;
    font-weight: bold;
    color: #007bff;
    display: block;
    margin-top: 8px;
}

.queue-item {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.queue-item.paused {
    background: #fff3cd;
    border-left: 4px solid #ffc107;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    margin: 0 4px;
    transition: all 0.2s ease;
}

.btn-success { background: #28a745; color: white; }
.btn-warning { background: #ffc107; color: #212529; }
.btn-danger { background: #dc3545; color: white; }

.btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
```

## Management Commands

### Task Management Commands

```bash
# Start task workers
python manage.py rundramatiq --processes 4 --threads 8

# Check task status
python manage.py task_status --verbose

# Clear task queues
python manage.py task_clear --queue=default

# Task statistics
python manage.py task_stats --days=7

# Monitor task performance
python manage.py task_monitor --interval=5
```

### Custom Management Commands

```python
# management/commands/task_monitor.py
from django.core.management.base import BaseCommand
from django_cfg.modules.django_tasks import DjangoTasks

class Command(BaseCommand):
    help = 'Monitor task queues in real-time'
    
    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=5, help='Update interval in seconds')
    
    def handle(self, *args, **options):
        interval = options['interval']
        task_manager = DjangoTasks()
        
        while True:
            # Display queue status
            queues = task_manager.get_queue_status()
            self.display_queue_status(queues)
            
            time.sleep(interval)
    
    def display_queue_status(self, queues):
        self.stdout.write(self.style.SUCCESS('=== Task Queue Status ==='))
        for queue in queues:
            status = f"Queue: {queue['name']} | Size: {queue['size']} | Workers: {queue['workers']}"
            if queue['is_paused']:
                status += " | PAUSED"
            self.stdout.write(status)
```

## Integration Examples

### Custom Task Creation

```python
# Create custom tasks for monitoring
import dramatiq

@dramatiq.actor(queue_name="monitoring")
def system_health_check():
    """Periodic system health check task"""
    from django_cfg.apps.tasks.views import TaskManagementViewSet
    
    # Perform health checks
    stats = get_task_statistics()
    
    if stats['success_rate'] < 90:
        send_alert("Task success rate below 90%")
    
    if stats['pending_tasks'] > 1000:
        send_alert("High number of pending tasks")

# Schedule periodic tasks
from django_cfg.modules.django_tasks import DjangoTasks

task_manager = DjangoTasks()
task_manager.schedule_periodic_task(
    system_health_check,
    interval=300  # Every 5 minutes
)
```

### Webhook Integration

```python
# Webhook for external monitoring
from django_cfg.apps.tasks.views import TaskManagementViewSet

class TaskWebhookView(APIView):
    """Webhook endpoint for task monitoring"""
    
    def post(self, request):
        action = request.data.get('action')
        
        if action == 'get_status':
            return Response(get_task_dashboard_data())
        
        elif action == 'pause_queue':
            queue_name = request.data.get('queue_name')
            result = pause_queue(queue_name)
            return Response({'success': result})
        
        return Response({'error': 'Invalid action'}, status=400)
```

## Related Documentation

- [**Dramatiq Integration**](/features/integrations/dramatiq/overview) - Background task processing
- [**Configuration Guide**](/fundamentals/configuration) - Task configuration
- [**Deployment Guide**](/deployment/environment-setup) - Production setup
- [**Monitoring Guide**](/deployment/monitoring) - System monitoring

The Task Management system provides comprehensive task monitoring for your Django applications! ⚙️

TAGS: tasks, queues, workers, monitoring, dashboard, dramatiq
DEPENDS_ON: [dramatiq, redis, configuration]
USED_BY: [all-apps, background-processing, monitoring]
