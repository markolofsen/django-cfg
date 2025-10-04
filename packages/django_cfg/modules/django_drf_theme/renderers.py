"""
Modern Tailwind-styled renderer for Django REST Framework.
"""

from rest_framework.renderers import BrowsableAPIRenderer


class TailwindBrowsableAPIRenderer(BrowsableAPIRenderer):
    """
    🎨 Tailwind CSS Browsable API Renderer

    Modern, user-friendly renderer with:
    - Dark/Light mode support
    - Glass morphism design
    - Keyboard shortcuts (? to see all)
    - Responsive mobile-first layout
    - Advanced JSON viewer with syntax highlighting
    - One-click copy for JSON/URLs
    - Smooth animations and transitions

    Extends BrowsableAPIRenderer to preserve all DRF functionality.
    """

    template = 'rest_framework/tailwind/api.html'

    def get_context(self, data, accepted_media_type, renderer_context):
        """Extend context with Tailwind-specific variables."""
        context = super().get_context(
            data, accepted_media_type, renderer_context
        )

        request = renderer_context.get('request')
        if request:
            # Theme from cookie or system preference
            theme = request.COOKIES.get('theme', 'auto')

            # Determine HTML class based on theme
            if theme == 'dark':
                html_class = 'dark'
            elif theme == 'light':
                html_class = ''
            else:  # auto
                html_class = ''  # Will use system preference via JS

            context.update({
                'theme': theme,
                'html_class': html_class,
                'tailwind_version': 4,
                'enable_dark_mode': True,
                'enable_shortcuts': True,
                'enable_animations': True,
            })

        return context

    def get_template_names(self):
        """Return only Tailwind template (no fallback)."""
        return [self.template]
