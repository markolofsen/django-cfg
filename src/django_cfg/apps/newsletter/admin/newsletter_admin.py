from django import forms
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.enums import ActionVariant
from django_cfg import ImportExportModelAdmin, ExportMixin, ImportForm, ExportForm

from ..models import EmailLog, Newsletter, NewsletterSubscription, NewsletterCampaign
from .filters import UserEmailFilter, UserNameFilter, HasUserFilter, EmailOpenedFilter, EmailClickedFilter
from .resources import NewsletterResource, NewsletterSubscriptionResource, EmailLogResource


@admin.register(EmailLog)
class EmailLogAdmin(ModelAdmin, ExportMixin):
    # Export-only configuration
    resource_class = EmailLogResource
    export_form_class = ExportForm
    list_display = ('user', 'recipient', 'subject', 'newsletter_link', 'status', 'created_at', 'sent_at', 'tracking_status')
    list_filter = ('status', 'created_at', 'sent_at', 'newsletter', EmailOpenedFilter, EmailClickedFilter, HasUserFilter, UserEmailFilter, UserNameFilter)
    autocomplete_fields = ('user',)
    search_fields = (
        'recipient',
        'subject',
        'body',
        'error_message',
        'user__username',
        'user__email',
        'newsletter__subject'
    )
    readonly_fields = ('created_at', 'sent_at', 'newsletter')
    raw_id_fields = ('user', 'newsletter')

    def newsletter_link(self, obj):
        if obj.newsletter:
            link = reverse("admin:django_cfg_newsletter_newsletter_change", args=[obj.newsletter.id])
            return format_html('<a href="{}">{}</a>', link, obj.newsletter.title)
        return "-"
    newsletter_link.short_description = 'Newsletter'
    
    def tracking_status(self, obj):
        """Show clean tracking status."""
        opened_status = "Opened" if obj.is_opened else "Not opened"
        clicked_status = "Clicked" if obj.is_clicked else "Not clicked"
        
        opened_color = "#28a745" if obj.is_opened else "#dc3545"
        clicked_color = "#007bff" if obj.is_clicked else "#6c757d"
        
        return format_html(
            '<div style="display: flex; gap: 8px;">'
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>'
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>'
            '</div>',
            opened_color, opened_status,
            clicked_color, clicked_status
        )
    tracking_status.short_description = "Tracking Status"


@admin.register(Newsletter)
class NewsletterAdmin(ModelAdmin, ImportExportModelAdmin):
    # Import/Export configuration
    resource_class = NewsletterResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('title', 'description', 'is_active', 'auto_subscribe', 'subscribers_count', 'created_at')
    list_filter = ('is_active', 'auto_subscribe', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('subscribers_count', 'created_at', 'updated_at')


class NewsletterSubscriptionInline(admin.TabularInline):
    model = NewsletterSubscription
    fields = ('email', 'user', 'is_active', 'subscribed_at')
    readonly_fields = ('subscribed_at',)
    extra = 0


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(ModelAdmin, ImportExportModelAdmin):
    # Import/Export configuration
    resource_class = NewsletterSubscriptionResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ('email', 'newsletter', 'user', 'is_active', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('is_active', 'newsletter', 'subscribed_at')
    search_fields = ('email', 'user__email', 'newsletter__title')
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    autocomplete_fields = ('user', 'newsletter')


# --- Form for NewsletterCampaignAdmin with Unfold Wysiwyg --- #
class NewsletterCampaignAdminForm(forms.ModelForm):
    main_html_content = forms.CharField(widget=WysiwygWidget(), required=False)

    class Meta:
        model = NewsletterCampaign
        fields = '__all__'


# --- Inline for Email Logs within Campaign Admin --- #
class EmailLogInline(admin.TabularInline):
    model = EmailLog
    fk_name = 'campaign'  # Specify which ForeignKey to use
    fields = ('user', 'recipient', 'status', 'sent_at')
    readonly_fields = ('user', 'recipient', 'status', 'created_at', 'sent_at')
    can_delete = False
    extra = 0
    show_change_link = True
    verbose_name = "Sent Email Log"
    verbose_name_plural = "Sent Email Logs"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(ModelAdmin):
    form = NewsletterCampaignAdminForm
    inlines = [EmailLogInline]
    list_display = (
        'newsletter',
        'subject',
        'status',
        'created_at',
        'sent_at',
        'recipient_count',
    )
    list_filter = ('status', 'newsletter', 'created_at')
    readonly_fields = ('status', 'created_at', 'sent_at', 'recipient_count')
    search_fields = ('subject', 'email_title', 'main_text')
    autocomplete_fields = ('newsletter',)
    
    # Django admin actions
    actions = ["send_selected_campaigns"]
    
    # Unfold actions configuration
    actions_list = []  # Changelist actions (removed send_selected_campaigns)
    actions_detail = ["send_campaign"]  # Detail page actions
    actions_submit_line = ["send_and_continue"]  # Form submit line actions

    @action(
        description="Send Campaign",
        icon="send",
        variant=ActionVariant.SUCCESS,
        permissions=["change"]
    )
    def send_campaign(self, request, object_id):
        """Send individual campaign from detail page."""
        try:
            campaign = self.get_object(request, object_id)
            if not campaign:
                self.message_user(request, "Campaign not found.", messages.ERROR)
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                
            if campaign.status != NewsletterCampaign.CampaignStatus.DRAFT:
                self.message_user(
                    request, 
                    f"Campaign '{campaign.subject}' is not in draft status.", 
                    messages.WARNING
                )
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            success = campaign.send_campaign()
            if success:
                self.message_user(
                    request, 
                    f"Campaign '{campaign.subject}' sent successfully.", 
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    f"Campaign '{campaign.subject}' failed to send.", 
                    messages.ERROR
                )
                
        except Exception as e:
            self.message_user(request, f"An error occurred: {e}", messages.ERROR)

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    def send_selected_campaigns(self, request, queryset):
        """Send multiple campaigns (standard Django admin action)."""
        sent_count = 0
        skipped_count = 0
        
        for campaign in queryset:
            if campaign.status == NewsletterCampaign.CampaignStatus.DRAFT:
                success = campaign.send_campaign()
                if success:
                    sent_count += 1
                else:
                    skipped_count += 1
            else:
                skipped_count += 1
                messages.warning(
                    request, 
                    f"Campaign '{campaign.subject}' skipped (not in Draft status)."
                )

        if sent_count > 0:
            self.message_user(
                request, 
                f"Successfully sent {sent_count} campaigns.", 
                messages.SUCCESS
            )
        
        if skipped_count > 0:
            self.message_user(
                request, 
                f"{skipped_count} campaigns were skipped.", 
                messages.WARNING
            )
    
    send_selected_campaigns.short_description = "Send selected campaigns"

    @action(
        description="Send & Continue Editing",
        icon="send",
        variant=ActionVariant.INFO,
        permissions=["change"]
    )
    def send_and_continue(self, request, obj):
        """Send campaign and continue editing (submit line action)."""
        if obj.status == NewsletterCampaign.CampaignStatus.DRAFT:
            success = obj.send_campaign()
            if success:
                self.message_user(
                    request, 
                    f"Campaign '{obj.subject}' sent successfully.", 
                    messages.SUCCESS
                )
            else:
                self.message_user(
                    request, 
                    f"Campaign '{obj.subject}' failed to send.", 
                    messages.ERROR
                )
        else:
            self.message_user(
                request, 
                f"Campaign '{obj.subject}' is not in draft status.", 
                messages.WARNING
            )
