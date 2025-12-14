"""
Config Service

Service for extracting user's DjangoConfig settings for dashboard display.
"""

from typing import Dict, Any
from django.conf import settings
from django_cfg.utils import get_logger

logger = get_logger(__name__)


class ConfigService:
    """Service for retrieving user's DjangoConfig settings."""

    @staticmethod
    def validate_serializer(config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that DjangoConfigSerializer matches the actual config structure.

        Compares actual config fields with serializer fields and reports:
        - Missing fields in serializer
        - Extra fields in serializer
        - Type mismatches

        Returns:
            Dict with validation results
        """
        from ..serializers.config import DjangoConfigSerializer
        from rest_framework import serializers

        validation = {
            'status': 'valid',
            'missing_in_serializer': [],
            'extra_in_serializer': [],
            'type_mismatches': [],
            'total_config_fields': len(config_dict),
            'total_serializer_fields': 0,
        }

        # Get serializer fields
        serializer = DjangoConfigSerializer()
        serializer_fields = serializer.fields
        validation['total_serializer_fields'] = len(serializer_fields)

        # Get actual config fields (excluding _meta as it's added separately)
        config_fields = set(config_dict.keys()) - {'_meta'}
        serializer_field_names = set(serializer_fields.keys())

        # Find missing fields (in config but not in serializer)
        missing = config_fields - serializer_field_names
        if missing:
            validation['missing_in_serializer'] = sorted(list(missing))
            validation['status'] = 'warning'

        # Find extra fields (in serializer but not in config)
        extra = serializer_field_names - config_fields - {'_meta'}
        if extra:
            validation['extra_in_serializer'] = sorted(list(extra))

        # Check type compatibility for common fields
        common_fields = config_fields & serializer_field_names
        for field_name in common_fields:
            config_value = config_dict[field_name]
            serializer_field = serializer_fields[field_name]

            # Skip None values
            if config_value is None:
                continue

            # Check type compatibility
            type_mismatch = False
            expected_type = None

            if isinstance(serializer_field, serializers.BooleanField):
                expected_type = 'boolean'
                if not isinstance(config_value, bool):
                    type_mismatch = True
            elif isinstance(serializer_field, serializers.IntegerField):
                expected_type = 'integer'
                if not isinstance(config_value, int):
                    type_mismatch = True
            elif isinstance(serializer_field, serializers.CharField):
                expected_type = 'string'
                if not isinstance(config_value, str):
                    type_mismatch = True
            elif isinstance(serializer_field, serializers.DictField):
                expected_type = 'dict'
                if not isinstance(config_value, dict):
                    type_mismatch = True
            elif isinstance(serializer_field, serializers.ListField):
                expected_type = 'list'
                if not isinstance(config_value, list):
                    type_mismatch = True

            if type_mismatch:
                validation['type_mismatches'].append({
                    'field': field_name,
                    'expected_type': expected_type,
                    'actual_type': type(config_value).__name__,
                })
                validation['status'] = 'error'

        return validation

    @staticmethod
    def get_config_data() -> Dict[str, Any]:
        """
        Get user's DjangoConfig as JSON-serializable dict.

        Returns the full config structure as-is, mimicking the user's config.py.
        This allows frontend to display the config tree exactly as user defined it.

        Returns:
            Dictionary with full config structure
        """
        from django_cfg.core.config import get_current_config

        config = get_current_config()

        if not config:
            return {'error': 'Config not available'}

        # Use Pydantic's model_dump_for_django to get full structure
        # This includes all nested models (grpc, centrifugo, databases, etc.)
        # Uses mode='python' which handles Python objects properly
        config_dict = config.model_dump_for_django(
            exclude={
                '_django_settings',  # Internal cache
                'secret_key',  # Security - don't expose
            }
        )

        # Clean callable objects (replace functions with string representations)
        config_dict = ConfigService._clean_callables(config_dict)

        # Sanitize sensitive data in config
        config_dict = ConfigService._sanitize_config_dict(config_dict)

        # Add some computed/helpful fields
        config_dict['_meta'] = {
            'config_class': config.__class__.__name__,
            'secret_key_configured': bool(config.secret_key and len(config.secret_key) >= 50),
        }

        return config_dict

    @staticmethod
    def get_django_settings() -> Dict[str, Any]:
        """
        Get all Django settings as JSON-serializable dict.

        Returns complete Django settings (DATABASES, MIDDLEWARE, etc.)
        Sanitizes sensitive values like SECRET_KEY, passwords.

        Returns:
            Dictionary with Django settings
        """
        settings_dict = {}

        # List of settings to exclude for security
        sensitive_keys = {
            'SECRET_KEY',
            'DATABASE_PASSWORD',
            'AWS_SECRET_ACCESS_KEY',
            'EMAIL_HOST_PASSWORD',
            'STRIPE_SECRET_KEY',
            'REDIS_PASSWORD',
        }

        # Get all settings from Django
        for key in dir(settings):
            # Skip private/internal settings
            if key.startswith('_'):
                continue

            # Skip methods and callables
            if callable(getattr(settings, key)):
                continue

            # Get value
            value = getattr(settings, key)

            # Special handling for DATABASES (always sanitize)
            if key == 'DATABASES':
                settings_dict[key] = ConfigService._sanitize_databases(value)
            # Sanitize sensitive values
            elif any(sensitive in key.upper() for sensitive in sensitive_keys):
                if key == 'SECRET_KEY':
                    settings_dict[key] = '***HIDDEN***' if value else None
                else:
                    settings_dict[key] = '***HIDDEN***' if value else None
            else:
                # Try to make value JSON-serializable
                try:
                    import json
                    json.dumps(value)  # Test if serializable
                    settings_dict[key] = value
                except (TypeError, ValueError):
                    # Convert to string if not serializable
                    settings_dict[key] = str(value)

        return settings_dict

    @staticmethod
    def _clean_callables(data: Any) -> Any:
        """
        Recursively clean callable objects from data structure.

        Replaces functions/callables with string representations like "<function: name>".
        Ensures data is JSON-serializable for DRF.

        Args:
            data: Data structure to clean (dict, list, or primitive)

        Returns:
            Cleaned data structure
        """
        import json

        # Handle callable/function
        if callable(data) and not isinstance(data, type):
            func_name = getattr(data, '__name__', 'unknown')
            module = getattr(data, '__module__', '')
            if module:
                return f"<function: {module}.{func_name}>"
            return f"<function: {func_name}>"

        # Handle dict
        if isinstance(data, dict):
            return {key: ConfigService._clean_callables(value) for key, value in data.items()}

        # Handle list/tuple
        if isinstance(data, (list, tuple)):
            cleaned = [ConfigService._clean_callables(item) for item in data]
            return cleaned if isinstance(data, list) else tuple(cleaned)

        # Handle Pydantic models that weren't dumped
        if hasattr(data, 'model_dump'):
            return ConfigService._clean_callables(data.model_dump(mode='python'))

        # Try JSON serialization to check if safe
        try:
            json.dumps(data)
            return data
        except (TypeError, ValueError):
            # Not JSON serializable - convert to string
            return str(data)

    @staticmethod
    def _sanitize_databases(databases: Dict) -> Dict:
        """Sanitize database passwords."""
        import copy
        sanitized = {}
        for alias, config in databases.items():
            # Deep copy to avoid modifying original
            sanitized_config = copy.deepcopy(config)
            if 'PASSWORD' in sanitized_config:
                sanitized_config['PASSWORD'] = '***HIDDEN***' if sanitized_config['PASSWORD'] else None
            sanitized[alias] = sanitized_config
        return sanitized


    @staticmethod
    def _sanitize_config_dict(config_dict: Dict) -> Dict:
        """
        Sanitize sensitive values in config dict.

        Hides passwords in:
        - databases.*.password
        - email.password
        - redis/cache passwords
        - any field with 'password', 'secret', 'token', 'key' in name
        """
        import copy

        sanitized = copy.deepcopy(config_dict)

        # Sanitize databases
        if 'databases' in sanitized and isinstance(sanitized['databases'], dict):
            logger.info(f"Sanitizing databases: {list(sanitized['databases'].keys())}")
            for db_alias, db_config in sanitized['databases'].items():
                if isinstance(db_config, dict) and 'password' in db_config:
                    logger.info(f"Found password in {db_alias}: {bool(db_config['password'])}")
                    if db_config['password']:
                        db_config['password'] = '***HIDDEN***'
                        logger.info(f"Sanitized password in {db_alias}")

        # Sanitize email password
        if 'email' in sanitized and isinstance(sanitized['email'], dict):
            if 'password' in sanitized['email'] and sanitized['email']['password']:
                sanitized['email']['password'] = '***HIDDEN***'

        # Sanitize cache/redis passwords
        if 'cache' in sanitized and isinstance(sanitized['cache'], dict):
            for cache_name, cache_config in sanitized['cache'].items():
                if isinstance(cache_config, dict) and 'password' in cache_config:
                    if cache_config['password']:
                        cache_config['password'] = '***HIDDEN***'

        # Sanitize django_rq redis passwords
        if 'django_rq' in sanitized and isinstance(sanitized['django_rq'], dict):
            if 'queues' in sanitized['django_rq'] and isinstance(sanitized['django_rq']['queues'], dict):
                for queue_name, queue_config in sanitized['django_rq']['queues'].items():
                    if isinstance(queue_config, dict) and 'password' in queue_config:
                        if queue_config['password']:
                            queue_config['password'] = '***HIDDEN***'

        # Generic sanitization: any field with sensitive keywords
        ConfigService._sanitize_dict_recursive(sanitized)

        return sanitized

    @staticmethod
    def _sanitize_dict_recursive(d: Dict) -> None:
        """Recursively sanitize sensitive fields in dict (modifies in-place)."""
        sensitive_keywords = {'api_key', 'secret_key', 'private_key', 'token', 'api_secret', 'secret', 'ipn_secret'}

        for key, value in d.items():
            # Check if key contains sensitive keyword
            key_lower = key.lower()
            if any(keyword in key_lower for keyword in sensitive_keywords):
                if value and not isinstance(value, (dict, list)):
                    d[key] = '***HIDDEN***'
            # Recurse into nested dicts
            elif isinstance(value, dict):
                ConfigService._sanitize_dict_recursive(value)
            # Recurse into lists of dicts
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        ConfigService._sanitize_dict_recursive(item)

