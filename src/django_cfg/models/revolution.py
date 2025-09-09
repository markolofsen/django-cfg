"""
Django Revolution Configuration with DRF Integration

Extended configuration model that includes DRF parameters for automatic
integration with django_revolution's create_drf_config.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from django_revolution.app_config import DjangoRevolutionConfig as BaseDjangoRevolutionConfig
from django_revolution.app_config import ZoneConfig


class ExtendedRevolutionConfig(BaseDjangoRevolutionConfig):
    """
    Extended Django Revolution configuration with DRF parameters.
    
    This extends the base DjangoRevolutionConfig to include DRF-specific
    parameters that will be passed to create_drf_config automatically.
    """
    
    # DRF Configuration parameters for create_drf_config
    drf_title: str = Field(
        default="API", 
        description="API title for DRF Spectacular"
    )
    drf_description: str = Field(
        default="RESTful API", 
        description="API description for DRF Spectacular"
    )
    drf_version: str = Field(
        default="1.0.0", 
        description="API version for DRF Spectacular"
    )
    drf_schema_path_prefix: Optional[str] = Field(
        default=None,  # Will default to f"/{api_prefix}/" if None
        description="Schema path prefix for DRF Spectacular"
    )
    drf_enable_browsable_api: bool = Field(
        default=False, 
        description="Enable DRF browsable API"
    )
    drf_enable_throttling: bool = Field(
        default=False, 
        description="Enable DRF throttling"
    )
    drf_serve_include_schema: bool = Field(
        default=False,
        description="Include schema in Spectacular UI (should be False for Django Revolution)"
    )
    
    def get_drf_schema_path_prefix(self) -> str:
        """Get the schema path prefix, defaulting to api_prefix if not set."""
        if self.drf_schema_path_prefix:
            return self.drf_schema_path_prefix
        return f"/{self.api_prefix}/"
    
    def get_drf_config_kwargs(self) -> Dict[str, Any]:
        """
        Get kwargs for create_drf_config from this configuration.
        
        Returns:
            Dict of parameters to pass to create_drf_config
        """
        return {
            "title": self.drf_title,
            "description": self.drf_description,
            "version": self.drf_version,
            "schema_path_prefix": self.get_drf_schema_path_prefix(),
            "enable_browsable_api": self.drf_enable_browsable_api,
            "enable_throttling": self.drf_enable_throttling,
            "serve_include_schema": self.drf_serve_include_schema,
        }
    
    def get_zones_with_defaults(self) -> Dict[str, Any]:
        """
        Get zones with django-cfg default zones automatically added.
        
        Returns:
            Dict of zones including default django-cfg zones
        """
        zones = dict(self.zones) if hasattr(self, 'zones') and self.zones else {}
        
        # Add default django-cfg zones if enabled
        try:
            from django_cfg.modules.base import BaseModule
            base_module = BaseModule()
            
            support_enabled = base_module.is_support_enabled()
            accounts_enabled = base_module.is_accounts_enabled()
            newsletter_enabled = base_module.is_newsletter_enabled()
            leads_enabled = base_module.is_leads_enabled()
            
            # Add Support zone if enabled
            default_support_zone = 'cfg_support'
            if support_enabled and default_support_zone not in zones:
                zones[default_support_zone] = ZoneConfig(
                    apps=["django_cfg.apps.support"],
                    title="Support API",
                    description="Support tickets and messages API",
                    public=False,
                    auth_required=True,
                    version="v1",
                )
            
            # Add Accounts zone if enabled
            default_accounts_zone = 'cfg_accounts'
            if accounts_enabled and default_accounts_zone not in zones:
                zones[default_accounts_zone] = ZoneConfig(
                    apps=["django_cfg.apps.accounts"],
                    title="Accounts API",
                    description="User management, OTP, profiles, and activity tracking API",
                    public=False,
                    auth_required=True,
                    version="v1",
                )
            
            # Add Newsletter zone if enabled
            default_newsletter_zone = 'cfg_newsletter'
            if newsletter_enabled and default_newsletter_zone not in zones:
                zones[default_newsletter_zone] = ZoneConfig(
                    apps=["django_cfg.apps.newsletter"],
                    title="Newsletter API",
                    description="Email campaigns, subscriptions, and newsletter management API",
                    public=False,
                    auth_required=True,
                    version="v1",
                )
            
            # Add Leads zone if enabled
            default_leads_zone = 'cfg_leads'
            if leads_enabled and default_leads_zone not in zones:
                zones[default_leads_zone] = ZoneConfig(
                    apps=["django_cfg.apps.leads"],
                    title="Leads API",
                    description="Lead collection, contact forms, and CRM integration API",
                    public=True,  # Leads can be public for contact forms
                    auth_required=False,
                    version="v1",
                )
        except Exception:
            pass
            
        return zones


# Alias for easier import
RevolutionConfig = ExtendedRevolutionConfig
