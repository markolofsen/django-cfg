# Generated manually for django_cfg.apps.integrations.grpc

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GRPCRequestLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_id', models.CharField(db_index=True, help_text='Unique request identifier (UUID)', max_length=100, unique=True)),
                ('service_name', models.CharField(db_index=True, help_text='gRPC service name (e.g., myapp.UserService)', max_length=200)),
                ('method_name', models.CharField(db_index=True, help_text='gRPC method name (e.g., GetUser)', max_length=200)),
                ('full_method', models.CharField(db_index=True, help_text='Full method path (e.g., /myapp.UserService/GetUser)', max_length=400)),
                ('request_size', models.IntegerField(blank=True, help_text='Request size in bytes', null=True)),
                ('response_size', models.IntegerField(blank=True, help_text='Response size in bytes', null=True)),
                ('request_data', models.JSONField(blank=True, help_text='Request data (if logged)', null=True)),
                ('response_data', models.JSONField(blank=True, help_text='Response data (if logged)', null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('error', 'Error'), ('cancelled', 'Cancelled'), ('timeout', 'Timeout')], db_index=True, default='pending', help_text='Current status of request', max_length=20)),
                ('grpc_status_code', models.CharField(blank=True, db_index=True, help_text='gRPC status code (OK, CANCELLED, INVALID_ARGUMENT, etc.)', max_length=50, null=True)),
                ('error_message', models.TextField(blank=True, help_text='Error message if failed', null=True)),
                ('error_details', models.JSONField(blank=True, help_text='Additional error details', null=True)),
                ('duration_ms', models.IntegerField(blank=True, help_text='Total duration in milliseconds', null=True)),
                ('is_authenticated', models.BooleanField(db_index=True, default=False, help_text='Whether request was authenticated')),
                ('client_ip', models.GenericIPAddressField(blank=True, help_text='Client IP address', null=True)),
                ('user_agent', models.TextField(blank=True, help_text='User agent from metadata', null=True)),
                ('peer', models.CharField(blank=True, help_text='gRPC peer information', max_length=200, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, help_text='When request was received')),
                ('completed_at', models.DateTimeField(blank=True, db_index=True, help_text='When request completed (success/error)', null=True)),
                ('user', models.ForeignKey(blank=True, help_text='Authenticated user (if applicable)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='grpc_request_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'gRPC Request Log',
                'verbose_name_plural': 'gRPC Request Logs',
                'db_table': 'django_cfg_grpc_request_log',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='grpcrequestlog',
            index=models.Index(fields=['service_name', '-created_at'], name='django_cfg__service_4c4a8e_idx'),
        ),
        migrations.AddIndex(
            model_name='grpcrequestlog',
            index=models.Index(fields=['method_name', '-created_at'], name='django_cfg__method__8e1a7c_idx'),
        ),
        migrations.AddIndex(
            model_name='grpcrequestlog',
            index=models.Index(fields=['status', '-created_at'], name='django_cfg__status_f3d9a1_idx'),
        ),
        migrations.AddIndex(
            model_name='grpcrequestlog',
            index=models.Index(fields=['user', '-created_at'], name='django_cfg__user_id_9c2b4f_idx'),
        ),
        migrations.AddIndex(
            model_name='grpcrequestlog',
            index=models.Index(fields=['grpc_status_code', '-created_at'], name='django_cfg__grpc_st_a7e5c2_idx'),
        ),
    ]
