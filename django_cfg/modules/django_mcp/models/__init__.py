"""MCP models for persistence."""

import uuid
from django.db import models


class MCPAuditLog(models.Model):
    """
    Audit log for all MCP operations.

    Tracks every agent query for security analysis and anomaly detection.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    session_id = models.CharField(max_length=100, db_index=True)
    tool_name = models.CharField(max_length=50, db_index=True)
    sql_preview = models.TextField(blank=True, help_text="First 500 chars of SQL")
    params_preview = models.JSONField(default=dict, blank=True)

    # Performance metrics
    cost = models.FloatField(default=0, help_text="EXPLAIN total cost")
    rows_returned = models.IntegerField(default=0)
    execution_ms = models.FloatField(default=0)
    scan_type = models.CharField(max_length=20, blank=True, help_text="sequential, index, bitmap")

    # Result status
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    # Context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['tool_name', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        status = "OK" if self.success else f"ERR: {self.error_message[:50]}"
        return f"MCP {self.tool_name} — {self.rows_returned} rows, {self.execution_ms:.0f}ms — {status}"
