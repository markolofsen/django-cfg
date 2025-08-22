"""
Admin configuration for Users app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.humanize.templatetags.humanize import naturaltime, naturalday
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from datetime import timedelta
from .models import User, UserProfile, UserActivity


# Unregister default Group admin and re-register with Unfold
admin.site.unregister(Group)


# Custom Filters
class UserStatusFilter(admin.SimpleListFilter):
    title = "User Status"
    parameter_name = "user_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("staff", "Staff"),
            ("superuser", "Superuser"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True, is_staff=False)
        elif self.value() == "inactive":
            return queryset.filter(is_active=False)
        elif self.value() == "staff":
            return queryset.filter(is_staff=True)
        elif self.value() == "superuser":
            return queryset.filter(is_superuser=True)
        return queryset


class ActivityTypeFilter(admin.SimpleListFilter):
    title = "Activity Type"
    parameter_name = "activity_type"

    def lookups(self, request, model_admin):
        return (
            ("login", "Login"),
            ("logout", "Logout"),
            ("create", "Create"),
            ("update", "Update"),
            ("delete", "Delete"),
            ("recent", "Recent (24h)"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "recent":
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        elif self.value():
            return queryset.filter(activity_type=self.value())
        return queryset


# Inline Admin Classes
class UserProfileInline(TabularInline):
    model = UserProfile
    extra = 0
    readonly_fields = ["posts_count", "comments_count", "orders_count", "created_at", "updated_at"]
    fields = ["website", "github", "twitter", "linkedin", "company", "job_title"]

    def has_add_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False


class UserActivityInline(TabularInline):
    model = UserActivity
    extra = 0
    readonly_fields = ["created_at"]
    fields = ["activity_type", "description", "ip_address", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """Admin for custom User model."""
    
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    list_display = [
        "avatar_display",
        "email",
        "full_name",
        "status_display",
        "activity_count",
        "last_login_display",
        "date_joined_display",
    ]
    list_display_links = ["avatar_display", "email", "full_name"]
    search_fields = ["username", "email", "first_name", "last_name"]
    list_filter = [UserStatusFilter, "is_staff", "is_active", "date_joined"]
    ordering = ["-date_joined"]
    readonly_fields = ["date_joined", "last_login", "created_at", "updated_at"]
    inlines = [UserProfileInline, UserActivityInline]
    
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": ("username", "email", "first_name", "last_name"),
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
                "fields": ("last_login", "date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2"),
            },
        ),
    )

    def full_name(self, obj):
        """Get user's full name."""
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or obj.username

    full_name.short_description = "Full Name"

    def status_display(self, obj):
        """Enhanced status display with icons."""
        if obj.is_superuser:
            return format_html('<span style="color: #dc3545;">👑 Superuser</span>')
        elif obj.is_staff:
            return format_html('<span style="color: #fd7e14;">⚙️ Staff</span>')
        elif obj.is_active:
            return format_html('<span style="color: #198754;">✅ Active</span>')
        else:
            return format_html('<span style="color: #6c757d;">❌ Inactive</span>')

    status_display.short_description = "Status"

    def activity_count(self, obj):
        """Show count of user activities."""
        count = obj.activities.count()
        if count == 0:
            return "—"
        return f"{count} activit{'ies' if count != 1 else 'y'}"

    activity_count.short_description = "Activities"

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

    def avatar_display(self, obj):
        """Enhanced avatar display."""
        initials = f"{obj.first_name[:1]}{obj.last_name[:1]}".upper() or obj.username[:2].upper()
        return format_html(
            '<div style="width: 32px; height: 32px; border-radius: 50%; background: #6c757d; '
            "color: white; display: flex; align-items: center; justify-content: center; "
            'font-weight: bold; font-size: 12px;">{}</div>',
            initials,
        )

    avatar_display.short_description = "Avatar"


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    """Enhanced Group admin with Unfold styling."""
    pass


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    """Enhanced admin for UserProfile model."""
    
    list_display = [
        'user_display', 
        'company_display', 
        'job_title', 
        'social_links_display',
        'stats_display',
        'created_at_display'
    ]
    list_display_links = ['user_display']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'company', 'job_title']
    readonly_fields = ['posts_count', 'comments_count', 'orders_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Social Links', {
            'fields': ('website', 'github', 'twitter', 'linkedin'),
            'description': 'Social media and professional profiles'
        }),
        ('Professional Info', {
            'fields': ('company', 'job_title')
        }),
        ('Statistics', {
            'fields': ('posts_count', 'comments_count', 'orders_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def user_display(self, obj):
        """Enhanced user display with avatar."""
        user = obj.user
        initials = f"{user.first_name[:1]}{user.last_name[:1]}".upper() or user.username[:2].upper()
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 24px; height: 24px; border-radius: 50%; background: #6c757d; '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-weight: bold; font-size: 10px;">{}</div>'
            '<span>{}</span></div>',
            initials,
            user.get_full_name() or user.username
        )
    
    user_display.short_description = "User"

    def company_display(self, obj):
        """Company with fallback."""
        return obj.company or "—"
    
    company_display.short_description = "Company"

    def social_links_display(self, obj):
        """Display social links count."""
        links = [obj.website, obj.github, obj.twitter, obj.linkedin]
        count = sum(1 for link in links if link)
        if count == 0:
            return "—"
        return f"{count} link{'s' if count != 1 else ''}"
    
    social_links_display.short_description = "Social Links"

    def stats_display(self, obj):
        """Display user statistics."""
        return format_html(
            '<small>📝 {} | 💬 {} | 🛒 {}</small>',
            obj.posts_count,
            obj.comments_count,
            obj.orders_count
        )
    
    stats_display.short_description = "Activity Stats"

    def created_at_display(self, obj):
        """Created date with natural time."""
        return naturalday(obj.created_at)
    
    created_at_display.short_description = "Created"


@admin.register(UserActivity)
class UserActivityAdmin(ModelAdmin):
    """Enhanced admin for UserActivity model."""
    
    list_display = [
        'user_display', 
        'activity_type_display', 
        'description_short', 
        'ip_address', 
        'created_at_display'
    ]
    list_display_links = ['user_display', 'activity_type_display']
    list_filter = [ActivityTypeFilter, 'activity_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'description', 'ip_address']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Activity', {
            'fields': ('user', 'activity_type', 'description')
        }),
        ('Related Object', {
            'fields': ('object_id', 'object_type'),
            'classes': ('collapse',),
            'description': 'Optional reference to related model instance'
        }),
        ('Request Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )

    def user_display(self, obj):
        """Enhanced user display."""
        user = obj.user
        initials = f"{user.first_name[:1]}{user.last_name[:1]}".upper() or user.username[:2].upper()
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 20px; height: 20px; border-radius: 50%; background: #6c757d; '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-weight: bold; font-size: 8px;">{}</div>'
            '<span>{}</span></div>',
            initials,
            user.get_full_name() or user.username
        )
    
    user_display.short_description = "User"

    def activity_type_display(self, obj):
        """Activity type with icons."""
        icons = {
            'login': '🔐',
            'logout': '🚪',
            'create': '➕',
            'update': '✏️',
            'delete': '🗑️',
            'view': '👁️',
        }
        icon = icons.get(obj.activity_type, '📝')
        return format_html('{} {}', icon, obj.get_activity_type_display())
    
    activity_type_display.short_description = "Activity"

    def description_short(self, obj):
        """Truncated description."""
        if len(obj.description) > 50:
            return f"{obj.description[:47]}..."
        return obj.description
    
    description_short.short_description = "Description"

    def created_at_display(self, obj):
        """Created time with natural time."""
        return naturaltime(obj.created_at)
    
    created_at_display.short_description = "When"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
