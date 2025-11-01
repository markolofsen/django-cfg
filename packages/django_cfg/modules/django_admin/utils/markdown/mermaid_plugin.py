"""
Mermaid diagram plugin for Mistune markdown parser.

Renders ```mermaid code blocks as interactive diagrams using Mermaid.js.
"""

import re
from typing import Any, Dict


def mermaid_plugin(md):
    """
    Mistune plugin to render Mermaid diagrams.

    Detects code fences with 'mermaid' language and renders them as
    Mermaid diagram containers that will be processed by Mermaid.js.

    Usage:
        ```mermaid
        graph TD
            A[Start] --> B{Decision}
            B -->|Yes| C[OK]
            B -->|No| D[Cancel]
        ```

    Args:
        md: Mistune markdown instance
    """

    def render_mermaid(text: str, **attrs: Any) -> str:
        """
        Render Mermaid diagram HTML.

        Args:
            text: Mermaid diagram code
            **attrs: Additional attributes

        Returns:
            HTML with Mermaid container
        """
        # Generate unique ID for this diagram
        import hashlib
        diagram_id = f"mermaid-{hashlib.md5(text.encode()).hexdigest()[:8]}"

        # Escape HTML special characters but preserve Mermaid syntax
        escaped_text = text.strip()

        # Return HTML container with Mermaid code
        return f'''<div class="mermaid-container">
    <div class="mermaid-wrapper">
        <pre class="mermaid" id="{diagram_id}">
{escaped_text}
        </pre>
    </div>
</div>'''

    # Override code block renderer for mermaid language
    original_code = md.renderer.block_code

    def patched_code(code: str, info: str = None, **attrs: Any) -> str:
        """
        Patched code block renderer that checks for mermaid language.

        Args:
            code: Code content
            info: Language info
            **attrs: Additional attributes

        Returns:
            Rendered code block (either Mermaid or normal code)
        """
        if info and info.strip().lower() == 'mermaid':
            return render_mermaid(code, **attrs)
        return original_code(code, info, **attrs)

    md.renderer.block_code = patched_code

    return md


def get_mermaid_styles() -> str:
    """
    Get CSS styles for Mermaid diagrams with Unfold semantic colors.

    Returns:
        CSS string for Mermaid container styling
    """
    return """
<style>
    /* Mermaid container styles with Unfold semantic colors */
    .mermaid-container {
        margin: 1.5rem 0;
        padding: 0;
    }

    .mermaid-wrapper {
        border: 1px solid rgb(var(--color-base-200));
        border-radius: 0.5rem;
        padding: 1.5rem;
        background: rgb(var(--color-base-50));
        overflow-x: auto;
    }

    /* Dark mode styles with semantic colors */
    .dark .mermaid-wrapper {
        border-color: rgb(var(--color-base-700));
        background: rgb(var(--color-base-900));
    }

    /* Mermaid diagram */
    .mermaid {
        display: flex;
        justify-content: center;
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        font-family: inherit !important;
    }

    /* Ensure diagrams are centered */
    .mermaid svg {
        max-width: 100%;
        height: auto;
    }

    /* Loading state with semantic colors */
    .mermaid[data-processed="false"] {
        color: rgb(var(--color-base-400));
        text-align: center;
        padding: 2rem;
    }

    .dark .mermaid[data-processed="false"] {
        color: rgb(var(--color-base-500));
    }

    /* Error state with semantic colors */
    .mermaid.error {
        color: rgb(239, 68, 68);
        border: 1px solid rgb(252, 165, 165);
        background: rgb(254, 242, 242);
        padding: 1rem;
        border-radius: 0.375rem;
    }

    .dark .mermaid.error {
        color: rgb(248, 113, 113);
        border-color: rgb(153, 27, 27);
        background: rgb(127, 29, 29);
    }
</style>
"""


def get_mermaid_script(theme: str = "default") -> str:
    """
    Get Mermaid.js initialization script with Unfold semantic colors.

    Args:
        theme: Mermaid theme ('default', 'dark', 'forest', 'neutral')

    Returns:
        HTML script tag with Mermaid.js and initialization
    """
    return f"""
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

    // Helper to get CSS variable value
    function getCSSVar(name) {{
        const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
        // Convert "R, G, B" format to "#RRGGBB"
        if (value.includes(',')) {{
            const [r, g, b] = value.split(',').map(x => parseInt(x.trim()));
            return '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');
        }}
        return value;
    }}

    // Auto-detect dark mode
    const isDarkMode = document.documentElement.classList.contains('dark') ||
                       window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Get Unfold semantic colors
    function getThemeColors() {{
        if (isDarkMode) {{
            return {{
                primaryColor: '#3b82f6',
                primaryTextColor: getCSSVar('--color-base-100'),
                primaryBorderColor: getCSSVar('--color-base-700'),
                lineColor: getCSSVar('--color-base-600'),
                secondaryColor: getCSSVar('--color-base-800'),
                tertiaryColor: getCSSVar('--color-base-700'),
                background: getCSSVar('--color-base-900'),
                mainBkg: getCSSVar('--color-base-800'),
                secondBkg: getCSSVar('--color-base-700'),
                border1: getCSSVar('--color-base-700'),
                border2: getCSSVar('--color-base-600'),
                note: getCSSVar('--color-base-800'),
                noteText: getCSSVar('--color-base-200'),
                noteBorder: getCSSVar('--color-base-600'),
                text: getCSSVar('--color-base-200'),
                critical: '#ef4444',
                done: '#10b981',
                active: '#3b82f6',
            }};
        }} else {{
            return {{
                primaryColor: '#2563eb',
                primaryTextColor: getCSSVar('--color-base-900'),
                primaryBorderColor: getCSSVar('--color-base-300'),
                lineColor: getCSSVar('--color-base-400'),
                secondaryColor: getCSSVar('--color-base-100'),
                tertiaryColor: '#ffffff',
                background: '#ffffff',
                mainBkg: getCSSVar('--color-base-50'),
                secondBkg: '#ffffff',
                border1: getCSSVar('--color-base-300'),
                border2: getCSSVar('--color-base-200'),
                note: '#fef3c7',
                noteText: getCSSVar('--color-base-900'),
                noteBorder: '#fbbf24',
                text: getCSSVar('--color-base-900'),
                critical: '#dc2626',
                done: '#059669',
                active: '#2563eb',
            }};
        }}
    }}

    // Initialize Mermaid with Unfold semantic colors
    mermaid.initialize({{
        startOnLoad: true,
        theme: 'base',
        securityLevel: 'loose',
        fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        themeVariables: getThemeColors()
    }});

    // Listen for dark mode changes and re-render
    const observer = new MutationObserver((mutations) => {{
        mutations.forEach((mutation) => {{
            if (mutation.attributeName === 'class') {{
                // Re-initialize with new theme colors
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'base',
                    securityLevel: 'loose',
                    fontFamily: 'ui-sans-serif, system-ui, sans-serif',
                    themeVariables: getThemeColors()
                }});
                // Re-render all diagrams
                mermaid.run({{
                    querySelector: '.mermaid',
                }});
            }}
        }});
    }});

    observer.observe(document.documentElement, {{
        attributes: true,
        attributeFilter: ['class'],
    }});

    // Error handling
    window.addEventListener('error', (event) => {{
        if (event.message && event.message.includes('mermaid')) {{
            console.error('Mermaid error:', event);
            const mermaidElements = document.querySelectorAll('.mermaid[data-processed="false"]');
            mermaidElements.forEach(el => {{
                el.classList.add('error');
                el.textContent = 'Error rendering diagram. Check console for details.';
            }});
        }}
    }});
</script>
"""


def get_mermaid_resources() -> str:
    """
    Get complete Mermaid resources (styles + script).

    Returns:
        HTML string with styles and script for Mermaid support
    """
    return get_mermaid_styles() + get_mermaid_script()
