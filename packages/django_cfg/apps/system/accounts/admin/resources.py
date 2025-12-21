"""
Import/Export resources for Accounts app.

Enhanced resources with better data validation and export optimization.
"""

from datetime import timedelta

from django.contrib.auth.models import Group
from django.utils import timezone
from import_export import fields, resources
from import_export.widgets import BooleanWidget, DateTimeWidget, ManyToManyWidget

from ..models import CustomUser, RegistrationSource, UserActivity


class CustomUserResource(resources.ModelResource):
    """Enhanced resource for importing/exporting users."""

    # Custom fields for better export/import
    full_name = fields.Field(
        column_name='full_name',
        attribute='get_full_name',
        readonly=True
    )

    groups = fields.Field(
        column_name='groups',
        attribute='groups',
        widget=ManyToManyWidget(Group, field='name', separator='|')
    )

    last_login = fields.Field(
        column_name='last_login',
        attribute='last_login',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    date_joined = fields.Field(
        column_name='date_joined',
        attribute='date_joined',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    is_active = fields.Field(
        column_name='is_active',
        attribute='is_active',
        widget=BooleanWidget()
    )

    is_staff = fields.Field(
        column_name='is_staff',
        attribute='is_staff',
        widget=BooleanWidget()
    )

    phone_verified = fields.Field(
        column_name='phone_verified',
        attribute='phone_verified',
        widget=BooleanWidget()
    )

    # Additional computed fields
    registration_sources = fields.Field(
        column_name='registration_sources',
        readonly=True
    )

    activities_count = fields.Field(
        column_name='activities_count',
        readonly=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'company',
            'phone',
            'phone_verified',
            'position',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'registration_sources',
            'activities_count',
            'last_login',
            'date_joined',
        )
        export_order = fields
        import_id_fields = ('email',)  # Use email as unique identifier
        skip_unchanged = True
        report_skipped = True

    def dehydrate_registration_sources(self, user):
        """Get registration sources for export."""
        sources = user.user_registration_sources.select_related('source').all()
        return '|'.join([source.source.name for source in sources])

    def dehydrate_activities_count(self, user):
        """Get activities count for export."""
        return user.activities.count()

    def before_import_row(self, row, **kwargs):
        """Process row before import with enhanced validation."""
        # Ensure email is lowercase and valid
        if 'email' in row:
            email = row['email'].lower().strip()
            if '@' not in email:
                raise ValueError(f"Invalid email format: {email}")
            row['email'] = email

        # Clean phone number
        if 'phone' in row and row['phone']:
            phone = ''.join(filter(str.isdigit, str(row['phone'])))
            row['phone'] = phone if phone else None

    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip rows with validation errors."""
        if import_validation_errors:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)


class UserActivityResource(resources.ModelResource):
    """Enhanced resource for exporting user activity (export only)."""

    user_email = fields.Field(
        column_name='user_email',
        attribute='user__email',
        readonly=True
    )

    user_full_name = fields.Field(
        column_name='user_full_name',
        attribute='user__get_full_name',
        readonly=True
    )

    activity_type_display = fields.Field(
        column_name='activity_type_display',
        attribute='get_activity_type_display',
        readonly=True
    )

    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    # Additional context fields
    user_agent_browser = fields.Field(
        column_name='user_agent_browser',
        readonly=True
    )

    class Meta:
        model = UserActivity
        fields = (
            'id',
            'user_email',
            'user_full_name',
            'activity_type',
            'activity_type_display',
            'description',
            'ip_address',
            'user_agent',
            'user_agent_browser',
            'object_id',
            'object_type',
            'created_at',
        )
        export_order = fields
        # No import - this is export only

    def dehydrate_user_agent_browser(self, activity):
        """Extract browser info from user agent."""
        if not activity.user_agent:
            return "Unknown"

        user_agent = activity.user_agent.lower()
        if 'chrome' in user_agent:
            return "Chrome"
        elif 'firefox' in user_agent:
            return "Firefox"
        elif 'safari' in user_agent:
            return "Safari"
        elif 'edge' in user_agent:
            return "Edge"
        else:
            return "Other"

    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('user')


class RegistrationSourceResource(resources.ModelResource):
    """Enhanced resource for importing/exporting registration sources."""

    is_active = fields.Field(
        column_name='is_active',
        attribute='is_active',
        widget=BooleanWidget()
    )

    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    updated_at = fields.Field(
        column_name='updated_at',
        attribute='updated_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    users_count = fields.Field(
        column_name='users_count',
        readonly=True
    )

    recent_registrations = fields.Field(
        column_name='recent_registrations_7d',
        readonly=True
    )

    class Meta:
        model = RegistrationSource
        fields = (
            'id',
            'name',
            'description',
            'is_active',
            'users_count',
            'recent_registrations',
            'created_at',
            'updated_at',
        )
        export_order = fields
        import_id_fields = ('name',)  # Use name as unique identifier
        skip_unchanged = True
        report_skipped = True

    def dehydrate_users_count(self, registration_source):
        """Calculate total users count for export."""
        return registration_source.user_registration_sources.count()

    def dehydrate_recent_registrations(self, registration_source):
        """Calculate recent registrations count."""

        week_ago = timezone.now() - timedelta(days=7)
        return registration_source.user_registration_sources.filter(
            created_at__gte=week_ago
        ).count()

    def before_import_row(self, row, **kwargs):
        """Process row before import with validation."""
        # Clean and validate name
        if 'name' in row and row['name']:
            row['name'] = row['name'].strip()
            if len(row['name']) < 2:
                raise ValueError(f"Registration source name too short: {row['name']}")
