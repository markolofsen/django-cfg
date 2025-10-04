from django.contrib.auth.models import UserManager
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from urllib.parse import urlparse
import random
import string
import logging
import traceback
from coolname import generate_slug
import re

logger = logging.getLogger(__name__)


class UserManager(UserManager):
    """
    Custom manager for user statistics and data calculations.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError("The email must be set")

        email = self.normalize_email(email)

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
            email = email.strip().lower()

            # Generate username if not provided
            if not username:
                username = self._generate_unique_username()

            # Set default values
            defaults = {
                "username": username,
                "is_active": True,
                "date_joined": timezone.now(),
                **extra_fields,
            }

            logger.info(
                f"Attempting to get_or_create user with email: {email}, username: {username}"
            )

            # Create or get user using self.model instead of importing CustomUser
            user, created = self.model.objects.get_or_create(
                email=email, defaults=defaults
            )

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
            from django_cfg.apps.accounts.models import RegistrationSource, UserRegistrationSource

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
        """Extract full hostname from URL including subdomains."""
        try:
            hostname = urlparse(url).netloc

            # Remove www. prefix if present (but keep other subdomains)
            if hostname.startswith("www."):
                hostname = hostname[4:]

            return hostname
        except:
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
        from django_cfg.apps.support.models import Ticket
        count = Ticket.objects.get_unanswered_messages_count(user)
        return count

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
