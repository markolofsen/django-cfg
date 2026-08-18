"""
User API key model for service-to-service authentication.

Each user has exactly one API key that acts as a long-lived alternative
to JWT tokens. Keys are auto-generated on user creation and can be
regenerated on demand.
"""

import uuid

from django.db import models


class UserAPIKeyManager(models.Manager):
    """Manager for UserAPIKey — the one place "get this user's key" lives.

    The 1:1 invariant (one durable key per user, reused by all of that user's
    agents) means "fetch or lazily create the user's key" is the canonical
    operation. Centralizing it here keeps the signal, the view, and any other
    caller from each hand-rolling `get_or_create(user=...)`.
    """

    def for_user(self, user) -> "UserAPIKey":
        """Return the user's API key, creating it if missing. No rotation.

        Idempotent: the existing key is returned unchanged (its value is
        stable — that's the contract agents rely on). Use ``regenerate()`` to
        rotate. This also backfills a user who somehow lacks a key.
        """
        api_key, _ = self.get_or_create(user=user)
        return api_key


class UserAPIKey(models.Model):
    """Per-user API key for automated/service access.

    ## The key is stored in plain text ON PURPOSE — do not "fix" this

    Reviewed and decided 2026-08-18. A hashed credential cannot be re-read, and
    re-reading is the product requirement here: ``POST .../reveal`` returns the
    full key to the signed-in user whenever they ask, because the same durable
    value is pasted into every one of that user's agents during onboarding. A
    user who sets up a fourth machine needs the key they already gave the other
    three. Hashing and reveal-on-demand are incompatible by construction, so
    choosing reveal is choosing plaintext.

    That trade is stated here rather than left implicit because the schema
    otherwise reads like an oversight: the sibling credential in the platform
    (``apps.apikeys.ApiKey``, the ``cmdop_live_*`` cabinet key) stores
    ``sha256`` and carries ``expires_at`` / ``revoked_at`` / ``is_active``. The
    two are different products, not two attempts at one: that one is
    show-once-and-rotate, this one is copy-it-again-whenever.

    ## Revocation exists, and it is ``regenerate()``

    ``key`` is a ``OneToOneField``, so there is no key *collection* and nothing
    to revoke selectively. ``regenerate()`` assigns a fresh uuid4 and stamps
    ``reissued_at``: every previously-issued copy stops authenticating at that
    moment. **Do not add a ``revoked_at`` column beside it** — it would be a
    second way to express "this key is dead", and a duplicated condition in this
    exact subsystem has already drifted once (an expired cabinet key kept opening
    the build plane while inference answered 401 for the same row).

    ## What this design does NOT give you, so nobody assumes it does

    - **No disable-without-rotate**, and no expiry. Cutting off API access for
      one user means rotating their key or deactivating the account
      (``CustomUser`` activeness is the only per-request gate the router applies).
    - **No last-used record.** ``reissued_at`` says when it was rotated; nothing
      says when or from where it was used. Incident forensics start from the
      consuming service's logs, not from this row.
    - **A database dump is a set of live credentials.** That is the accepted cost
      of the reveal affordance; treat this table as secret material at rest.
    """

    objects = UserAPIKeyManager()

    user = models.OneToOneField(
        "django_cfg_accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="api_key",
    )
    key = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        # Plain text is the deliberate consequence of the reveal affordance, not
        # a missing hash — see the class docstring before changing this.
        help_text=(
            "API key in plain text (UUIDv4). Stored unhashed on purpose so "
            "`/reveal` can return it to its owner for agent onboarding; rotate "
            "with regenerate() to revoke."
        ),
    )
    reissued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the key was last regenerated.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "django_cfg_accounts"
        verbose_name = "User API Key"
        verbose_name_plural = "User API Keys"

    def __str__(self) -> str:
        return f"API key for {self.user.email}"

    def regenerate(self) -> "UserAPIKey":
        """Generate a new key and update reissued_at."""
        from django.utils import timezone

        self.key = uuid.uuid4()
        self.reissued_at = timezone.now()
        self.save(update_fields=["key", "reissued_at"])
        return self

    @property
    def full_key(self) -> str:
        """Return the full key as a string — the copyable inference credential.

        The semantic counterpart to ``masked_key``: callers that genuinely need
        the real value (a reveal action, an agent paste flow) use this so the
        intent reads explicitly, instead of reaching for ``str(obj.key)``. The
        default display path should still prefer ``masked_key``.
        """
        return str(self.key)

    @property
    def masked_key(self) -> str:
        """Return a masked representation of the key for display."""
        key_str = str(self.key)
        if len(key_str) < 12:
            return key_str
        return f"{key_str[:6]}{'•' * (len(key_str) - 12)}{key_str[-6:]}"
