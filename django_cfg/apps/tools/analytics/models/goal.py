"""Operator-configured conversion goals and ordered funnels."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class AnalyticsScopedDefinition(models.Model):
    """A definition belongs to exactly one host or logical property."""

    site = models.ForeignKey(
        "cfg_analytics.AnalyticsSite",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_definitions",
    )
    property = models.ForeignKey(
        "cfg_analytics.AnalyticsProperty",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_definitions",
    )
    name = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def clean(self) -> None:
        super().clean()
        if bool(self.site_id) == bool(self.property_id):
            raise ValidationError("Choose exactly one analytics site or property.")


class AnalyticsGoal(AnalyticsScopedDefinition):
    """One named conversion: a visitor reaching one event name."""

    event_name = models.CharField(max_length=64)

    class Meta:
        app_label = "cfg_analytics"
        db_table = "cfg_analytics_goal"
        verbose_name = "Analytics goal"
        verbose_name_plural = "Analytics goals"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(site__isnull=False, property__isnull=True) | Q(site__isnull=True, property__isnull=False)),
                name="cfg_an_goal_one_source",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class AnalyticsFunnel(AnalyticsScopedDefinition):
    """An ordered visitor journey composed of product event names."""

    class Meta:
        app_label = "cfg_analytics"
        db_table = "cfg_analytics_funnel"
        verbose_name = "Analytics funnel"
        verbose_name_plural = "Analytics funnels"
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(
                condition=(Q(site__isnull=False, property__isnull=True) | Q(site__isnull=True, property__isnull=False)),
                name="cfg_an_funnel_one_source",
            ),
        ]

    def __str__(self) -> str:
        return self.name


class AnalyticsFunnelStep(models.Model):
    funnel = models.ForeignKey(
        "cfg_analytics.AnalyticsFunnel",
        on_delete=models.CASCADE,
        related_name="steps",
    )
    position = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=128)
    event_name = models.CharField(max_length=64)

    class Meta:
        app_label = "cfg_analytics"
        db_table = "cfg_analytics_funnel_step"
        verbose_name = "Analytics funnel step"
        verbose_name_plural = "Analytics funnel steps"
        ordering = ["funnel", "position"]
        constraints = [
            models.UniqueConstraint(fields=["funnel", "position"], name="cfg_an_funnel_step_position"),
            models.UniqueConstraint(fields=["funnel", "event_name"], name="cfg_an_funnel_step_event"),
        ]

    def __str__(self) -> str:
        return f"{self.funnel}: {self.position}. {self.name}"
