"""
🎨 Django DRF Tailwind Theme

Modern, user-friendly Tailwind CSS theme for Django REST Framework Browsable API.

Features:
- 🌓 Dark/Light mode with smooth transitions
- 📱 Fully responsive design
- ⌨️  Keyboard shortcuts
- 🎯 Glass morphism UI
- 🚀 Alpine.js powered interactivity
- 💫 Smooth animations
- 📋 One-click copy for JSON/URLs
- 🔍 Advanced JSON tree viewer
"""

from .renderers import TailwindBrowsableAPIRenderer

__all__ = [
    "TailwindBrowsableAPIRenderer",
]

__version__ = "1.0.0"
