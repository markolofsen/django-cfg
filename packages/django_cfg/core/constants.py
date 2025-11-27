"""Default configurations and constants for django-cfg."""

from typing import List

# Default Django apps installed by django-cfg
DEFAULT_APPS: List[str] = [
    # WhiteNoise for static files (must be before django.contrib.staticfiles)
    "whitenoise.runserver_nostatic",
    # Unfold Admin
    "unfold",
    "unfold.contrib.filters",  # optional, if special filters are needed
    "unfold.contrib.forms",  # optional, if special form elements are needed
    "unfold.contrib.inlines",  # optional, if special inlines are needed
    "import_export",  # django-import-export package
    "unfold.contrib.import_export",  # optional, if django-import-export package is used
    "unfold.contrib.guardian",  # optional, if django-guardian package is used
    "unfold.contrib.simple_history",  # optional, if django-simple-history package is used
    "unfold.contrib.location_field",  # optional, if django-location-field package is used
    "unfold.contrib.constance",  # optional, if django-constance package is used
    # Django Core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # Third-party
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "rest_framework_nested",
    "adrf",  # Async Django REST Framework
    "rangefilter",
    "django_filters",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "django_json_widget",
    "django_extensions",
    "constance",
    "constance.backends.database",
    # Security
    "axes",  # django-axes for brute-force protection
    # Django CFG Core
    "django_cfg",
    "django_cfg.modules.django_client",
    "django_cfg.modules.django_admin",
]

# Default middleware stack
DEFAULT_MIDDLEWARE: List[str] = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Public API CORS - handles /cfg/leads/ and other public endpoints BEFORE corsheaders
    "django_cfg.core.middleware.PublicAPICORSMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Security: django-axes must be after AuthenticationMiddleware
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Debug apps (added only in development)
DEBUG_APPS: List[str] = [
    "debug_toolbar",
]

# Debug middleware (added only in development)
DEBUG_MIDDLEWARE: List[str] = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
