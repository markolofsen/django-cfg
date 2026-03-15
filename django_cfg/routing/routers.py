"""
Database Router for Django Config Toolkit

Simple and reliable database routing.
"""

from django.conf import settings


class DatabaseRouter:
    """
    Simple database router that routes based on app labels.
    
    Uses DATABASE_ROUTING_RULES setting to determine which apps
    should use which databases.
    """

    @staticmethod
    def _resolve_alias(alias: str) -> str:
        """
        If alias is a TEST MIRROR of another alias, return that source alias.

        In tests, Django sets TEST.MIRROR on secondary aliases to point them at
        the same physical DB as 'default'. Routing writes to a mirrored alias
        would open a second transaction on the same DB, breaking FK constraints.
        Returning the mirror source keeps everything on one connection.
        """
        databases = getattr(settings, 'DATABASES', {})
        mirror = databases.get(alias, {}).get('TEST', {}).get('MIRROR')
        if mirror:
            return mirror
        return alias

    def db_for_read(self, model, **hints):
        """Route reads to correct database."""
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        alias = rules.get(model._meta.app_label)
        return self._resolve_alias(alias) if alias else None

    def db_for_write(self, model, **hints):
        """Route writes to correct database."""
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        alias = rules.get(model._meta.app_label)
        return self._resolve_alias(alias) if alias else None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects.

        - If both objects are routed: only allow if they're in the same database
        - If one or both objects are NOT routed (e.g., User in default): allow
          (This enables cross-database ForeignKeys for shared models like User)
        """
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        db1 = rules.get(obj1._meta.app_label)
        db2 = rules.get(obj2._meta.app_label)

        # If both are routed, they must be in the same database
        if db1 and db2:
            return db1 == db2

        # If one or both are not routed (e.g., User in default db), allow the relation
        # This enables routed apps (blog, shop) to have ForeignKeys to shared models (User)
        return True

    def allow_migrate(self, db, app_label, **hints):
        """Allow migrations to correct database."""
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        target_db = rules.get(app_label)

        if target_db:
            # This app IS configured in the rules.
            if db == target_db:
                return True
            # If target_db is a TEST MIRROR alias pointing to db, also allow migration.
            # This handles test setups where a secondary alias mirrors 'default',
            # so routed app tables are created in the shared test DB.
            databases = getattr(settings, 'DATABASES', {})
            target_test = databases.get(target_db, {}).get('TEST', {})
            if target_test.get('MIRROR') == db:
                return True
            return False
        elif db in rules.values():
            # This app is NOT configured, but the target DB is used by other apps
            return db == 'default'

        # Allow migration to default
        return None
