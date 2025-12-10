"""Authentication forms with development autofill support."""

from django.conf import settings
from unfold.forms import AuthenticationForm


class DevAuthForm(AuthenticationForm):
    """
    Login form with autofill support.

    Autofill is enabled when:
    - DEBUG=True, OR
    - environment.is_development=True, OR
    - DEV_AUTOFILL_FORCE=True
    """

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)

        # Get autofill settings from UNFOLD config
        unfold = getattr(settings, 'UNFOLD', {})

        force_autofill = unfold.get('DEV_AUTOFILL_FORCE', False)

        # Check if development environment
        is_dev = False
        try:
            from django_cfg.core.state import get_current_config
            config = get_current_config()
            if config and hasattr(config, 'environment'):
                is_dev = config.environment.is_development
        except (ImportError, AttributeError):
            pass

        # Only autofill if DEBUG OR development environment OR force is enabled
        if not settings.DEBUG and not is_dev and not force_autofill:
            return

        email = unfold.get('DEV_AUTOFILL_EMAIL')
        password = unfold.get('DEV_AUTOFILL_PASSWORD')

        if email:
            self.fields['username'].initial = email

        if password:
            # Password widget doesn't render value by default - enable it
            self.fields['password'].widget.render_value = True
            self.fields['password'].initial = password
