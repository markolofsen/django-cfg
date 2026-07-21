"""Typed failures for temporary public-media transport."""


class TemporaryPublicationError(RuntimeError):
    """Base error; messages never contain bearer URLs or revoke tokens."""


class TemporaryPublicationTransportError(TemporaryPublicationError):
    """Network or service-side failure."""


class TemporaryPublicationRateLimitError(TemporaryPublicationTransportError):
    """The anonymous gateway rate limit was exceeded."""


class TemporaryPublicationTooLargeError(TemporaryPublicationError):
    """The input exceeds the concrete gateway limit."""


class TemporaryPublicationInvalidResponseError(TemporaryPublicationError):
    """The gateway response violated the publication contract."""
