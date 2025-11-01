"""
Progress bar elements for Django Admin.

Provides progress bar rendering with multiple colored segments.
"""

from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe


class ProgressElements:
    """Progress bar display elements."""

    @staticmethod
    def segment(percentage: float, variant: str = 'primary', label: str = ''):
        """
        Create progress bar segment with named parameters.

        Args:
            percentage: Percentage value (0-100)
            variant: Color variant ('success', 'warning', 'danger', 'info', 'primary')
            label: Label text

        Usage:
            html.segment(percentage=60, variant='success', label='Available')

        Returns:
            dict with segment data
        """
        return {'percentage': percentage, 'variant': variant, 'label': label}

    @staticmethod
    def progress_bar(
        *segments,
        width: str = "w-full max-w-xs",
        height: str = "h-6",
        show_labels: bool = True,
        rounded: bool = True
    ) -> SafeString:
        """
        Render progress bar with multiple colored segments using Tailwind.

        Args:
            *segments: Variable number of segment dicts (from html.segment())
            width: Tailwind width classes (default: "w-full max-w-xs")
            height: Tailwind height class (default: "h-6" = 24px for visibility)
            show_labels: Show percentage labels below the bar
            rounded: Use rounded corners

        Usage:
            html.progress_bar(
                html.segment(percentage=60, variant='success', label='Available'),
                html.segment(percentage=40, variant='warning', label='Locked')
            )

        Returns:
            SafeString with progress bar HTML
        """
        # Standard Tailwind colors with dark mode (работают всегда!)
        # Progress bars need visible contrast
        variant_bg_map = {
            'success': 'bg-green-600 dark:bg-green-500',
            'warning': 'bg-yellow-600 dark:bg-yellow-500',
            'danger': 'bg-red-600 dark:bg-red-500',
            'info': 'bg-blue-600 dark:bg-blue-500',
            'primary': 'bg-primary-600 dark:bg-primary-500',
            'secondary': 'bg-gray-400 dark:bg-gray-500',
        }

        # Standard Tailwind text colors with dark mode
        variant_text_map = {
            'success': 'text-green-700 dark:text-green-300',
            'warning': 'text-yellow-700 dark:text-yellow-300',
            'danger': 'text-red-700 dark:text-red-300',
            'info': 'text-blue-700 dark:text-blue-300',
            'primary': 'text-primary-700 dark:text-primary-300',
            'secondary': 'text-gray-600 dark:text-gray-400',
        }

        # Build segments HTML
        segments_html = []
        for seg in segments:
            pct = seg['percentage']
            variant = seg['variant']
            bg_class = variant_bg_map.get(variant, 'bg-base-200 dark:bg-base-700')

            if pct > 0:
                segments_html.append(
                    f'<div class="{bg_class}" style="width: {pct}%; height: 100%;"></div>'
                )

        # Build labels HTML
        labels_html = ""
        if show_labels:
            label_parts = []
            for seg in segments:
                pct = seg['percentage']
                variant = seg['variant']
                label = seg['label']
                text_class = variant_text_map.get(variant, 'text-base-600')

                if pct > 0 or label:
                    label_parts.append(
                        f'<span class="{text_class}">{escape(label)}: {pct:.1f}%</span>'
                    )

            if label_parts:
                labels_html = (
                    f'<div class="flex justify-between mt-1 text-xs">'
                    f'{"".join(label_parts)}'
                    f'</div>'
                )

        # Rounded class
        rounded_class = 'rounded-lg' if rounded else ''

        # Combine
        html = (
            f'<div class="{width}">'
            f'<div class="bg-base-100 dark:bg-base-800 {height} {rounded_class} overflow-hidden flex">'
            f'{"".join(segments_html)}'
            f'</div>'
            f'{labels_html}'
            f'</div>'
        )

        return mark_safe(html)
