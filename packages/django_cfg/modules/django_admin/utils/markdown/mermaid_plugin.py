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

    IMPORTANT - Mermaid rendering gotchas:
    =====================================
    1. Mermaid CANNOT calculate SVG dimensions when parent element is hidden (display: none)
       - Results in viewBox: "-8 -8 16 16" (empty 16x16 diagram)
       - Solution: Only call mermaid.run() AFTER container is visible
       - See: https://github.com/mermaid-js/mermaid/issues/1846

    2. For modals/dialogs:
       - Set startOnLoad: false
       - Call window.renderMermaid() when modal opens (via $watch in Alpine.js)
       - Don't use MutationObserver for auto-rendering (fires while hidden)

    3. Dark mode:
       - Use theme: 'base' with explicit themeVariables
       - Set visible text colors (nodeTextColor, textColor) for dark backgrounds

    Args:
        theme: Mermaid theme ('default', 'dark', 'forest', 'neutral')

    Returns:
        HTML script tag with Mermaid.js and initialization
    """
    return """
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';

    // Make mermaid available globally for Alpine.js components
    window.mermaid = mermaid;

    // Auto-detect dark mode
    const isDarkMode = document.documentElement.classList.contains('dark') ||
                       window.matchMedia('(prefers-color-scheme: dark)').matches;

    // =========================================================================
    // IMPORTANT: startOnLoad must be FALSE for modal/dynamic content!
    // Mermaid cannot calculate SVG size when element is hidden (display: none).
    // Call window.renderMermaid() manually when container becomes visible.
    // =========================================================================
    mermaid.initialize({
        startOnLoad: false,
        theme: 'base',
        securityLevel: 'loose',
        fontFamily: 'ui-sans-serif, system-ui, sans-serif',
        themeVariables: isDarkMode ? {
            // Dark mode - explicit colors for visibility
            primaryColor: '#3b82f6',
            primaryTextColor: '#ffffff',
            primaryBorderColor: '#60a5fa',
            lineColor: '#94a3b8',
            secondaryColor: '#10b981',
            tertiaryColor: '#334155',
            background: '#1e293b',
            mainBkg: '#334155',
            textColor: '#f1f5f9',
            nodeTextColor: '#f1f5f9',
            clusterBkg: '#1e293b',
            clusterBorder: '#475569',
        } : {
            // Light mode
            primaryColor: '#3b82f6',
            primaryTextColor: '#1e293b',
            primaryBorderColor: '#3b82f6',
            lineColor: '#64748b',
            secondaryColor: '#10b981',
            tertiaryColor: '#f1f5f9',
            background: '#ffffff',
            mainBkg: '#f8fafc',
            textColor: '#1e293b',
        }
    });

    /**
     * Render mermaid diagrams that haven't been processed yet.
     *
     * IMPORTANT: Only call this when the container element is VISIBLE!
     * Mermaid calculates SVG dimensions based on rendered text size.
     * If container is hidden (display: none), dimensions will be wrong.
     *
     * Usage in Alpine.js:
     *   this.$watch('open', (isOpen) => {
     *       if (isOpen) {
     *           this.$nextTick(() => window.renderMermaid());
     *       }
     *   });
     */
    async function renderMermaid() {
        const elements = document.querySelectorAll('.mermaid:not([data-processed="true"])');
        if (elements.length > 0) {
            console.log('Mermaid: rendering', elements.length, 'diagrams');
            try {
                await mermaid.run({ nodes: elements });
                console.log('Mermaid: render complete');
            } catch (err) {
                console.error('Mermaid render error:', err);
                elements.forEach(el => {
                    el.innerHTML = '<div style="color: #ef4444; padding: 1rem; border: 1px solid #ef4444; border-radius: 0.5rem;">Mermaid Error: ' + err.message + '</div>';
                });
            }
        }
    }

    // Expose for Alpine.js components
    // DO NOT render automatically - let the caller decide when container is visible
    window.renderMermaid = renderMermaid;

    console.log('Mermaid ready - call window.renderMermaid() when content is visible');
</script>
"""


def get_mermaid_resources() -> str:
    """
    Get complete Mermaid resources (styles + script).

    Returns:
        HTML string with styles and script for Mermaid support
    """
    return get_mermaid_styles() + get_mermaid_script()
