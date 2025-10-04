"""
Scheduled maintenance service.

Handles automatic execution of scheduled maintenance events.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

from ..models import ScheduledMaintenance, CloudflareSite
from .bulk_operations_service import bulk_operations

logger = logging.getLogger(__name__)


class ScheduledMaintenanceService:
    """Service for managing scheduled maintenance events."""
    
    def __init__(self):
        """Initialize scheduled maintenance service."""
        pass
    
    def create_scheduled_maintenance(self,
                                   title: str,
                                   scheduled_start: datetime,
                                   estimated_duration: timedelta,
                                   sites: List[CloudflareSite],
                                   description: str = "",
                                   maintenance_message: str = "",
                                   template: str = "modern",
                                   priority: str = "normal",
                                   auto_enable: bool = True,
                                   auto_disable: bool = True,
                                   notify_before: timedelta = timedelta(hours=1),
                                   created_by: str = "") -> ScheduledMaintenance:
        """
        Create a new scheduled maintenance event.
        
        Args:
            title: Maintenance event title
            scheduled_start: When maintenance should start
            estimated_duration: Expected duration
            sites: List of sites to affect
            description: Detailed description
            maintenance_message: Message to display during maintenance
            template: Template to use for maintenance page
            priority: Priority level
            auto_enable: Automatically enable maintenance
            auto_disable: Automatically disable maintenance
            notify_before: When to send notification before start
            created_by: Who created this maintenance
            
        Returns:
            Created ScheduledMaintenance instance
        """
        with transaction.atomic():
            scheduled_maintenance = ScheduledMaintenance.objects.create(
                title=title,
                description=description,
                scheduled_start=scheduled_start,
                estimated_duration=estimated_duration,
                maintenance_message=maintenance_message,
                template=template,
                priority=priority,
                auto_enable=auto_enable,
                auto_disable=auto_disable,
                notify_before=notify_before,
                created_by=created_by
            )
            
            # Add sites
            scheduled_maintenance.sites.set(sites)
            
            logger.info(f"Created scheduled maintenance: {scheduled_maintenance}")
            return scheduled_maintenance
    
    def process_due_maintenances(self) -> Dict[str, Any]:
        """
        Process all maintenance events that are due to start.
        
        Returns:
            Dict with processing results
        """
        due_maintenances = ScheduledMaintenance.get_due_maintenances()
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for maintenance in due_maintenances:
            if maintenance.auto_enable:
                try:
                    result = maintenance.start_maintenance()
                    
                    if result['success']:
                        results['successful'] += 1
                        logger.info(f"Started scheduled maintenance: {maintenance.title}")
                    else:
                        results['failed'] += 1
                        logger.error(f"Failed to start maintenance {maintenance.title}: {result.get('error')}")
                    
                    results['details'].append({
                        'maintenance_id': maintenance.id,
                        'title': maintenance.title,
                        'success': result['success'],
                        'sites_affected': result.get('sites_affected', 0),
                        'error': result.get('error')
                    })
                    
                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"Exception starting maintenance {maintenance.title}: {e}")
                    
                    results['details'].append({
                        'maintenance_id': maintenance.id,
                        'title': maintenance.title,
                        'success': False,
                        'error': str(e)
                    })
                
                results['processed'] += 1
        
        if results['processed'] > 0:
            logger.info(f"Processed {results['processed']} due maintenances: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def process_overdue_maintenances(self) -> Dict[str, Any]:
        """
        Process all maintenance events that should have ended.
        
        Returns:
            Dict with processing results
        """
        overdue_maintenances = ScheduledMaintenance.get_overdue_maintenances()
        
        results = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for maintenance in overdue_maintenances:
            if maintenance.auto_disable:
                try:
                    result = maintenance.complete_maintenance()
                    
                    if result['success']:
                        results['successful'] += 1
                        logger.info(f"Completed overdue maintenance: {maintenance.title}")
                    else:
                        results['failed'] += 1
                        logger.error(f"Failed to complete maintenance {maintenance.title}: {result.get('error')}")
                    
                    results['details'].append({
                        'maintenance_id': maintenance.id,
                        'title': maintenance.title,
                        'success': result['success'],
                        'sites_affected': result.get('sites_affected', 0),
                        'actual_duration': result.get('actual_duration'),
                        'error': result.get('error')
                    })
                    
                except Exception as e:
                    results['failed'] += 1
                    logger.error(f"Exception completing maintenance {maintenance.title}: {e}")
                    
                    results['details'].append({
                        'maintenance_id': maintenance.id,
                        'title': maintenance.title,
                        'success': False,
                        'error': str(e)
                    })
                
                results['processed'] += 1
        
        if results['processed'] > 0:
            logger.info(f"Processed {results['processed']} overdue maintenances: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def get_upcoming_maintenances(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get upcoming maintenance events.
        
        Args:
            hours: Look ahead this many hours
            
        Returns:
            List of upcoming maintenance info
        """
        upcoming = ScheduledMaintenance.get_upcoming_maintenances(hours=hours)
        
        return [
            {
                'id': maintenance.id,
                'title': maintenance.title,
                'scheduled_start': maintenance.scheduled_start.isoformat(),
                'estimated_duration': maintenance.estimated_duration.total_seconds(),
                'sites_count': maintenance.affected_sites_count,
                'priority': maintenance.priority,
                'time_until_start': maintenance.time_until_start.total_seconds() if maintenance.time_until_start else None,
                'auto_enable': maintenance.auto_enable,
                'template': maintenance.template
            }
            for maintenance in upcoming
        ]
    
    def get_active_maintenances(self) -> List[Dict[str, Any]]:
        """Get currently active maintenance events."""
        active = ScheduledMaintenance.objects.filter(
            status=ScheduledMaintenance.Status.ACTIVE
        )
        
        return [
            {
                'id': maintenance.id,
                'title': maintenance.title,
                'started_at': maintenance.actual_start.isoformat() if maintenance.actual_start else None,
                'scheduled_end': maintenance.scheduled_end.isoformat(),
                'sites_count': maintenance.affected_sites_count,
                'priority': maintenance.priority,
                'time_until_end': maintenance.time_until_end.total_seconds() if maintenance.time_until_end else None,
                'auto_disable': maintenance.auto_disable,
                'is_overdue': maintenance.is_overdue
            }
            for maintenance in active
        ]
    
    def get_maintenance_calendar(self, days: int = 30) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get maintenance calendar for specified days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            Dict with dates as keys and maintenance events as values
        """
        end_date = timezone.now() + timedelta(days=days)
        
        maintenances = ScheduledMaintenance.objects.filter(
            scheduled_start__gte=timezone.now(),
            scheduled_start__lte=end_date
        ).order_by('scheduled_start')
        
        calendar = {}
        
        for maintenance in maintenances:
            date_key = maintenance.scheduled_start.date().isoformat()
            
            if date_key not in calendar:
                calendar[date_key] = []
            
            calendar[date_key].append({
                'id': maintenance.id,
                'title': maintenance.title,
                'start_time': maintenance.scheduled_start.time().isoformat(),
                'duration': maintenance.estimated_duration.total_seconds(),
                'sites_count': maintenance.affected_sites_count,
                'priority': maintenance.priority,
                'status': maintenance.status
            })
        
        return calendar
    
    def bulk_schedule_maintenance(self,
                                 title_template: str,
                                 sites_groups: List[List[CloudflareSite]],
                                 start_times: List[datetime],
                                 estimated_duration: timedelta,
                                 **kwargs) -> List[ScheduledMaintenance]:
        """
        Bulk schedule multiple maintenance events.
        
        Args:
            title_template: Template for titles (can include {index})
            sites_groups: List of site groups for each maintenance
            start_times: List of start times for each maintenance
            estimated_duration: Duration for all maintenances
            **kwargs: Additional arguments for create_scheduled_maintenance
            
        Returns:
            List of created ScheduledMaintenance instances
        """
        if len(sites_groups) != len(start_times):
            raise ValueError("sites_groups and start_times must have same length")
        
        created_maintenances = []
        
        for i, (sites, start_time) in enumerate(zip(sites_groups, start_times)):
            title = title_template.format(index=i+1, start_time=start_time.strftime('%Y-%m-%d %H:%M'))
            
            maintenance = self.create_scheduled_maintenance(
                title=title,
                scheduled_start=start_time,
                estimated_duration=estimated_duration,
                sites=sites,
                **kwargs
            )
            
            created_maintenances.append(maintenance)
        
        logger.info(f"Bulk created {len(created_maintenances)} scheduled maintenances")
        return created_maintenances
    
    def cancel_conflicting_maintenances(self, 
                                       new_start: datetime,
                                       new_end: datetime,
                                       sites: List[CloudflareSite],
                                       reason: str = "Conflicting maintenance") -> List[ScheduledMaintenance]:
        """
        Cancel maintenance events that conflict with a new maintenance window.
        
        Args:
            new_start: Start time of new maintenance
            new_end: End time of new maintenance
            sites: Sites affected by new maintenance
            reason: Reason for cancellation
            
        Returns:
            List of cancelled maintenance events
        """
        site_ids = [site.id for site in sites]
        
        # Find conflicting maintenances
        conflicting = ScheduledMaintenance.objects.filter(
            status__in=[ScheduledMaintenance.Status.SCHEDULED, ScheduledMaintenance.Status.ACTIVE],
            sites__id__in=site_ids,
            scheduled_start__lt=new_end,
            scheduled_end__gt=new_start
        ).distinct()
        
        cancelled = []
        
        for maintenance in conflicting:
            result = maintenance.cancel_maintenance(reason=reason)
            if result['success']:
                cancelled.append(maintenance)
                logger.info(f"Cancelled conflicting maintenance: {maintenance.title}")
        
        return cancelled


# Global instance
scheduled_maintenance_service = ScheduledMaintenanceService()


# Convenience functions
def schedule_maintenance_for_sites(sites: List[CloudflareSite],
                                  title: str,
                                  start_time: datetime,
                                  duration_hours: int = 2,
                                  **kwargs) -> ScheduledMaintenance:
    """Convenience function to schedule maintenance for sites."""
    return scheduled_maintenance_service.create_scheduled_maintenance(
        title=title,
        scheduled_start=start_time,
        estimated_duration=timedelta(hours=duration_hours),
        sites=sites,
        **kwargs
    )


def process_scheduled_maintenances() -> Dict[str, Any]:
    """Process all due and overdue maintenances."""
    due_results = scheduled_maintenance_service.process_due_maintenances()
    overdue_results = scheduled_maintenance_service.process_overdue_maintenances()
    
    return {
        'due_maintenances': due_results,
        'overdue_maintenances': overdue_results,
        'total_processed': due_results['processed'] + overdue_results['processed']
    }
