"""
Import/Export resources for Accounts app.
"""

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget, BooleanWidget, ManyToManyWidget
from django.contrib.auth.models import Group

from ..models import CustomUser, UserActivity, RegistrationSource, TwilioResponse


class CustomUserResource(resources.ModelResource):
    """Resource for importing/exporting users."""
    
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
            'last_login',
            'date_joined',
        )
        export_order = fields
        import_id_fields = ('email',)  # Use email as unique identifier
        skip_unchanged = True
        report_skipped = True
        
    def before_import_row(self, row, **kwargs):
        """Process row before import."""
        # Ensure email is lowercase
        if 'email' in row:
            row['email'] = row['email'].lower().strip()
            
    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip rows with validation errors."""
        if import_validation_errors:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)


class UserActivityResource(resources.ModelResource):
    """Resource for exporting user activity (export only)."""
    
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
            'object_id',
            'object_type',
            'created_at',
        )
        export_order = fields
        # No import - this is export only
        
    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('user')


class RegistrationSourceResource(resources.ModelResource):
    """Resource for importing/exporting registration sources."""
    
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

    class Meta:
        model = RegistrationSource
        fields = (
            'id',
            'url',
            'name',
            'description',
            'is_active',
            'users_count',
            'created_at',
            'updated_at',
        )
        export_order = fields
        import_id_fields = ('url',)  # Use URL as unique identifier
        skip_unchanged = True
        report_skipped = True
        
    def dehydrate_users_count(self, registration_source):
        """Calculate users count for export."""
        return registration_source.user_registration_sources.count()
        
    def before_import_row(self, row, **kwargs):
        """Process row before import."""
        # Ensure URL is properly formatted
        if 'url' in row and row['url']:
            url = row['url'].strip()
            if not url.startswith(('http://', 'https://')):
                row['url'] = f'https://{url}'
            else:
                row['url'] = url


class TwilioResponseResource(resources.ModelResource):
    """Resource for exporting Twilio responses (export only)."""
    
    otp_recipient = fields.Field(
        column_name='otp_recipient',
        attribute='otp_secret__recipient',
        readonly=True
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
    
    twilio_created_at = fields.Field(
        column_name='twilio_created_at',
        attribute='twilio_created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    has_error = fields.Field(
        column_name='has_error',
        attribute='has_error',
        widget=BooleanWidget(),
        readonly=True
    )
    
    is_successful = fields.Field(
        column_name='is_successful',
        attribute='is_successful',
        widget=BooleanWidget(),
        readonly=True
    )

    class Meta:
        model = TwilioResponse
        fields = (
            'id',
            'response_type',
            'service_type',
            'status',
            'message_sid',
            'verification_sid',
            'to_number',
            'from_number',
            'otp_recipient',
            'error_code',
            'error_message',
            'price',
            'price_unit',
            'has_error',
            'is_successful',
            'created_at',
            'updated_at',
            'twilio_created_at',
        )
        export_order = fields
        # No import - this is export only
        
    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('otp_secret')
