# 📖 DRF Tailwind Theme - Examples

## 🚀 Basic Usage

### Default Configuration (Recommended)

The Tailwind theme is enabled by default. Just create your config:

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.api.drf import DRFConfig

class MyProjectConfig(DjangoConfig):
    """My API configuration with Tailwind DRF theme enabled by default."""

    project_name: str = "My Amazing API"
    project_version: str = "1.0.0"
    secret_key: str = "your-secret-key-here-min-50-chars-long-for-security"

    # DRF is automatically configured with Tailwind theme ✨
    drf: DRFConfig = DRFConfig(
        page_size=50,
    )

# Usage
config = MyProjectConfig()
settings = config.to_settings()
```

**Result**: Beautiful Tailwind DRF Browsable API with glass morphism, dark mode, and keyboard shortcuts! 🎨

---

## 🎨 Theme Customization

### Disable Tailwind Theme

If you prefer the classic Bootstrap 3 look:

```python
class MyProjectConfig(DjangoConfig):
    project_name: str = "Classic API"
    secret_key: str = "your-secret-key-here-min-50-chars-long-for-security"

    # Disable Tailwind theme
    enable_drf_tailwind: bool = False
```

### Custom Renderer

Use your own renderer while keeping other settings:

```python
from django_cfg.models.api.drf import DRFConfig

class MyProjectConfig(DjangoConfig):
    project_name: str = "Custom API"
    secret_key: str = "your-secret-key-here-min-50-chars-long-for-security"

    drf: DRFConfig = DRFConfig(
        renderer_classes=[
            'rest_framework.renderers.JSONRenderer',
            'my_app.renderers.MyCustomRenderer',
        ]
    )
```

### Multiple Renderers

Support both Tailwind and your custom renderer:

```python
class MyProjectConfig(DjangoConfig):
    project_name: str = "Multi-Renderer API"
    secret_key: str = "your-secret-key-here-min-50-chars-long-for-security"

    drf: DRFConfig = DRFConfig(
        renderer_classes=[
            'rest_framework.renderers.JSONRenderer',
            'django_cfg.modules.django_drf_theme.renderers.TailwindBrowsableAPIRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',  # Fallback
            'my_app.renderers.PDFRenderer',
        ]
    )
```

---

## 🔧 Advanced Configuration

### Full DRF Configuration with Tailwind

```python
from django_cfg import DjangoConfig
from django_cfg.models.api.drf import DRFConfig
from django_cfg.models.api.spectacular import SpectacularConfig

class ProductionAPIConfig(DjangoConfig):
    """Production-ready API with Tailwind theme."""

    # Project
    project_name: str = "Production API"
    project_version: str = "2.0.0"
    project_description: str = "High-performance REST API with modern UI"
    secret_key: str = "your-secret-key-here-min-50-chars-long-for-security"

    # Environment
    debug: bool = False

    # Security
    security_domains: list[str] = ["api.example.com", "www.example.com"]

    # DRF with Tailwind
    drf: DRFConfig = DRFConfig(
        # Authentication
        authentication_classes=[
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],

        # Permissions
        permission_classes=[
            'rest_framework.permissions.IsAuthenticated',
        ],

        # Renderers (Tailwind enabled by default)
        renderer_classes=[
            'rest_framework.renderers.JSONRenderer',
            'django_cfg.modules.django_drf_theme.renderers.TailwindBrowsableAPIRenderer',
        ],

        # Pagination
        page_size=100,

        # Throttling
        throttle_rates={
            'anon': '100/hour',
            'user': '1000/hour',
        },

        # Versioning
        default_version='v2',
        allowed_versions=['v1', 'v2'],
    )

    # API Documentation
    spectacular: SpectacularConfig = SpectacularConfig(
        title="Production API",
        version="2.0.0",
        description="Modern REST API with Tailwind Browsable API",
    )
```

---

## 🎯 ViewSet Examples

### Basic ViewSet

```python
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products.

    This will automatically use the Tailwind theme for browsable API! 🎨
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    # Tailwind theme will render this beautifully!
```

### ViewSet with Filters

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class ProductViewSet(viewsets.ModelViewSet):
    """Products with filtering - Tailwind theme shows filters in sidebar!"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    # These filters will appear in the beautiful Tailwind sidebar ✨
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'price', 'in_stock']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'price']
```

---

## 🌓 Theme Modes

Your users can switch themes using:

### Keyboard Shortcuts
- `⌘D` (Mac) or `Ctrl+D` (Windows/Linux) - Toggle theme

### Theme Dropdown
Click the theme icon in the navbar and choose:
- ☀️ Light Mode
- 🌙 Dark Mode
- 💡 Auto Mode (system preference)

### Cookie-Based
Theme preference is saved in cookies and persists across sessions!

---

## ⌨️ Power User Features

### Command Palette

Press `⌘K` or `Ctrl+K` to open:
- 📋 Copy Current URL
- 🌓 Toggle Theme
- ⌨️ Show Keyboard Shortcuts

### Keyboard Shortcuts

```
⌘K / Ctrl+K  → Open command palette
⌘D / Ctrl+D  → Toggle theme (light/dark/auto)
⌘C / Ctrl+C  → Copy current URL
?            → Show shortcuts help
Esc          → Close dialogs
```

---

## 📱 Mobile Support

The Tailwind theme is fully responsive:

```python
# Works perfectly on:
# - 📱 Mobile phones (portrait/landscape)
# - 📲 Tablets
# - 💻 Laptops
# - 🖥️ Desktops
# - 📺 Large displays
```

No extra configuration needed - it just works! ✨

---

## 🧪 Testing Your Setup

### Quick Test

1. Create a simple ViewSet:

```python
# views.py
from rest_framework import viewsets
from rest_framework.response import Response

class TestViewSet(viewsets.ViewSet):
    """Test endpoint for Tailwind theme."""

    def list(self, request):
        return Response({
            'message': 'Tailwind theme is working! 🎨',
            'features': [
                'Glass morphism design',
                'Dark/Light/Auto modes',
                'Command palette (⌘K)',
                'Keyboard shortcuts',
                'Copy buttons',
                'Syntax highlighting',
            ]
        })
```

2. Add to URLs:

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .views import TestViewSet

router = DefaultRouter()
router.register('test', TestViewSet, basename='test')

urlpatterns = router.urls
```

3. Visit `http://localhost:8000/api/test/` and enjoy the beautiful UI! 🎉

---

## 🎨 Template Override

### Override Base Template

Create your own version at:
```
your_app/templates/rest_framework/tailwind/base.html
```

### Override Specific Components

```
your_app/templates/rest_framework/tailwind/
├── base.html              # Full override
├── api.html               # Content override
└── forms/
    ├── raw_data_form.html
    └── filter_form.html
```

### Example Custom Base

```html
<!-- your_app/templates/rest_framework/tailwind/base.html -->
{% extends "rest_framework/tailwind/base.html" %}

{% block branding %}
    <img src="/static/logo.png" alt="My Logo" class="h-8">
    {{ block.super }}
{% endblock %}
```

---

## 🔗 Integration Examples

### With drf-spectacular

```python
from django_cfg import DjangoConfig
from django_cfg.models.api.drf import DRFConfig
from django_cfg.models.api.spectacular import SpectacularConfig

class MyConfig(DjangoConfig):
    project_name: str = "Documented API"
    secret_key: str = "your-secret-key-here-min-50-chars-long-for-security"

    # Tailwind theme for browsable API
    drf: DRFConfig = DRFConfig()

    # Swagger/ReDoc for API docs
    spectacular: SpectacularConfig = SpectacularConfig(
        title="My API",
        description="Beautiful API with Tailwind UI",
    )
```

Visit:
- `/api/` - Tailwind Browsable API 🎨
- `/api/schema/swagger-ui/` - Swagger UI 📊
- `/api/schema/redoc/` - ReDoc 📖

### With Custom Middleware

```python
class MyConfig(DjangoConfig):
    project_name: str = "API with Middleware"
    secret_key: str = "your-secret-key-here-min-50-chars-long-for-security"

    # Tailwind works with any middleware!
    extra_middleware: list[str] = [
        'my_app.middleware.CustomMiddleware',
    ]

    drf: DRFConfig = DRFConfig()
```

---

## 💡 Tips & Tricks

### 1. Dark Mode by Default

```python
# Set in your base template or add JavaScript:
document.cookie = 'theme=dark; path=/; max-age=31536000';
```

### 2. Custom Project Name

```python
class MyConfig(DjangoConfig):
    project_name: str = "🚀 My Awesome API"  # Emojis work!
    # ...
```

### 3. Disable Specific Features

```python
# In your custom template, remove command palette:
# Delete the command palette div in base.html
```

### 4. Add Custom Shortcuts

```javascript
// Add to base.html
handleKeyboard(event) {
    // Your existing shortcuts

    // Custom shortcut: Ctrl+H for home
    if ((event.metaKey || event.ctrlKey) && event.key === 'h') {
        window.location.href = '/';
    }
}
```

---

## 🐛 Troubleshooting

### Theme Not Appearing

**Problem**: Still seeing Bootstrap theme
**Solution**:
```python
# Check config
config = MyProjectConfig()
print(config.enable_drf_tailwind)  # Should be True
print(config.drf.renderer_classes)  # Should include TailwindBrowsableAPIRenderer
```

### Tailwind CSS Not Loading

**Problem**: No styles visible
**Solution**: Make sure `django-tailwind` is configured:
```bash
python manage.py tailwind install
python manage.py tailwind start  # Development
python manage.py tailwind build  # Production
```

### Import Error

**Problem**: `ModuleNotFoundError: No module named 'django_cfg.modules.django_drf_theme'`
**Solution**:
```python
# Verify module is in INSTALLED_APPS
config = MyProjectConfig()
apps = config.get_installed_apps()
assert 'django_cfg.modules.django_drf_theme' in apps
```

---

## 📚 Learn More

- [README.md](./README.md) - Full documentation
- [IMPLEMENTATION.md](./IMPLEMENTATION.md) - Implementation details
- [@sources/django-tailwind-drf/](../../../../../../../@sources/django-tailwind-drf/) - Design docs

---

Enjoy your beautiful new DRF Browsable API! 🎉✨
