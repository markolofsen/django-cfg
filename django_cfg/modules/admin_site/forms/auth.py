"""Admin login form with development autofill support."""

from django.conf import settings
from django.contrib.admin.forms import AdminAuthenticationForm


class DevAuthForm(AdminAuthenticationForm):
    """
    Admin login form with autofill support.

    Autofill is enabled when:
    - DEBUG=True, OR
    - environment.is_development=True, OR
    - DEV_AUTOFILL_FORCE=True
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        # Autofill values come from the CFG_ADMIN_SITE settings dict built by AdminSiteConfig.
        site = getattr(settings, 'CFG_ADMIN_SITE', {})

        force_autofill = site.get('DEV_AUTOFILL_FORCE', False)

        is_dev = False
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()
            if config and hasattr(config, 'environment'):
                is_dev = config.environment.is_development
        except (ImportError, AttributeError):
            pass

        if not settings.DEBUG and not is_dev and not force_autofill:
            return

        email = site.get('DEV_AUTOFILL_EMAIL')
        password = site.get('DEV_AUTOFILL_PASSWORD')

        if email:
            self.fields['username'].initial = email

        if password:
            # Password widget doesn't render value by default - enable it
            self.fields['password'].widget.render_value = True
            self.fields['password'].initial = password
