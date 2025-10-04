"""
Import/Export resources for Leads app.
"""

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget, BooleanWidget, JSONWidget
from django.contrib.auth import get_user_model

from ..models import Lead

User = get_user_model()


class LeadResource(resources.ModelResource):
    """Resource for importing/exporting leads."""
    
    # Custom fields for better export/import
    user_email = fields.Field(
        column_name='user_email',
        attribute='user__email',
        widget=ForeignKeyWidget(User, field='email'),
        readonly=False
    )
    
    status_display = fields.Field(
        column_name='status_display',
        attribute='get_status_display',
        readonly=True
    )
    
    contact_type_display = fields.Field(
        column_name='contact_type_display',
        attribute='get_contact_type_display',
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
    
    extra = fields.Field(
        column_name='extra',
        attribute='extra',
        widget=JSONWidget()
    )

    class Meta:
        model = Lead
        fields = (
            'id',
            'name',
            'email',
            'company',
            'company_site',
            'contact_type',
            'contact_type_display',
            'contact_value',
            'subject',
            'message',
            'extra',
            'site_url',
            'user_agent',
            'ip_address',
            'status',
            'status_display',
            'user_email',
            'admin_notes',
            'created_at',
            'updated_at',
        )
        export_order = fields
        import_id_fields = ('email', 'site_url', 'created_at')  # Composite unique identifier
        skip_unchanged = True
        report_skipped = True
        
    def before_import_row(self, row, **kwargs):
        """Process row before import."""
        # Ensure email is lowercase
        if 'email' in row:
            row['email'] = row['email'].lower().strip()
            
        # Handle user assignment by email
        if 'user_email' in row and row['user_email']:
            try:
                user = User.objects.get(email=row['user_email'].lower().strip())
                row['user'] = user.pk
            except User.DoesNotExist:
                # Clear user field if email not found
                row['user'] = None
                
        # Validate status
        if 'status' in row and row['status']:
            valid_statuses = [choice[0] for choice in Lead.StatusChoices.choices]
            if row['status'] not in valid_statuses:
                row['status'] = Lead.StatusChoices.NEW
                
        # Validate contact_type
        if 'contact_type' in row and row['contact_type']:
            valid_types = [choice[0] for choice in Lead.ContactTypeChoices.choices]
            if row['contact_type'] not in valid_types:
                row['contact_type'] = Lead.ContactTypeChoices.EMAIL
                
    def skip_row(self, instance, original, row, import_validation_errors=None):
        """Skip rows with validation errors."""
        if import_validation_errors:
            return True
        return super().skip_row(instance, original, row, import_validation_errors)
        
    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('user')
