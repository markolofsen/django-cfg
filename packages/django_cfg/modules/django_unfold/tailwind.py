"""
Tailwind CSS Configuration

Configuration for Tailwind CSS with semantic colors for Django admin.
"""

import json
from pathlib import Path
from typing import Dict, Any


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
    Get CSS variables for semantic colors.
    
    Returns:
        str: CSS variables as string
    """
    return """
/* CSS variables for semantic colors */
:root {
  /* Base colors */
  --color-base-50: 249, 250, 251;
  --color-base-100: 243, 244, 246;
  --color-base-200: 229, 231, 235;
  --color-base-300: 209, 213, 219;
  --color-base-400: 156, 163, 175;
  --color-base-500: 107, 114, 128;
  --color-base-600: 75, 85, 99;
  --color-base-700: 55, 65, 81;
  --color-base-800: 31, 41, 55;
  --color-base-900: 17, 24, 39;
  --color-base-950: 3, 7, 18;

  /* Primary colors */
  --color-primary-50: 239, 246, 255;
  --color-primary-100: 219, 234, 254;
  --color-primary-200: 191, 219, 254;
  --color-primary-300: 147, 197, 253;
  --color-primary-400: 96, 165, 250;
  --color-primary-500: 59, 130, 246;
  --color-primary-600: 37, 99, 235;
  --color-primary-700: 29, 78, 216;
  --color-primary-800: 30, 64, 175;
  --color-primary-900: 30, 58, 138;
  --color-primary-950: 23, 37, 84;

  /* Font colors for light theme */
  --color-font-subtle-light: var(--color-base-500);
  --color-font-default-light: var(--color-base-600);
  --color-font-important-light: var(--color-base-900);
}

/* Dark theme */
.dark {
  /* Font colors for dark theme */
  --color-font-subtle-dark: var(--color-base-400);
  --color-font-default-dark: var(--color-base-300);
  --color-font-important-dark: var(--color-base-100);
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
    Get color configuration for Unfold settings.
    
    Returns:
        Dict[str, Any]: Color configuration for Unfold
    """
    return {
        "primary": {
            "50": "239, 246, 255",
            "100": "219, 234, 254",
            "200": "191, 219, 254",
            "300": "147, 197, 253",
            "400": "96, 165, 250",
            "500": "59, 130, 246",
            "600": "37, 99, 235",
            "700": "29, 78, 216",
            "800": "30, 64, 175",
            "900": "30, 58, 138",
            "950": "23, 37, 84",
        },
        "base": {
            "50": "249, 250, 251",
            "100": "243, 244, 246",
            "200": "229, 231, 235",
            "300": "209, 213, 219",
            "400": "156, 163, 175",
            "500": "107, 114, 128",
            "600": "75, 85, 99",
            "700": "55, 65, 81",
            "800": "31, 41, 55",
            "900": "17, 24, 39",
            "950": "3, 7, 18",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        }
    }
