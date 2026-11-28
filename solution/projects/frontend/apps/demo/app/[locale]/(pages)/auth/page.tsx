'use client';

import { AuthLayout } from '@djangocfg/layouts';

import { settings } from '@core/settings';
import { privateRoutes } from '@routes/private';
import { routes } from '@routes/public';

/**
 * `AuthLayout` from @djangocfg/layouts ships the full sign-in flow
 * (identifier → OTP → 2FA → success) wired to the framework auth
 * context. The demo just mounts it and points at the dashboard on
 * success.
 */
export default function AuthPage() {
  return (
    <AuthLayout
      variant="centered"
      sourceUrl={settings.app.siteUrl || '/'}
      redirectUrl={privateRoutes.dashboard}
      termsUrl={routes.legal.terms}
      privacyUrl={routes.legal.privacy}
    />
  );
}
