"""
User admin interface using Django Admin Utilities.

Enhanced user management with Material Icons, status badges, and optimized queries.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import redirect
from django.urls import reverse
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django_cfg import ImportExportModelAdmin

from django_cfg.modules.base import BaseCfgModule
from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StandaloneActionsMixin,
    standalone_action,
    UserDisplayConfig,
    DateTimeDisplayConfig,
    StatusBadgeConfig,
    Icons,
    ActionVariant,
    display,
    action
)
from django_cfg.modules.django_admin.utils.displays import UserDisplay
from django_cfg.modules.django_admin.utils.badges import StatusBadge

from ..models import CustomUser
from .filters import UserStatusFilter
from .inlines import UserRegistrationSourceInline, UserActivityInline, UserEmailLogInline, UserSupportTicketsInline
from .resources import CustomUserResource


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin, OptimizedModelAdmin, DisplayMixin, StandaloneActionsMixin, ModelAdmin, ImportExportModelAdmin):
    """Enhanced user admin using Django Admin Utilities."""
    
    # Import/Export configuration
    resource_class = CustomUserResource
    
    # Forms loaded from unfold.forms
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    # Performance optimization
    select_related_fields = []
    prefetch_related_fields = ['groups', 'user_permissions']
    
    list_display = [
        'avatar_display',
        'email_display',
        'full_name_display',
        'status_display',
        'sources_count_display',
        'activity_count_display',
        'emails_count_display',
        'tickets_count_display',
        'last_login_display',
        'date_joined_display',
    ]
    list_display_links = ['avatar_display', 'email_display', 'full_name_display']
    search_fields = ['email', 'first_name', 'last_name']
    list_filter = [UserStatusFilter, 'is_staff', 'is_active', 'date_joined']
    ordering = ['-date_joined']
    readonly_fields = ['date_joined', 'last_login']
    
    # Register standalone actions
    actions_list = ['view_user_emails', 'view_user_tickets', 'export_user_data']
    
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
    
    def get_inlines(self, request, obj):
        """Get inlines based on enabled apps."""
        inlines = [UserRegistrationSourceInline, UserActivityInline]
        
        # Add email log inline if newsletter app is enabled
        try:
            base_module = BaseCfgModule()
            if base_module.is_newsletter_enabled():
                inlines.append(UserEmailLogInline)
            if base_module.is_support_enabled():
                inlines.append(UserSupportTicketsInline)
        except Exception:
            pass
            
        return inlines
    
    @display(description="Avatar", header=True)
    def avatar_display(self, obj):
        """Enhanced avatar display with fallback initials."""
        config = UserDisplayConfig(
            show_avatar=True,
            avatar_size=32
        )
        return UserDisplay.with_avatar(obj, config)
    
    @display(description="Email")
    def email_display(self, obj):
        """Email display with user icon."""
        config = StatusBadgeConfig(show_icons=True, icon=Icons.EMAIL)
        return StatusBadge.create(
            text=obj.email,
            variant="info",
            config=config
        )
    
    @display(description="Full Name")
    def full_name_display(self, obj):
        """Full name display."""
        full_name = obj.__class__.objects.get_full_name(obj)
        if not full_name:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.PERSON)
            return StatusBadge.create(text="No name", variant="secondary", config=config)
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.PERSON)
        return StatusBadge.create(text=full_name, variant="primary", config=config)
    
    @display(description="Status", label=True)
    def status_display(self, obj):
        """Enhanced status display with appropriate icons and colors."""
        if obj.is_superuser:
            status = "Superuser"
            icon = Icons.ADMIN_PANEL_SETTINGS
            variant = "danger"
        elif obj.is_staff:
            status = "Staff"
            icon = Icons.SETTINGS
            variant = "warning"
        elif obj.is_active:
            status = "Active"
            icon = Icons.CHECK_CIRCLE
            variant = "success"
        else:
            status = "Inactive"
            icon = Icons.CANCEL
            variant = "secondary"
        
        config = StatusBadgeConfig(
            show_icons=True,
            icon=icon,
            custom_mappings={status: variant}
        )
        return self.display_status_auto(
            type('obj', (), {'status': status})(),
            'status',
            config
        )
    
    @display(description="Sources")
    def sources_count_display(self, obj):
        """Show count of registration sources for user."""
        count = obj.user_registration_sources.count()
        if count == 0:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.SOURCE)
        return StatusBadge.create(
            text=f"{count} source{'s' if count != 1 else ''}",
            variant="info",
            config=config
        )
    
    @display(description="Activities")
    def activity_count_display(self, obj):
        """Show count of user activities."""
        count = obj.activities.count()
        if count == 0:
            return "—"
        
        config = StatusBadgeConfig(show_icons=True, icon=Icons.HISTORY)
        return StatusBadge.create(
            text=f"{count} activit{'ies' if count != 1 else 'y'}",
            variant="info",
            config=config
        )
    
    @display(description="Emails")
    def emails_count_display(self, obj):
        """Show count of emails sent to user (if newsletter app is enabled)."""
        try:
            base_module = BaseCfgModule()
            
            if not base_module.is_newsletter_enabled():
                return "—"
            
            from django_cfg.apps.newsletter.models import EmailLog
            count = EmailLog.objects.filter(user=obj).count()
            if count == 0:
                return "—"
            
            config = StatusBadgeConfig(show_icons=True, icon=Icons.EMAIL)
            return StatusBadge.create(
                text=f"{count} email{'s' if count != 1 else ''}",
                variant="success",
                config=config
            )
        except (ImportError, Exception):
            return "—"
    
    @display(description="Tickets")
    def tickets_count_display(self, obj):
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
            
            config = StatusBadgeConfig(show_icons=True, icon=Icons.SUPPORT_AGENT)
            return StatusBadge.create(
                text=f"{count} ticket{'s' if count != 1 else ''}",
                variant="warning",
                config=config
            )
        except (ImportError, Exception):
            return "—"
    
    @display(description="Last Login")
    def last_login_display(self, obj):
        """Last login with relative time."""
        if not obj.last_login:
            config = StatusBadgeConfig(show_icons=True, icon=Icons.LOGIN)
            return StatusBadge.create(text="Never", variant="secondary", config=config)
        
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'last_login', config)
    
    @display(description="Joined")
    def date_joined_display(self, obj):
        """Join date with relative time."""
        config = DateTimeDisplayConfig(show_relative=True)
        return self.display_datetime_relative(obj, 'date_joined', config)
    
    # Standalone Actions
    @standalone_action(
        description="📧 View Email History",
        variant=ActionVariant.INFO,
        icon="mail_outline",
        success_message="Redirected to email history for {result}",
        error_message="❌ Error accessing email history: {error}"
    )
    def view_user_emails(self, request):
        """View all emails sent to this user."""
        # Extract object_id from request path
        # URL format: /admin/django_cfg_accounts/customuser/<object_id>/view-user-emails/
        path_parts = request.path.strip('/').split('/')
        try:
            object_id = path_parts[-2]  # Get the ID before the action name
        except IndexError:
            raise Exception("Could not determine user ID from URL")

        # Get the user object
        user = self.get_object(request, object_id)
        if not user:
            raise Exception("User not found")

        # Check if newsletter app is enabled
        from django_cfg.modules.base import BaseCfgModule
        base_module = BaseCfgModule()

        if not base_module.is_newsletter_enabled():
            raise Exception("Newsletter app is not enabled")

        # Redirect to EmailLog changelist filtered by this user
        url = reverse('admin:django_cfg_newsletter_emaillog_changelist')
        redirect_url = f"{url}?user__id__exact={user.id}"

        # Return redirect (handled by standalone_action decorator)
        return redirect(redirect_url)

    @standalone_action(
        description="🎫 View Support Tickets",
        variant=ActionVariant.SUCCESS,
        icon="support_agent",
        success_message="Redirected to support tickets for {result}",
        error_message="❌ Error accessing support tickets: {error}"
    )
    def view_user_tickets(self, request):
        """View all support tickets for this user."""
        # Extract object_id from request path
        path_parts = request.path.strip('/').split('/')
        try:
            object_id = path_parts[-2]  # Get the ID before the action name
        except IndexError:
            raise Exception("Could not determine user ID from URL")

        # Get the user object
        user = self.get_object(request, object_id)
        if not user:
            raise Exception("User not found")

        # Check if support app is enabled
        from django_cfg.modules.base import BaseCfgModule
        base_module = BaseCfgModule()

        if not base_module.is_support_enabled():
            raise Exception("Support app is not enabled")

        # Redirect to Ticket changelist filtered by this user
        url = reverse('admin:django_cfg_support_ticket_changelist')
        redirect_url = f"{url}?user__id__exact={user.id}"

        return redirect(redirect_url)

    @standalone_action(
        description="📊 Export User Data",
        variant=ActionVariant.WARNING,
        icon="download",
        success_message="📊 User data export completed: {result}",
        error_message="❌ Export failed: {error}"
    )
    def export_user_data(self, request):
        """Export comprehensive user data."""
        # Extract object_id from request path
        path_parts = request.path.strip('/').split('/')
        try:
            object_id = path_parts[-2]  # Get the ID before the action name
        except IndexError:
            raise Exception("Could not determine user ID from URL")

        user = self.get_object(request, object_id)
        if not user:
            raise Exception("User not found")

        # Here you would implement actual export logic
        # For now, just return a success message
        return f"Data for {user.get_full_name() or user.email}"
