"""
Progress bar elements for Django Admin.

Provides progress bar rendering with multiple colored segments.
"""

from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from . import _classes as C


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
        width: str = "",
        height: str = "",
        show_labels: bool = True,
        rounded: bool = True
    ) -> SafeString:
        """
        Render a progress bar with several coloured segments.

        Args:
            *segments: Segment dicts (from html.segment())
            width: extra CSS classes for the wrapper (``cfg-progress`` sets the size)
            height: extra CSS classes for the bar
            show_labels: Show percentage labels below the bar
            rounded: kept for the call signature; ``cfg.css`` decides the shape

        Usage:
            html.progress_bar(
                html.segment(percentage=60, variant='success', label='Available'),
                html.segment(percentage=40, variant='warning', label='Locked')
            )
        """
        bar = []
        labels = []
        for seg in segments:
            pct = float(seg['percentage'])
            fill = C.text_tone(seg.get('variant')) or C.MUTED
            if pct > 0:
                bar.append(format_html('<span class="{}" style="width: {}%"></span>', fill, f"{pct:g}"))
            label = seg.get('label', '')
            if show_labels and (pct > 0 or label):
                labels.append(format_html('<span class="{}">{}: {}%</span>', fill, label, f"{pct:.1f}"))

        labels_html = (
            format_html('<div class="{}">{}</div>', C.join(C.PROGRESS_LABELS, C.SMALL), mark_safe("".join(labels)))
            if labels else ""
        )
        return format_html(
            '<div class="{}"><div class="{}">{}</div>{}</div>',
            C.join(C.STACK, width),
            C.join(C.PROGRESS, height),
            mark_safe("".join(bar)),
            labels_html,
        )
