"""Reusable QuerySet predicates for CustomUser.

These wrap the two privilege flags (``is_staff``, ``is_superuser``)
into named, testable selections. Downstream apps can compose them
through FK joins, e.g.::

    Client.objects.exclude(user__in=User.objects.staff_members())

without re-deriving the OR-condition in every place.

The class is mixed into ``UserManager`` via ``Manager.from_queryset``
so the same methods are available on the manager:

    User.objects.staff_members()
    User.objects.regular_users()
"""

from django.db import models
from django.db.models import Q


class UserQuerySet(models.QuerySet):
    """Queryset extensions for ``CustomUser``."""

    # ── Privilege filters ────────────────────────────────────────────

    def staff_members(self):
        """Users with operational privileges — staff or superuser.

        ``is_staff`` is the canonical "can log into admin" flag;
        ``is_superuser`` bypasses permissions. We treat both as
        "internal team" for downstream filtering purposes.
        """
        return self.filter(Q(is_staff=True) | Q(is_superuser=True))

    def regular_users(self):
        """End-user accounts only — no staff, no superuser."""
        return self.filter(is_staff=False, is_superuser=False)

    def exclude_staff(self):
        """Drop staff/superuser rows from the current selection.

        Idempotent. Cheaper than computing ``.regular_users()`` when
        you've already narrowed by other criteria — the planner gets
        a single negation rather than a fresh predicate set.
        """
        return self.exclude(Q(is_staff=True) | Q(is_superuser=True))

    # ── Lifecycle filters ────────────────────────────────────────────

    def alive(self):
        """Active, non-soft-deleted users."""
        return self.filter(is_active=True, deleted_at__isnull=True)
