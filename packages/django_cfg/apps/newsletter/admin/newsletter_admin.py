"""
Newsletter admin interfaces using Django Admin Utilities v2.0.

Enhanced newsletter management with Material Icons and optimized queries.
"""

from django import forms
from django.contrib import admin, messages
from django.db.models import Count, Q
from unfold.admin import TabularInline
from unfold.contrib.filters.admin import AutocompleteSelectFilter
from unfold.contrib.forms.widgets import WysiwygWidget

from django_cfg.modules.django_admin import (
    ActionConfig,
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    TextField,
    UserField,
    computed_field
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import EmailLog, Newsletter, NewsletterCampaign, NewsletterSubscription
from .actions import (
    activate_newsletters,
    activate_subscriptions,
    cancel_campaigns,
    deactivate_newsletters,
    deactivate_subscriptions,
    enable_auto_subscribe,
    schedule_campaigns,
    send_campaigns,
)
from .filters import (
    EmailClickedFilter,
    EmailOpenedFilter,
    HasUserFilter,
    UserEmailFilter,
    UserNameFilter,
)
from .resources import EmailLogResource, NewsletterResource, NewsletterSubscriptionResource


# ===== EmailLog Admin Config =====

emaillog_config = AdminConfig(
    model=EmailLog,

    # Performance optimization
    select_related=['user', 'newsletter'],

    # Import/Export
    import_export_enabled=True,
    resource_class=EmailLogResource,

    # List display
    list_display=[
        "user_display",
        "recipient_display",
        "subject_display",
        "newsletter_display",
        "status_display",
        "created_at_display",
        "sent_at_display",
        "tracking_display"
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="user",
            title="User"
        ),
        BadgeField(
            name="recipient",
            title="Recipient",
            variant="info",
            icon=Icons.EMAIL
        ),
        BadgeField(
            name="subject",
            title="Subject",
            variant="primary",
            icon=Icons.MAIL
        ),
        BadgeField(
            name="newsletter",
            title="Newsletter",
            variant="secondary",
            icon=Icons.CAMPAIGN
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        DateTimeField(
            name="created_at",
            title="Created"
        ),
        DateTimeField(
            name="sent_at",
            title="Sent"
        ),
    ],

    # Search and filters
    search_fields=[
        "recipient",
        "subject",
        "body",
        "error_message",
        "user__username",
        "user__email",
        "newsletter__subject"
    ],
    list_filter=[
        "status",
        "created_at",
        "sent_at",
        "newsletter",
        EmailOpenedFilter,
        EmailClickedFilter,
        HasUserFilter,
        UserEmailFilter,
        UserNameFilter
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(EmailLog)
class EmailLogAdmin(PydanticAdmin):
    """Admin interface for EmailLog using Django Admin Utilities v2.0."""
    config = emaillog_config

    # Readonly fields
    readonly_fields = ['created_at', 'sent_at', 'newsletter']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Email Information",
            fields=['recipient', 'subject', 'body']
        ),
        FieldsetConfig(
            title="User & Newsletter",
            fields=['user', 'newsletter']
        ),
        FieldsetConfig(
            title="Status & Tracking",
            fields=['status', 'is_opened', 'is_clicked']
        ),
        FieldsetConfig(
            title="Error Details",
            fields=['error_message'],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'sent_at'],
            collapsed=True
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("User")
    def user_display(self, obj: EmailLog) -> str:
        """Display user."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Recipient")
    def recipient_display(self, obj: EmailLog) -> str:
        """Display recipient email."""
        return self.html.badge(obj.recipient, variant="info", icon=Icons.EMAIL)

    @computed_field("Subject")
    def subject_display(self, obj: EmailLog) -> str:
        """Display email subject."""
        if not obj.subject:
            return "—"

        subject = obj.subject
        if len(subject) > 50:
            subject = subject[:47] + "..."

        return self.html.badge(subject, variant="primary", icon=Icons.MAIL)

    @computed_field("Newsletter")
    def newsletter_display(self, obj: EmailLog) -> str:
        """Display newsletter link."""
        if not obj.newsletter:
            return "—"

        return self.html.badge(obj.newsletter.title, variant="secondary", icon=Icons.CAMPAIGN)

    @computed_field("Status")
    def status_display(self, obj: EmailLog) -> str:
        """Display email status."""
        # Determine icon based on status
        icon_map = {
            'pending': Icons.SCHEDULE,
            'sent': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'bounced': Icons.BOUNCE_EMAIL
        }

        # Determine variant based on status
        variant_map = {
            'pending': 'warning',
            'sent': 'success',
            'failed': 'danger',
            'bounced': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.SCHEDULE)
        variant = variant_map.get(obj.status, 'warning')

        return self.html.badge(obj.get_status_display(), variant=variant, icon=icon)

    @computed_field("Created")
    def created_at_display(self, obj: EmailLog) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at

    @computed_field("Sent")
    def sent_at_display(self, obj: EmailLog) -> str:
        """Sent time with relative display."""
        if not obj.sent_at:
            return "Not sent"
        # DateTimeField in display_fields handles formatting automatically
        return obj.sent_at

    @computed_field("Tracking")
    def tracking_display(self, obj: EmailLog) -> str:
        """Display tracking status with badges."""
        badges = []

        if obj.is_opened:
            badges.append(self.html.badge("Opened", variant="success", icon=Icons.VISIBILITY))
        else:
            badges.append(self.html.badge("Not Opened", variant="secondary", icon=Icons.VISIBILITY_OFF))

        if obj.is_clicked:
            badges.append(self.html.badge("Clicked", variant="info", icon=Icons.MOUSE))
        else:
            badges.append(self.html.badge("Not Clicked", variant="secondary", icon=Icons.TOUCH_APP))

        return " | ".join(badges)


# ===== Newsletter Admin Config =====

newsletter_config = AdminConfig(
    model=Newsletter,

    # Import/Export
    import_export_enabled=True,
    resource_class=NewsletterResource,

    # List display
    list_display=[
        "title_display",
        "description_display",
        "active_display",
        "auto_subscribe_display",
        "subscribers_count_display",
        "created_at_display"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="title",
            title="Title",
            variant="primary",
            icon=Icons.CAMPAIGN
        ),
        TextField(
            name="description",
            title="Description"
        ),
        BadgeField(
            name="is_active",
            title="Active"
        ),
        BadgeField(
            name="auto_subscribe",
            title="Auto Subscribe",
            variant="info",
            icon=Icons.AUTO_AWESOME
        ),
        TextField(
            name="subscribers_count",
            title="Subscribers"
        ),
        DateTimeField(
            name="created_at",
            title="Created"
        ),
    ],

    # Search and filters
    search_fields=["title", "description"],
    list_filter=["is_active", "auto_subscribe", "created_at"],

    # Actions
    actions=[
        ActionConfig(
            name="activate_newsletters",
            description="Activate newsletters",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=activate_newsletters
        ),
        ActionConfig(
            name="deactivate_newsletters",
            description="Deactivate newsletters",
            variant="warning",
            icon=Icons.CANCEL,
            handler=deactivate_newsletters
        ),
        ActionConfig(
            name="enable_auto_subscribe",
            description="Enable auto subscribe",
            variant="primary",
            icon=Icons.AUTO_AWESOME,
            handler=enable_auto_subscribe
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(Newsletter)
class NewsletterAdmin(PydanticAdmin):
    """Admin interface for Newsletter using Django Admin Utilities v2.0."""
    config = newsletter_config

    # Required for autocomplete (used by NewsletterSubscriptionAdmin and NewsletterCampaignAdmin)
    search_fields = ['title', 'description']

    # Readonly fields
    readonly_fields = ['subscribers_count', 'created_at', 'updated_at']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Newsletter Information",
            fields=['title', 'description']
        ),
        FieldsetConfig(
            title="Settings",
            fields=['is_active', 'auto_subscribe']
        ),
        FieldsetConfig(
            title="Statistics",
            fields=['subscribers_count'],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['created_at', 'updated_at'],
            collapsed=True
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Title")
    def title_display(self, obj: Newsletter) -> str:
        """Display newsletter title."""
        return self.html.badge(obj.title, variant="primary", icon=Icons.CAMPAIGN)

    @computed_field("Description")
    def description_display(self, obj: Newsletter) -> str:
        """Display newsletter description."""
        if not obj.description:
            return "—"

        description = obj.description
        if len(description) > 100:
            description = description[:97] + "..."

        return description

    @computed_field("Active")
    def active_display(self, obj: Newsletter) -> str:
        """Display active status."""
        if obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="secondary", icon=Icons.CANCEL)

    @computed_field("Auto Subscribe")
    def auto_subscribe_display(self, obj: Newsletter) -> str:
        """Display auto subscribe status."""
        if obj.auto_subscribe:
            return self.html.badge("Auto", variant="info", icon=Icons.AUTO_AWESOME)
        else:
            return "Manual"

    @computed_field("Subscribers")
    def subscribers_count_display(self, obj: Newsletter) -> str:
        """Display subscribers count."""
        count = obj.subscribers_count or 0
        if count == 0:
            return "No subscribers"
        elif count == 1:
            return "1 subscriber"
        else:
            return f"{count} subscribers"

    @computed_field("Created")
    def created_at_display(self, obj: Newsletter) -> str:
        """Created time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.created_at


# ===== NewsletterSubscription Inline (unchanged) =====

class NewsletterSubscriptionInline(TabularInline):
    """Inline for newsletter subscriptions."""

    model = NewsletterSubscription
    fields = ['email', 'user', 'is_active', 'subscribed_at']
    readonly_fields = ['subscribed_at']
    extra = 0


# ===== NewsletterSubscription Admin Config =====

newslettersubscription_config = AdminConfig(
    model=NewsletterSubscription,

    # Performance optimization
    select_related=['user', 'newsletter'],

    # Import/Export
    import_export_enabled=True,
    resource_class=NewsletterSubscriptionResource,

    # List display
    list_display=[
        "email_display",
        "newsletter_display",
        "user_display",
        "active_display",
        "subscribed_at_display",
        "unsubscribed_at_display"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="email",
            title="Email",
            variant="info",
            icon=Icons.EMAIL
        ),
        BadgeField(
            name="newsletter",
            title="Newsletter",
            variant="primary",
            icon=Icons.CAMPAIGN
        ),
        UserField(
            name="user",
            title="User"
        ),
        BadgeField(
            name="is_active",
            title="Active"
        ),
        DateTimeField(
            name="subscribed_at",
            title="Subscribed"
        ),
        DateTimeField(
            name="unsubscribed_at",
            title="Unsubscribed"
        ),
    ],

    # Search and filters
    search_fields=["email", "user__email", "newsletter__title"],
    list_filter=["is_active", "newsletter", "subscribed_at"],

    # Actions
    actions=[
        ActionConfig(
            name="activate_subscriptions",
            description="Activate subscriptions",
            variant="success",
            icon=Icons.CHECK_CIRCLE,
            handler=activate_subscriptions
        ),
        ActionConfig(
            name="deactivate_subscriptions",
            description="Deactivate subscriptions",
            variant="warning",
            icon=Icons.CANCEL,
            handler=deactivate_subscriptions
        ),
    ],

    # Ordering
    ordering=["-subscribed_at"],
)


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(PydanticAdmin):
    """Admin interface for NewsletterSubscription using Django Admin Utilities v2.0."""
    config = newslettersubscription_config

    # Readonly fields
    readonly_fields = ['subscribed_at', 'unsubscribed_at']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Subscription Information",
            fields=['email', 'newsletter', 'user']
        ),
        FieldsetConfig(
            title="Status",
            fields=['is_active']
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['subscribed_at', 'unsubscribed_at']
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Email")
    def email_display(self, obj: NewsletterSubscription) -> str:
        """Display subscription email."""
        return self.html.badge(obj.email, variant="info", icon=Icons.EMAIL)

    @computed_field("Newsletter")
    def newsletter_display(self, obj: NewsletterSubscription) -> str:
        """Display newsletter."""
        if not obj.newsletter:
            return "—"

        return self.html.badge(obj.newsletter.title, variant="primary", icon=Icons.CAMPAIGN)

    @computed_field("User")
    def user_display(self, obj: NewsletterSubscription) -> str:
        """Display user."""
        if not obj.user:
            return "—"
        # Simple username display, UserField handles avatar and styling
        return obj.user.username

    @computed_field("Active")
    def active_display(self, obj: NewsletterSubscription) -> str:
        """Display active status."""
        if obj.is_active:
            return self.html.badge("Active", variant="success", icon=Icons.CHECK_CIRCLE)
        else:
            return self.html.badge("Inactive", variant="secondary", icon=Icons.CANCEL)

    @computed_field("Subscribed")
    def subscribed_at_display(self, obj: NewsletterSubscription) -> str:
        """Subscribed time with relative display."""
        # DateTimeField in display_fields handles formatting automatically
        return obj.subscribed_at

    @computed_field("Unsubscribed")
    def unsubscribed_at_display(self, obj: NewsletterSubscription) -> str:
        """Unsubscribed time with relative display."""
        if not obj.unsubscribed_at:
            return "—"
        # DateTimeField in display_fields handles formatting automatically
        return obj.unsubscribed_at


# ===== NewsletterCampaign Form (unchanged) =====

class NewsletterCampaignAdminForm(forms.ModelForm):
    main_html_content = forms.CharField(widget=WysiwygWidget(), required=False)

    class Meta:
        model = NewsletterCampaign
        fields = '__all__'


# ===== NewsletterCampaign Admin Config =====

newslettercampaign_config = AdminConfig(
    model=NewsletterCampaign,

    # Performance optimization
    select_related=['newsletter'],

    # List display
    list_display=[
        "subject_display",
        "newsletter_display",
        "status_display",
        "sent_at_display",
        "recipient_count_display"
    ],

    # Display fields with UI widgets
    display_fields=[
        BadgeField(
            name="subject",
            title="Subject",
            variant="primary",
            icon=Icons.MAIL
        ),
        BadgeField(
            name="newsletter",
            title="Newsletter",
            variant="secondary",
            icon=Icons.CAMPAIGN
        ),
        BadgeField(
            name="status",
            title="Status"
        ),
        DateTimeField(
            name="sent_at",
            title="Sent"
        ),
        TextField(
            name="recipient_count",
            title="Recipients"
        ),
    ],

    # Search and filters
    search_fields=["subject", "newsletter__title", "main_html_content"],
    list_filter=["status", "newsletter", "sent_at"],

    # Actions
    actions=[
        ActionConfig(
            name="send_campaigns",
            description="Send campaigns",
            variant="primary",
            icon=Icons.SEND,
            confirmation=True,
            handler=send_campaigns
        ),
        ActionConfig(
            name="schedule_campaigns",
            description="Schedule campaigns",
            variant="warning",
            icon=Icons.SCHEDULE,
            handler=schedule_campaigns
        ),
        ActionConfig(
            name="cancel_campaigns",
            description="Cancel campaigns",
            variant="danger",
            icon=Icons.CANCEL,
            confirmation=True,
            handler=cancel_campaigns
        ),
    ],

    # Ordering
    ordering=["-created_at"],
)


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(PydanticAdmin):
    """Admin interface for NewsletterCampaign using Django Admin Utilities v2.0."""
    config = newslettercampaign_config

    # Custom form
    form = NewsletterCampaignAdminForm

    # Readonly fields
    readonly_fields = ['sent_at', 'recipient_count', 'created_at']

    # Fieldsets
    fieldsets = [
        FieldsetConfig(
            title="Campaign Information",
            fields=['subject', 'newsletter']
        ),
        FieldsetConfig(
            title="Content",
            fields=['main_html_content']
        ),
        FieldsetConfig(
            title="Status & Stats",
            fields=['status', 'recipient_count']
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=['sent_at', 'created_at'],
            collapsed=True
        )
    ]

    # Custom display methods using @computed_field decorator
    @computed_field("Subject")
    def subject_display(self, obj: NewsletterCampaign) -> str:
        """Display campaign subject."""
        return self.html.badge(obj.subject, variant="primary", icon=Icons.MAIL)

    @computed_field("Newsletter")
    def newsletter_display(self, obj: NewsletterCampaign) -> str:
        """Display newsletter."""
        if not obj.newsletter:
            return "—"

        return self.html.badge(obj.newsletter.title, variant="secondary", icon=Icons.CAMPAIGN)

    @computed_field("Status")
    def status_display(self, obj: NewsletterCampaign) -> str:
        """Display campaign status."""
        # Determine icon based on status
        icon_map = {
            'draft': Icons.EDIT,
            'scheduled': Icons.SCHEDULE,
            'sending': Icons.SEND,
            'sent': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'cancelled': Icons.CANCEL
        }

        # Determine variant based on status
        variant_map = {
            'draft': 'secondary',
            'scheduled': 'warning',
            'sending': 'info',
            'sent': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        }

        icon = icon_map.get(obj.status, Icons.EDIT)
        variant = variant_map.get(obj.status, 'secondary')

        return self.html.badge(obj.get_status_display(), variant=variant, icon=icon)

    @computed_field("Sent")
    def sent_at_display(self, obj: NewsletterCampaign) -> str:
        """Sent time with relative display."""
        if not obj.sent_at:
            return "Not sent"
        # DateTimeField in display_fields handles formatting automatically
        return obj.sent_at

    @computed_field("Recipients")
    def recipient_count_display(self, obj: NewsletterCampaign) -> str:
        """Display recipients count."""
        count = obj.recipient_count or 0
        if count == 0:
            return "No recipients"
        elif count == 1:
            return "1 recipient"
        else:
            return f"{count} recipients"

    def changelist_view(self, request, extra_context=None):
        """Add campaign statistics to changelist."""
        extra_context = extra_context or {}

        queryset = self.get_queryset(request)
        stats = queryset.aggregate(
            total_campaigns=Count('id'),
            draft_campaigns=Count('id', filter=Q(status='draft')),
            scheduled_campaigns=Count('id', filter=Q(status='scheduled')),
            sent_campaigns=Count('id', filter=Q(status='sent')),
            failed_campaigns=Count('id', filter=Q(status='failed'))
        )

        extra_context['campaign_stats'] = {
            'total_campaigns': stats['total_campaigns'] or 0,
            'draft_campaigns': stats['draft_campaigns'] or 0,
            'scheduled_campaigns': stats['scheduled_campaigns'] or 0,
            'sent_campaigns': stats['sent_campaigns'] or 0,
            'failed_campaigns': stats['failed_campaigns'] or 0
        }

        return super().changelist_view(request, extra_context)
