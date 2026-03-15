from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_totp_section() -> NavigationSection:
    return NavigationSection(
        title="TOTP",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.item("TOTP Devices", Icons.PHONE_ANDROID, "django_cfg_totp", "totpdevice"),
            NavBuilder.item("Backup Codes", Icons.SECURITY, "django_cfg_totp", "backupcode"),
            NavBuilder.item("2FA Sessions", Icons.VERIFIED_USER, "django_cfg_totp", "twofactorsession"),
        ],
    )
