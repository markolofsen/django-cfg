import logging
import random
import re
import traceback
from urllib.parse import urlparse

from coolname import generate_slug
from django.contrib.auth.models import UserManager
from django.utils import timezone

logger = logging.getLogger(__name__)


class UserManager(UserManager):
    """
    Custom manager for user statistics and data calculations.
    """

    # ------------------------------------------------------------------
    # Input normalization helpers
    #
    # Use these everywhere data arrives from an external source:
    # OTP requests, OAuth callbacks, API inputs, admin forms.
    # ------------------------------------------------------------------

    @staticmethod
    def clean_email(email: str) -> str:
        """
        Normalize email for storage and lookup.

        - strip whitespace
        - lowercase the full address (local part + domain)

        Django's normalize_email only lowercases the domain; we go further
        so that 'User@EXAMPLE.COM' and 'user@example.com' are always equal.
        """
        if not email:
            return ''
        return email.strip().lower()

    @staticmethod
    def clean_phone(phone: str) -> str:
        """
        Normalize phone number for storage.

        Keeps only digits and leading '+'. Strips spaces, dashes, parentheses.
        Examples: ' +7 (999) 123-45-67 ' → '+79991234567'
        """
        if not phone:
            return ''
        cleaned = ''.join(c for c in phone.strip() if c.isdigit() or c == '+')
        # Collapse multiple '+' signs (defensive)
        if cleaned.count('+') > 1:
            cleaned = '+' + cleaned.replace('+', '')
        return cleaned

    @staticmethod
    def clean_name(name: str, max_length: int = 50) -> str:
        """
        Normalize a name field (first_name, last_name, etc.).

        - strip leading/trailing whitespace
        - collapse internal multiple spaces
        - truncate to max_length
        """
        if not name:
            return ''
        return ' '.join(name.split())[:max_length]

    @staticmethod
    def clean_language(lang_code: str) -> str:
        """
        Normalize a BCP-47 language tag to a lowercase 2-letter code.

        'EN' → 'en', 'ru-RU' → 'ru', '  ZH-HANS  ' → 'zh'
        """
        if not lang_code:
            return ''
        return lang_code.strip().lower().split('-')[0].split('_')[0][:10]

    @staticmethod
    def clean_username(username: str) -> str:
        """
        Normalize username for storage.

        - strip whitespace
        - lowercase
        """
        if not username:
            return ''
        return username.strip().lower()

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The email must be set")

        email = self.clean_email(email)

        # Generate username if not provided
        if "username" not in extra_fields:
            extra_fields["username"] = self._generate_unique_username()

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create a superuser with the given email and password
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def register_user(self, email, username=None, source_url=None, **extra_fields):
        """
        Register a new user with OTP authentication.

        Args:
            email: User's email address
            username: Optional username (will be generated if not provided)
            source_url: Optional source URL for tracking registration
            **extra_fields: Additional fields for user creation

        Returns:
            tuple: (user, created) where created is True if user was created
        """
        try:
            # Clean email
            email = self.clean_email(email)

            # Generate username if not provided
            if not username:
                username = self._generate_unique_username()

            logger.info(
                f"Attempting to register user with email: {email}, username: {username}"
            )

            # Look up only active (non-deleted) accounts.
            # Deleted accounts are archived — re-registration creates a fresh account.
            user = self.model.objects.filter(
                email=email, deleted_at__isnull=True
            ).first()

            if user is not None:
                created = False
            else:
                user = self.model.objects.create_user(
                    email=email,
                    username=username,
                    is_active=True,
                    date_joined=timezone.now(),
                    **extra_fields,
                )
                created = True

            # Handle source tracking
            if source_url:
                self._link_user_to_source(user, source_url, created)

            logger.info(
                f"User {'created' if created else 'found'} successfully: {email}"
            )
            return user, created

        except Exception as e:
            logger.error(f"Error in register_user for email {email}: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def _link_user_to_source(self, user, source_url, is_new_user=False):
        """
        Link user to a source, creating the source if it doesn't exist.

        Args:
            user: User instance
            source_url: Source URL
            is_new_user: Whether this is a new user registration
        """
        try:
            from django_cfg.apps.system.accounts.models import RegistrationSource, UserRegistrationSource

            # Get or create source
            source, source_created = RegistrationSource.objects.get_or_create(
                url=source_url,
                defaults={
                    "name": self._extract_domain_name(source_url),
                    "is_active": True,
                },
            )

            # Check if user is already linked to this source
            user_source, user_source_created = (
                UserRegistrationSource.objects.get_or_create(
                    user=user,
                    source=source,
                    defaults={"first_registration": is_new_user},
                )
            )

            if user_source_created:
                logger.info(f"Linked user {user.email} to source {source.url}")
            else:
                logger.info(f"User {user.email} already linked to source {source.url}")

        except Exception as e:
            logger.error(f"Error linking user to source: {e}")
            # Don't raise exception to avoid breaking user registration

    def _extract_domain_name(self, url):
        """Extract normalized hostname from URL including subdomains."""
        try:
            hostname = urlparse(url).netloc.lower()
            if hostname.startswith("www."):
                hostname = hostname[4:]
            return hostname
        except Exception:
            return url

    def _generate_unique_username(self):
        """
        Generate a unique username.
        """
        try:
            # Use self.model instead of importing CustomUser
            # Try different username generation strategies
            strategies = [
                self._generate_coolname_username,
                self._generate_timestamp_username,
            ]

            for strategy in strategies:
                try:
                    username = strategy()
                    if (
                        username
                        and not self.model.objects.filter(username=username).exists()
                    ):
                        return username
                except Exception as e:
                    logger.warning(
                        f"Username generation strategy {strategy.__name__} failed: {e}"
                    )
                    continue

            # Final fallback
            return f"user{timezone.now().strftime('%m%d%H%M%S')}"
        except Exception as e:
            logger.error(f"Error in _generate_unique_username: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Return a simple fallback
            return f"user{timezone.now().strftime('%m%d%H%M%S')}"

    def _generate_coolname_username(self):
        """Generate username using coolname library."""
        try:

            # Generate and clean
            raw_username = generate_slug()
            username = re.sub(r"[^a-zA-Z0-9_]", "", raw_username)

            # Shorten if too long
            if len(username) > 12:
                username = username[:8] + str(random.randint(10, 99))

            return username if len(username) <= 12 else None

        except ImportError:
            logger.warning(
                "coolname library not available, skipping coolname username generation"
            )
            return None
        except Exception as e:
            logger.warning(f"Error generating coolname username: {e}")
            return None

    def _generate_timestamp_username(self):
        """Generate username with timestamp."""
        try:
            timestamp = timezone.now().strftime("%m%d%H%M")
            return f"user{timestamp}"
        except Exception as e:
            logger.warning(f"Error generating timestamp username: {e}")
            return None

    def get_unanswered_messages_count(self, user) -> int:
        """
        Get the count of unanswered messages for the user.
        Args:
            user: User instance to get count for
        Returns:
            int: Count of unanswered messages
        """
        from django_cfg.modules.base import BaseCfgModule

        # Get config and check if support app is enabled
        config = BaseCfgModule.get_config()
        if not config or not getattr(config, 'enable_support', False):
            return 0

        try:
            from django_cfg.apps.business.support.models import Ticket
            count = Ticket.objects.get_unanswered_messages_count(user)
            return count
        except (ImportError, Exception):
            # If support app is not installed or any error occurs, return 0
            return 0

    def get_full_name(self, user) -> str:
        """
        Get user's full name.
        Args:
            user: User instance
        Returns:
            str: User's full name
        """
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        elif user.first_name:
            return user.first_name
        elif user.last_name:
            return user.last_name
        return user.email

    def get_initials(self, user) -> str:
        """
        Get user's initials for avatar fallback.
        Args:
            user: User instance
        Returns:
            str: User's initials
        """
        if user.first_name and user.last_name:
            return f"{user.first_name[0]}{user.last_name[0]}".upper()
        elif user.first_name:
            return user.first_name[0].upper()
        elif user.last_name:
            return user.last_name[0].upper()
        return user.email[0].upper()

    def get_display_username(self, user) -> str:
        """
        Get formatted username for display.
        Args:
            user: User instance
        Returns:
            str: Formatted display username
        """
        if user.username:
            # Remove special characters and format nicely
            clean_username = (
                user.username.replace("_", " ").replace("-", " ").replace(".", " ")
            )
            # Capitalize first letter of each word
            formatted = " ".join(word.capitalize() for word in clean_username.split())
            return formatted
        elif user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        elif user.first_name:
            return user.first_name
        elif user.last_name:
            return user.last_name
        return user.email.split("@")[0].capitalize()
