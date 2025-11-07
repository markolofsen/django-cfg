"""
gRPC service monitoring and testing utilities.

This package provides tools for monitoring gRPC service health,
performance, and testing service functionality.

**Components**:
- monitoring: Service health monitoring and metrics
- testing: Testing utilities for gRPC services

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.monitoring import (
    MonitoringService,
    TestingService,
)

# Monitor service health
monitor = MonitoringService()
health = monitor.check_health()

# Test service
tester = TestingService()
results = tester.run_tests()
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

# Export when modules are refactored
# from .monitoring import MonitoringService
# from .testing import TestingService

__all__ = [
    # 'MonitoringService',
    # 'TestingService',
]
