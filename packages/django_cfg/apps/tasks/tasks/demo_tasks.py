"""
Demo tasks for Tasks Dashboard demonstration.

These tasks are used to generate test data for the dashboard
and demonstrate different queue behaviors and execution times.
"""

import logging
import random
import time
from datetime import datetime

import dramatiq

logger = logging.getLogger(__name__)


@dramatiq.actor(queue_name='default')
def quick_task(task_id: str, duration: int = 2):
    """Quick processing task (2-3 seconds)."""
    logger.info(f'🚀 Quick task {task_id} started at {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(duration)
    logger.info(f'✅ Quick task {task_id} completed in {duration}s')
    return f'Quick task {task_id} done in {duration}s'


@dramatiq.actor(queue_name='background')
def medium_task(task_id: str, duration: int = 5):
    """Medium processing task (5-8 seconds)."""
    logger.info(f'🔄 Medium task {task_id} started at {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(duration)
    logger.info(f'✅ Medium task {task_id} completed in {duration}s')
    return f'Medium task {task_id} done in {duration}s'


@dramatiq.actor(queue_name='low')
def slow_task(task_id: str, duration: int = 10):
    """Slow processing task (10-15 seconds)."""
    logger.info(f'🐌 Slow task {task_id} started at {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(duration)
    logger.info(f'✅ Slow task {task_id} completed in {duration}s')
    return f'Slow task {task_id} done in {duration}s'


@dramatiq.actor(queue_name='critical')
def critical_task(task_id: str, duration: int = 3):
    """Critical processing task (2-4 seconds)."""
    logger.info(f'🔥 Critical task {task_id} started at {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(duration)
    logger.info(f'✅ Critical task {task_id} completed in {duration}s')
    return f'Critical task {task_id} done in {duration}s'


@dramatiq.actor(queue_name='payments')
def payment_task(task_id: str, amount: float):
    """Payment processing task (1-3 seconds)."""
    duration = random.randint(1, 3)
    logger.info(f'💳 Payment task {task_id} processing ${amount} at {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(duration)
    logger.info(f'✅ Payment task {task_id} completed in {duration}s')
    return f'Payment ${amount} processed in {duration}s'


@dramatiq.actor(queue_name='agents')
def agent_task(task_id: str, query: str):
    """AI agent processing task (3-7 seconds)."""
    duration = random.randint(3, 7)
    logger.info(f'🤖 Agent task {task_id} processing query "{query}" at {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(duration)
    logger.info(f'✅ Agent task {task_id} completed in {duration}s')
    return f'Agent processed query "{query}" in {duration}s'


@dramatiq.actor(queue_name='high')
def priority_task(task_id: str, priority_level: str):
    """High priority task (1-4 seconds)."""
    duration = random.randint(1, 4)
    logger.info(f'⚡ Priority task {task_id} ({priority_level}) started at {datetime.now().strftime("%H:%M:%S")}')
    time.sleep(duration)
    logger.info(f'✅ Priority task {task_id} completed in {duration}s')
    return f'Priority task {task_id} ({priority_level}) done in {duration}s'


def generate_demo_tasks() -> int:
    """
    Generate a variety of demo tasks for dashboard demonstration.
    
    Returns:
        Number of tasks created
    """
    tasks_count = 0

    # Quick tasks (3-5 tasks)
    for i in range(random.randint(3, 5)):
        quick_task.send(f'quick_{i+1}', random.randint(2, 3))
        tasks_count += 1

    # Medium tasks (2-4 tasks)
    for i in range(random.randint(2, 4)):
        medium_task.send(f'medium_{i+1}', random.randint(5, 8))
        tasks_count += 1

    # Slow tasks (1-2 tasks)
    for i in range(random.randint(1, 2)):
        slow_task.send(f'slow_{i+1}', random.randint(10, 15))
        tasks_count += 1

    # Critical tasks (2-3 tasks)
    for i in range(random.randint(2, 3)):
        critical_task.send(f'critical_{i+1}', random.randint(2, 4))
        tasks_count += 1

    # Payment tasks (1-3 tasks)
    for i in range(random.randint(1, 3)):
        amount = round(random.uniform(10.0, 500.0), 2)
        payment_task.send(f'payment_{i+1}', amount)
        tasks_count += 1

    # Agent tasks (1-2 tasks)
    for i in range(random.randint(1, 2)):
        queries = ['analyze data', 'generate report', 'process document', 'classify content']
        query = random.choice(queries)
        agent_task.send(f'agent_{i+1}', query)
        tasks_count += 1

    # Priority tasks (1-2 tasks)
    for i in range(random.randint(1, 2)):
        priority_levels = ['urgent', 'high', 'critical']
        priority = random.choice(priority_levels)
        priority_task.send(f'priority_{i+1}', priority)
        tasks_count += 1

    logger.info(f"Generated {tasks_count} demo tasks across all queues")
    return tasks_count
