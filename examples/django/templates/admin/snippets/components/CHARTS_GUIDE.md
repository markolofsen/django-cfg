# Chart.js Integration Guide

## Overview

This guide documents the Chart.js integration in the Django CFG dashboard, including key insights, best practices, and solutions to common issues.

## Architecture

### Data Flow

```
Python (callbacks/charts.py)
  → Pydantic Models (ChartData, ChartDataset)
  → JSON Serialization (.model_dump())
  → Django Template (|safe filter)
  → JavaScript (Chart.js)
```

### File Structure

- **Backend**: `/django_cfg/modules/django_unfold/callbacks/charts.py` - Chart data generation
- **Models**: `/django_cfg/modules/django_unfold/models/charts.py` - Pydantic data models
- **Template**: `/django_cfg/templates/admin/snippets/components/charts_section.html` - Chart rendering

## Key Implementation Details

### 1. Container Height - CRITICAL

**❌ WRONG - Infinite Height Growth:**
```html
<canvas id="myChart" height="300"></canvas>
```

**✅ CORRECT - Fixed Container:**
```html
<div class="relative h-[300px]">
    <canvas id="myChart"></canvas>
</div>
```

**Why:** Chart.js with `responsive: true` + `maintainAspectRatio: false` needs a fixed-height parent container. Without it, the canvas grows infinitely as Chart.js tries to maintain responsiveness.

### 2. Data Format

Chart.js expects this structure:

```javascript
{
    type: 'line',  // or 'bar', 'pie', etc.
    data: {
        labels: ['Day 1', 'Day 2', ...],
        datasets: [{
            label: 'Dataset Name',
            data: [10, 20, 30, ...],
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderColor: 'rgb(59, 130, 246)',
            tension: 0.4  // for line charts
        }]
    },
    options: { ... }
}
```

**Our Implementation:**
```javascript
new Chart(ctx, {
    type: 'line',
    data: chartData,  // chartData = {labels: [...], datasets: [...]}
    options: { ... }
});
```

### 3. Python to JavaScript Bridge

**Backend (charts.py):**
```python
from .models.charts import ChartData, ChartDataset

def get_user_registration_chart_data(self) -> Dict[str, Any]:
    chart_data = ChartData(
        labels=["09/26", "09/27", ...],
        datasets=[
            ChartDataset(
                label="New Users",
                data=[2, 5, 3, ...],
                backgroundColor="rgba(59, 130, 246, 0.1)",
                borderColor="rgb(59, 130, 246)",
                tension=0.4
            )
        ]
    )
    return chart_data.model_dump()  # Converts Pydantic to dict
```

**Template:**
```html
<!-- Serialize to JSON for JavaScript -->
"charts": {
    "user_registrations_json": json.dumps(self.get_user_registration_chart_data()),
    "user_registrations": self.get_user_registration_chart_data(),
}
```

**HTML/JavaScript:**
```html
<script>
    const chartData = {{ charts.user_registrations_json|safe }};
    new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: { ... }
    });
</script>
```

### 4. Chart.js Configuration Best Practices

```javascript
{
    type: 'line',  // or 'bar'
    data: chartData,
    options: {
        responsive: true,              // Chart resizes with container
        maintainAspectRatio: false,   // Don't maintain aspect ratio
        plugins: {
            legend: {
                display: true,
                position: 'top'
            }
        },
        scales: {
            y: {
                beginAtZero: true,    // Start Y axis at 0
                ticks: {
                    precision: 0      // Show integers only (no decimals)
                }
            }
        }
    }
}
```

## Common Issues & Solutions

### Issue 1: Charts Not Displaying

**Symptoms:** Canvas element exists but no chart visible

**Debug Checklist:**
```javascript
console.log('Chart.js loaded:', typeof Chart !== 'undefined');
console.log('Canvas element:', document.getElementById('myChart'));
console.log('Chart data:', chartData);
console.log('Data has labels:', 'labels' in chartData);
console.log('Data has datasets:', 'datasets' in chartData);
```

**Common Causes:**
1. Chart.js library not loaded
2. Canvas ID mismatch
3. Data format incorrect
4. DOMContentLoaded not fired yet

### Issue 2: Infinite Height Growth

**Symptoms:** Chart keeps expanding vertically, page becomes very tall

**Solution:** Wrap canvas in fixed-height container (see section 1 above)

### Issue 3: Data Not Updating

**Symptoms:** Chart shows old data after refresh

**Solution:** Ensure Chart.js recreates instead of updates:
```javascript
// Destroy existing chart first
if (window.myChart) {
    window.myChart.destroy();
}
window.myChart = new Chart(ctx, config);
```

### Issue 4: Dark Mode Colors

**Best Practices:**
```python
ChartDataset(
    backgroundColor="rgba(59, 130, 246, 0.1)",  # Light with transparency
    borderColor="rgb(59, 130, 246)",            # Solid color
    # Use theme-aware colors that work in both light/dark modes
)
```

## Template Integration

### Complete Working Example

```html
{% if charts.user_registrations %}
    <div class="relative h-[300px]">
        <canvas id="userRegistrationsChart"></canvas>
    </div>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('userRegistrationsChart');
            const chartData = {{ charts.user_registrations_json|safe }};

            if (ctx && typeof Chart !== 'undefined') {
                try {
                    new Chart(ctx, {
                        type: 'line',
                        data: chartData,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: true,
                                    position: 'top'
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        precision: 0
                                    }
                                }
                            }
                        }
                    });
                } catch (error) {
                    console.error('Error creating chart:', error);
                }
            }
        });
    </script>
{% else %}
    <div class="h-[300px] flex items-center justify-center">
        <p class="text-gray-500">No chart data available</p>
    </div>
{% endif %}
```

## Testing Chart Integration

### 1. Verify Chart.js Load

```javascript
console.log('Chart.js version:', Chart.version); // Should show: 4.4.0
```

### 2. Check Data Structure

```python
# In callbacks/charts.py
chart_data = self.get_user_registration_chart_data()
print(f"Labels: {chart_data['labels']}")
print(f"Dataset count: {len(chart_data['datasets'])}")
print(f"Data points: {chart_data['datasets'][0]['data']}")
```

### 3. Template Debugging

```html
<!-- Add temporary debug output -->
<pre>{{ charts.user_registrations|pprint }}</pre>
```

## Performance Considerations

1. **Limit Data Points**: Keep chart data to reasonable size (e.g., 7-90 days max)
2. **Lazy Loading**: Load charts only when tab/section is visible
3. **Caching**: Cache chart data in backend if queries are expensive
4. **Animation**: Disable animations for large datasets:
   ```javascript
   options: {
       animation: false  // or { duration: 0 }
   }
   ```

## Future Enhancements

### 1. Interactive Features
- Click to drill down
- Hover tooltips with detailed info
- Date range picker integration

### 2. Additional Chart Types
- Pie/Doughnut for distribution
- Mixed charts (line + bar)
- Area charts for cumulative data

### 3. Export Functionality
- Download as PNG/SVG
- Export data as CSV
- Share chart snapshots

## Troubleshooting Reference

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| Chart not visible | No fixed-height container | Add `h-[300px]` to parent div |
| Infinite scrolling | Canvas height attribute set | Remove `height="300"` from canvas |
| No data | Backend not providing data | Check callback method |
| Wrong data | Cache issue | Clear browser cache |
| Colors don't match theme | Hardcoded colors | Use CSS variables or theme-aware colors |
| Chart flickers | Multiple DOMContentLoaded listeners | Ensure single initialization |

## References

- [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- [Chart.js Examples](https://www.chartjs.org/docs/latest/samples/)
- [Tailwind CSS Height Utilities](https://tailwindcss.com/docs/height)
- Pydantic Models: `/django_cfg/modules/django_unfold/models/charts.py`
- Chart Callbacks: `/django_cfg/modules/django_unfold/callbacks/charts.py`

---

**Last Updated:** 2025-10-03
**Chart.js Version:** 4.4.0
**Django Version:** 5.x
