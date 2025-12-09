"""
Base configuration for knowbase extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.knowbase import BaseKnowbaseSettings

    class KnowbaseSettings(BaseKnowbaseSettings):
        pass

    settings = KnowbaseSettings()
"""

from pydantic import Field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BaseKnowbaseSettings(BaseExtensionSettings):
    """Base settings for knowbase extension."""

    # === Manifest defaults ===
    name: str = "knowbase"
    version: str = "1.0.0"
    description: str = "Knowledge Base with vector search"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "knowbase"
    url_prefix: str = "knowbase"
    url_namespace: str = "knowbase"

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Knowledge Base",
            icon=Icons.MENU_BOOK,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Document Categories",
                    icon=Icons.FOLDER,
                    app="knowbase",
                    model="documentcategory",
                ),
                NavigationItem(
                    title="Documents",
                    icon=Icons.DESCRIPTION,
                    app="knowbase",
                    model="document",
                ),
                NavigationItem(
                    title="Document Chunks",
                    icon=Icons.TEXT_SNIPPET,
                    app="knowbase",
                    model="documentchunk",
                ),
                NavigationItem(
                    title="Document Archives",
                    icon=Icons.ARCHIVE,
                    app="knowbase",
                    model="documentarchive",
                ),
                NavigationItem(
                    title="Archive Items",
                    icon=Icons.FOLDER_OPEN,
                    app="knowbase",
                    model="archiveitem",
                ),
                NavigationItem(
                    title="Archive Item Chunks",
                    icon=Icons.SNIPPET_FOLDER,
                    app="knowbase",
                    model="archiveitemchunk",
                ),
                NavigationItem(
                    title="External Data",
                    icon=Icons.CLOUD_SYNC,
                    app="knowbase",
                    model="externaldata",
                ),
                NavigationItem(
                    title="External Data Chunks",
                    icon=Icons.AUTO_AWESOME_MOTION,
                    app="knowbase",
                    model="externaldatachunk",
                ),
                NavigationItem(
                    title="Chat Sessions",
                    icon=Icons.CHAT,
                    app="knowbase",
                    model="chatsession",
                ),
                NavigationItem(
                    title="Chat Messages",
                    icon=Icons.MESSAGE,
                    app="knowbase",
                    model="chatmessage",
                ),
            ],
        ),
    )
