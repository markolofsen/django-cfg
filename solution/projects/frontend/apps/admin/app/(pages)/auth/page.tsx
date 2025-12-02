'use client';

import { AuthLayout } from '@djangocfg/layouts';
import { routes } from '@routes/index';
import { settings } from '@core/settings';

/**
 * Authentication Page
 * Path: /auth
 *
 * Handles both:
 * - Regular OTP auth (email form)
 * - GitHub OAuth callback (/auth?provider=github&code=XXX&state=YYY)
 *
 * OAuthCallback is automatically included when enableGithubAuth=true
 */
export default function AuthPage() {
  return (
    <AuthLayout
      sourceUrl={settings.app.siteUrl}
      supportUrl={routes.public.contact?.path}
      termsUrl={routes.public.terms?.path}
      privacyUrl={routes.public.privacy?.path}
      enablePhoneAuth={false}
      enableGithubAuth={true}
      redirectUrl={routes.private.home.path}
    >
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground">
          Welcome to {settings.app.name}
        </h2>
        <p className="text-sm text-muted-foreground mt-2">
          Secure authentication powered by OTP
        </p>
      </div>
    </AuthLayout>
  );
}
