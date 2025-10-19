"""
Django management command for simulating Dramatiq tasks and workers.

Usage:
    python manage.py rundramatiq_simulator --help
    python manage.py rundramatiq_simulator --workers 5
    python manage.py rundramatiq_simulator --clear-only
    python manage.py rundramatiq_simulator --show-keys
"""

import json
import random
import time
from datetime import datetime, timezone
from typing import Any, Dict

import redis
from django.core.management.base import BaseCommand, CommandError

from django_cfg.modules.django_tasks import DjangoTasks


class TaskSimulator:
    """Task data simulator for Tasks Dashboard."""

    def __init__(self):
        """Initialize the simulator."""
        self.tasks_service = DjangoTasks()

        # Get Redis client using the same logic as DjangoTasks
        try:
            redis_url = self.tasks_service.get_redis_url()
            if not redis_url:
                raise RuntimeError("No Redis URL available")

            # Parse URL for connection
            from urllib.parse import urlparse
            parsed = urlparse(redis_url)

            self.redis_client = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=int(parsed.path.lstrip('/')) if parsed.path else 1,
                decode_responses=True
            )

        except Exception as e:
            raise CommandError(f"Failed to connect to Redis: {e}")

        # Get queue configuration
        try:
            config = self.tasks_service.get_config()
            self.queues = config.tasks.dramatiq.queues
        except Exception:
            # Use default queues if we can't get configuration
            self.queues = ['critical', 'high', 'default', 'low', 'background', 'payments', 'agents', 'knowbase']

    def clear_all_data(self) -> int:
        """
        Clear all test data.
        
        Returns:
            Number of deleted keys
        """
        keys = self.redis_client.keys("dramatiq:*")
        if keys:
            deleted = self.redis_client.delete(*keys)
            return deleted
        return 0

    def simulate_queues(self, pending_tasks_per_queue=None, failed_tasks_per_queue=None) -> Dict[str, Dict[str, int]]:
        """
        Simulate queues with tasks.
        
        Args:
            pending_tasks_per_queue: Dict[str, int] - number of pending tasks per queue
            failed_tasks_per_queue: Dict[str, int] - number of failed tasks per queue
            
        Returns:
            Dict with information about created tasks
        """
        if pending_tasks_per_queue is None:
            pending_tasks_per_queue = {
                'critical': 2,
                'high': 5,
                'default': 12,
                'low': 8,
                'background': 15,
                'payments': 3,
                'agents': 7,
                'knowbase': 4
            }

        if failed_tasks_per_queue is None:
            failed_tasks_per_queue = {
                'critical': 0,
                'high': 1,
                'default': 3,
                'low': 2,
                'background': 1,
                'payments': 0,
                'agents': 1,
                'knowbase': 0
            }

        results = {}

        for queue_name in self.queues:
            queue_results = {'pending': 0, 'failed': 0}

            # Pending tasks
            pending_count = pending_tasks_per_queue.get(queue_name, 0)
            if pending_count > 0:
                queue_key = f"dramatiq:default.DQ.{queue_name}"

                # Add fake tasks to queue
                for i in range(pending_count):
                    task_data = {
                        "queue_name": queue_name,
                        "actor_name": f"process_{queue_name}_task",
                        "args": [f"task_{i}"],
                        "kwargs": {},
                        "options": {},
                        "message_id": f"msg_{queue_name}_{i}_{int(time.time())}",
                        "message_timestamp": int(time.time() * 1000)
                    }
                    self.redis_client.lpush(queue_key, json.dumps(task_data))

                queue_results['pending'] = pending_count

            # Failed tasks
            failed_count = failed_tasks_per_queue.get(queue_name, 0)
            if failed_count > 0:
                failed_key = f"dramatiq:default.DQ.{queue_name}.failed"

                # Add fake failed tasks
                for i in range(failed_count):
                    failed_task_data = {
                        "queue_name": queue_name,
                        "actor_name": f"failed_{queue_name}_task",
                        "args": [f"failed_task_{i}"],
                        "kwargs": {},
                        "options": {},
                        "message_id": f"failed_msg_{queue_name}_{i}_{int(time.time())}",
                        "message_timestamp": int(time.time() * 1000),
                        "error": f"Simulated error for {queue_name} task {i}"
                    }
                    self.redis_client.lpush(failed_key, json.dumps(failed_task_data))

                queue_results['failed'] = failed_count

            if queue_results['pending'] > 0 or queue_results['failed'] > 0:
                results[queue_name] = queue_results

        return results

    def simulate_workers(self, worker_count=3) -> list:
        """
        Симулировать активных воркеров.
        
        Args:
            worker_count: Количество воркеров для симуляции
            
        Returns:
            Список ID созданных воркеров
        """
        worker_ids = []

        for i in range(worker_count):
            worker_id = f"worker_{i}_{int(time.time())}"
            worker_key = f"dramatiq:worker:{worker_id}"

            worker_data = {
                "worker_id": worker_id,
                "hostname": "localhost",
                "pid": 1000 + i,
                "queues": self.queues,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                "status": "active"
            }

            # Устанавливаем данные воркера с TTL
            self.redis_client.setex(
                worker_key,
                300,  # 5 минут TTL
                json.dumps(worker_data)
            )

            worker_ids.append(worker_id)

        return worker_ids

    def simulate_task_statistics(self) -> Dict[str, Any]:
        """
        Симулировать статистику задач.
        
        Returns:
            Созданная статистика
        """
        stats_data = {
            "total_processed": random.randint(1000, 2000),
            "total_failed": random.randint(30, 80),
            "total_retried": random.randint(15, 40),
            "processing_time_avg": round(random.uniform(1.5, 4.0), 2),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

        stats_key = "dramatiq:stats"
        self.redis_client.setex(stats_key, 3600, json.dumps(stats_data))

        return stats_data

    def run_simulation(self, workers=3, clear_first=True) -> Dict[str, Any]:
        """
        Запустить полную симуляцию.
        
        Args:
            workers: Количество воркеров
            clear_first: Очистить данные перед симуляцией
            
        Returns:
            Результаты симуляции
        """
        results = {
            'cleared_keys': 0,
            'queues': {},
            'workers': [],
            'statistics': {}
        }

        if clear_first:
            results['cleared_keys'] = self.clear_all_data()

        results['queues'] = self.simulate_queues()
        results['workers'] = self.simulate_workers(workers)
        results['statistics'] = self.simulate_task_statistics()

        return results

    def get_redis_summary(self) -> Dict[str, Any]:
        """Получить сводку по данным в Redis."""
        summary = {
            'total_keys': 0,
            'queues': {},
            'workers': 0,
            'statistics': None
        }

        # Подсчитываем все ключи
        all_keys = self.redis_client.keys("dramatiq:*")
        summary['total_keys'] = len(all_keys)

        # Анализируем очереди
        for queue_name in self.queues:
            pending_key = f"dramatiq:default.DQ.{queue_name}"
            failed_key = f"dramatiq:default.DQ.{queue_name}.failed"

            pending = self.redis_client.llen(pending_key)
            failed = self.redis_client.llen(failed_key)

            if pending > 0 or failed > 0:
                summary['queues'][queue_name] = {
                    'pending': pending,
                    'failed': failed
                }

        # Подсчитываем воркеров
        worker_keys = self.redis_client.keys("dramatiq:worker:*")
        summary['workers'] = len(worker_keys)

        # Получаем статистику
        stats_key = "dramatiq:stats"
        if self.redis_client.exists(stats_key):
            try:
                stats_data = self.redis_client.get(stats_key)
                summary['statistics'] = json.loads(stats_data)
            except:
                pass

        return summary


class Command(BaseCommand):
    """Django management command для симуляции Dramatiq данных."""

    # Web execution metadata
    web_executable = False
    requires_input = False
    is_destructive = False

    help = 'Simulate Dramatiq tasks and workers for dashboard testing'

    def add_arguments(self, parser):
        """Добавить аргументы команды."""
        parser.add_argument(
            '--workers',
            type=int,
            default=3,
            help='Number of workers to simulate (default: 3)'
        )

        parser.add_argument(
            '--no-clear',
            action='store_true',
            help='Do not clear existing data before simulation'
        )

        parser.add_argument(
            '--clear-only',
            action='store_true',
            help='Only clear data, do not simulate'
        )

        parser.add_argument(
            '--show-keys',
            action='store_true',
            help='Show Redis keys after operation'
        )

        parser.add_argument(
            '--summary',
            action='store_true',
            help='Show summary of current Redis data'
        )

    def handle(self, *args, **options):
        """Выполнить команду."""
        try:
            simulator = TaskSimulator()

            # Показать только сводку
            if options['summary']:
                self.show_summary(simulator)
                return

            # Только очистка
            if options['clear_only']:
                self.stdout.write("🧹 Clearing all test data...")
                cleared = simulator.clear_all_data()
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Cleared {cleared} Redis keys")
                )
                return

            # Полная симуляция
            self.stdout.write("🎭 Starting Dramatiq Task Simulation")
            self.stdout.write("=" * 50)

            results = simulator.run_simulation(
                workers=options['workers'],
                clear_first=not options['no_clear']
            )

            # Показываем результаты
            if results['cleared_keys'] > 0:
                self.stdout.write(f"🧹 Cleared {results['cleared_keys']} existing keys")

            self.stdout.write("📋 Created queues:")
            total_pending = 0
            total_failed = 0

            for queue_name, counts in results['queues'].items():
                pending = counts['pending']
                failed = counts['failed']
                total_pending += pending
                total_failed += failed

                self.stdout.write(f"   {queue_name}: {pending} pending, {failed} failed")

            self.stdout.write(f"👷 Created {len(results['workers'])} workers")
            self.stdout.write("📊 Added task statistics")

            self.stdout.write("=" * 50)
            self.stdout.write(self.style.SUCCESS("✅ Simulation completed!"))

            self.stdout.write("\n📊 Summary:")
            active_queues = len(results['queues'])
            self.stdout.write(f"   Active Queues: {active_queues}")
            self.stdout.write(f"   Active Workers: {len(results['workers'])}")
            self.stdout.write(f"   Pending Tasks: {total_pending}")
            self.stdout.write(f"   Failed Tasks: {total_failed}")

            self.stdout.write("\n🌐 Dashboard URL: http://localhost:8000/cfg/admin/django_cfg_tasks/admin/dashboard/")

            # Показать ключи если запрошено
            if options['show_keys']:
                self.show_redis_keys(simulator)

        except Exception as e:
            raise CommandError(f"Simulation failed: {e}")

    def show_summary(self, simulator: TaskSimulator):
        """Показать сводку текущих данных."""
        self.stdout.write("📊 Current Redis Data Summary")
        self.stdout.write("=" * 40)

        summary = simulator.get_redis_summary()

        self.stdout.write(f"Total Redis keys: {summary['total_keys']}")
        self.stdout.write(f"Active workers: {summary['workers']}")

        if summary['queues']:
            self.stdout.write("\nQueues:")
            for queue_name, counts in summary['queues'].items():
                self.stdout.write(f"   {queue_name}: {counts['pending']} pending, {counts['failed']} failed")
        else:
            self.stdout.write("\nNo active queues found")

        if summary['statistics']:
            stats = summary['statistics']
            self.stdout.write("\nStatistics:")
            self.stdout.write(f"   Total processed: {stats.get('total_processed', 'N/A')}")
            self.stdout.write(f"   Total failed: {stats.get('total_failed', 'N/A')}")
            self.stdout.write(f"   Avg processing time: {stats.get('processing_time_avg', 'N/A')}s")

    def show_redis_keys(self, simulator: TaskSimulator):
        """Показать все Redis ключи."""
        self.stdout.write("\n🔍 Redis Keys:")
        keys = simulator.redis_client.keys("dramatiq:*")

        if not keys:
            self.stdout.write("   No Dramatiq keys found")
            return

        for key in sorted(keys):
            key_type = simulator.redis_client.type(key)
            if key_type == 'list':
                length = simulator.redis_client.llen(key)
                self.stdout.write(f"   {key} (list): {length} items")
            elif key_type == 'string':
                ttl = simulator.redis_client.ttl(key)
                ttl_str = f"TTL {ttl}s" if ttl > 0 else "no TTL"
                self.stdout.write(f"   {key} (string): {ttl_str}")
            else:
                self.stdout.write(f"   {key} ({key_type})")
