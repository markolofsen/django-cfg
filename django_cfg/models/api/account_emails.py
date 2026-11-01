"""Opt-in security emails of the accounts app."""

from pydantic import BaseModel, ConfigDict, Field


class AccountEmailsConfig(BaseModel):
    """Security emails that are off unless a project asks for them.

    A user who just signed in or filled in their own name needs no letter about
    it. Both switches gate only the email to the user; the Telegram and admin
    notifications are unaffected.

    Example:
        ```python
        from django_cfg import AccountEmailsConfig, DjangoConfig

        class MyConfig(DjangoConfig):
            account_emails: AccountEmailsConfig = AccountEmailsConfig(
                profile_change_email=True,
                new_sign_in_email=True,
            )
        ```
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    profile_change_email: bool = Field(
        default=False,
        description=(
            "Email the previous address when the account's email address is changed "
            "(never for a name or username, a first fill, or a change made by sign-in)."
        ),
    )
    new_sign_in_email: bool = Field(
        default=False,
        description=(
            "Email 'New sign-in to your account' when a user signs in from a device not seen in the "
            "last 24 hours, outside the first 24 hours after registration."
        ),
    )


__all__ = ["AccountEmailsConfig"]
