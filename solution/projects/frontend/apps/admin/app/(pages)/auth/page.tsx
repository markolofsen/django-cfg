'use client';

import { AuthLayout as BaseAuthLayout } from '@djangocfg/layouts';
import { routes } from '@routes/index';
import { settings } from '@core/settings';

/**
 * Authentication Page
 * Path: /auth
 */
export default function AuthPage() {
  return (
    <BaseAuthLayout
      sourceUrl={settings.app.siteUrl}
      supportUrl={routes.public.contact?.path}
      termsUrl={routes.public.terms?.path}
      privacyUrl={routes.public.privacy?.path}
      enablePhoneAuth={false}
    >
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-foreground">
          Welcome to {settings.app.name}
        </h2>
        <p className="text-sm text-muted-foreground mt-2">
          Secure authentication powered by OTP
        </p>
      </div>
    </BaseAuthLayout>
  );
}
