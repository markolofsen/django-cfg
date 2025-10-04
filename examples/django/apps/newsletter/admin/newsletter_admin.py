"""
Newsletter admin interfaces using Django Admin Utilities.

Enhanced newsletter management with Material Icons and optimized queries.
"""

from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import models
from django.db.models import Count, Q
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.forms.widgets import WysiwygWidget
from django_cfg import ImportExportModelAdmin, ExportMixin, ImportForm, ExportForm

from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import EmailLog, Newsletter, NewsletterSubscription, NewsletterCampaign
from .filters import UserEmailFilter, UserNameFilter, HasUserFilter, EmailOpenedFilter, EmailClickedFilter
from .resources import NewsletterResource, NewsletterSubscriptionResource, EmailLogResource


@admin.register(EmailLog)
class EmailLogAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ExportMixin):
    """Admin interface for EmailLog using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user', 'newsletter']
    
    # Export-only configuration
    resource_class = EmailLogResource
    export_form_class = ExportForm
    
    list_display = [
        'user_display', 'recipient_display', 'subject_display', 'newsletter_display', 
        'status_display', 'created_at_display', 'sent_at_display', 'tracking_display'
    ]
    list_display_links = ['subject_display']
    ordering = ['-created_at']
    list_filter = [
        'status', 'created_at', 'sent_at', 'newsletter', 
        EmailOpenedFilter, EmailClickedFilter, HasUserFilter, UserEmailFilter, UserNameFilter
    ]
    autocomplete_fields = ['user']
    search_fields = [
        'recipient',
        'subject',
        'body',
        'error_message',
        'user__username',
        'user__email',
        'newsletter__subject'
    ]
    readonly_fields = ['created_at', 'sent_at', 'newsletter']
    raw_id_fields = ['user', 'newsletter']
    
    fieldsets = [
        ('📧 Email Information', {
            'fields': ['recipient', 'subject', 'body'],
            'classes': ('tab',)
        }),
        ('👤 User & Newsletter', {
            'fields': ['user', 'newsletter'],
            'classes': ('tab',)
        }),
        ('📊 Status & Tracking', {
            'fields': ['status', 'is_opened', 'is_clicked'],
            'classes': ('tab',)
        }),
        ('❌ Error Details', {
            'fields': ['error_message'],
            'classes': ('tab', 'collapse')
        }),
        ('⏰ Timestamps', {
            'fields': ['created_at', 'sent_at'],
            'classes': ('tab', 'collapse')
        })
    ]
    
    @display(description="User")
    def user_display(self, obj: EmailLog) -> str:
        """Display user."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Recipient", ordering="recipient")
    def recipient_display(self, obj: EmailLog) -> str:
        """Display recipient email."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EMAIL)
        return StatusBadge.create(
            text=obj.recipient,
            variant="info",
            config=config
        )
    
    @display(description="Subject", ordering="subject")
    def subject_display(self, obj: EmailLog) -> str:
        """Display email subject."""
        if not obj.subject:
            return "—"
        
        subject = obj.subject
        if len(subject) > 50:
            subject = subject[:47] + "..."
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.MAIL)
        return StatusBadge.create(
            text=subject,
            variant="primary",
            config=config
        )
    
    @display(description="Newsletter")
    def newsletter_display(self, obj: EmailLog) -> str:
        """Display newsletter link."""
        if not obj.newsletter:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CAMPAIGN)
        return StatusBadge.create(
            text=obj.newsletter.title,
            variant="secondary",
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj: EmailLog) -> str:
        """Display email status."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'pending': 'warning',
                'sent': 'success',
                'failed': 'danger',
                'bounced': 'secondary'
            },
            show_icons=True,
            icon=Icons.SCHEDULE if obj.status == 'pending' else Icons.CHECK_CIRCLE if obj.status == 'sent' else Icons.ERROR if obj.status == 'failed' else Icons.BOUNCE_EMAIL
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    @display(description="Created")
    def created_at_display(self, obj: EmailLog) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @display(description="Sent")
    def sent_at_display(self, obj: EmailLog) -> str:
        """Sent time with relative display."""
        if not obj.sent_at:
            return "Not sent"
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'sent_at', config)
    
    @display(description="Tracking")
    def tracking_display(self, obj: EmailLog) -> str:
        """Display tracking status with badges."""
        badges = []
        
        if obj.is_opened:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.VISIBILITY)
            badges.append(StatusBadge.create(text="Opened", variant="success", config=config))
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.VISIBILITY_OFF)
            badges.append(StatusBadge.create(text="Not Opened", variant="secondary", config=config))
        
        if obj.is_clicked:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.MOUSE)
            badges.append(StatusBadge.create(text="Clicked", variant="info", config=config))
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.TOUCH_APP)
            badges.append(StatusBadge.create(text="Not Clicked", variant="secondary", config=config))
        
        return " | ".join(badges)


@admin.register(Newsletter)
class NewsletterAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ImportExportModelAdmin):
    """Admin interface for Newsletter using Django Admin Utilities."""
    
    # Import/Export configuration
    resource_class = NewsletterResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    list_display = [
        'title_display', 'description_display', 'active_display', 
        'auto_subscribe_display', 'subscribers_count_display', 'created_at_display'
    ]
    list_display_links = ['title_display']
    ordering = ['-created_at']
    list_filter = ['is_active', 'auto_subscribe', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['subscribers_count', 'created_at', 'updated_at']
    
    fieldsets = [
        ('📰 Newsletter Information', {
            'fields': ['title', 'description'],
            'classes': ('tab',)
        }),
        ('⚙️ Settings', {
            'fields': ['is_active', 'auto_subscribe'],
            'classes': ('tab',)
        }),
        ('📊 Statistics', {
            'fields': ['subscribers_count'],
            'classes': ('tab', 'collapse')
        }),
        ('⏰ Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ('tab', 'collapse')
        })
    ]
    
    actions = ['activate_newsletters', 'deactivate_newsletters', 'enable_auto_subscribe']
    
    @display(description="Title", ordering="title")
    def title_display(self, obj: Newsletter) -> str:
        """Display newsletter title."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CAMPAIGN)
        return StatusBadge.create(
            text=obj.title,
            variant="primary",
            config=config
        )
    
    @display(description="Description")
    def description_display(self, obj: Newsletter) -> str:
        """Display newsletter description."""
        if not obj.description:
            return "—"
        
        description = obj.description
        if len(description) > 100:
            description = description[:97] + "..."
        
        return description
    
    @display(description="Active")
    def active_display(self, obj: Newsletter) -> str:
        """Display active status."""
        if obj.is_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Active", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CANCEL)
            return StatusBadge.create(text="Inactive", variant="secondary", config=config)
    
    @display(description="Auto Subscribe")
    def auto_subscribe_display(self, obj: Newsletter) -> str:
        """Display auto subscribe status."""
        if obj.auto_subscribe:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.AUTO_AWESOME)
            return StatusBadge.create(text="Auto", variant="info", config=config)
        else:
            return "Manual"
    
    @display(description="Subscribers")
    def subscribers_count_display(self, obj: Newsletter) -> str:
        """Display subscribers count."""
        count = obj.subscribers_count or 0
        if count == 0:
            return "No subscribers"
        elif count == 1:
            return "1 subscriber"
        else:
            return f"{count} subscribers"
    
    @display(description="Created")
    def created_at_display(self, obj: Newsletter) -> str:
        """Created time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'created_at', config)
    
    @action(description="Activate newsletters", variant=ActionVariant.SUCCESS)
    def activate_newsletters(self, request, queryset):
        """Activate selected newsletters."""
        count = queryset.update(is_active=True)
        messages.success(request, f"Successfully activated {count} newsletters.")
    
    @action(description="Deactivate newsletters", variant=ActionVariant.DANGER)
    def deactivate_newsletters(self, request, queryset):
        """Deactivate selected newsletters."""
        count = queryset.update(is_active=False)
        messages.warning(request, f"Successfully deactivated {count} newsletters.")
    
    @action(description="Enable auto subscribe", variant=ActionVariant.INFO)
    def enable_auto_subscribe(self, request, queryset):
        """Enable auto subscribe for selected newsletters."""
        count = queryset.update(auto_subscribe=True)
        messages.info(request, f"Enabled auto subscribe for {count} newsletters.")


class NewsletterSubscriptionInline(TabularInline):
    """Inline for newsletter subscriptions."""
    
    model = NewsletterSubscription
    fields = ['email', 'user', 'is_active', 'subscribed_at']
    readonly_fields = ['subscribed_at']
    extra = 0


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ImportExportModelAdmin):
    """Admin interface for NewsletterSubscription using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['user', 'newsletter']
    
    # Import/Export configuration
    resource_class = NewsletterSubscriptionResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    
    list_display = [
        'email_display', 'newsletter_display', 'user_display', 'active_display', 
        'subscribed_at_display', 'unsubscribed_at_display'
    ]
    list_display_links = ['email_display']
    ordering = ['-subscribed_at']
    list_filter = ['is_active', 'newsletter', 'subscribed_at']
    search_fields = ['email', 'user__email', 'newsletter__title']
    readonly_fields = ['subscribed_at', 'unsubscribed_at']
    autocomplete_fields = ['user', 'newsletter']
    
    fieldsets = [
        ('📧 Subscription Information', {
            'fields': ['email', 'newsletter', 'user'],
            'classes': ('tab',)
        }),
        ('⚙️ Status', {
            'fields': ['is_active'],
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ['subscribed_at', 'unsubscribed_at'],
            'classes': ('tab',)
        })
    ]
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    @display(description="Email", ordering="email")
    def email_display(self, obj: NewsletterSubscription) -> str:
        """Display subscription email."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EMAIL)
        return StatusBadge.create(
            text=obj.email,
            variant="info",
            config=config
        )
    
    @display(description="Newsletter")
    def newsletter_display(self, obj: NewsletterSubscription) -> str:
        """Display newsletter."""
        if not obj.newsletter:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CAMPAIGN)
        return StatusBadge.create(
            text=obj.newsletter.title,
            variant="primary",
            config=config
        )
    
    @display(description="User")
    def user_display(self, obj: NewsletterSubscription) -> str:
        """Display user."""
        if not obj.user:
            return "—"
        return self.display_user_simple(obj.user)
    
    @display(description="Active")
    def active_display(self, obj: NewsletterSubscription) -> str:
        """Display active status."""
        if obj.is_active:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
            return StatusBadge.create(text="Active", variant="success", config=config)
        else:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.CANCEL)
            return StatusBadge.create(text="Inactive", variant="secondary", config=config)
    
    @display(description="Subscribed")
    def subscribed_at_display(self, obj: NewsletterSubscription) -> str:
        """Subscribed time with relative display."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'subscribed_at', config)
    
    @display(description="Unsubscribed")
    def unsubscribed_at_display(self, obj: NewsletterSubscription) -> str:
        """Unsubscribed time with relative display."""
        if not obj.unsubscribed_at:
            return "—"
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'unsubscribed_at', config)
    
    @action(description="Activate subscriptions", variant=ActionVariant.SUCCESS)
    def activate_subscriptions(self, request, queryset):
        """Activate selected subscriptions."""
        count = queryset.update(is_active=True)
        messages.success(request, f"Successfully activated {count} subscriptions.")
    
    @action(description="Deactivate subscriptions", variant=ActionVariant.DANGER)
    def deactivate_subscriptions(self, request, queryset):
        """Deactivate selected subscriptions."""
        count = queryset.update(is_active=False)
        messages.warning(request, f"Successfully deactivated {count} subscriptions.")


# Form for NewsletterCampaignAdmin with Unfold Wysiwyg
class NewsletterCampaignAdminForm(forms.ModelForm):
    main_html_content = forms.CharField(widget=WysiwygWidget(), required=False)

    class Meta:
        model = NewsletterCampaign
        fields = '__all__'


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin, ImportExportModelAdmin):
    """Admin interface for NewsletterCampaign using Django Admin Utilities."""
    
    # Performance optimization
    select_related_fields = ['newsletter']
    
    form = NewsletterCampaignAdminForm
    
    list_display = [
        'subject_display', 'newsletter_display', 'status_display', 
        'sent_at_display', 'recipient_count_display'
    ]
    list_display_links = ['subject_display']
    ordering = ['-created_at']
    list_filter = ['status', 'newsletter', 'sent_at']
    search_fields = ['subject', 'newsletter__title', 'main_html_content']
    readonly_fields = ['sent_at', 'recipient_count', 'created_at']
    autocomplete_fields = ['newsletter']
    
    fieldsets = [
        ('📧 Campaign Information', {
            'fields': ['subject', 'newsletter'],
            'classes': ('tab',)
        }),
        ('📝 Content', {
            'fields': ['main_html_content'],
            'classes': ('tab',)
        }),
        ('📊 Status & Stats', {
            'fields': ['status', 'recipient_count'],
            'classes': ('tab',)
        }),
        ('⏰ Timestamps', {
            'fields': ['sent_at', 'created_at'],
            'classes': ('tab', 'collapse')
        })
    ]
    
    actions = ['send_campaigns', 'schedule_campaigns', 'cancel_campaigns']
    
    @display(description="Subject", ordering="subject")
    def subject_display(self, obj: NewsletterCampaign) -> str:
        """Display campaign subject."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.MAIL)
        return StatusBadge.create(
            text=obj.subject,
            variant="primary",
            config=config
        )
    
    @display(description="Newsletter")
    def newsletter_display(self, obj: NewsletterCampaign) -> str:
        """Display newsletter."""
        if not obj.newsletter:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.CAMPAIGN)
        return StatusBadge.create(
            text=obj.newsletter.title,
            variant="secondary",
            config=config
        )
    
    @display(description="Status")
    def status_display(self, obj: NewsletterCampaign) -> str:
        """Display campaign status."""
        status_config = StatusBadgeConfig(
            custom_mappings={
                'draft': 'secondary',
                'scheduled': 'warning',
                'sending': 'info',
                'sent': 'success',
                'failed': 'danger',
                'cancelled': 'secondary'
            },
            show_icons=True,
            icon=Icons.EDIT if obj.status == 'draft' else Icons.SCHEDULE if obj.status == 'scheduled' else Icons.SEND if obj.status == 'sending' else Icons.CHECK_CIRCLE if obj.status == 'sent' else Icons.ERROR if obj.status == 'failed' else Icons.CANCEL
        )
        return self.display_status_auto(obj, 'status', status_config)
    
    
    @display(description="Sent")
    def sent_at_display(self, obj: NewsletterCampaign) -> str:
        """Sent time with relative display."""
        if not obj.sent_at:
            return "Not sent"
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'sent_at', config)
    
    @display(description="Recipients")
    def recipient_count_display(self, obj: NewsletterCampaign) -> str:
        """Display recipients count."""
        count = obj.recipient_count or 0
        if count == 0:
            return "No recipients"
        elif count == 1:
            return "1 recipient"
        else:
            return f"{count} recipients"
    
    @action(description="Send campaigns", variant=ActionVariant.SUCCESS)
    def send_campaigns(self, request, queryset):
        """Send selected campaigns."""
        sendable_count = queryset.filter(status__in=['draft', 'scheduled']).count()
        if sendable_count == 0:
            messages.error(request, "No sendable campaigns selected.")
            return
        
        queryset.filter(status__in=['draft', 'scheduled']).update(status='sending')
        messages.success(request, f"Started sending {sendable_count} campaigns.")
    
    @action(description="Schedule campaigns", variant=ActionVariant.WARNING)
    def schedule_campaigns(self, request, queryset):
        """Schedule selected campaigns."""
        schedulable_count = queryset.filter(status='draft').count()
        if schedulable_count == 0:
            messages.error(request, "No draft campaigns selected.")
            return
        
        queryset.filter(status='draft').update(status='scheduled')
        messages.warning(request, f"Scheduled {schedulable_count} campaigns.")
    
    @action(description="Cancel campaigns", variant=ActionVariant.DANGER)
    def cancel_campaigns(self, request, queryset):
        """Cancel selected campaigns."""
        cancelable_count = queryset.filter(status__in=['draft', 'scheduled']).count()
        if cancelable_count == 0:
            messages.error(request, "No cancelable campaigns selected.")
            return
        
        queryset.filter(status__in=['draft', 'scheduled']).update(status='cancelled')
        messages.error(request, f"Cancelled {cancelable_count} campaigns.")
    
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
