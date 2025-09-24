"""
User admin configuration.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from django.shortcuts import redirect
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.decorators import action
from unfold.enums import ActionVariant
from django_cfg import ImportExportModelAdmin

from ..models import CustomUser
from .filters import UserStatusFilter
from .inlines import UserRegistrationSourceInline, UserActivityInline, UserEmailLogInline, UserSupportTicketsInline
from .resources import CustomUserResource


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin, ImportExportModelAdmin):
    # Import/Export configuration
    resource_class = CustomUserResource
    
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = [
        "avatar",
        "email",
        "full_name",
        "status",
        "sources_count",
        "activity_count",
        "emails_count",
        "tickets_count",
        "last_login_display",
        "date_joined_display",
    ]
    list_display_links = ["avatar", "email", "full_name"]
    search_fields = ["email", "first_name", "last_name"]
    list_filter = [UserStatusFilter, "is_staff", "is_active", "date_joined"]
    ordering = ["-date_joined"]
    readonly_fields = ["date_joined", "last_login"]
    def get_inlines(self, request, obj):
        """Get inlines based on enabled apps."""
        inlines = [UserRegistrationSourceInline, UserActivityInline]
        
        # Add email log inline if newsletter app is enabled
        try:
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            if base_module.is_newsletter_enabled():
                inlines.append(UserEmailLogInline)
            if base_module.is_support_enabled():
                inlines.append(UserSupportTicketsInline)
        except Exception:
            pass
            
        return inlines
    
    # Static actions for Unfold - always show, but check inside methods
    actions_detail = ["view_user_emails", "view_user_tickets"]

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": ("email", "first_name", "last_name", "avatar"),
            },
        ),
        (
            "Contact Information",
            {
                "fields": ("company", "phone", "position"),
            },
        ),
        (
            "Authentication",
            {
                "fields": ("password",),
                "classes": ("collapse",),
            },
        ),
        (
            "Permissions & Status",
            {
                "fields": (
                    ("is_active", "is_staff", "is_superuser"),
                    ("groups",),
                    ("user_permissions",),
                ),
            },
        ),
        (
            "Important Dates",
            {
                "fields": ("last_login", "date_joined"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    def full_name(self, obj):
        """Get user's full name."""
        return obj.__class__.objects.get_full_name(obj) or "—"

    full_name.short_description = "Full Name"

    def status(self, obj):
        """Enhanced status display with icons."""
        if obj.is_superuser:
            return format_html('<span style="color: #dc3545;">👑 Superuser</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #fd7e14;">⚙️ Staff</span>')
        elif obj.is_active:
            return format_html('<span style="color: #198754;">✅ Active</span>')
        else:
            return format_html('<span style="color: #6c757d;">❌ Inactive</span>')

    status.short_description = "Status"

    def sources_count(self, obj):
        """Show count of sources for user."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return "—"
        return f"{count} source{'s' if count != 1 else ''}"

    sources_count.short_description = "Sources"

    def activity_count(self, obj):
        """Show count of user activities."""
        count = obj.activities.count()
        if count == 0:
            return "—"
        return f"{count} activit{'ies' if count != 1 else 'y'}"

    activity_count.short_description = "Activities"

    def emails_count(self, obj):
        """Show count of emails sent to user (if newsletter app is enabled)."""
        try:
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            
            if not base_module.is_newsletter_enabled():
                return "—"
            
            from django_cfg.apps.newsletter.models import EmailLog
            count = EmailLog.objects.filter(user=obj).count()
            if count == 0:
                return "—"
            return f"{count} email{'s' if count != 1 else ''}"
        except (ImportError, Exception):
            return "—"

    emails_count.short_description = "Emails"

    def tickets_count(self, obj):
        """Show count of support tickets for user (if support app is enabled)."""
        try:
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            
            if not base_module.is_support_enabled():
                return "—"
            
            from django_cfg.apps.support.models import Ticket
            count = Ticket.objects.filter(user=obj).count()
            if count == 0:
                return "—"
            return f"{count} ticket{'s' if count != 1 else ''}"
        except (ImportError, Exception):
            return "—"

    tickets_count.short_description = "Tickets"

    def last_login_display(self, obj):
        """Last login with natural time."""
        if obj.last_login:
            return naturaltime(obj.last_login)
        return "Never"

    last_login_display.short_description = "Last Login"

    def date_joined_display(self, obj):
        """Join date with natural day."""
        return naturalday(obj.date_joined)

    date_joined_display.short_description = "Joined"

    def avatar(self, obj):
        """Enhanced avatar display."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="width: 32px; height: 32px; border-radius: 50%; object-fit: cover;" />',
                obj.avatar.url,
            )
        else:
            initials = obj.__class__.objects.get_initials(obj)
            return format_html(
                '<div style="width: 32px; height: 32px; border-radius: 50%; background: #6c757d; '
                "color: white; display: flex; align-items: center; justify-content: center; "
                'font-weight: bold; font-size: 12px;">{}</div>',
                initials,
            )

    avatar.short_description = "Avatar"
    
    @action(
        description="📧 View Email History",
        icon="mail_outline",
        variant=ActionVariant.INFO
    )
    def view_user_emails(self, request, object_id):
        """View all emails sent to this user."""
        try:
            # Get the user object
            user = self.get_object(request, object_id)
            if not user:
                self.message_user(request, "User not found.", level='error')
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Check if newsletter app is enabled
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            
            if not base_module.is_newsletter_enabled():
                self.message_user(
                    request, 
                    "Newsletter app is not enabled.", 
                    level='warning'
                )
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Redirect to EmailLog changelist filtered by this user
            url = reverse('admin:django_cfg_newsletter_emaillog_changelist')
            return redirect(f"{url}?user__id__exact={user.id}")
            
        except Exception as e:
            self.message_user(
                request, 
                f"Error accessing email history: {e}", 
                level='error'
            )
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))
    
    @action(
        description="🎫 View Support Tickets",
        icon="support_agent",
        variant=ActionVariant.SUCCESS
    )
    def view_user_tickets(self, request, object_id):
        """View all support tickets for this user."""
        try:
            # Get the user object
            user = self.get_object(request, object_id)
            if not user:
                self.message_user(request, "User not found.", level='error')
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Check if support app is enabled
            from django_cfg.modules.base import BaseCfgModule
            base_module = BaseCfgModule()
            
            if not base_module.is_support_enabled():
                self.message_user(
                    request, 
                    "Support app is not enabled.", 
                    level='warning'
                )
                return redirect(request.META.get('HTTP_REFERER', '/admin/'))
            
            # Redirect to Ticket changelist filtered by this user
            url = reverse('admin:django_cfg_support_ticket_changelist')
            return redirect(f"{url}?user__id__exact={user.id}")
            
        except Exception as e:
            self.message_user(
                request, 
                f"Error accessing support tickets: {e}", 
                level='error'
            )
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))
