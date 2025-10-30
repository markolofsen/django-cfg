"""
Task execution log model.

Stores history of task executions for monitoring and debugging.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone


class TaskLog(models.Model):
    """
    Log of task executions.

    Stores execution history from ReArq task queue.
    Status values match ReArq's JobStatus enum.
    """

    class StatusChoices(models.TextChoices):
        """Task status matching ReArq JobStatus enum."""
        DEFERRED = "deferred", "Deferred"
        QUEUED = "queued", "Queued"
        IN_PROGRESS = "in_progress", "In Progress"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        CANCELED = "canceled", "Canceled"

    # Task identification
    job_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique job identifier from ReArq"
    )
    task_name = models.CharField(
        max_length=200,
        db_index=True,
        help_text="Name of the task function"
    )
    queue_name = models.CharField(
        max_length=100,
        db_index=True,
        help_text="Queue where task was executed"
    )

    # Arguments
    args = models.JSONField(
        default=list,
        help_text="Positional arguments passed to task"
    )
    kwargs = models.JSONField(
        default=dict,
        help_text="Keyword arguments passed to task"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.QUEUED,
        db_index=True,
        help_text="Current task status"
    )

    # Performance metrics
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Task execution duration in milliseconds"
    )

    # Retry configuration (from ReArq Job)
    job_retry = models.IntegerField(
        default=0,
        help_text="Maximum number of retries allowed (from task definition)"
    )
    job_retries = models.IntegerField(
        default=0,
        help_text="Number of retries performed so far"
    )
    job_retry_after = models.IntegerField(
        default=60,
        help_text="Seconds to wait before retry"
    )

    # Result tracking
    success = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether task completed successfully (null = not finished)"
    )
    result = models.TextField(
        null=True,
        blank=True,
        help_text="Task result (JSON string)"
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text="Error message if task failed"
    )

    # Worker information
    worker_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="ID of worker that processed the task"
    )

    # Timestamps (matching ReArq Job fields)
    enqueue_time = models.DateTimeField(
        db_index=True,
        help_text="When job was enqueued to ReArq (from Job.enqueue_time)"
    )
    expire_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When job will expire (from Job.expire_time)"
    )
    start_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When task execution started (from JobResult.start_time)"
    )
    finish_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When task execution finished (from JobResult.finish_time)"
    )

    # Django-specific timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When TaskLog record was created in Django DB"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When TaskLog record was last updated"
    )

    # User tracking (optional)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who triggered the task (if applicable)"
    )

    class Meta:
        # app_label is derived from apps.py: django_cfg.apps.tasks -> last segment = "tasks"
        # To get "django_cfg_tasks" for consistent admin URLs, we explicitly set it:
        app_label = "django_cfg_tasks"
        db_table = "django_cfg_task_log"
        ordering = ["-enqueue_time"]
        indexes = [
            models.Index(fields=["task_name", "-enqueue_time"]),
            models.Index(fields=["status", "-enqueue_time"]),
            models.Index(fields=["queue_name", "status"]),
            models.Index(fields=["success", "-enqueue_time"]),
            models.Index(fields=["-created_at"]),  # For Django admin
        ]
        verbose_name = "Task Log"
        verbose_name_plural = "Task Logs"

    def __str__(self) -> str:
        return f"{self.task_name} ({self.status})"

    @property
    def is_completed(self) -> bool:
        """Check if task is in a terminal state."""
        return self.status in [
            self.StatusChoices.SUCCESS,
            self.StatusChoices.FAILED,
            self.StatusChoices.EXPIRED,
            self.StatusChoices.CANCELED,
        ]

    @property
    def is_successful(self) -> bool:
        """Check if task completed successfully."""
        return self.status == self.StatusChoices.SUCCESS and self.success is True

    @property
    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status in [
            self.StatusChoices.FAILED,
            self.StatusChoices.EXPIRED,
        ] or self.success is False

    def mark_started(self, worker_id: str = None, start_time=None):
        """Mark task as started (from ReArq JobResult)."""
        self.status = self.StatusChoices.IN_PROGRESS
        self.start_time = start_time or timezone.now()
        if worker_id:
            self.worker_id = worker_id
        self.save(update_fields=["status", "start_time", "worker_id", "updated_at"])

    def mark_completed(self, result: str = None, finish_time=None):
        """Mark task as completed successfully (from ReArq JobResult)."""
        self.status = self.StatusChoices.SUCCESS
        self.success = True
        self.finish_time = finish_time or timezone.now()
        if result is not None:
            self.result = result

        # Calculate duration
        if self.start_time and self.finish_time:
            delta = self.finish_time - self.start_time
            self.duration_ms = int(delta.total_seconds() * 1000)

        self.save(update_fields=["status", "success", "finish_time", "result", "duration_ms", "updated_at"])

    def mark_failed(self, error_message: str, finish_time=None):
        """Mark task as failed with error message (from ReArq JobResult)."""
        self.status = self.StatusChoices.FAILED
        self.success = False
        self.error_message = error_message
        self.finish_time = finish_time or timezone.now()

        # Calculate duration
        if self.start_time and self.finish_time:
            delta = self.finish_time - self.start_time
            self.duration_ms = int(delta.total_seconds() * 1000)

        self.save(update_fields=["status", "success", "error_message", "finish_time", "duration_ms", "updated_at"])

    def mark_expired(self):
        """Mark task as expired (from ReArq Job.status)."""
        self.status = self.StatusChoices.EXPIRED
        self.success = False
        self.save(update_fields=["status", "success", "updated_at"])

    def mark_canceled(self):
        """Mark task as canceled (from ReArq Job.status)."""
        self.status = self.StatusChoices.CANCELED
        self.success = False
        self.save(update_fields=["status", "success", "updated_at"])

    def increment_retry(self):
        """Increment retry counter (from ReArq Job.job_retries)."""
        self.job_retries += 1
        self.save(update_fields=["job_retries", "updated_at"])
