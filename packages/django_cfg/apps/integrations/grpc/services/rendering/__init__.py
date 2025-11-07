"""
gRPC content rendering services.

This package provides tools for generating charts, graphs, and other
visual content for gRPC responses.

**Components**:
- charts: Chart generation service

**Usage Example**:
```python
from django_cfg.apps.integrations.grpc.services.rendering import ChartGenerator

generator = ChartGenerator()
chart_data = generator.generate_chart(data=timeseries, chart_type="line")
```

Created: 2025-11-07
Status: %%PRODUCTION%%
"""

# Export when modules are refactored
# from .charts import ChartGenerator

__all__ = [
    # 'ChartGenerator',
]
