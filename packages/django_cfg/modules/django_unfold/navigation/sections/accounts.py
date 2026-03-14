from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_accounts_section(is_github_oauth_enabled: bool = False) -> NavigationSection:
    items = [
        NavBuilder.item("Users", Icons.PEOPLE, "django_cfg_accounts", "customuser"),
        NavBuilder.url_item("User Groups", Icons.GROUP, "admin:auth_group_changelist"),
        NavBuilder.item("OTP Secrets", Icons.SECURITY, "django_cfg_accounts", "otpsecret"),
        NavBuilder.item("Registration Sources", Icons.LINK, "django_cfg_accounts", "registrationsource"),
        NavBuilder.item("User Registration Sources", Icons.PERSON, "django_cfg_accounts", "userregistrationsource"),
    ]
    if is_github_oauth_enabled:
        items.extend([
            NavBuilder.item("OAuth Connections", Icons.LINK, "django_cfg_accounts", "oauthconnection"),
            NavBuilder.item("OAuth States", Icons.KEY, "django_cfg_accounts", "oauthstate"),
        ])
    return NavigationSection(title="Users & Access", separator=True, collapsible=True, items=items)
