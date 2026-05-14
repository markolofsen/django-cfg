from django.http import HttpRequest
import django
import sys
import platform


def callback(request: HttpRequest) -> dict:
    from django.contrib.auth import get_user_model
    from django.db import connection

    User = get_user_model()
    total_users = User.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    staff = User.objects.filter(is_staff=True).count()

    # DB table count
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'"
        )
        table_count = cursor.fetchone()[0]

    return {
        'django_version': django.get_version(),
        'python_version': sys.version.split()[0],
        'platform': platform.system(),
        'total_users': total_users,
        'superusers': superusers,
        'staff_users': staff,
        'db_table_count': table_count,
    }
