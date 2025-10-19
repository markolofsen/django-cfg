"""
Base dashboard section classes.

Provides foundation for dashboard sections following Unfold's pattern.
"""

from typing import Any, Dict, Optional

from django.http import HttpRequest
from django.template.loader import render_to_string


class DashboardSection:
    """
    Base class for dashboard sections.

    Each section is responsible for:
    - Data collection
    - Context preparation
    - Template rendering

    Usage:
        class MySection(DashboardSection):
            template_name = "admin/sections/my_section.html"

            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['custom_data'] = self.get_custom_data()
                return context
    """

    template_name: Optional[str] = None
    title: Optional[str] = None
    icon: Optional[str] = None

    def __init__(self, request: HttpRequest) -> None:
        """Initialize section with request context."""
        self.request = request

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """
        Get context data for template rendering.

        Override this method to add custom context.
        """
        context = {
            'request': self.request,
            'section': self,
        }

        if self.title:
            context['title'] = self.title

        if self.icon:
            context['icon'] = self.icon

        context.update(kwargs)
        return context

    def render(self, **kwargs) -> str:
        """
        Render the section template.

        Args:
            **kwargs: Additional context to pass to template

        Returns:
            Rendered HTML string
        """
        if not self.template_name:
            raise NotImplementedError(
                f"{self.__class__.__name__} must define 'template_name' or override render()"
            )

        context = self.get_context_data(**kwargs)
        return render_to_string(self.template_name, context=context, request=self.request)

    def __str__(self) -> str:
        """String representation."""
        return self.title or self.__class__.__name__


class DataSection(DashboardSection):
    """
    Section that provides data-driven content.

    Extend this for sections that need to fetch and process data.
    """

    def get_data(self) -> Any:
        """
        Get section data.

        Override this to provide section-specific data.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_data()"
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add data to context."""
        context = super().get_context_data(**kwargs)
        context['data'] = self.get_data()
        return context


class CardSection(DashboardSection):
    """
    Section rendered as a card component.

    Automatically wraps content in card template.
    """

    template_name = "admin/components/card.html"
    content_template: Optional[str] = None

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add card-specific context."""
        context = super().get_context_data(**kwargs)

        # Render content if content_template is provided
        if self.content_template:
            context['content'] = render_to_string(
                self.content_template,
                context=context,
                request=self.request
            )

        return context
