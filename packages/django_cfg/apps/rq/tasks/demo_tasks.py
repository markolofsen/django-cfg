"""
Demo tasks for RQ testing and simulation.

These tasks provide various scenarios for testing RQ functionality:
- Successful completion
- Failure scenarios
- Long-running tasks
- Progress tracking
- Crash simulation
- Retry logic
"""

import time
import random
from django_cfg.modules.django_logging import get_logger

logger = get_logger("rq.demo_tasks")


def demo_success_task(duration: int = 2, message: str = "Demo task completed"):
    """
    Simple task that always succeeds.

    Args:
        duration: How long to run (seconds)
        message: Custom message to return

    Returns:
        dict: Success result with message and metadata
    """
    logger.info(f"Starting demo_success_task (duration={duration}s)")
    time.sleep(duration)

    result = {
        "status": "success",
        "message": message,
        "duration": duration,
        "timestamp": time.time(),
    }

    logger.info(f"Completed demo_success_task: {result}")
    return result


def demo_failure_task(error_message: str = "Simulated failure"):
    """
    Task that always fails with an exception.

    Args:
        error_message: Custom error message

    Raises:
        ValueError: Always raises this exception
    """
    logger.warning(f"Starting demo_failure_task (will fail with: {error_message})")
    time.sleep(1)
    raise ValueError(error_message)


def demo_slow_task(duration: int = 30, step_interval: int = 5):
    """
    Long-running task for testing worker timeouts and monitoring.

    Args:
        duration: Total duration (seconds)
        step_interval: How often to log progress (seconds)

    Returns:
        dict: Success result with timing info
    """
    logger.info(f"Starting demo_slow_task (duration={duration}s)")

    steps = duration // step_interval
    for i in range(steps):
        time.sleep(step_interval)
        progress = ((i + 1) / steps) * 100
        logger.info(f"Progress: {progress:.1f}%")

    result = {
        "status": "success",
        "message": "Slow task completed",
        "duration": duration,
        "steps": steps,
    }

    logger.info(f"Completed demo_slow_task: {result}")
    return result


def demo_progress_task(total_items: int = 100):
    """
    Task that updates progress in job meta.

    Args:
        total_items: Number of items to process

    Returns:
        dict: Success result with processed items count
    """
    from rq import get_current_job

    logger.info(f"Starting demo_progress_task (items={total_items})")

    job = get_current_job()

    for i in range(total_items):
        # Simulate work
        time.sleep(0.1)

        # Update progress in job meta
        if job:
            job.meta['progress'] = {
                'current': i + 1,
                'total': total_items,
                'percentage': ((i + 1) / total_items) * 100,
            }
            job.save_meta()

        if (i + 1) % 10 == 0:
            logger.info(f"Processed {i + 1}/{total_items} items")

    result = {
        "status": "success",
        "message": "Progress task completed",
        "processed_items": total_items,
    }

    logger.info(f"Completed demo_progress_task: {result}")
    return result


def demo_crash_task():
    """
    Task that simulates a worker crash (raises SystemExit).

    WARNING: This will actually crash the worker! Use with caution.

    Raises:
        SystemExit: Simulates worker crash
    """
    logger.warning("Starting demo_crash_task (will crash worker!)")
    time.sleep(1)
    raise SystemExit("Simulated worker crash")


def demo_retry_task(max_attempts: int = 3, fail_until_attempt: int = 2):
    """
    Task that fails N times before succeeding.

    Useful for testing retry logic.

    Args:
        max_attempts: Maximum retry attempts
        fail_until_attempt: Succeed on this attempt

    Returns:
        dict: Success result if attempt succeeds

    Raises:
        ValueError: If attempt should fail
    """
    from rq import get_current_job

    job = get_current_job()

    # Track attempt count in job meta
    if job:
        attempts = job.meta.get('attempts', 0) + 1
        job.meta['attempts'] = attempts
        job.save_meta()
    else:
        attempts = 1

    logger.info(f"demo_retry_task attempt {attempts}/{max_attempts}")

    if attempts < fail_until_attempt:
        error_msg = f"Retry attempt {attempts} - failing until attempt {fail_until_attempt}"
        logger.warning(error_msg)
        raise ValueError(error_msg)

    result = {
        "status": "success",
        "message": f"Succeeded on attempt {attempts}",
        "attempts": attempts,
    }

    logger.info(f"Completed demo_retry_task: {result}")
    return result


def demo_random_task(success_rate: float = 0.7):
    """
    Task that randomly succeeds or fails.

    Args:
        success_rate: Probability of success (0.0 to 1.0)

    Returns:
        dict: Success result if task succeeds

    Raises:
        ValueError: If task randomly fails
    """
    logger.info(f"Starting demo_random_task (success_rate={success_rate})")
    time.sleep(2)

    if random.random() < success_rate:
        result = {
            "status": "success",
            "message": "Random task succeeded",
            "success_rate": success_rate,
        }
        logger.info(f"demo_random_task succeeded: {result}")
        return result
    else:
        error_msg = f"Random task failed (success_rate={success_rate})"
        logger.warning(error_msg)
        raise ValueError(error_msg)


def demo_memory_intensive_task(mb_to_allocate: int = 100):
    """
    Task that allocates memory for testing worker memory limits.

    Args:
        mb_to_allocate: Megabytes of memory to allocate

    Returns:
        dict: Success result with memory info
    """
    logger.info(f"Starting demo_memory_intensive_task (allocating {mb_to_allocate}MB)")

    # Allocate memory (1MB = 1024*1024 bytes, store as list of integers)
    data = []
    chunk_size = 1024 * 1024  # 1MB chunks

    for i in range(mb_to_allocate):
        chunk = [0] * (chunk_size // 8)  # 8 bytes per integer
        data.append(chunk)

        if (i + 1) % 10 == 0:
            logger.info(f"Allocated {i + 1}MB")

    time.sleep(2)

    result = {
        "status": "success",
        "message": "Memory intensive task completed",
        "mb_allocated": mb_to_allocate,
    }

    logger.info(f"Completed demo_memory_intensive_task: {result}")
    return result


def demo_cpu_intensive_task(iterations: int = 1000000):
    """
    CPU-intensive task for testing worker CPU limits.

    Args:
        iterations: Number of iterations to compute

    Returns:
        dict: Success result with computation info
    """
    logger.info(f"Starting demo_cpu_intensive_task (iterations={iterations})")

    # Perform CPU-intensive calculation
    result_value = 0
    for i in range(iterations):
        result_value += i ** 2

        if (i + 1) % 100000 == 0:
            logger.info(f"Processed {i + 1}/{iterations} iterations")

    result = {
        "status": "success",
        "message": "CPU intensive task completed",
        "iterations": iterations,
        "result": result_value,
    }

    logger.info(f"Completed demo_cpu_intensive_task: {result}")
    return result
