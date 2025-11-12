"""
Django Config Serializers

Serializers for displaying user's DjangoConfig settings.
"""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes


# Nested serializers for complex structures

class DatabaseConfigSerializer(serializers.Serializer):
    """Database configuration."""
    engine = serializers.CharField()
    name = serializers.CharField()
    user = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=False, allow_null=True)
    host = serializers.CharField(required=False, allow_null=True)
    port = serializers.IntegerField(required=False, allow_null=True)
    connect_timeout = serializers.IntegerField(required=False, allow_null=True)
    sslmode = serializers.CharField(required=False, allow_null=True)
    options = serializers.JSONField(required=False, allow_null=True)
    apps = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    operations = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    migrate_to = serializers.CharField(required=False, allow_null=True)
    routing_description = serializers.CharField(required=False, allow_null=True)


class EmailConfigSerializer(serializers.Serializer):
    """Email configuration."""
    backend = serializers.CharField(required=False, allow_null=True)
    host = serializers.CharField(required=False, allow_null=True)
    port = serializers.IntegerField(required=False, allow_null=True)
    username = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=False, allow_null=True)
    use_tls = serializers.BooleanField(required=False, allow_null=True)
    use_ssl = serializers.BooleanField(required=False, allow_null=True)
    ssl_verify = serializers.BooleanField(required=False, allow_null=True)
    timeout = serializers.IntegerField(required=False, allow_null=True)
    default_from = serializers.CharField(required=False, allow_null=True)


class PaymentsNowPaymentsSerializer(serializers.Serializer):
    """NowPayments configuration."""
    api_key = serializers.CharField(required=False, allow_null=True)
    ipn_secret = serializers.CharField(required=False, allow_null=True)
    sandbox = serializers.BooleanField(required=False, allow_null=True)
    enabled = serializers.BooleanField(required=False, allow_null=True)


class PaymentsConfigSerializer(serializers.Serializer):
    """Payments configuration."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    nowpayments = PaymentsNowPaymentsSerializer(required=False, allow_null=True)


class GRPCConfigDashboardSerializer(serializers.Serializer):
    """gRPC configuration for dashboard."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    host = serializers.CharField(required=False, allow_null=True)
    port = serializers.IntegerField(required=False, allow_null=True)
    max_workers = serializers.IntegerField(required=False, allow_null=True)
    reflection = serializers.BooleanField(required=False, allow_null=True)
    health_check = serializers.BooleanField(required=False, allow_null=True)
    interceptors = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)


class CentrifugoConfigSerializer(serializers.Serializer):
    """Centrifugo configuration."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    api_url = serializers.CharField(required=False, allow_null=True)
    api_key = serializers.CharField(required=False, allow_null=True)
    token_hmac_secret_key = serializers.CharField(required=False, allow_null=True)
    timeout = serializers.IntegerField(required=False, allow_null=True)


class RedisQueueConfigSerializer(serializers.Serializer):
    """Redis Queue configuration."""
    url = serializers.CharField(required=False, allow_null=True)
    host = serializers.CharField(required=False, allow_null=True)
    port = serializers.IntegerField(required=False, allow_null=True)
    db = serializers.IntegerField(required=False, allow_null=True)
    username = serializers.CharField(required=False, allow_null=True)
    password = serializers.CharField(required=False, allow_null=True)
    default_timeout = serializers.IntegerField(required=False, allow_null=True)
    default_result_ttl = serializers.IntegerField(required=False, allow_null=True)
    sentinels = serializers.JSONField(required=False, allow_null=True)  # List of tuples (host, port)
    master_name = serializers.CharField(required=False, allow_null=True)
    socket_timeout = serializers.IntegerField(required=False, allow_null=True)


class RQScheduleSerializer(serializers.Serializer):
    """Redis Queue schedule configuration."""
    func = serializers.CharField(required=False, allow_null=True)
    cron_string = serializers.CharField(required=False, allow_null=True)
    queue = serializers.CharField(required=False, allow_null=True)
    kwargs = serializers.JSONField(required=False, allow_null=True)
    args = serializers.ListField(child=serializers.JSONField(), required=False, allow_null=True)
    meta = serializers.JSONField(required=False, allow_null=True)
    repeat = serializers.IntegerField(required=False, allow_null=True)
    result_ttl = serializers.IntegerField(required=False, allow_null=True)


class DjangoRQConfigSerializer(serializers.Serializer):
    """Django-RQ configuration."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    queues = serializers.ListField(child=RedisQueueConfigSerializer(), required=False, allow_null=True)
    show_admin_link = serializers.BooleanField(required=False, allow_null=True)
    exception_handlers = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    api_token = serializers.CharField(required=False, allow_null=True)
    prometheus_enabled = serializers.BooleanField(required=False, allow_null=True)
    schedules = serializers.ListField(child=RQScheduleSerializer(), required=False, allow_null=True)


class DRFConfigSerializer(serializers.Serializer):
    """Django REST Framework configuration."""
    default_pagination_class = serializers.CharField(required=False, allow_null=True)
    page_size = serializers.IntegerField(required=False, allow_null=True)


class SpectacularConfigSerializer(serializers.Serializer):
    """DRF Spectacular configuration."""
    title = serializers.CharField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_null=True)
    version = serializers.CharField(required=False, allow_null=True)


class JWTConfigSerializer(serializers.Serializer):
    """JWT configuration."""
    access_token_lifetime = serializers.IntegerField(required=False, allow_null=True)
    refresh_token_lifetime = serializers.IntegerField(required=False, allow_null=True)
    algorithm = serializers.CharField(required=False, allow_null=True)


class ConfigMetaSerializer(serializers.Serializer):
    """Config metadata."""
    config_class = serializers.CharField()
    secret_key_configured = serializers.BooleanField()


class TelegramConfigSerializer(serializers.Serializer):
    """Telegram service configuration."""
    bot_token = serializers.CharField(required=False, allow_null=True)
    chat_id = serializers.IntegerField(required=False, allow_null=True)
    parse_mode = serializers.CharField(required=False, allow_null=True)
    disable_notification = serializers.BooleanField(required=False, allow_null=True)
    disable_web_page_preview = serializers.BooleanField(required=False, allow_null=True)
    timeout = serializers.IntegerField(required=False, allow_null=True)
    webhook_url = serializers.CharField(required=False, allow_null=True)
    webhook_secret = serializers.CharField(required=False, allow_null=True)
    max_retries = serializers.IntegerField(required=False, allow_null=True)
    retry_delay = serializers.FloatField(required=False, allow_null=True)


class NgrokConfigSerializer(serializers.Serializer):
    """Ngrok tunneling configuration."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    authtoken = serializers.CharField(required=False, allow_null=True)
    basic_auth = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    compression = serializers.BooleanField(required=False, allow_null=True)


class AxesConfigSerializer(serializers.Serializer):
    """Django-Axes brute-force protection configuration."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    failure_limit = serializers.IntegerField(required=False, allow_null=True)
    cooloff_time = serializers.IntegerField(required=False, allow_null=True)
    lock_out_at_failure = serializers.BooleanField(required=False, allow_null=True)
    reset_on_success = serializers.BooleanField(required=False, allow_null=True)
    only_user_failures = serializers.BooleanField(required=False, allow_null=True)
    lockout_template = serializers.CharField(required=False, allow_null=True)
    lockout_url = serializers.CharField(required=False, allow_null=True)
    verbose = serializers.BooleanField(required=False, allow_null=True)
    enable_access_failure_log = serializers.BooleanField(required=False, allow_null=True)
    ipware_proxy_count = serializers.IntegerField(required=False, allow_null=True)
    ipware_meta_precedence_order = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    allowed_ips = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    denied_ips = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    cache_name = serializers.CharField(required=False, allow_null=True)
    use_user_agent = serializers.BooleanField(required=False, allow_null=True)
    username_form_field = serializers.CharField(required=False, allow_null=True)


class NextJSAdminConfigSerializer(serializers.Serializer):
    """Next.js Admin application configuration."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    url = serializers.CharField(required=False, allow_null=True)
    api_base_url = serializers.CharField(required=False, allow_null=True)


class ConstanceConfigSerializer(serializers.Serializer):
    """Django-Constance dynamic settings configuration."""
    config = serializers.JSONField(required=False, allow_null=True)
    config_fieldsets = serializers.JSONField(required=False, allow_null=True)
    backend = serializers.CharField(required=False, allow_null=True)
    database_prefix = serializers.CharField(required=False, allow_null=True)
    database_cache_backend = serializers.CharField(required=False, allow_null=True)
    additional_config = serializers.JSONField(required=False, allow_null=True)


class OpenAPIClientConfigSerializer(serializers.Serializer):
    """OpenAPI Client generation configuration."""
    enabled = serializers.BooleanField(required=False, allow_null=True)
    output_dir = serializers.CharField(required=False, allow_null=True)
    client_name = serializers.CharField(required=False, allow_null=True)
    schema_url = serializers.CharField(required=False, allow_null=True)
    generator = serializers.CharField(required=False, allow_null=True)
    additional_properties = serializers.JSONField(required=False, allow_null=True)
    templates = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    global_properties = serializers.JSONField(required=False, allow_null=True)


class DjangoConfigSerializer(serializers.Serializer):
    """
    Typed serializer for user's DjangoConfig settings.

    Reflects the actual structure of DjangoConfig model.
    All passwords and sensitive data are sanitized before reaching this serializer.
    """

    # Project info
    env_mode = serializers.CharField(required=False, allow_null=True)
    project_name = serializers.CharField(required=False, allow_null=True)
    project_logo = serializers.CharField(required=False, allow_null=True)
    project_version = serializers.CharField(required=False, allow_null=True)
    project_description = serializers.CharField(required=False, allow_null=True)
    startup_info_mode = serializers.CharField(required=False, allow_null=True)

    # Feature flags
    enable_support = serializers.BooleanField(required=False, allow_null=True)
    enable_accounts = serializers.BooleanField(required=False, allow_null=True)
    enable_newsletter = serializers.BooleanField(required=False, allow_null=True)
    enable_leads = serializers.BooleanField(required=False, allow_null=True)
    enable_knowbase = serializers.BooleanField(required=False, allow_null=True)
    enable_agents = serializers.BooleanField(required=False, allow_null=True)
    enable_maintenance = serializers.BooleanField(required=False, allow_null=True)
    enable_frontend = serializers.BooleanField(required=False, allow_null=True)
    enable_drf_tailwind = serializers.BooleanField(required=False, allow_null=True)
    enable_pool_cleanup = serializers.BooleanField(required=False, allow_null=True)

    # URLs
    site_url = serializers.CharField(required=False, allow_null=True)
    api_url = serializers.CharField(required=False, allow_null=True)

    # Debug settings
    debug = serializers.BooleanField(required=False, allow_null=True)
    debug_warnings = serializers.BooleanField(required=False, allow_null=True)

    # Django settings
    root_urlconf = serializers.CharField(required=False, allow_null=True)
    wsgi_application = serializers.CharField(required=False, allow_null=True)
    auth_user_model = serializers.CharField(required=False, allow_null=True)
    project_apps = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)

    # Infrastructure
    databases = serializers.DictField(child=DatabaseConfigSerializer(), required=False, allow_null=True)
    redis_url = serializers.CharField(required=False, allow_null=True)
    cache_default = serializers.CharField(required=False, allow_null=True)
    cache_sessions = serializers.CharField(required=False, allow_null=True)

    # Security
    security_domains = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    ssl_redirect = serializers.BooleanField(required=False, allow_null=True)
    cors_allow_headers = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)

    # Integrations
    email = EmailConfigSerializer(required=False, allow_null=True)
    payments = PaymentsConfigSerializer(required=False, allow_null=True)
    grpc = GRPCConfigDashboardSerializer(required=False, allow_null=True)
    centrifugo = CentrifugoConfigSerializer(required=False, allow_null=True)
    django_rq = DjangoRQConfigSerializer(required=False, allow_null=True)
    drf = DRFConfigSerializer(required=False, allow_null=True)
    spectacular = SpectacularConfigSerializer(required=False, allow_null=True)
    jwt = JWTConfigSerializer(required=False, allow_null=True)

    # Services & Security (now typed!)
    telegram = TelegramConfigSerializer(required=False, allow_null=True)
    ngrok = NgrokConfigSerializer(required=False, allow_null=True)
    axes = AxesConfigSerializer(required=False, allow_null=True)
    crypto_fields = serializers.JSONField(required=False, allow_null=True)
    unfold = serializers.JSONField(required=False, allow_null=True)  # Complex Unfold config object
    tailwind_app_name = serializers.CharField(required=False, allow_null=True)
    tailwind_version = serializers.IntegerField(required=False, allow_null=True)  # Integer version number
    limits = serializers.JSONField(required=False, allow_null=True)
    api_keys = serializers.JSONField(required=False, allow_null=True)
    custom_middleware = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    nextjs_admin = NextJSAdminConfigSerializer(required=False, allow_null=True)
    admin_emails = serializers.ListField(child=serializers.CharField(), required=False, allow_null=True)
    constance = ConstanceConfigSerializer(required=False, allow_null=True)
    openapi_client = OpenAPIClientConfigSerializer(required=False, allow_null=True)

    # Metadata
    _meta = ConfigMetaSerializer(required=False, allow_null=True)


class ConfigValidationSerializer(serializers.Serializer):
    """Validation result for config serializer."""
    status = serializers.CharField(help_text="Validation status: 'valid', 'warning', or 'error'")
    missing_in_serializer = serializers.ListField(
        child=serializers.CharField(),
        help_text="Fields present in config but missing in serializer"
    )
    extra_in_serializer = serializers.ListField(
        child=serializers.CharField(),
        help_text="Fields present in serializer but not in config"
    )
    type_mismatches = serializers.ListField(
        child=serializers.JSONField(),
        help_text="Fields with type mismatches"
    )
    total_config_fields = serializers.IntegerField(help_text="Total fields in config")
    total_serializer_fields = serializers.IntegerField(help_text="Total fields in serializer")


class ConfigDataSerializer(serializers.Serializer):
    """
    Serializer for complete config data endpoint.

    Returns both DjangoConfig and Django settings with validation info.
    """

    django_config = DjangoConfigSerializer(
        help_text="User's DjangoConfig settings"
    )
    django_settings = serializers.JSONField(
        help_text="Complete Django settings (sanitized, contains mixed types)"
    )
    _validation = ConfigValidationSerializer(
        help_text="Validation result comparing serializer with actual config"
    )
