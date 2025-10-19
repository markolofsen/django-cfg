"""
Django settings for Django CFG Sample Project.

This file demonstrates how to use django_cfg for complete Django configuration.
All settings are generated from the type-safe Pydantic configuration.
"""

from api.config import config

# Generate all Django settings from our type-safe configuration
locals().update(config.get_all_settings())

# The above line replaces hundreds of lines of traditional Django settings!
# Everything is automatically configured:
# - DATABASES with routing
# - CACHES 
# - EMAIL settings
# - INSTALLED_APPS with all integrations
# - MIDDLEWARE
# - TEMPLATES
# - STATIC/MEDIA files
# - SECURITY settings
# - DRF configuration
# - Unfold admin
# - Constance dynamic settings
# - And much more!

# Optional: Add any custom settings here if needed
# CUSTOM_SETTING = "custom_value"

# Print configuration summary
if config.debug:
    print("=" * 60)
    print("🚀 Django CFG Sample Project")
    print(f"📦 Version: {config.project_version}")
    print(f"🗄️  Databases: {len(config.databases)}")
    print(f"📱 Apps: {len(config.project_apps)}")
    print(f"⚙️  Constance Fields: {len(config.constance.get_all_fields())}")
    print("=" * 60)
