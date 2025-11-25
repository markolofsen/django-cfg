"""Video display utility with smart URL parsing."""

import re
from typing import Any, Dict, Optional

from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class VideoDisplay:
    """
    Display video thumbnails with platform detection.

    Supports:
    - YouTube (youtube.com, youtu.be)
    - Vimeo
    - Direct video URLs (.mp4, .webm, etc.)
    """

    # Platform patterns
    YOUTUBE_PATTERNS = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    VIMEO_PATTERN = r'vimeo\.com/(\d+)'

    @classmethod
    def parse_url(cls, url: str) -> Dict[str, Any]:
        """
        Parse video URL and extract platform info.

        Returns:
            Dict with keys: platform, video_id, thumbnail_url, embed_url
        """
        if not url:
            return {'platform': None}

        url = str(url)

        # YouTube
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                return {
                    'platform': 'youtube',
                    'video_id': video_id,
                    'thumbnail_url': f'https://img.youtube.com/vi/{video_id}/mqdefault.jpg',
                    'embed_url': f'https://www.youtube.com/embed/{video_id}',
                    'watch_url': f'https://www.youtube.com/watch?v={video_id}',
                    'icon': 'smart_display',
                }

        # Vimeo
        match = re.search(cls.VIMEO_PATTERN, url)
        if match:
            video_id = match.group(1)
            return {
                'platform': 'vimeo',
                'video_id': video_id,
                'thumbnail_url': None,  # Vimeo requires API for thumbnails
                'embed_url': f'https://player.vimeo.com/video/{video_id}',
                'watch_url': f'https://vimeo.com/{video_id}',
                'icon': 'play_circle',
            }

        # Direct video URL
        if any(url.lower().endswith(ext) for ext in ['.mp4', '.webm', '.ogg', '.mov']):
            return {
                'platform': 'direct',
                'video_id': None,
                'thumbnail_url': None,
                'embed_url': url,
                'watch_url': url,
                'icon': 'videocam',
            }

        # Unknown - treat as direct link
        return {
            'platform': 'unknown',
            'video_id': None,
            'thumbnail_url': None,
            'embed_url': None,
            'watch_url': url,
            'icon': 'link',
        }

    @classmethod
    def render(cls, url: str, config: Optional[Dict[str, Any]] = None) -> str:
        """
        Render video thumbnail/player.

        Args:
            url: Video URL
            config: Display configuration

        Returns:
            HTML string
        """
        config = config or {}
        video_info = cls.parse_url(url)

        if not video_info['platform']:
            fallback = config.get('fallback_text', '—')
            return fallback

        context = {
            'video_info': video_info,
            'url': url,
            'thumbnail_width': config.get('thumbnail_width', '200px'),
            'thumbnail_height': config.get('thumbnail_height', '112px'),
            'border_radius': config.get('border_radius', '8px'),
            'show_inline': config.get('show_inline', False),
            'show_platform': config.get('show_platform', True),
        }

        return render_to_string('django_admin/widgets/video_display.html', context)

    @classmethod
    def from_field(
        cls,
        obj: Any,
        field: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render video from model field.

        Args:
            obj: Model instance
            field: Field name
            config: Configuration options

        Returns:
            HTML string
        """
        config = config or {}

        # Get URL value
        value = getattr(obj, field, None)
        if callable(value):
            url = value()
        else:
            url = value

        if not url:
            return config.get('empty_value', '—')

        return cls.render(str(url), config)
