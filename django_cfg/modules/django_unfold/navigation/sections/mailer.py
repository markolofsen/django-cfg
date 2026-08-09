from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.django_unfold.models.navigation import NavigationSection
from django_cfg.modules.django_unfold.navigation.builder import NavBuilder


def build_mailer_section() -> NavigationSection:
    """Letter copy and the send log.

    Its own section rather than an entry under "Users & Access": the copy is not
    a property of a user, and the log answers an operational question ("did that
    letter go out, in which language") that belongs next to the content it is
    about.
    """
    return NavigationSection(
        title="Mail",
        separator=True,
        collapsible=True,
        items=[
            NavBuilder.item(
                "Email Content", Icons.TRANSLATE, "django_cfg_mailer", "emailcontent"
            ),
            NavBuilder.item(
                "Email Log", Icons.OUTGOING_MAIL, "django_cfg_mailer", "emaillog"
            ),
        ],
    )
