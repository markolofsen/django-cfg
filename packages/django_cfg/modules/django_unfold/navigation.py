"""
Default Navigation Configuration for Django CFG Unfold

Provides default navigation sections based on enabled django-cfg modules.
"""

from typing import Any, Dict, List

from django.urls import reverse_lazy

from django_cfg.modules.django_admin.icons import Icons
from django_cfg.modules.base import BaseCfgModule

from .models.navigation import NavigationItem, NavigationSection


class NavigationManager(BaseCfgModule):
    """
    Navigation configuration manager for Unfold.

    Generates default navigation sections based on enabled django-cfg modules.
    """

    def __init__(self, config=None):
        """Initialize navigation manager."""
        super().__init__()
        self._config = config
        self._config_loaded = config is not None

    @property
    def config(self):
        """Lazy load config on first access."""
        if not self._config_loaded:
            try:
                self._config = self.get_config()
            except Exception:
                self._config = None
            finally:
                self._config_loaded = True
        return self._config

    def get_navigation_config(self) -> List[Dict[str, Any]]:
        """Get complete default navigation configuration for Unfold sidebar."""
        navigation_sections = [
            NavigationSection(
                title="Dashboard",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Overview", icon=Icons.DASHBOARD, link=str(reverse_lazy("admin:index"))),
                    NavigationItem(title="Settings", icon=Icons.SETTINGS, link=str(reverse_lazy("admin:constance_config_changelist"))),
                    NavigationItem(title="Health Check", icon=Icons.HEALTH_AND_SAFETY, link=str(reverse_lazy("django_cfg_drf_health"))),
                    NavigationItem(title="Endpoints Status", icon=Icons.API, link=str(reverse_lazy("endpoints_status_drf"))),
                ]
            ),
        ]

        # Centrifugo Dashboard (if enabled)
        if self.is_centrifugo_enabled():
            navigation_sections.append(
                NavigationSection(
                    title="Centrifugo",
                    separator=True,
                    collapsible=True,
                    items=[
                        NavigationItem(title="Dashboard", icon=Icons.MONITOR_HEART, link="/cfg/admin/private/centrifugo"),
                        NavigationItem(title="Logs", icon=Icons.LIST_ALT, link=str(reverse_lazy("admin:django_cfg_centrifugo_centrifugolog_changelist"))),
                    ]
                )
            )

        # Add Operations section (System & Monitoring tools)
        operations_items = []

        # Background Tasks (if enabled)
        if self.should_enable_tasks():
            operations_items.extend([
                NavigationItem(title="Background Tasks", icon=Icons.TASK, link=str(reverse_lazy("admin:django_dramatiq_task_changelist"))),
                NavigationItem(title="Task Dashboard", icon=Icons.SETTINGS_APPLICATIONS, link=str(reverse_lazy("dashboard"))),
            ])

        # Maintenance Mode (if enabled)
        if self.is_maintenance_enabled():
            operations_items.append(
                NavigationItem(title="Maintenance", icon=Icons.BUILD, link=str(reverse_lazy("admin:maintenance_cloudflaresite_changelist")))
            )

        # Add Operations section if there are any items
        if operations_items:
            navigation_sections.append(NavigationSection(
                title="Operations",
                separator=True,
                collapsible=True,
                items=operations_items
            ))

        # Add Accounts section if enabled
        if self.is_accounts_enabled():
            navigation_sections.append(NavigationSection(
                title="Users & Access",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Users", icon=Icons.PEOPLE, link=str(reverse_lazy("admin:django_cfg_accounts_customuser_changelist"))),
                    NavigationItem(title="User Groups", icon=Icons.GROUP, link=str(reverse_lazy("admin:auth_group_changelist"))),
                    NavigationItem(title="OTP Secrets", icon=Icons.SECURITY, link=str(reverse_lazy("admin:django_cfg_accounts_otpsecret_changelist"))),
                    NavigationItem(title="Registration Sources", icon=Icons.LINK, link=str(reverse_lazy("admin:django_cfg_accounts_registrationsource_changelist"))),
                    NavigationItem(title="User Registration Sources", icon=Icons.PERSON, link=str(reverse_lazy("admin:django_cfg_accounts_userregistrationsource_changelist"))),
                ]
            ))

        # Add Support section if enabled
        if self.is_support_enabled():
            navigation_sections.append(NavigationSection(
                title="Support",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Tickets", icon=Icons.SUPPORT_AGENT, link=str(reverse_lazy("admin:django_cfg_support_ticket_changelist"))),
                    NavigationItem(title="Messages", icon=Icons.CHAT, link=str(reverse_lazy("admin:django_cfg_support_message_changelist"))),
                ]
            ))

        # Add Newsletter section if enabled
        if self.is_newsletter_enabled():
            navigation_sections.append(NavigationSection(
                title="Newsletter",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Newsletters", icon=Icons.EMAIL, link=str(reverse_lazy("admin:django_cfg_newsletter_newsletter_changelist"))),
                    NavigationItem(title="Subscriptions", icon=Icons.PERSON_ADD, link=str(reverse_lazy("admin:django_cfg_newsletter_newslettersubscription_changelist"))),
                    NavigationItem(title="Campaigns", icon=Icons.CAMPAIGN, link=str(reverse_lazy("admin:django_cfg_newsletter_newslettercampaign_changelist"))),
                    NavigationItem(title="Email Logs", icon=Icons.MAIL_OUTLINE, link=str(reverse_lazy("admin:django_cfg_newsletter_emaillog_changelist"))),
                ]
            ))

        # Add Leads section if enabled
        if self.is_leads_enabled():
            navigation_sections.append(NavigationSection(
                title="Leads",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Leads", icon=Icons.CONTACT_PAGE, link=str(reverse_lazy("admin:django_cfg_leads_lead_changelist"))),
                ]
            ))

        # Add Agents section if enabled
        if self.is_agents_enabled():
            navigation_sections.append(NavigationSection(
                title="AI Agents",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Agent Definitions", icon=Icons.SMART_TOY, link=str(reverse_lazy("admin:django_cfg_agents_agentdefinition_changelist"))),
                    NavigationItem(title="Agent Templates", icon=Icons.DESCRIPTION, link=str(reverse_lazy("admin:django_cfg_agents_agenttemplate_changelist"))),
                    NavigationItem(title="Agent Executions", icon=Icons.PLAY_ARROW, link=str(reverse_lazy("admin:django_cfg_agents_agentexecution_changelist"))),
                    NavigationItem(title="Workflow Executions", icon=Icons.AUTORENEW, link=str(reverse_lazy("admin:django_cfg_agents_workflowexecution_changelist"))),
                    NavigationItem(title="Tool Executions", icon=Icons.BUILD, link=str(reverse_lazy("admin:django_cfg_agents_toolexecution_changelist"))),
                    NavigationItem(title="Toolset Configurations", icon=Icons.SETTINGS, link=str(reverse_lazy("admin:django_cfg_agents_toolsetconfiguration_changelist"))),
                ]
            ))

        # Add Knowledge Base section if enabled
        if self.is_knowbase_enabled():
            navigation_sections.append(NavigationSection(
                title="Knowledge Base",
                separator=True,
                collapsible=True,
                items=[
                    NavigationItem(title="Document Categories", icon=Icons.FOLDER, link=str(reverse_lazy("admin:django_cfg_knowbase_documentcategory_changelist"))),
                    NavigationItem(title="Documents", icon=Icons.DESCRIPTION, link=str(reverse_lazy("admin:django_cfg_knowbase_document_changelist"))),
                    NavigationItem(title="Document Chunks", icon=Icons.TEXT_SNIPPET, link=str(reverse_lazy("admin:django_cfg_knowbase_documentchunk_changelist"))),
                    NavigationItem(title="Document Archives", icon=Icons.ARCHIVE, link=str(reverse_lazy("admin:django_cfg_knowbase_documentarchive_changelist"))),
                    NavigationItem(title="Archive Items", icon=Icons.FOLDER_OPEN, link=str(reverse_lazy("admin:django_cfg_knowbase_archiveitem_changelist"))),
                    NavigationItem(title="Archive Item Chunks", icon=Icons.SNIPPET_FOLDER, link=str(reverse_lazy("admin:django_cfg_knowbase_archiveitemchunk_changelist"))),
                    NavigationItem(title="External Data", icon=Icons.CLOUD_SYNC, link=str(reverse_lazy("admin:django_cfg_knowbase_externaldata_changelist"))),
                    NavigationItem(title="External Data Chunks", icon=Icons.AUTO_AWESOME_MOTION, link=str(reverse_lazy("admin:django_cfg_knowbase_externaldatachunk_changelist"))),
                    NavigationItem(title="Chat Sessions", icon=Icons.CHAT, link=str(reverse_lazy("admin:django_cfg_knowbase_chatsession_changelist"))),
                    NavigationItem(title="Chat Messages", icon=Icons.MESSAGE, link=str(reverse_lazy("admin:django_cfg_knowbase_chatmessage_changelist"))),
                ]
            ))

        # Add Payments section if enabled (v2.0)
        if self.is_payments_enabled():
            payments_items = [
                # Core payment models (v2.0)
                NavigationItem(title="Payments", icon=Icons.ACCOUNT_BALANCE, link=str(reverse_lazy("admin:payments_payment_changelist"))),
                NavigationItem(title="Currencies", icon=Icons.CURRENCY_BITCOIN, link=str(reverse_lazy("admin:payments_currency_changelist"))),
                NavigationItem(title="User Balances", icon=Icons.ACCOUNT_BALANCE_WALLET, link=str(reverse_lazy("admin:payments_userbalance_changelist"))),
                NavigationItem(title="Transactions", icon=Icons.RECEIPT_LONG, link=str(reverse_lazy("admin:payments_transaction_changelist"))),
                NavigationItem(title="Withdrawal Requests", icon=Icons.DOWNLOAD, link=str(reverse_lazy("admin:payments_withdrawalrequest_changelist"))),
            ]

            navigation_sections.append(NavigationSection(
                title="Payments",
                separator=True,
                collapsible=True,
                items=payments_items
            ))

        # Convert all NavigationSection objects to dictionaries
        return [section.to_dict() for section in navigation_sections]


# Lazy initialization to avoid circular imports
_navigation_manager = None

def get_navigation_manager() -> NavigationManager:
    """Get the global navigation manager instance."""
    global _navigation_manager
    if _navigation_manager is None:
        _navigation_manager = NavigationManager()
    return _navigation_manager
