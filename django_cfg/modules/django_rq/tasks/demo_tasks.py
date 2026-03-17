"""
Demo tasks for RQ testing and simulation.

This module provides a simple heartbeat task for verifying RQ scheduler functionality.
"""

import datetime
from django_cfg.utils import get_logger

# Logger for RQ tasks - auto-prefixed to django_cfg.integrations
# Will write to logs/djangocfg/integrations.log
logger = get_logger("integrations")


def demo_scheduler_heartbeat():
    """
    Simple heartbeat task for testing RQ scheduler.

    This task is designed to run periodically (e.g., every 1 minute) to verify
    that the scheduler is working correctly. It logs a message and returns
    a success status with timestamp.

    **IMPORTANT**: This task only runs in DEVELOPMENT mode. In production or test
    environments, it will skip execution and return early.

    Returns:
        dict: Success result with timestamp, or skip result if not in development
    """
    from django_cfg.core.config import get_current_config

    # Get current config to check environment mode
    config = get_current_config()

    # Only run in development mode
    if not config or not config.is_development:
        logger.debug(
            f"⏭️  Skipping demo_scheduler_heartbeat (is_development={config.is_development if config else False}, only runs in development)"
        )
        return {
            "status": "skipped",
            "message": "Demo task skipped (not in development mode)",
            "env_mode": config.env_mode if config else "unknown",
        }

    timestamp = datetime.datetime.now()
    logger.info(f"💓 RQ Scheduler Heartbeat: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    result = {
        "status": "success",
        "message": "RQ Scheduler is alive and working!",
        "timestamp": timestamp.isoformat(),
        "env_mode": config.env_mode,
    }

    return result
