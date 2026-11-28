/**
 * Auth Layout
 *
 * Shell-based authentication layout with three variants:
 * - `fullsplit` (default) — full-bleed 50/50: photo half carrying the brand,
 *   form on a solid panel opposite. Collapses to a plain centered form on mobile
 * - `centered` — Apple-style frameless, centered, glow background
 * - `split` — Two-column frosted card on desktop, single-column on mobile
 *
 * Supports: email/phone OTP and OAuth (Google, GitHub: the buttons come from the server). A 2FA challenge opens as a dialog
 * over the page (`TwoFactorChallengeDialog`), not as a step of this layout.
 */

'use client';

import React, { memo, useMemo } from 'react';

import { consumeSavedRedirect, useAuth, useCfgRouter } from '@djangocfg/api/auth';
import { useAnalytics } from '@djangocfg/analytics';
import { Alert, AlertDescription, AlertTitle, Preloader } from '@djangocfg/ui-core/components';
import { useAppT } from '@djangocfg/i18n';

import { Suspense } from '../../components';
import { TwoFactorChallengeDialog } from '../../snippets/TwoFactor';
import { AuthBrandPanel, AuthTopBar } from './components/shared';
import { OAuthCallback } from './components/oauth';
import { IdentifierStep, OTPStep } from './components/steps';
import { AUTH } from './constants';
import { AuthFormProvider, useAuthFormContext } from './context';
import { AuthShell } from './shells';

import './styles/auth.css';
import './styles/oauth.css';
import './styles/centered-shell.css';
import './styles/split-shell.css';
import './styles/fullsplit-shell.css';

import type { AuthLayoutProps } from './types';
import { AuthLayoutContext } from './layoutContext';
export { useAuthLayoutContext } from './layoutContext';

// ─── Layout-level context (header suppression, etc.) ─────────────────────────

/**
 * The provider itself, for harnesses that mount the steps without `AuthLayout`
 * (Storybook does, via `AuthShell`). Without it those previews always read the
 * context defaults, so a story cannot show what a real screen renders — the
 * brand appeared both on the photo and above the form, in the one story meant
 * to prove it does not.
 */
export const AuthLayoutProvider = AuthLayoutContext.Provider;

// ─── Layout ──────────────────────────────────────────────────────────────────

/**
 * Single sign-in: the visitor was sent back to a host that could not see the shared session
 * (`?sso_error=cookie`), so this host shows the form instead of sending them back again.
 */
function SsoCookieNotice() {
  const [failed, setFailed] = React.useState(false);
  React.useEffect(() => {
    setFailed(new URLSearchParams(window.location.search).get('sso_error') === 'cookie');
  }, []);
  if (!failed) return null;
  return (
    <Alert variant="destructive" className="mb-4">
      <AlertTitle>The sign-in did not carry over to the site you came from</AlertTitle>
      <AlertDescription>
        Your browser did not share the session between the two sites (cookies for the whole domain are blocked, or the
        sites are on different domains). Allow cookies for this domain and sign in again.
      </AlertDescription>
    </Alert>
  );
}

export const AuthLayout: React.FC<AuthLayoutProps> = (props) => {
  const {
    variant = 'fullsplit',
    mediaSide = 'left',
    background,
    sidebar,
    logo,
    // No default here — an unset prop falls through to the saved back-url /
    // resolved routes.defaultCallback chain at navigation time (AuthSuccess).
    redirectUrl,
    onOAuthSuccess,
    onOTPSuccess,
    onError,
    className,
    children,
  } = props;

  const hideHeader = Boolean(children);

  /*
   * The media half of `fullsplit` is a full-height photograph, and its content
   * is the `sidebar` slot. Left to the consumer it was simply empty in four of
   * the nine apps that mount this layout — a large photo carrying nothing while
   * the brand crowded the form opposite. So when the app gives us a brand and
   * no sidebar, the layout puts the brand where the room is.
   *
   * An explicit `sidebar` always wins; `centered` and `split` are untouched
   * (neither has a photo half to fill).
   */
  const resolvedSidebar = useMemo(() => {
    if (sidebar) return sidebar;
    if (variant !== 'fullsplit' || !logo) return undefined;
    return <AuthBrandPanel logo={logo} />;
  }, [sidebar, variant, logo]);

  const hasBrandPanel = !sidebar && Boolean(resolvedSidebar);

  const layoutContextValue = useMemo(
    () => ({ hideHeader, hasBrandPanel }),
    [hideHeader, hasBrandPanel],
  );

  // The way out and the locale, pinned to the top of the form column. Owned by
  // the layout so it does not depend on `logo` or `sidebar`, which are optional.
  const topBar = useMemo(() => <AuthTopBar brandPanel={hasBrandPanel} />, [hasBrandPanel]);

  // Always mounted: it renders nothing unless the URL carries `?provider=<id>`.
  const oauthCallback = useMemo(
    () => (
      <Suspense fallback={null}>
        <OAuthCallback redirectUrl={redirectUrl} onSuccess={onOAuthSuccess} onError={onError} />
      </Suspense>
    ),
    [redirectUrl, onOAuthSuccess, onError],
  );

  // Single sign-in: a follower host never shows the form. The provider is already sending the
  // visitor to the sign-in host (with `next`); this only keeps the form from flashing meanwhile.
  const { sso, isAuthenticated } = useAuth();
  if (sso?.enabled && !sso.isAuthHost && !isAuthenticated) {
    return <Preloader variant="fullscreen" text="Redirecting to sign-in..." size="lg" />;
  }

  return (
    <Suspense>
      <AuthFormProvider {...props}>
        <AuthLayoutContext.Provider value={layoutContextValue}>
          {/* Full-screen success overlay */}
          <AuthSuccessOverlay />
          <AuthFunnelTracker />
          <AuthTwoFactorChallenge onVerified={onOTPSuccess} />

          <AuthShell
            variant={variant}
            mediaSide={mediaSide}
            background={background}
            sidebar={resolvedSidebar}
            topBar={topBar}
            className={className}
          >
            <SsoCookieNotice />
            {/* Finishes a provider sign-in when the URL carries one */}
            {oauthCallback}

            <AuthHeaderSlot>{children}</AuthHeaderSlot>
            <AuthContent />
          </AuthShell>
        </AuthLayoutContext.Provider>
      </AuthFormProvider>
    </Suspense>
  );
};

/**
 * A lightweight UI breadcrumb around the server-confirmed auth events.
 *
 * `auth_login_success` remains server-authoritative. This event only answers
 * where a person stopped in the layout, and quietly becomes a no-op when an
 * app intentionally does not mount AnalyticsProvider.
 */
const AuthFunnelTracker: React.FC = memo(function AuthFunnelTracker() {
  const { step } = useAuthFormContext();
  const { event, isEnabled } = useAnalytics();
  const lastStep = React.useRef<string | null>(null);

  React.useEffect(() => {
    if (!isEnabled || lastStep.current === step) return;
    lastStep.current = step;
    event('layouts.auth.step_viewed', { step });
  }, [event, isEnabled, step]);

  return null;
});

/** Renders custom children only on the identifier step. */
const AuthHeaderSlot: React.FC<{ children?: React.ReactNode }> = memo(function AuthHeaderSlot({ children }) {
  const { step } = useAuthFormContext();
  if (!children || step !== 'identifier') return null;
  return <>{children}</>;
});

/** Wires the challenge dialog to the form: success shows the success screen, cancel restarts sign-in. */
const AuthTwoFactorChallenge: React.FC<{ onVerified?: () => void }> = memo(function AuthTwoFactorChallenge({ onVerified }) {
  const { setStep, setOtp, handleBackToIdentifier } = useAuthFormContext();

  const handleVerified = React.useCallback(() => {
    setStep('success');
    onVerified?.();
  }, [setStep, onVerified]);

  // The email code is spent by now, so going back to it would only fail.
  const handleCancel = React.useCallback(() => {
    setOtp('');
    handleBackToIdentifier();
  }, [setOtp, handleBackToIdentifier]);

  return <TwoFactorChallengeDialog onVerified={handleVerified} onCancel={handleCancel} />;
});

const AuthContent: React.FC = memo(function AuthContent() {
  const { step } = useAuthFormContext();

  switch (step) {
    case 'identifier':
      return <IdentifierStep />;
    case 'otp':
      return <OTPStep />;
    case 'success':
      // Success is rendered as full-screen overlay, return null here
      return null;
    default:
      return <IdentifierStep />;
  }
});

const AuthSuccessOverlay: React.FC = memo(function AuthSuccessOverlay() {
  const { step, redirectUrl } = useAuthFormContext();

  if (step !== 'success') {
    return null;
  }

  return <AuthSuccess redirectUrl={redirectUrl} />;
});

// AuthSuccess component - Apple-style success screen
interface AuthSuccessInlineProps {
  redirectUrl?: string;
  redirectDelay?: number;
}

const AuthSuccess: React.FC<AuthSuccessInlineProps> = memo(function AuthSuccess({
  redirectUrl,
  redirectDelay = AUTH.REDIRECT_DELAY,
}) {
  const router = useCfgRouter();
  const { routes } = useAuth();
  const t = useAppT();
  const [isVisible, setIsVisible] = React.useState(false);

  const content = React.useMemo(
    () => ({
      message: t('layouts.auth.success.message'),
      redirecting: t('layouts.auth.success.redirecting'),
    }),
    [t],
  );

  React.useEffect(() => {
    const animTimer = setTimeout(() => setIsVisible(true), AUTH.ANIMATION_START_DELAY);
    const redirectTimer = setTimeout(() => {
      // Priority: saved back-url (where the guard bounced the user from,
      // single-use) > the app's static redirectUrl prop > resolved default.
      const finalUrl = consumeSavedRedirect() || redirectUrl || routes.defaultCallback;
      router.hardPush(finalUrl);
    }, redirectDelay);

    return () => {
      clearTimeout(animTimer);
      clearTimeout(redirectTimer);
    };
  }, [redirectUrl, redirectDelay, router, routes.defaultCallback]);

  return <AuthSuccessScreen visible={isVisible} {...content} />;
});

export interface AuthSuccessScreenProps {
  /** Drives the group fade. False on the first frame, then true. */
  visible?: boolean;
  /** The outcome. */
  message: string;
  /** What the pause before the redirect is for. */
  redirecting?: string;
}

/**
 * The success screen's markup, with no timer and no router.
 *
 * Split out so it can be rendered on its own: the screen had no Storybook
 * story at all, because the only thing that could draw it also navigated away
 * 1.5s later. A screen nobody can look at is a screen nobody reviews.
 *
 * The checkmark is the confirmation, always — the brand is not a substitute
 * for it. Showing the logo INSTEAD (the previous behaviour, whenever an app
 * passed `logo`) produced a screen that never actually said the sign-in
 * worked; it read as a splash screen, which is what a sign-in has just
 * finished not being.
 *
 * `role="status"` rather than `alert`: this is the expected outcome, so it is
 * announced politely, and the whole overlay is one live region so a screen
 * reader hears the confirmation and the redirect notice together.
 */
export const AuthSuccessScreen: React.FC<AuthSuccessScreenProps> = memo(
  function AuthSuccessScreen({ visible = true, message, redirecting }) {
    return (
      <div className="auth-success-overlay" role="status" aria-live="polite">
        <div className="auth-success-content" data-visible={visible}>
          <div className="auth-success-check">
            <svg
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>

          <div className="auth-success-copy">
            <p className="auth-success-text">{message}</p>
            {/* Says what the wait is for. Without it the screen states an
                outcome and then moves on its own, which reads as a glitch. */}
            {redirecting && <p className="auth-success-hint">{redirecting}</p>}
          </div>
        </div>
      </div>
    );
  },
);
