"""
Crontab Service

Business logic for crontab/scheduled jobs monitoring and information.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class CrontabService:
    """
    Service for crontab monitoring and information.

    %%PRIORITY:HIGH%%
    %%AI_HINT: Provides information about scheduled cron jobs%%

    TAGS: crontab, scheduling, monitoring, service
    DEPENDS_ON: [django_cfg.core.config]
    """

    def __init__(self):
        """Initialize crontab service."""
        self.logger = logger

    def _get_schedule_display(self, job) -> str:
        """
        Generate human-readable schedule description.

        Args:
            job: CrontabJobConfig instance

        Returns:
            Human-readable schedule string
        """
        parts = []

        # Minute
        if job.minute == "*":
            parts.append("every minute")
        elif job.minute.startswith("*/"):
            interval = job.minute[2:]
            parts.append(f"every {interval} minutes")
        else:
            parts.append(f"at minute {job.minute}")

        # Hour
        if job.hour == "*":
            parts.append("of every hour")
        elif job.hour.startswith("*/"):
            interval = job.hour[2:]
            parts.append(f"every {interval} hours")
        else:
            parts.append(f"at {job.hour}:00")

        # Day of month
        if job.day_of_month != "*":
            parts.append(f"on day {job.day_of_month}")

        # Month
        if job.month_of_year != "*":
            months = {
                "1": "January", "2": "February", "3": "March", "4": "April",
                "5": "May", "6": "June", "7": "July", "8": "August",
                "9": "September", "10": "October", "11": "November", "12": "December"
            }
            month_name = months.get(job.month_of_year, job.month_of_year)
            parts.append(f"in {month_name}")

        # Day of week
        if job.day_of_week != "*":
            days = {
                "0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
                "4": "Thursday", "5": "Friday", "6": "Saturday"
            }
            if "-" in job.day_of_week:
                parts.append(f"on weekdays ({job.day_of_week})")
            else:
                day_name = days.get(job.day_of_week, job.day_of_week)
                parts.append(f"on {day_name}")

        return " ".join(parts)

    def _format_job(self, job) -> Dict[str, Any]:
        """
        Format a single job for API response.

        Args:
            job: CrontabJobConfig instance

        Returns:
            Formatted job dictionary
        """
        job_data = {
            'name': job.name,
            'job_type': job.job_type,
            'minute': job.minute,
            'hour': job.hour,
            'day_of_month': job.day_of_month,
            'month_of_year': job.month_of_year,
            'day_of_week': job.day_of_week,
            'enabled': job.enabled,
            'schedule_display': self._get_schedule_display(job),
        }

        # Add command or callable info
        if job.job_type == 'command':
            job_data['command'] = job.command
            if job.command_args:
                job_data['command_args'] = job.command_args
            if job.command_kwargs:
                job_data['command_kwargs'] = job.command_kwargs
        else:
            job_data['callable_path'] = job.callable_path

        # Add comment if present
        if job.comment:
            job_data['comment'] = job.comment

        return job_data

    def get_all_jobs(self) -> Dict[str, Any]:
        """
        Get all configured cron jobs.

        Returns:
            Dictionary with jobs list and summary

        USED_BY: CrontabViewSet.jobs endpoint
        """
        try:
            from django_cfg.core.config import get_current_config

            config = get_current_config()

            # Check if crontab is configured
            if not hasattr(config, 'crontab') or not config.crontab:
                return {
                    'enabled': False,
                    'jobs_count': 0,
                    'enabled_jobs_count': 0,
                    'jobs': []
                }

            crontab_config = config.crontab

            # Format all jobs
            jobs = [self._format_job(job) for job in crontab_config.jobs]

            # Count enabled jobs
            enabled_jobs_count = sum(1 for job in crontab_config.jobs if job.enabled)

            return {
                'enabled': crontab_config.enabled,
                'jobs_count': len(jobs),
                'enabled_jobs_count': enabled_jobs_count,
                'jobs': jobs
            }

        except Exception as e:
            self.logger.error(f"Failed to get cron jobs: {e}", exc_info=True)
            raise

    def get_status(self) -> Dict[str, Any]:
        """
        Get crontab configuration status and summary.

        Returns:
            Dictionary with crontab configuration status

        USED_BY: CrontabViewSet.crontab_status endpoint
        """
        try:
            from django_cfg.core.config import get_current_config

            config = get_current_config()

            # Check if crontab is configured
            if not hasattr(config, 'crontab') or not config.crontab:
                return {
                    'enabled': False,
                    'jobs_count': 0,
                    'enabled_jobs_count': 0,
                    'lock_jobs': False,
                    'command_prefix': None,
                    'comment': None,
                    'timestamp': datetime.now().isoformat(),
                }

            crontab_config = config.crontab

            # Count enabled jobs
            enabled_jobs_count = sum(1 for job in crontab_config.jobs if job.enabled)

            return {
                'enabled': crontab_config.enabled,
                'jobs_count': len(crontab_config.jobs),
                'enabled_jobs_count': enabled_jobs_count,
                'lock_jobs': crontab_config.lock_jobs,
                'command_prefix': crontab_config.command_prefix,
                'comment': crontab_config.comment,
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Failed to get crontab status: {e}", exc_info=True)
            raise
