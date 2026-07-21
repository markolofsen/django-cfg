"""Typed failures raised while preparing provider media."""


class MediaTransportError(ValueError):
    """A media source cannot be represented under the selected policy."""


class MediaSourceError(MediaTransportError):
    """The source is missing, unreadable, ambiguous, or unsafe."""


class MediaPolicyError(MediaTransportError):
    """No allowed transport can represent the source."""
