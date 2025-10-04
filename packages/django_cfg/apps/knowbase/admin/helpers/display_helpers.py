"""
Shared display helper methods for document admins.

Provides reusable display methods to eliminate duplication across
DocumentAdmin, DocumentChunkAdmin, and DocumentCategoryAdmin.
"""

from django_cfg.modules.django_admin import display
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from .configs import DocumentAdminConfigs


class DocumentDisplayHelpers:
    """Shared display methods for document admin interfaces."""

    @staticmethod
    @display(description="User")
    def display_user(obj, display_mixin):
        """
        Display user with standard formatting.

        Args:
            obj: Model instance with user field
            display_mixin: DisplayMixin instance for formatting

        Returns:
            Formatted user display or "—" if no user
        """
        if not obj.user:
            return "—"
        return display_mixin.display_user_simple(obj.user)

    @staticmethod
    @display(description="Visibility")
    def display_visibility(obj):
        """
        Display visibility status (public/private).

        Args:
            obj: Model instance with is_public field

        Returns:
            Status badge showing public or private status
        """
        if obj.is_public:
            return StatusBadge.create(
                text="Public",
                variant="success",
                config=DocumentAdminConfigs.VISIBILITY_PUBLIC
            )
        else:
            return StatusBadge.create(
                text="Private",
                variant="danger",
                config=DocumentAdminConfigs.VISIBILITY_PRIVATE
            )

    @staticmethod
    @display(description="Tokens")
    def display_token_count(obj, field_name='token_count'):
        """
        Display token count with K formatting.

        Args:
            obj: Model instance with token count field
            field_name: Name of the token count field

        Returns:
            Formatted token count (e.g., "1.5K" or "500")
        """
        tokens = getattr(obj, field_name, 0)
        if tokens > 1000:
            return f"{tokens/1000:.1f}K"
        return str(tokens)

    @staticmethod
    @display(description="Cost (USD)")
    def display_cost_usd(obj, display_mixin, field_name='total_cost_usd'):
        """
        Display cost with currency formatting.

        Args:
            obj: Model instance with cost field
            display_mixin: DisplayMixin instance for formatting
            field_name: Name of the cost field

        Returns:
            Formatted cost with currency
        """
        return display_mixin.display_money_amount(
            obj, field_name, DocumentAdminConfigs.COST_USD
        )

    @staticmethod
    @display(description="Created")
    def display_created_at(obj, display_mixin):
        """
        Display created time with relative display.

        Args:
            obj: Model instance with created_at field
            display_mixin: DisplayMixin instance for formatting

        Returns:
            Formatted datetime with relative time
        """
        return display_mixin.display_datetime_relative(
            obj, 'created_at', DocumentAdminConfigs.CREATED_AT
        )

    @staticmethod
    @display(description="Embedding")
    def display_embedding_status(obj):
        """
        Display embedding vectorization status.

        Args:
            obj: Model instance with embedding field

        Returns:
            Status badge showing vectorization status
        """
        has_embedding = obj.embedding is not None and len(obj.embedding) > 0
        if has_embedding:
            return StatusBadge.create(
                text="✓ Vectorized",
                variant="success",
                config=DocumentAdminConfigs.VECTORIZED
            )
        else:
            return StatusBadge.create(
                text="✗ Not vectorized",
                variant="danger",
                config=DocumentAdminConfigs.NOT_VECTORIZED
            )

    @staticmethod
    @display(description="Content Preview")
    def display_content_preview(obj, max_length=200):
        """
        Display content preview with truncation.

        Args:
            obj: Model instance with content field
            max_length: Maximum length before truncation

        Returns:
            Truncated content preview
        """
        if not obj.content:
            return "—"
        content = obj.content
        if len(content) > max_length:
            return content[:max_length] + "..."
        return content
