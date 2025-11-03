"""
Config Service

Service for extracting user's DjangoConfig settings for dashboard display.
"""

from typing import Dict, Any
from django.conf import settings
from django_cfg.modules.django_logging import get_logger

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

        # Use Pydantic's model_dump to get full JSON-serializable structure
        # This includes all nested models (grpc, centrifugo, databases, etc.)
        try:
            config_dict = config.model_dump(
                mode='json',  # JSON-serializable types
                exclude={
                    '_django_settings',  # Internal cache
                    'secret_key',  # Security - don't expose
                },
                exclude_none=False,  # Keep None values to show what's not set
                by_alias=False,
            )
            # Sanitize sensitive data in config
            config_dict = ConfigService._sanitize_config_dict(config_dict)
        except Exception as e:
            # Expected: some config fields contain functions that can't be serialized
            # Fallback to safe extraction which replaces functions with "<function: name>"
            logger.debug(f"Using fallback extraction due to: {e}")
            config_dict = ConfigService._safe_extract_config(config)

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
    def _safe_extract_config(config) -> Dict[str, Any]:
        """
        Safely extract config fields, skipping non-serializable values.

        Used as fallback when model_dump fails.
        """
        import json
        safe_dict = {}

        # Get model fields
        for field_name, field_info in config.model_fields.items():
            # Skip secret_key
            if field_name in ('secret_key', '_django_settings'):
                continue

            try:
                value = getattr(config, field_name)

                # Replace callables/functions with descriptive string
                if callable(value) and not isinstance(value, type):
                    func_name = getattr(value, '__name__', 'unknown')
                    safe_dict[field_name] = f"<function: {func_name}>"
                    continue

                # Try to JSON serialize to check if safe
                try:
                    json.dumps(value)
                    safe_dict[field_name] = value
                except (TypeError, ValueError):
                    # Try to convert nested Pydantic models
                    if hasattr(value, 'model_dump'):
                        try:
                            safe_dict[field_name] = value.model_dump(mode='json')
                        except:
                            safe_dict[field_name] = str(value)
                    elif isinstance(value, dict):
                        # Try to dump dict items - recursively clean functions
                        safe_dict[field_name] = ConfigService._safe_dump_dict(value)
                    else:
                        # Convert to string as last resort
                        safe_dict[field_name] = str(value)
            except Exception:
                # Skip fields that can't be accessed
                continue

        # Sanitize the extracted config
        safe_dict = ConfigService._sanitize_config_dict(safe_dict)

        return safe_dict

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

    @staticmethod
    def _safe_dump_dict(d: Dict) -> Dict:
        """Recursively dump dict, converting Pydantic models and replacing functions."""
        import json
        result = {}
        for key, value in d.items():
            try:
                # Replace callables/functions with descriptive string
                if callable(value) and not isinstance(value, type):
                    func_name = getattr(value, '__name__', 'unknown')
                    result[key] = f"<function: {func_name}>"
                elif hasattr(value, 'model_dump'):
                    result[key] = value.model_dump(mode='json')
                elif isinstance(value, dict):
                    result[key] = ConfigService._safe_dump_dict(value)
                elif isinstance(value, list):
                    # Handle lists that might contain functions or dicts
                    result[key] = ConfigService._safe_dump_list(value)
                else:
                    # Test JSON serializability
                    json.dumps(value)
                    result[key] = value
            except:
                result[key] = str(value)
        return result

    @staticmethod
    def _safe_dump_list(lst: list) -> list:
        """Recursively dump list, converting Pydantic models and replacing functions."""
        import json
        result = []
        for item in lst:
            try:
                # Replace callables/functions with descriptive string
                if callable(item) and not isinstance(item, type):
                    func_name = getattr(item, '__name__', 'unknown')
                    result.append(f"<function: {func_name}>")
                elif hasattr(item, 'model_dump'):
                    result.append(item.model_dump(mode='json'))
                elif isinstance(item, dict):
                    result.append(ConfigService._safe_dump_dict(item))
                elif isinstance(item, list):
                    result.append(ConfigService._safe_dump_list(item))
                else:
                    # Test JSON serializability
                    json.dumps(item)
                    result.append(item)
            except:
                result.append(str(item))
        return result
