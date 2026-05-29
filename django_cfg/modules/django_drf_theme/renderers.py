"""
Tailwind v4 + Alpine.js Browsable API renderer for Django REST Framework.

Lean, decomposed theme (Tailwind v4 Play CDN, no build step). Templates live under
templates/rest_framework/tailwind/ as small components; styling/behaviour in
static/django_drf_theme/.
"""

from rest_framework.renderers import BrowsableAPIRenderer


class TailwindBrowsableAPIRenderer(BrowsableAPIRenderer):
    """Browsable API renderer styled with Tailwind v4 + Alpine.js.

    Preserves all DRF functionality; only the presentation layer is replaced.
    Extra context:
    - ``theme`` (light/dark/auto), read from the ``theme`` cookie, applied before paint.
    - ``schema_url`` / ``group_name``: the drf-spectacular schema for the current API
      group, used by the left sidepanel to build an endpoint navigation tree.
    """

    template = 'rest_framework/tailwind/api.html'

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        request = renderer_context.get('request')
        if request:
            context['theme'] = request.COOKIES.get('theme', 'auto')
            group, schema_url = self._resolve_schema(request)
            context['group_name'] = group
            context['schema_url'] = schema_url
            # JSON array of method names (minus OPTIONS) for the request console.
            import json
            methods = [m for m in context.get('allowed_methods', []) if m != 'OPTIONS']
            context['allowed_methods_json'] = json.dumps(methods)
        return context

    @staticmethod
    def _resolve_schema(request):
        """Map the current request path to its OpenAPI group + schema URL.

        Convention (django-cfg): API endpoints live at /{api_prefix}/{group}/...
        and the matching drf-spectacular schema at /cfg/openapi/{group}/schema/.
        Returns (group_name, schema_url) or (None, None) if it can't be derived.
        """
        try:
            from django.urls import reverse, NoReverseMatch
            parts = [p for p in request.path.split('/') if p]
            if len(parts) < 2:
                return None, None
            group = parts[1]  # /{prefix}/{group}/...
            try:
                return group, reverse(f'openapi-schema-{group}')
            except NoReverseMatch:
                return group, f'/cfg/openapi/{group}/schema/'
        except Exception:
            return None, None

    def get_template_names(self):
        return [self.template]
