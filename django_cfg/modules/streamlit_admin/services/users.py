"""Users service for Streamlit admin.

Provides user management functionality.
"""

from models.users import UserInfo, UserProfile
from services.base import BaseService


class UsersService(BaseService):
    """User management service."""

    def get_current_user(self) -> UserProfile | None:
        """Get current authenticated user profile."""

        def fetch() -> UserProfile:
            # User model from cfg__accounts__user_profile
            data = self.api.cfg_user_profile.accounts_profile_retrieve()
            return UserProfile(
                id=str(data.id),
                email=data.email,
                username=None,  # User model doesn't have username
                display_name=data.display_username,
                avatar_url=data.avatar,
                is_staff=data.is_staff,
                is_superuser=data.is_superuser,
                date_joined=data.date_joined,
                last_login=data.last_login,
            )

        return self._safe_call("get_current_user", fetch, None)

    def update_profile(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> bool:
        """Update current user profile."""

        def fetch() -> bool:
            from api.generated.cfg.cfg__accounts__user_profile.models import (
                PatchedUserProfileUpdateRequest,
            )

            data = PatchedUserProfileUpdateRequest(
                first_name=first_name,
                last_name=last_name,
                company=None,
                phone=None,
                position=None,
            )
            self.api.cfg_user_profile.accounts_profile_partial_partial_update(data=data)
            return True

        return self._safe_call("update_profile", fetch, False)

    def get_oauth_connections(self) -> list[dict]:
        """Get OAuth connections for current user."""

        def fetch() -> list[dict]:
            # Returns list[OAuthConnection]
            connections = self.api.cfg_oauth.accounts_oauth_connections_list()
            return [
                {
                    "id": c.id,
                    "provider": c.provider.value,
                    "provider_username": c.provider_username,
                    "provider_email": c.provider_email,
                    "connected_at": c.connected_at,
                    "last_login_at": c.last_login_at,
                }
                for c in connections
            ]

        return self._safe_call("get_oauth_connections", fetch, [])

    def disconnect_oauth(self, provider: str) -> bool:
        """Disconnect OAuth provider."""

        def fetch() -> bool:
            from api.generated.cfg.cfg__accounts__oauth.models import (
                OAuthDisconnectRequestRequest,
            )
            from api.generated.cfg.enums import OAuthConnectionProvider

            request = OAuthDisconnectRequestRequest(
                provider=OAuthConnectionProvider(provider)
            )
            self.api.cfg_oauth.accounts_oauth_disconnect_create(data=request)
            return True

        return self._safe_call("disconnect_oauth", fetch, False)

    def get_totp_devices(self) -> list[dict]:
        """Get TOTP devices for current user."""

        def fetch() -> list[dict]:
            # PaginatedDeviceListResponseList has .results with DeviceListResponse
            # DeviceListResponse has .devices with list[DeviceList]
            paginated = self.api.cfg_totp_management.totp_devices_list()
            devices = []
            for response in paginated.results:
                for d in response.devices:
                    devices.append({
                        "id": d.id,
                        "name": d.name,
                        "is_primary": d.is_primary,
                        "status": d.status.value,
                        "created_at": d.created_at,
                        "confirmed_at": d.confirmed_at,
                        "last_used_at": d.last_used_at,
                    })
            return devices

        return self._safe_call("get_totp_devices", fetch, [])

    def get_backup_codes_status(self) -> dict:
        """Get backup codes status."""

        def fetch() -> dict:
            # BackupCodesStatus
            data = self.api.cfg_backup_codes.totp_backup_codes_retrieve()
            return {
                "remaining_count": data.remaining_count,
                "total_generated": data.total_generated,
                "warning": data.warning,
            }

        return self._safe_call(
            "get_backup_codes_status",
            fetch,
            {"remaining_count": 0, "total_generated": 0, "warning": None},
        )

    def regenerate_backup_codes(self, totp_code: str) -> list[str] | None:
        """Regenerate backup codes. Requires TOTP code for verification."""

        def fetch() -> list[str]:
            from api.generated.cfg.cfg__totp__backup_codes.models import (
                BackupCodesRegenerateRequest,
            )

            request = BackupCodesRegenerateRequest(code=totp_code)
            data = self.api.cfg_backup_codes.totp_backup_codes_regenerate_create(
                data=request
            )
            return data.backup_codes

        return self._safe_call("regenerate_backup_codes", fetch, None)
