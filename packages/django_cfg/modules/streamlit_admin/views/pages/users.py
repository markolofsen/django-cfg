"""Users page view for Streamlit admin."""

import streamlit as st

from services.users import UsersService


def render_users_page(service: UsersService) -> None:
    """Render user management page.

    Args:
        service: UsersService instance for data fetching.
    """
    st.title("User Profile")

    profile = service.get_current_user()

    if not profile:
        st.error("Failed to load user profile")
        return

    # Profile section
    col1, col2 = st.columns([1, 2])

    with col1:
        if profile.avatar_url:
            st.image(profile.avatar_url, width=150)
        else:
            st.markdown(
                """
                <div style="width: 150px; height: 150px;
                            background: #333; border-radius: 50%;
                            display: flex; align-items: center;
                            justify-content: center; font-size: 48px;">
                    👤
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        st.subheader(profile.display_name or profile.username or profile.email)
        st.caption(profile.email)

        if profile.is_superuser:
            st.badge("Superuser", icon="⭐")
        elif profile.is_staff:
            st.badge("Staff", icon="🛡️")

        if profile.date_joined:
            st.caption(f"Joined: {profile.date_joined.strftime('%Y-%m-%d')}")
        if profile.last_login:
            st.caption(f"Last login: {profile.last_login.strftime('%Y-%m-%d %H:%M')}")

    st.divider()

    # Tabs
    tabs = st.tabs(["Edit Profile", "OAuth Connections", "2FA Settings"])

    with tabs[0]:
        _render_edit_profile(service, profile)

    with tabs[1]:
        _render_oauth_connections(service)

    with tabs[2]:
        _render_2fa_settings(service)


def _render_edit_profile(service: UsersService, profile) -> None:
    """Render edit profile form."""
    st.subheader("Edit Profile")

    display_name = st.text_input(
        "Display Name",
        value=profile.display_name or "",
        placeholder="Your display name",
    )

    if st.button("Save Changes", type="primary"):
        if service.update_profile(display_name=display_name if display_name else None):
            st.success("Profile updated")
            st.rerun()
        else:
            st.error("Failed to update profile")


def _render_oauth_connections(service: UsersService) -> None:
    """Render OAuth connections section."""
    st.subheader("OAuth Connections")

    connections = service.get_oauth_connections()

    if connections:
        for conn in connections:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{conn['provider'].title()}**")
            with col2:
                st.caption(conn["uid"])
            with col3:
                if st.button("Disconnect", key=f"oauth_{conn['provider']}"):
                    if service.disconnect_oauth(conn["provider"]):
                        st.success(f"Disconnected {conn['provider']}")
                        st.rerun()
                    else:
                        st.error("Failed to disconnect")
    else:
        st.info("No OAuth connections")


def _render_2fa_settings(service: UsersService) -> None:
    """Render 2FA settings section."""
    st.subheader("Two-Factor Authentication")

    # TOTP Devices
    devices = service.get_totp_devices()
    if devices:
        st.write("**Authenticator Apps**")
        for device in devices:
            col1, col2 = st.columns([3, 1])
            with col1:
                status = "✅ Confirmed" if device["confirmed"] else "⏳ Pending"
                st.write(f"{device['name']} - {status}")
            with col2:
                st.caption(device.get("created_at", ""))
    else:
        st.info("No authenticator apps configured")

    st.divider()

    # Backup Codes
    st.write("**Backup Codes**")
    backup_status = service.get_backup_codes_status()

    if backup_status["remaining_count"] > 0:
        st.write(f"Remaining codes: {backup_status['remaining_count']}")
        if st.button("Regenerate Codes", type="secondary"):
            codes = service.regenerate_backup_codes()
            if codes:
                st.warning("Save these codes securely. They won't be shown again!")
                st.code("\n".join(codes))
            else:
                st.error("Failed to regenerate codes")
    else:
        st.info("No backup codes generated")
        if st.button("Generate Backup Codes", type="primary"):
            codes = service.regenerate_backup_codes()
            if codes:
                st.warning("Save these codes securely. They won't be shown again!")
                st.code("\n".join(codes))
            else:
                st.error("Failed to generate codes")
