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

    def db_for_read(self, model, **hints):
        """Route reads to correct database."""
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        return rules.get(model._meta.app_label)

    def db_for_write(self, model, **hints):
        """Route writes to correct database.""" 
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        return rules.get(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between same database."""
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        db1 = rules.get(obj1._meta.app_label)
        db2 = rules.get(obj2._meta.app_label)
        return db1 == db2 if db1 and db2 else None

    def allow_migrate(self, db, app_label, **hints):
        """Allow migrations to correct database."""
        rules = getattr(settings, 'DATABASE_ROUTING_RULES', {})
        target_db = rules.get(app_label)

        if target_db:
            # This app IS configured in the rules
            return db == target_db
        elif db in rules.values():
            # This app is NOT configured, but the target DB is used by other apps
            return db == 'default'
        
        # Allow migration to default
        return None
