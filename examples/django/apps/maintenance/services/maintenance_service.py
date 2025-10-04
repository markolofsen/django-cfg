"""
Super simple maintenance service using Page Rules.

No Workers, no templates, no complexity - just Page Rules!
"""

import logging
import time
from typing import Dict, Any
from cloudflare import Cloudflare

from ..models import CloudflareSite, MaintenanceLog
from ..utils import retry_on_failure

logger = logging.getLogger(__name__)

class MaintenanceService:
    """
    Simple maintenance via Cloudflare Page Rules.
    
    Enable: Create Page Rule redirect to maintenance.reforms.ai
    Disable: Delete Page Rule
    """
    
    def __init__(self, site: CloudflareSite):
        """Initialize service for specific site."""
        self.site = site
        self.client = Cloudflare(api_token=site.api_key.api_token)
    
    def enable_maintenance(self, reason: str = "Scheduled maintenance") -> MaintenanceLog:
        """
        Enable maintenance mode using Page Rule redirect.
        
        Steps:
        1. Create Page Rule redirect to maintenance.reforms.ai
        2. Update site.maintenance_active = True
        3. Log the operation
        """
        start_time = time.time()
        log_entry = MaintenanceLog.log_pending(self.site, MaintenanceLog.Action.ENABLE, reason)
        
        try:
            # 1. Create Page Rule for maintenance redirect
            logger.info(f"Creating page rule for: {self.site.domain} → {self.site.get_maintenance_url()}")
            page_rule_response = self._create_maintenance_page_rule()
            
            # 2. Update site status
            self.site.enable_maintenance()
            
            # 3. Log success
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.SUCCESS
            log_entry.duration_seconds = duration
            log_entry.cloudflare_response = {
                'page_rule_create': self._serialize_response(page_rule_response)
            }
            log_entry.save()
            
            return log_entry
            
        except Exception as e:
            # Log failure
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.FAILED
            log_entry.error_message = str(e)
            log_entry.duration_seconds = duration
            log_entry.save()
            
            raise e
    
    def disable_maintenance(self) -> MaintenanceLog:
        """
        Disable maintenance mode by removing Page Rule.
        
        Steps:
        1. Remove Page Rule redirect
        2. Update site.maintenance_active = False  
        3. Log the operation
        """
        start_time = time.time()
        log_entry = MaintenanceLog.log_pending(self.site, MaintenanceLog.Action.DISABLE)
        
        try:
            # 1. Remove Page Rule
            logger.info(f"Removing page rule for: {self.site.domain}")
            page_rule_response = self._delete_maintenance_page_rule()
            
            # 2. Update site status
            self.site.disable_maintenance()
            
            # 3. Log success
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.SUCCESS
            log_entry.duration_seconds = duration
            log_entry.cloudflare_response = {
                'page_rule_delete': self._serialize_response(page_rule_response)
            }
            log_entry.save()
            
            return log_entry
            
        except Exception as e:
            # Log failure
            duration = int(time.time() - start_time)
            log_entry.status = MaintenanceLog.Status.FAILED
            log_entry.error_message = str(e)
            log_entry.duration_seconds = duration
            log_entry.save()
            
            raise e
    
    def get_status(self) -> bool:
        """Get current maintenance status for site."""
        return self.site.maintenance_active
    
    # Private helper methods
    
    def _serialize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Cloudflare API response to JSON serializable format."""
        import json
        from datetime import datetime
        
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            else:
                return obj
        
        try:
            # Convert all datetime objects to ISO strings
            serializable = convert_datetime(response)
            # Test JSON serialization
            json.dumps(serializable)
            return serializable
        except Exception:
            # If serialization fails, return simple success message
            return {"success": True, "serialization_error": True}
    
    @retry_on_failure(max_retries=3, base_delay=1.0)
    def _create_maintenance_page_rule(self) -> Dict[str, Any]:
        """Create Page Rules to redirect all traffic to maintenance page (including subdomains)."""
        maintenance_url = self.site.get_maintenance_url()
        patterns = self.site.get_domain_patterns()
        
        logger.info(f"Creating page rules for {self.site.domain}: {patterns} → {maintenance_url}")
        
        # First, check if conflicting Page Rules already exist and delete them
        try:
            existing_rules = self.client.page_rules.list(zone_id=self.site.zone_id)
            
            # Handle different API response formats
            if hasattr(existing_rules, 'result'):
                rules = existing_rules.result
            else:
                rules = existing_rules
            
            # Look for conflicting rules with same patterns
            for rule in rules:
                if (hasattr(rule, 'targets') and rule.targets and 
                    len(rule.targets) > 0 and 
                    hasattr(rule.targets[0], 'constraint') and 
                    hasattr(rule.targets[0].constraint, 'value')):
                    
                    rule_pattern = rule.targets[0].constraint.value
                    if rule_pattern in patterns:
                        logger.info(f"Found conflicting page rule {rule.id} with pattern {rule_pattern}, deleting...")
                        self.client.page_rules.delete(
            zone_id=self.site.zone_id,
                            pagerule_id=rule.id
                        )
                        logger.info(f"Deleted conflicting page rule {rule.id}")
                    
        except Exception as e:
            logger.warning(f"Error checking existing page rules: {e}")
            # Continue with creation anyway
        
        # Create Page Rules for each pattern
        created_rules = []
        for pattern in patterns:
            try:
                logger.info(f"Creating page rule: {pattern} → {maintenance_url}")
                response = self.client.page_rules.create(
                    zone_id=self.site.zone_id,
                    targets=[{
                        "target": "url",
                        "constraint": {
                            "operator": "matches",
                            "value": pattern
                        }
                    }],
                    actions=[{
                        "id": "forwarding_url",
                        "value": {
                            "url": maintenance_url,
                            "status_code": 302
                        }
                    }],
                    status="active"
                )
                created_rules.append({
                    "pattern": pattern,
                    "rule_id": response.id if hasattr(response, 'id') else 'unknown',
                    "response": response.model_dump()
                })
                logger.info(f"Created page rule for pattern {pattern}")
                
            except Exception as e:
                logger.error(f"Failed to create page rule for pattern {pattern}: {e}")
                # Continue with other patterns
        
        return {
            "success": True,
            "patterns": patterns,
            "created_rules": created_rules,
            "total_rules": len(created_rules)
        }
    
    @retry_on_failure(max_retries=3, base_delay=1.0)
    def _delete_maintenance_page_rule(self) -> Dict[str, Any]:
        """Delete maintenance Page Rules with retry logic (including subdomains)."""
        # Find the maintenance page rules
        page_rules_response = self.client.page_rules.list(zone_id=self.site.zone_id)
        
        # Handle different API response formats
        if hasattr(page_rules_response, 'result'):
            page_rules = page_rules_response.result
        else:
            page_rules = page_rules_response
        
        patterns = self.site.get_domain_patterns()
        maintenance_url = self.site.get_maintenance_url()
        
        logger.info(f"Looking for page rules to delete: patterns={patterns}, url={maintenance_url}")
        logger.info(f"Found {len(page_rules)} page rules total")
        
        deleted_rules = []
        
        for rule in page_rules:
            logger.info(f"Checking rule {rule.id}: targets={getattr(rule, 'targets', None)}, actions={getattr(rule, 'actions', None)}")
            
            # Check if this rule matches our maintenance patterns
            rule_matches = False
            
            # Check by pattern
            if (hasattr(rule, 'targets') and rule.targets and 
                len(rule.targets) > 0 and 
                hasattr(rule.targets[0], 'constraint') and 
                hasattr(rule.targets[0].constraint, 'value')):
                
                rule_pattern = rule.targets[0].constraint.value
                if rule_pattern in patterns:
                    rule_matches = True
                    logger.info(f"Rule {rule.id} matches pattern: {rule_pattern}")
            
            # Also check by URL (fallback for older rules)
            if not rule_matches and (hasattr(rule, 'actions') and rule.actions and 
                len(rule.actions) > 0 and 
                hasattr(rule.actions[0], 'id') and 
                rule.actions[0].id == "forwarding_url"):
                
                action_value = getattr(rule.actions[0], 'value', {})
                action_url = getattr(action_value, 'url', '')
                
                logger.info(f"Found forwarding rule with URL: {action_url}")
                
                if ("maintenance.reforms.ai" in action_url or 
                    "djangocfg.com/maintenance" in action_url):
                    rule_matches = True
                    logger.info(f"Rule {rule.id} matches maintenance URL")
            
            # Delete matching rule
            if rule_matches:
                try:
                    logger.info(f"Deleting maintenance page rule: {rule.id}")
                    response = self.client.page_rules.delete(
                        zone_id=self.site.zone_id,
                        pagerule_id=rule.id
                    )
                    deleted_rules.append({
                        "rule_id": rule.id,
                        "pattern": getattr(rule.targets[0].constraint, 'value', 'unknown') if hasattr(rule, 'targets') and rule.targets else 'unknown',
                        "response": response.model_dump()
                    })
                    logger.info(f"Successfully deleted page rule: {rule.id}")
                    
                except Exception as e:
                    logger.error(f"Failed to delete page rule {rule.id}: {e}")
        
        if deleted_rules:
            logger.info(f"Deleted {len(deleted_rules)} maintenance page rules for {self.site.domain}")
            return {
                "success": True,
                "deleted_rules": deleted_rules,
                "total_deleted": len(deleted_rules)
            }
        else:
            logger.warning(f"No maintenance page rules found for {self.site.domain}")
            return {"success": True, "message": "No page rules to delete"}
    


# Convenience functions for easy usage

def enable_maintenance_for_domain(domain: str, reason: str = "Scheduled maintenance") -> MaintenanceLog:
    """Enable maintenance for a domain."""
    site = CloudflareSite.objects.get(domain=domain)
    service = MaintenanceService(site)
    return service.enable_maintenance(reason)


def disable_maintenance_for_domain(domain: str) -> MaintenanceLog:
    """Disable maintenance for a domain."""
    site = CloudflareSite.objects.get(domain=domain)
    service = MaintenanceService(site)
    return service.disable_maintenance()
