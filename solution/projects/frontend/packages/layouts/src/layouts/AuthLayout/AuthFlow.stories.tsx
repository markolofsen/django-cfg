import type { Meta, StoryObj } from '@storybook/react-vite';
import { expect, userEvent, waitFor, within } from 'storybook/test';

import { Fragment, useLayoutEffect, useMemo, useState, type ChangeEvent, type ReactNode } from 'react';
import { SearchParamsContext } from 'next/dist/shared/lib/hooks-client-context.shared-runtime';
import type { ReadonlyURLSearchParams } from 'next/navigation';

import { CFG_KEYS, cfgStorage } from '@djangocfg/api/storage';
import { I18nProvider } from '@djangocfg/i18n';
import { ar, de, en, ru } from '@djangocfg/i18n/locales';
import {
  AuthBrandPanel,
  AuthLayout,
  AuthLayoutProvider,
  AuthShell,
  AuthSuccessScreen,
  AuthTopBar,
  getOAuthApiMock,
  IdentifierStep,
  MockAuthFormProvider,
  MockAuthProvider,
  OAUTH_SERVER_ERROR_CODES,
  oauthApiMock,
  OTPStep,
  seedOAuthBrowser,
  type AuthStep,
  type MockAuthFormProviderProps,
  type OAuthApiScript,
  type OAuthServerErrorCode,
} from '@djangocfg/layouts/testing';

// ─── Helpers ────────────────────────────────────────────────────────────────

// Background photo for the split variant so the desktop frosted-glass card has
// something to blur over. Unsplash — stable URL, no key needed.
const BG_IMAGE =
  'https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=2000&q=80';

// Sidebar for the floating `split` card (sits on a tinted --muted panel, so it
// uses theme text colors). `split` has no photo half, so the brand stays above
// the form here and the sidebar carries only the quote.
function Sidebar() {
  return (
    <div className="flex h-full flex-col justify-end">
      <blockquote className="space-y-3">
        <p className="text-lg leading-snug text-foreground">
          “Set up auth, profile and billing in an afternoon — not a sprint.”
        </p>
        <footer className="text-sm text-muted-foreground">
          — A djangocfg developer
        </footer>
      </blockquote>
    </div>
  );
}

// Sidebar for the `fullsplit` media half — laid over a photo, so text is white.
function MediaSidebar() {
  return (
    <>
      <span aria-hidden="true" />
      <blockquote className="space-y-3">
        <p className="text-2xl font-medium leading-snug">
          “Set up auth, profile and billing in an afternoon — not a sprint.”
        </p>
        <footer className="text-sm text-white/70">— A djangocfg developer</footer>
      </blockquote>
    </>
  );
}

// Renders the current step inside the shell, the same way AuthLayout
// would — but reading state from MockAuthFormProvider so we can pin
// each story to a specific step + sub-state without API wiring.
function FlowFrame({
  variant = 'centered',
  mediaSide = 'left',
  step = 'identifier',
  appSidebar = true,
  locale,
  ...mockProps
}: {
  /** Render the step in a longer-label locale (the buttons must stay one line). */
  locale?: 'de' | 'ru' | 'ar';
  variant?: 'centered' | 'split' | 'fullsplit';
  mediaSide?: 'left' | 'right';
  /**
   * Whether the APP supplies a `sidebar`. Set it false to preview what
   * `AuthLayout` renders on its own — the configuration four production apps
   * actually ship. This harness mounts `AuthShell` directly, so it has to
   * stand in for the layout's default here (`AuthBrandPanel`); with the flag
   * hardcoded true, the empty-media-half defect had no story and went unseen.
   */
  appSidebar?: boolean;
} & Omit<MockAuthFormProviderProps, 'children' | 'step'> & { step?: AuthStep }) {
  const isSplit = variant === 'split';
  const isFullSplit = variant === 'fullsplit';
  const hasMedia = isSplit || isFullSplit;
  const logo = mockProps.logo;

  let sidebar: ReactNode;
  let hasBrandPanel = false;
  if (isFullSplit) {
    if (appSidebar) {
      sidebar = <MediaSidebar />;
    } else if (logo) {
      sidebar = <AuthBrandPanel logo={logo} />;
      hasBrandPanel = true;
    }
  } else if (isSplit) {
    sidebar = appSidebar ? <Sidebar /> : undefined;
  }

  const frame = (
    <div className="h-[760px]" dir={locale === 'ar' ? 'rtl' : undefined}>
      <MockAuthFormProvider step={step} {...mockProps}>
        {/* The same layout-level facts AuthLayout states in production, so the
            preview and the real screen agree about where the brand is. */}
        <AuthLayoutProvider value={{ hideHeader: false, hasBrandPanel }}>
          <AuthShell
            variant={variant}
            mediaSide={mediaSide}
            background={hasMedia ? { imageUrl: BG_IMAGE } : undefined}
            sidebar={sidebar}
            topBar={<AuthTopBar brandPanel={hasBrandPanel} />}
          >
            {step === 'identifier' && <IdentifierStep />}
            {step === 'otp' && <OTPStep />}
          </AuthShell>
        </AuthLayoutProvider>
      </MockAuthFormProvider>
    </div>
  );

  return locale ? (
    <I18nProvider locale={locale} translations={LOCALES[locale]}>
      {frame}
    </I18nProvider>
  ) : (
    frame
  );
}

const LOCALES = { de, ru, ar } as const;

// ─── Meta ───────────────────────────────────────────────────────────────────

const meta = {
  title: 'Packages/Layouts/AuthFlow',
  parameters: {
    layout: 'fullscreen',
    docs: {
      description: {
        component:
          'Full `AuthLayout` driven by `MockAuthFormProvider` — pick a step from the Controls panel to preview every sub-state without calling the real auth API.',
      },
    },
  },
  argTypes: {
    variant: {
      control: 'inline-radio',
      options: ['centered', 'split', 'fullsplit'],
    },
    mediaSide: {
      control: 'inline-radio',
      options: ['left', 'right'],
    },
    appSidebar: { control: 'boolean' },
    step: {
      control: 'select',
      options: ['identifier', 'otp'],
    },
    isLoading: { control: 'boolean' },
    error: { control: 'text' },
    identifier: { control: 'text' },
    otp: { control: 'text' },
    rateLimitSeconds: { control: 'number' },
    resendSeconds: { control: 'number' },
    oauthProviders: { control: 'check', options: ['github', 'google'] },
    oauthPending: { control: 'boolean' },
    oauthFromServer: { control: 'boolean' },
    termsUrl: { control: 'text' },
    privacyUrl: { control: 'text' },
  },
  args: {
    variant: 'centered',
    step: 'identifier',
    isLoading: false,
    error: '',
    identifier: '',
    otp: '',
    rateLimitSeconds: 0,
    resendSeconds: 0,
    termsUrl: 'https://example.com/terms',
    privacyUrl: 'https://example.com/privacy',
  },
  render: (args) => <FlowFrame {...args} />,
} satisfies Meta<typeof FlowFrame>;

export default meta;
type Story = StoryObj<typeof meta>;

// ─── Identifier step ────────────────────────────────────────────────────────

export const IdentifierEmpty: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  args: { step: 'identifier' },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const identifier = canvas.getByRole('textbox');

    await expect(identifier).toHaveFocus();
    await userEvent.type(identifier, 'developer@example.com');
    await expect(identifier).toHaveValue('developer@example.com');
  },
};

export const IdentifierFilled: Story = {
  args: { step: 'identifier', identifier: 'user@example.com' },
};

export const IdentifierLoading: Story = {
  args: { step: 'identifier', identifier: 'user@example.com', isLoading: true },
};

export const IdentifierError: Story = {
  args: {
    step: 'identifier',
    identifier: 'bad@example',
    error: 'Please enter a valid email address.',
  },
};

export const IdentifierRateLimited: Story = {
  args: {
    step: 'identifier',
    identifier: 'user@example.com',
    rateLimitSeconds: 120,
  },
};

// ─── OTP step ───────────────────────────────────────────────────────────────

export const OtpEmpty: Story = {
  args: { step: 'otp', identifier: 'user@example.com' },
};

export const OtpFilled: Story = {
  args: { step: 'otp', identifier: 'user@example.com', otp: '482915' },
};

export const OtpResendCountdown: Story = {
  args: { step: 'otp', identifier: 'user@example.com', resendSeconds: 24 },
};

export const OtpLoading: Story = {
  args: { step: 'otp', identifier: 'user@example.com', otp: '482915', isLoading: true },
};

export const OtpError: Story = {
  args: {
    step: 'otp',
    identifier: 'user@example.com',
    otp: '000000',
    error: 'Code is invalid or expired.',
  },
};

// ─── Split variant quick view ───────────────────────────────────────────────

export const SplitIdentifier: Story = {
  args: { variant: 'split', step: 'identifier' },
};

export const SplitOtp: Story = {
  args: { variant: 'split', step: 'otp', identifier: 'user@example.com' },
};

// ─── Full-bleed split (large-SaaS look) ──────────────────────────────────────

// `logo` is now a ReactNode, not a URL. A `currentColor` inline-SVG fills its
// slot and follows the theme (no per-theme asset swap) — the whole point of the
// new API. `text-primary` tints it with the brand accent.
const LOGO = (
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={2}
    strokeLinecap="round"
    strokeLinejoin="round"
    className="h-full w-full text-primary"
    aria-hidden="true"
  >
    <path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3z" />
  </svg>
);

export const FullSplitIdentifier: Story = {
  args: { variant: 'fullsplit', step: 'identifier', logo: LOGO },
};

export const FullSplitOtp: Story = {
  args: { variant: 'fullsplit', step: 'otp', identifier: 'user@example.com', logo: LOGO },
};

export const FullSplitMirrored: Story = {
  args: { variant: 'fullsplit', mediaSide: 'right', step: 'identifier', logo: LOGO },
};

/**
 * What an app gets with `logo` + `background` and NO `sidebar` — the
 * configuration carapis/listing and the three mls web apps actually ship.
 *
 * Until `AuthBrandPanel` existed this rendered a full-height photograph with
 * nothing on it while the brand sat above the form opposite; every story
 * passed a sidebar of its own, so the state no app was in was the only one
 * ever reviewed. Keep this story: it is the default path.
 */
export const FullSplitNoSidebar: Story = {
  args: { variant: 'fullsplit', step: 'identifier', logo: LOGO, appSidebar: false },
};

/**
 * The Kino sign-in: the app supplies its own `sidebar` and NO `logo`.
 *
 * On a phone the media half is gone and nothing is left above the form, so
 * before the top bar existed this screen had no route off it at all. The way
 * out is a real link the layout owns, and the locale sits at the opposite edge.
 */
export const MobileWithoutLogo: Story = {
  args: { variant: 'fullsplit', step: 'identifier', appSidebar: true },
  parameters: { viewport: { defaultViewport: 'mobile1' } },
  play: async ({ canvasElement }) => {
    const home = within(canvasElement).getByRole('link', { name: /home/i });
    await expect(home).toHaveAttribute('href', '/');
  },
};

/**
 * An error the backend did not write prose for.
 *
 * `resolveAuthError` turns the transport's own `HTTP 404:` into copy a person
 * can act on, so the string below is what the auth layer now produces — never
 * the status line. The message also sits under the field it concerns.
 */
/**
 * The screen after a verified code, before the redirect fires.
 *
 * It had no story until now: the only component that could draw it also
 * navigated away 1.5s later, so nobody could sit and look at it — which is
 * how it kept a layout that showed the brand INSTEAD of a confirmation.
 * `AuthSuccessScreen` is the markup without the timer.
 */
export const Success: StoryObj = {
  render: () => (
    <AuthSuccessScreen message="Signed in successfully" redirecting="Taking you in…" />
  ),
};

export const FullSplitError: Story = {
  args: {
    variant: 'fullsplit',
    step: 'identifier',
    logo: LOGO,
    appSidebar: false,
    identifier: 'user@example.com',
    error: 'Server is unavailable',
  },
};

// ─── Provider sign-in ───────────────────────────────────────────────────────
//
// The network is faked in ONE place, `oauthApiMock` (testing/mockOAuthApi.ts):
// it answers `GET /oauth/providers/`, `POST /oauth/<provider>/authorize/` and
// `.../callback/` at the `fetch` level, so the real client and hooks run, and it
// holds back full-page navigations. A story states the server's answers in its
// `beforeEach`; nothing here reaches a backend.

const AUTH_IDENTIFIER = { step: 'identifier', oauthFromServer: true } as const;

/** Every provider button on the page, in document order. */
const providerButtons = (root: HTMLElement) =>
  Array.from(root.querySelectorAll<HTMLButtonElement>('button[data-provider]'));

/** Resolves any CSS colour (oklch, hsl, rgb) to [r, g, b] through a canvas. */
function toRgb(color: string): [number, number, number] {
  const ctx = document.createElement('canvas').getContext('2d')!;
  ctx.fillStyle = '#000';
  ctx.fillStyle = color;
  ctx.fillRect(0, 0, 1, 1);
  const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
  return [r!, g!, b!];
}

const luminance = ([r, g, b]: [number, number, number]) => (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;

/** Waits until the provider list has arrived and the block shows its buttons. */
const readyButtons = async (root: HTMLElement, count: number) => {
  await waitFor(() => expect(providerButtons(root)).toHaveLength(count));
  return providerButtons(root);
};

// --- Which buttons the server's list produces ---

/** The list request is still open: the block holds its room, the email form already works. */
export const OAuthProvidersLoading: Story = {
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: 'pending' }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(() => expect(getOAuthApiMock().calls[0]).toMatchObject({ method: 'GET' }));
    await expect(getOAuthApiMock().calls[0]!.path).toMatch(/\/oauth\/providers\/$/);
    await expect(canvas.getByRole('textbox')).toBeEnabled();
    await expect(providerButtons(canvasElement)).toHaveLength(0);
    // The reserved room is decoration: hidden from assistive technology, not a teaser.
    const reserve = canvasElement.querySelector('.auth-oauth-reserve');
    await expect(reserve).not.toBeNull();
    await expect(reserve).toHaveAttribute('aria-hidden', 'true');
  },
};

/** No provider enabled: exactly the email page, no button, no divider, no teaser. */
export const OAuthNoneEnabled: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: [] }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    // Focus lands in the field once we know there is nothing above it.
    await waitFor(() => expect(canvas.getByRole('textbox')).toHaveFocus());
    await expect(providerButtons(canvasElement)).toHaveLength(0);
    await expect(canvas.queryByRole('group')).toBeNull();
    await expect(canvas.queryByText('or')).toBeNull();
    await expect(canvasElement.querySelector('.auth-oauth-reserve')).toBeNull();
    await expect(canvas.queryByText(/Google|GitHub/)).toBeNull();
  },
};

/** The list request fails: the same page as "none", never an error on the email form. */
export const OAuthListUnavailable: Story = {
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: 'unavailable' }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await waitFor(() => expect(canvas.getByRole('textbox')).toHaveFocus());
    await expect(providerButtons(canvasElement)).toHaveLength(0);
    await expect(canvas.queryByRole('alert')).toBeNull();
    await expect(canvas.getByRole('button', { name: 'Continue' })).toBeInTheDocument();
  },
};

export const OAuthGithub: Story = {
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: ['github'] }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await readyButtons(canvasElement, 1);
    await expect(canvas.getByRole('button', { name: 'Continue with GitHub' })).toBeEnabled();
    await expect(canvas.queryByRole('button', { name: /Google/ })).toBeNull();
  },
};

/** One server-enabled provider: the button comes first, then "or", then the email path. */
export const OAuthGoogle: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  args: { ...AUTH_IDENTIFIER, termsUrl: 'https://example.com/terms' },
  beforeEach: oauthApiMock({ providers: ['google'] }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const [google] = await readyButtons(canvasElement, 1);
    await expect(google).toHaveAccessibleName('Continue with Google');
    await expect(google).toBeEnabled();
    await waitFor(() => expect(canvas.getByText('or')).toBeVisible());
    // Buttons above the field: it must not take focus (the keyboard would cover them).
    await expect(canvas.getByRole('textbox')).not.toHaveFocus();
    await expect(canvas.queryByRole('button', { name: /GitHub/ })).toBeNull();
  },
};

/** Two providers: the server's order wins (here Google first), same size and weight. */
export const OAuthGithubAndGoogle: Story = {
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: ['google', 'github'] }),
  play: async ({ canvasElement }) => {
    const buttons = await readyButtons(canvasElement, 2);
    await expect(buttons.map((b) => b.dataset.provider)).toEqual(['google', 'github']);
    const [a, b] = buttons;
    await expect(a!.offsetHeight).toBe(b!.offsetHeight);
    await expect(a!.offsetWidth).toBe(b!.offsetWidth);
  },
};

/** `oauthProviders` only narrows what the server enabled; it can never add a provider. */
export const OAuthNarrowedByProp: Story = {
  args: { ...AUTH_IDENTIFIER, oauthProviders: ['github'] },
  beforeEach: oauthApiMock({ providers: ['google', 'github'] }),
  play: async ({ canvasElement }) => {
    const buttons = await readyButtons(canvasElement, 1);
    await expect(buttons[0]!.dataset.provider).toBe('github');
  },
};

// --- A click ---

/** Authorize is in flight: progress only on the clicked button, the other waits. */
export const OAuthPending: Story = {
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: ['google', 'github'], authorize: 'pending' }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await readyButtons(canvasElement, 2);
    await userEvent.click(canvas.getByRole('button', { name: 'Continue with Google' }));

    const google = canvas.getByRole('button', { name: 'Continue with Google' });
    const github = canvas.getByRole('button', { name: 'Continue with GitHub' });
    await waitFor(() => expect(google).toHaveAttribute('aria-busy', 'true'));
    await expect(google).toBeDisabled();
    await expect(github).toBeDisabled();
    await expect(github).not.toHaveAttribute('aria-busy');

    await waitFor(() => expect(getOAuthApiMock().calls.some((c) => c.method === 'POST')).toBe(true));
    const post = getOAuthApiMock().calls.find((c) => c.method === 'POST');
    await expect(post).toMatchObject({ provider: 'google' });
    await expect(post!.path).toMatch(/\/oauth\/google\/authorize\/$/);
    // No redirect_uri: the server derives it from the request origin.
    await expect(post!.body).not.toHaveProperty('redirect_uri');
  },
};

/** The server answered: the state is kept and the tab goes to the provider (held back here). */
export const OAuthRedirectsToProvider: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: ['google', 'github'] }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await readyButtons(canvasElement, 2);
    await userEvent.click(canvas.getByRole('button', { name: 'Continue with GitHub' }));

    await waitFor(() => expect(getOAuthApiMock().navigations).toHaveLength(1));
    const target = new URL(getOAuthApiMock().navigations[0]!);
    await expect(target.origin + target.pathname).toBe('https://github.com/login/oauth/authorize');
    await expect(cfgStorage.read(CFG_KEYS.oauthState.key)).toBe('mock-state-github');
    await expect(cfgStorage.read(CFG_KEYS.oauthProvider.key)).toBe('github');
    // The tab is leaving: the spinner stays on and nothing else can be clicked.
    await expect(canvas.getByRole('button', { name: 'Continue with GitHub' })).toHaveAttribute('aria-busy', 'true');
    await expect(canvas.getByRole('button', { name: 'Continue with Google' })).toBeDisabled();
  },
};

/** Authorize failed (rate limit): a sentence about it, and both buttons usable again. */
export const OAuthStartFailed: Story = {
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: ['google', 'github'], authorize: 'rate_limited' }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await readyButtons(canvasElement, 2);
    await userEvent.click(canvas.getByRole('button', { name: 'Continue with Google' }));

    const alert = await canvas.findByRole('alert');
    await expect(alert).toHaveTextContent(en.layouts.auth.oauth.error.rate_limited);
    await expect(canvas.getByRole('button', { name: 'Continue with Google' })).toBeEnabled();
    await expect(canvas.getByRole('button', { name: 'Continue with GitHub' })).toBeEnabled();
    await expect(getOAuthApiMock().navigations).toHaveLength(0);
  },
};

/** The email form is submitting: every provider button waits. */
export const OAuthDisabledWhileSubmitting: Story = {
  args: { ...AUTH_IDENTIFIER, identifier: 'user@example.com', isLoading: true },
  beforeEach: oauthApiMock({ providers: ['github', 'google'] }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await readyButtons(canvasElement, 2);
    await expect(canvas.getByRole('button', { name: 'Continue with Google' })).toBeDisabled();
    await expect(canvas.getByRole('button', { name: 'Continue with GitHub' })).toBeDisabled();
  },
};

// --- Locales, direction, theme, viewport ---

/** One line, one row height, nothing clipped, whatever the language. */
const expectOneLine = async (button: HTMLElement) => {
  // Layout size, not the painted box: the page fades in with a small scale.
  await expect(button.offsetHeight).toBe(48);
  await expect(button.scrollWidth).toBeLessThanOrEqual(button.clientWidth);
};

/** German has the longest label: both buttons must stay one line. */
export const OAuthLongLabelGerman: Story = {
  args: { ...AUTH_IDENTIFIER, locale: 'de' },
  beforeEach: oauthApiMock({ providers: ['github', 'google'] }),
  play: async ({ canvasElement }) => {
    await readyButtons(canvasElement, 2);
    const canvas = within(canvasElement);
    await expectOneLine(canvas.getByRole('button', { name: 'Mit Google fortfahren' }));
    await expectOneLine(canvas.getByRole('button', { name: de.layouts.auth.identifier.oauth.continueWith.replace('{provider}', 'GitHub') }));
  },
};

export const OAuthRussian: Story = {
  args: { ...AUTH_IDENTIFIER, locale: 'ru' },
  beforeEach: oauthApiMock({ providers: ['github', 'google'] }),
  play: async ({ canvasElement }) => {
    await readyButtons(canvasElement, 2);
    const canvas = within(canvasElement);
    await expectOneLine(canvas.getByRole('button', { name: 'Войти через Google' }));
    await expectOneLine(canvas.getByRole('button', { name: ru.layouts.auth.identifier.oauth.continueWith.replace('{provider}', 'GitHub') }));
  },
};

/** Right-to-left: the icon sits at the start (right) edge through logical layout, no physical margins. */
export const OAuthArabic: Story = {
  args: { ...AUTH_IDENTIFIER, locale: 'ar' },
  beforeEach: oauthApiMock({ providers: ['github', 'google'] }),
  play: async ({ canvasElement }) => {
    const buttons = await readyButtons(canvasElement, 2);
    await expect(canvasElement.querySelector('[dir="rtl"]')).not.toBeNull();
    for (const button of buttons) {
      await expectOneLine(button);
      const box = button.getBoundingClientRect();
      const icon = button.querySelector('svg')!.getBoundingClientRect();
      await expect(icon.left + icon.width / 2).toBeGreaterThan(box.left + box.width / 2);
    }
  },
};

/**
 * Google's branding rules, measured on the rendered button (guidelines fetched
 * 2026-11-01): fill, 1px stroke and text per theme, 12px / 10px / 12px padding,
 * 14/20 weight 500, the G at 20px in its four fixed colours.
 */
const expectGoogleBranding = async (root: HTMLElement, mode: 'light' | 'dark') => {
  const button = within(root).getByRole('button', { name: 'Continue with Google' });
  const palette = {
    light: { fill: [255, 255, 255], stroke: [116, 119, 117], text: [31, 31, 31] },
    dark: { fill: [19, 19, 20], stroke: [142, 145, 143], text: [227, 227, 227] },
  }[mode];

  await waitFor(() => expect(toRgb(getComputedStyle(button).backgroundColor)).toEqual(palette.fill));
  const style = getComputedStyle(button);
  await expect(toRgb(style.borderTopColor)).toEqual(palette.stroke);
  await expect(style.borderTopWidth).toBe('1px');
  await expect(toRgb(style.color)).toEqual(palette.text);
  await expect(style.paddingLeft).toBe('12px');
  await expect(style.paddingRight).toBe('12px');
  await expect(style.columnGap).toBe('10px');
  await expect(style.fontSize).toBe('14px');
  await expect(style.fontWeight).toBe('500');
  await expect(style.lineHeight).toBe('20px');

  const icon = button.querySelector('svg')!;
  await expect(getComputedStyle(icon).width).toBe('20px');
  const fills = Array.from(icon.querySelectorAll('path'), (p) => p.getAttribute('fill'));
  // Same four colours in both themes: the mark is never recoloured.
  await expect(fills).toEqual(['#EA4335', '#34A853', '#4A90E2', '#FBBC05']);
};

/** The GitHub mark is one colour: the button's foreground, dark on light and light on dark. */
const expectGithubTheming = async (root: HTMLElement, mode: 'light' | 'dark') => {
  const button = within(root).getByRole('button', { name: 'Continue with GitHub' });
  const icon = button.querySelector('svg')!;
  const foreground = toRgb(getComputedStyle(button).color);
  await expect(toRgb(getComputedStyle(icon).color)).toEqual(foreground);
  await expect(toRgb(getComputedStyle(icon.querySelector('path')!).fill)).toEqual(foreground);
  const light = luminance(foreground);
  await (mode === 'light' ? expect(light).toBeLessThan(0.4) : expect(light).toBeGreaterThan(0.6));
};

/** Light theme: Google's white button and a dark GitHub mark. */
export const OAuthLight: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  globals: { theme: 'light' },
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: ['github', 'google'] }),
  play: async ({ canvasElement }) => {
    await readyButtons(canvasElement, 2);
    await expect(document.documentElement).not.toHaveClass('dark');
    await expectGoogleBranding(canvasElement, 'light');
    await expectGithubTheming(canvasElement, 'light');
  },
};

/** Dark theme: Google's #131314 button and a light GitHub mark. */
export const OAuthDark: Story = {
  tags: ['contract'],
  parameters: { a11y: { test: 'error' } },
  globals: { theme: 'dark' },
  args: { ...AUTH_IDENTIFIER },
  beforeEach: oauthApiMock({ providers: ['github', 'google'] }),
  play: async ({ canvasElement }) => {
    await readyButtons(canvasElement, 2);
    await expect(document.documentElement).toHaveClass('dark');
    await expectGoogleBranding(canvasElement, 'dark');
    await expectGithubTheming(canvasElement, 'dark');
  },
};

/** A phone: the buttons stay inside the column and keep the full tap height. */
export const OAuthMobile: Story = {
  args: { ...AUTH_IDENTIFIER },
  parameters: { viewport: { defaultViewport: 'mobile1' } },
  beforeEach: oauthApiMock({ providers: ['github', 'google'] }),
  play: async ({ canvasElement }) => {
    const buttons = await readyButtons(canvasElement, 2);
    await expect(document.documentElement.scrollWidth).toBeLessThanOrEqual(document.documentElement.clientWidth);
    for (const button of buttons) {
      const box = button.getBoundingClientRect();
      await expect(box.left).toBeGreaterThanOrEqual(0);
      await expect(box.right).toBeLessThanOrEqual(window.innerWidth);
      await expect(box.height).toBeGreaterThanOrEqual(44);
    }
  },
};

// ─── Provider callback ──────────────────────────────────────────────────────
//
// The page the provider returns to. The real `OAuthCallback` runs against the
// faked network: the harness puts the provider's parameters in the address bar
// and the stored state in sessionStorage, as a real round trip would leave them.

interface CallbackFrameProps {
  /** The callback URL's query string, as the provider left it. */
  query: string;
  /** What the server answers to the code exchange. */
  answer?: OAuthApiScript['callback'];
  /** The state this browser stored; defaults to the one in the URL, `null` is a browser that never started a flow. */
  storedState?: string | null;
  /** The back-url a route guard saved before sign-in. */
  savedRedirect?: string;
  /** Offer a picker of the server's answers, to walk every error code in one story. */
  picker?: boolean;
}

const CALLBACK_QUERY = 'provider=google&code=mock-code&state=mock-state-google';

/** Runs before the callback's own effect: puts the browser in the state a returning visitor has. */
function CallbackSeed({ query, answer, storedState, savedRedirect }: CallbackFrameProps) {
  useLayoutEffect(() => {
    const params = new URLSearchParams(query);
    const provider = params.get('provider');
    seedOAuthBrowser({
      state: storedState === null ? undefined : (storedState ?? params.get('state') ?? undefined),
      provider: provider === 'github' || provider === 'google' ? provider : undefined,
      savedRedirect,
    });
    getOAuthApiMock().set({ callback: answer });
    // The provider's redirect leaves these in the address bar; the callback must strip them.
    const url = new URL(window.location.href);
    params.forEach((value, key) => url.searchParams.set(key, value));
    window.history.replaceState(window.history.state, '', url);
  }, [query, answer, storedState, savedRedirect]);
  return null;
}

function CallbackFrame(props: CallbackFrameProps) {
  const { query, picker } = props;
  const [answer, setAnswer] = useState<OAuthApiScript['callback']>(props.answer ?? 'ok');
  const [run, setRun] = useState(0);
  const params = useMemo(() => new URLSearchParams(query) as unknown as ReadonlyURLSearchParams, [query]);

  const onPick = (event: ChangeEvent<HTMLSelectElement>) => {
    setAnswer(event.target.value as OAuthServerErrorCode);
    setRun((n) => n + 1); // A new attempt: the card mounts again and reads the URL again.
  };

  return (
    <SearchParamsContext.Provider value={params}>
        <MockAuthProvider>
          <div className="min-h-[560px]">
            {/* The picker sits above the callback overlay (z-50), which would otherwise cover it. */}
            {picker && (
              <label className="fixed left-4 top-4 z-[60] flex items-center gap-2 rounded-md border bg-background p-2 text-sm text-foreground">
                Server answer to the code exchange
                <select
                  className="rounded border bg-background px-2 py-1"
                  value={String(answer)}
                  onChange={onPick}
                >
                  {OAUTH_SERVER_ERROR_CODES.map((code) => (
                    <option key={code} value={code}>
                      {code}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <Fragment key={run}>
              <CallbackSeed {...props} answer={answer} />
              <AuthLayout variant="centered" sourceUrl="https://example.com" redirectUrl="/home" />
            </Fragment>
          </div>
        </MockAuthProvider>
    </SearchParamsContext.Provider>
  );
}

const callbackStory = (
  args: CallbackFrameProps,
  script: OAuthApiScript = {},
): Pick<StoryObj, 'beforeEach' | 'render' | 'parameters'> => ({
  parameters: { layout: 'fullscreen' },
  beforeEach: oauthApiMock({ providers: ['google'], ...script }),
  render: () => <CallbackFrame {...args} />,
});

/** Callback request in flight: a polite status, no controls to double-submit. */
export const OAuthCallbackProcessing: StoryObj = {
  ...callbackStory({ query: CALLBACK_QUERY, answer: 'pending' }),
  play: async ({ canvasElement }) => {
    const status = await within(canvasElement).findByRole('status');
    await expect(status).toHaveTextContent(en.layouts.auth.oauth.signingIn);
    await expect(status).toHaveTextContent('complete your Google sign-in');
  },
};

/**
 * The whole round trip: the code is exchanged with the matching state, the
 * session is stored, the success screen shows, and the saved back-url (with its
 * hash) is where the tab goes; the address bar is clean.
 */
export const OAuthCallbackSuccess: StoryObj = {
  ...callbackStory({ query: CALLBACK_QUERY, savedRedirect: '/x#settings/mcp?request=1' }),
  tags: ['contract'],
  play: async ({ canvasElement }) => {
    const status = await within(canvasElement).findByText(en.layouts.auth.success.message);
    // The screen fades in; the text is there from the first frame, visible a moment later.
    await waitFor(() => expect(status).toBeVisible());

    const exchange = getOAuthApiMock().calls.filter((c) => c.method === 'POST');
    await expect(exchange).toHaveLength(1);
    await expect(exchange[0]!.path).toMatch(/\/oauth\/google\/callback\/$/);
    await expect(exchange[0]!.body).toEqual({ code: 'mock-code', state: 'mock-state-google' });
    await expect(cfgStorage.read(CFG_KEYS.accessToken.key)).toBe('mock-access-token');
    // Single use: the stored state is gone, and the URL no longer carries the code.
    await expect(cfgStorage.read(CFG_KEYS.oauthState.key)).toBeNull();
    const here = new URL(window.location.href);
    for (const key of ['provider', 'code', 'state']) await expect(here.searchParams.has(key)).toBe(false);

    // After the pause the success screen sends the tab to the saved back-url, hash intact.
    await waitFor(() => expect(getOAuthApiMock().navigations).toHaveLength(1), { timeout: 4000 });
    await expect(new URL(getOAuthApiMock().navigations[0]!).pathname + new URL(getOAuthApiMock().navigations[0]!).hash).toBe(
      '/x#settings/mcp?request=1',
    );
  },
};

/** The notice's sentence for a copy key, as the stories' provider (Google) reads it. */
const noticeCopy = (key: keyof typeof en.layouts.auth.oauth.error) =>
  en.layouts.auth.oauth.error[key].replace('{provider}', 'Google');

/** Cancel on Google's page returns `?error=access_denied`: back at the form, nothing said. */
export const OAuthCallbackCancelled: StoryObj = {
  ...callbackStory({ query: 'provider=google&error=access_denied' }),
  tags: ['contract'],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(await canvas.findByRole('textbox')).toBeVisible();
    await expect(canvas.queryByText(noticeCopy('cancelled'))).toBeNull();
    await expect(canvas.queryByRole('alert')).toBeNull();
    // Nothing to exchange, so nothing is sent.
    await expect(getOAuthApiMock().calls.filter((c) => c.method === 'POST')).toHaveLength(0);
  },
};

/**
 * A staff address cannot sign in with Google: the form shows one calm sentence
 * and no button: the email field is right below and takes the cursor. The close
 * button and Escape dismiss it.
 */
export const OAuthCallbackLinkNotAllowed: StoryObj = {
  ...callbackStory({ query: CALLBACK_QUERY, answer: 'link_not_allowed' }),
  tags: ['contract'],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await canvas.findByText(en.layouts.auth.oauth.notice.linkNotAllowedTitle);
    const notice = canvas.getByRole('status');
    await expect(notice).toHaveTextContent(noticeCopy('link_not_allowed'));
    await expect(canvas.queryByRole('alert')).toBeNull();

    await expect(within(notice).queryByRole('button', { name: /email/i })).toBeNull();
    await expect(canvas.getByRole('textbox')).toHaveFocus();
    await userEvent.click(within(notice).getByRole('button', { name: en.layouts.auth.oauth.notice.dismiss }));
    await expect(canvas.queryByText(en.layouts.auth.oauth.notice.linkNotAllowedTitle)).toBeNull();
  },
};

/** The close button and Escape both dismiss the notice. */
export const OAuthCallbackNoticeDismiss: StoryObj = {
  ...callbackStory({ query: CALLBACK_QUERY, answer: 'rate_limited' }),
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await canvas.findByText(noticeCopy('rate_limited'));
    await userEvent.click(canvas.getByRole('button', { name: en.layouts.auth.oauth.notice.dismiss }));
    await expect(canvas.queryByText(noticeCopy('rate_limited'))).toBeNull();
  },
};

/** A provider this client has no button for: the generic sentence, no request. */
export const OAuthCallbackUnknownProvider: StoryObj = {
  ...callbackStory({ query: 'provider=facebook&code=c&state=s' }),
  play: async ({ canvasElement }) => {
    await within(canvasElement).findByText(noticeCopy('generic'));
    await expect(getOAuthApiMock().calls.filter((c) => c.method === 'POST')).toHaveLength(0);
  },
};

/** The URL has a code but no `state`: refused before any request. */
export const OAuthCallbackMissingState: StoryObj = {
  ...callbackStory({ query: 'provider=google&code=mock-code' }),
  play: async ({ canvasElement }) => {
    await within(canvasElement).findByText(noticeCopy('invalid_state'));
    await expect(getOAuthApiMock().calls.filter((c) => c.method === 'POST')).toHaveLength(0);
  },
};

/** The state in the URL is not the one this browser stored (a link made elsewhere): refused, no exchange. */
export const OAuthCallbackWrongState: StoryObj = {
  ...callbackStory({ query: CALLBACK_QUERY, storedState: 'another-state' }),
  tags: ['contract'],
  play: async ({ canvasElement }) => {
    await within(canvasElement).findByText(noticeCopy('invalid_state'));
    await expect(getOAuthApiMock().calls.filter((c) => c.method === 'POST')).toHaveLength(0);
    await expect(cfgStorage.read(CFG_KEYS.oauthState.key)).toBeNull();
  },
};

/** A browser that never started a flow (the link was opened elsewhere): same refusal. */
export const OAuthCallbackNoStoredState: StoryObj = {
  ...callbackStory({ query: CALLBACK_QUERY, storedState: null }),
  play: async ({ canvasElement }) => {
    await within(canvasElement).findByText(noticeCopy('invalid_state'));
    await expect(getOAuthApiMock().calls.filter((c) => c.method === 'POST')).toHaveLength(0);
  },
};

/** The sentence each server code maps to (several configuration faults share one, on purpose). */
const ERROR_COPY: Record<OAuthServerErrorCode, keyof typeof en.layouts.auth.oauth.error> = {
  oauth_disabled: 'provider_unavailable',
  github_oauth_disabled: 'provider_unavailable',
  origin_not_allowed: 'generic',
  missing_redirect_uri: 'generic',
  invalid_state: 'invalid_state',
  oauth_exchange_failed: 'oauth_exchange_failed',
  invalid_id_token: 'invalid_id_token',
  email_missing: 'email_missing',
  email_not_verified: 'email_not_verified',
  hosted_domain_not_allowed: 'hosted_domain_not_allowed',
  account_inactive: 'account_inactive',
  link_not_allowed: 'link_not_allowed',
  rate_limited: 'rate_limited',
  provider_unavailable: 'provider_unavailable',
  server_error: 'generic',
  not_found: 'generic',
};

/**
 * Every code the backend can answer the exchange with, one real round trip each:
 * the picker re-runs the callback and the form shows that code's sentence.
 */
export const OAuthCallbackEveryErrorCode: StoryObj = {
  ...callbackStory({ query: CALLBACK_QUERY, answer: OAUTH_SERVER_ERROR_CODES[0], picker: true }),
  tags: ['contract'],
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const picker = canvas.getByLabelText('Server answer to the code exchange');
    for (const code of OAUTH_SERVER_ERROR_CODES) {
      if (code !== OAUTH_SERVER_ERROR_CODES[0]) await userEvent.selectOptions(picker, code);
      const expected = noticeCopy(ERROR_COPY[code]);
      await waitFor(() => expect(canvas.getByText(expected)).toBeVisible(), { timeout: 4000 });
    }
    // One exchange per code, all of them with the matching state.
    const exchanges = getOAuthApiMock().calls.filter((c) => c.method === 'POST');
    await expect(exchanges).toHaveLength(OAUTH_SERVER_ERROR_CODES.length);
  },
};
