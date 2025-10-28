"""
Tailwind CSS Configuration

Configuration for Tailwind CSS with semantic colors for Django admin.
"""

from typing import Any, Dict


def get_tailwind_config() -> Dict[str, Any]:
    """
    Get Tailwind CSS configuration with semantic colors.
    
    Returns:
        Dict[str, Any]: Tailwind configuration dictionary
    """
    return {
        # Dark mode support
        "darkMode": "class",

        # Content paths for scanning
        "content": [
            "./django_cfg/templates/**/*.{html,py,js}",
            "./src/**/*.{html,py,js}",
            "./**/*.py",
            "./**/*.html"
        ],

        "theme": {
            "extend": {
                # Semantic colors for Unfold
                "colors": {
                    # Base colors for backgrounds and borders
                    "base": {
                        "50": "rgb(var(--color-base-50) / <alpha-value>)",
                        "100": "rgb(var(--color-base-100) / <alpha-value>)",
                        "200": "rgb(var(--color-base-200) / <alpha-value>)",
                        "300": "rgb(var(--color-base-300) / <alpha-value>)",
                        "400": "rgb(var(--color-base-400) / <alpha-value>)",
                        "500": "rgb(var(--color-base-500) / <alpha-value>)",
                        "600": "rgb(var(--color-base-600) / <alpha-value>)",
                        "700": "rgb(var(--color-base-700) / <alpha-value>)",
                        "800": "rgb(var(--color-base-800) / <alpha-value>)",
                        "900": "rgb(var(--color-base-900) / <alpha-value>)",
                        "950": "rgb(var(--color-base-950) / <alpha-value>)",
                    },

                    # Primary colors for accents
                    "primary": {
                        "50": "rgb(var(--color-primary-50) / <alpha-value>)",
                        "100": "rgb(var(--color-primary-100) / <alpha-value>)",
                        "200": "rgb(var(--color-primary-200) / <alpha-value>)",
                        "300": "rgb(var(--color-primary-300) / <alpha-value>)",
                        "400": "rgb(var(--color-primary-400) / <alpha-value>)",
                        "500": "rgb(var(--color-primary-500) / <alpha-value>)",
                        "600": "rgb(var(--color-primary-600) / <alpha-value>)",
                        "700": "rgb(var(--color-primary-700) / <alpha-value>)",
                        "800": "rgb(var(--color-primary-800) / <alpha-value>)",
                        "900": "rgb(var(--color-primary-900) / <alpha-value>)",
                        "950": "rgb(var(--color-primary-950) / <alpha-value>)",
                    },

                    # Font colors for text
                    "font": {
                        "subtle-light": "rgb(var(--color-font-subtle-light) / <alpha-value>)",
                        "subtle-dark": "rgb(var(--color-font-subtle-dark) / <alpha-value>)",
                        "default-light": "rgb(var(--color-font-default-light) / <alpha-value>)",
                        "default-dark": "rgb(var(--color-font-default-dark) / <alpha-value>)",
                        "important-light": "rgb(var(--color-font-important-light) / <alpha-value>)",
                        "important-dark": "rgb(var(--color-font-important-dark) / <alpha-value>)",
                    },

                    # Status colors
                    "success": {
                        "50": "rgb(240, 253, 244)",
                        "100": "rgb(220, 252, 231)",
                        "200": "rgb(187, 247, 208)",
                        "300": "rgb(134, 239, 172)",
                        "400": "rgb(74, 222, 128)",
                        "500": "rgb(34, 197, 94)",
                        "600": "rgb(22, 163, 74)",
                        "700": "rgb(21, 128, 61)",
                        "800": "rgb(22, 101, 52)",
                        "900": "rgb(20, 83, 45)",
                        "950": "rgb(5, 46, 22)",
                    },

                    "warning": {
                        "50": "rgb(255, 251, 235)",
                        "100": "rgb(254, 243, 199)",
                        "200": "rgb(253, 230, 138)",
                        "300": "rgb(252, 211, 77)",
                        "400": "rgb(251, 191, 36)",
                        "500": "rgb(245, 158, 11)",
                        "600": "rgb(217, 119, 6)",
                        "700": "rgb(180, 83, 9)",
                        "800": "rgb(146, 64, 14)",
                        "900": "rgb(120, 53, 15)",
                        "950": "rgb(69, 26, 3)",
                    },

                    "error": {
                        "50": "rgb(254, 242, 242)",
                        "100": "rgb(254, 226, 226)",
                        "200": "rgb(254, 202, 202)",
                        "300": "rgb(252, 165, 165)",
                        "400": "rgb(248, 113, 113)",
                        "500": "rgb(239, 68, 68)",
                        "600": "rgb(220, 38, 38)",
                        "700": "rgb(185, 28, 28)",
                        "800": "rgb(153, 27, 27)",
                        "900": "rgb(127, 29, 29)",
                        "950": "rgb(69, 10, 10)",
                    },

                    "info": {
                        "50": "rgb(239, 246, 255)",
                        "100": "rgb(219, 234, 254)",
                        "200": "rgb(191, 219, 254)",
                        "300": "rgb(147, 197, 253)",
                        "400": "rgb(96, 165, 250)",
                        "500": "rgb(59, 130, 246)",
                        "600": "rgb(37, 99, 235)",
                        "700": "rgb(29, 78, 216)",
                        "800": "rgb(30, 64, 175)",
                        "900": "rgb(30, 58, 138)",
                        "950": "rgb(23, 37, 84)",
                    }
                },

                # Additional utilities
                "borderRadius": {
                    "default": "0.5rem",
                },

                "boxShadow": {
                    "xs": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
                }
            }
        },

        "plugins": []
    }


def get_css_variables() -> str:
    """
    Get CSS variables for semantic colors matching Next.js UI package.

    This function provides base color definitions for the Unfold admin interface.
    Color variables are defined in OKLCH format for proper color-mix() support.

    Returns:
        str: CSS variables as string
    """
    return """
/* ============================================== */
/* CSS Variables - Base Color Definitions        */
/* ============================================== */

/* Tailwind Dark Mode Class Support */
html.dark {
  color-scheme: dark;
}

html:not(.dark) {
  color-scheme: light;
}

"""


def get_modal_fix_css() -> str:
    """
    Get CSS fixes for modal scroll issues and other UI improvements.
    
    Returns:
        str: CSS fixes as string
    """
    return """
/* Modal scroll fixes and UI improvements */

/* Ensure proper modal scroll behavior */
.modal-scrollable {
    max-height: calc(80vh - 8rem);
    overflow-y: auto;
}

/* Command modal specific fixes */
#commandModal .overflow-y-auto {
    scrollbar-width: thin;
    scrollbar-color: rgb(156, 163, 175) transparent;
}

#commandModal .overflow-y-auto::-webkit-scrollbar {
    width: 8px;
}

#commandModal .overflow-y-auto::-webkit-scrollbar-track {
    background: transparent;
}

#commandModal .overflow-y-auto::-webkit-scrollbar-thumb {
    background-color: rgb(156, 163, 175);
    border-radius: 4px;
}

#commandModal .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background-color: rgb(107, 114, 128);
}

/* Dark theme scrollbar */
.dark #commandModal .overflow-y-auto {
    scrollbar-color: rgb(75, 85, 99) transparent;
}

.dark #commandModal .overflow-y-auto::-webkit-scrollbar-thumb {
    background-color: rgb(75, 85, 99);
}

.dark #commandModal .overflow-y-auto::-webkit-scrollbar-thumb:hover {
    background-color: rgb(107, 114, 128);
}

/* Improved focus states */
.focus-visible\\:outline-primary-600:focus-visible {
    outline: 2px solid rgb(37, 99, 235);
    outline-offset: 2px;
}

/* Better button transitions */
.transition-colors {
    transition-property: color, background-color, border-color;
    transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
    transition-duration: 150ms;
}

"""


def get_unfold_colors() -> Dict[str, Any]:
    """
    Get color configuration for Unfold settings matching Next.js UI package.

    Colors synchronized with:
    - packages/ui/src/styles/theme/light.css
    - packages/ui/src/styles/theme/dark.css

    IMPORTANT: Returns OKLCH format for Unfold's color-mix() CSS compatibility.

    Returns:
        Dict[str, Any]: Color configuration for Unfold in OKLCH format
    """
    # Import from UnfoldConfig to keep colors in sync
    from .models.config import UnfoldConfig

    # Create temporary config to get color scheme
    temp_config = UnfoldConfig(site_title="temp")
    return temp_config.get_color_scheme()
