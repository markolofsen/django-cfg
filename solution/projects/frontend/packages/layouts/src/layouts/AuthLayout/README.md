# AuthLayout

Shell-based authentication layout with three visual variants:
- `fullsplit` **(default)** — **full-bleed 50/50** (the large-SaaS look —
  Vercel / Linear / IBM). Desktop: edge-to-edge — `background` image on one side
  (left by default, see `mediaSide`) with the `sidebar` (quote/brand) overlaid
  and a soft bottom-up shadow scrim; form on a solid panel on the other side.
  The photo fades in once loaded and gets a slow Ken Burns zoom. Mobile: the
  image half drops away, leaving a plain centered form.
- `centered` — Apple HIG-style, frameless, centered, glow background.
- `split` — on desktop a two-column **frosted-glass** card (form + sidebar)
  floating over the `background` image; on mobile it collapses to a plain,
  frameless centered form (no image, no glass, no sidebar).

## One sign-in host (SSO)

`BaseApp auth={{ sso: true }}` makes one host (`auth.<apex>`) the only place the form is shown. Elsewhere the layout is a
preloader and the provider sends the visitor to `{authHost}/auth?next=<page>`; after sign-in they return to `next`. On the
host, `?sso_error=cookie` (the shared cookie did not reach the site they came from) shows a notice and stops the send-back.
Off unless `sso` is set. Setup and the `next` rules: docs → *One sign-in host for subdomains*; code: `@djangocfg/api`
`auth/utils/sso.ts`.

## Where the brand goes

**One brand per screen, placed where there is room for it.** Pass `logo`; the
layout decides.

| Variant | Desktop | Below 1024px |
|---|---|---|
| `fullsplit` | on the photo half (`AuthBrandPanel`) | above the form |
| `centered`, `split` | above the form | above the form |

On `fullsplit` the media half is a full-height photograph, and its content is
the `sidebar` slot. When an app passes `logo` and **no** `sidebar`, the layout
supplies `AuthBrandPanel` itself and the form header stands its logo down — so
the photo carries the brand and the form carries only the task. An explicit
`sidebar` always wins and the logo stays above the form.

> This default exists because the slot was previously the consumer's problem
> alone: four of the nine apps mounting this layout passed `logo` + `background`
> and no `sidebar`, rendering a large photograph with nothing on it while the
> brand crowded the form opposite. Every Storybook story supplied a sidebar of
> its own, so the shipped configuration was the one never reviewed. See
> `FullSplitNoSidebar` in `AuthFlow.stories.tsx`.

Below 1024px `fullsplit` drops the media half, so the logo above the form is
the only brand left and it returns. CSS owns that half of the rule
(`.auth-header[data-brand-elsewhere]`) — a JS width branch would need a
viewport the server does not have and would flicker on hydration.

**The mark is a link to `/`** — the way out. A sign-in screen is otherwise a
dead end: arrive by a direct link, or get bounced here by an expired session,
and there is no route back to the site (Back has nowhere to return to either).
There is no prop for it: every app has a root, and a localized app resolves `/`
through next-intl's own `Link`, so `/ru/auth` returns to `/ru`. The href lives
in `constants.ts` as `AUTH.HOME_URL`.

The link carries `aria-label` from `layouts.navigation.home` rather than
relying on its contents: `logo` is an opaque node, and a brand that is a bare
SVG would otherwise announce as an unnamed link.

## The top bar: the way out and the language

Every variant pins one bar to the top of the form column: **`‹ Home`** on the
left, the **locale picker** on the right. The layout owns it (`AuthTopBar`,
passed to the shell as `topBar`), so it does not depend on `logo` or `sidebar`.

> It exists because the brand link above was the only exit, and the brand is
> optional. An app that passed its own `sidebar` and no `logo` (the Kino sign-in)
> left a phone visitor with no route off the screen: the media half is hidden
> below 1024px and the form header had nothing to render. The locale, meanwhile,
> floated above the title inside the centered stack.

- The link is a real `<a href="/">` (`AUTH.HOME_URL`) with a visible label, the
  way an iOS back button names its destination. A bare arrow reads as browser
  Back, and Back has nowhere to go after a direct link. The label is
  `layouts.navigation.home`, translated in all 17 locales.
- Both controls are at least 44px tall. The bar clears the notch with
  `env(safe-area-inset-top)`.
- When the layout's own `AuthBrandPanel` is on the photo half (`fullsplit`, `logo`
  and no `sidebar`) the home link stands down from 1024px, since the panel links
  home already. With a custom `sidebar` the bar's link stays: the layout cannot
  know the sidebar links anywhere.
- The locale picker mounts whenever `LayoutI18nProvider` does (`BaseApp` does it
  when the host passes `i18n`). It moved out of `AuthContainer`.

**Height.** Every shell is `min-height: 100dvh` with a `100vh` fallback, so the
mobile address bar does not leave a gap. The form centers itself in the space the
bar leaves with `margin: auto` on its own block, not `justify-content: center` on
the column: with the keyboard open the form scrolls from its top instead of
having its first field pushed out of reach. It sits slightly above the true
center (`padding-bottom: clamp(0rem, 8dvh, 4rem)`), the optical center of a form.

`logo` is a **`ReactNode`** — an inline-SVG brand component, an `<img>`, a
horizontal lock-up. **The slot fits the artwork, not the reverse:** it caps the
height (44px in the form header, 2.5rem on the brand panel) and lets the width
follow, so a square mark and a wide lock-up both keep their aspect ratio. Use a
`currentColor` SVG and it inherits the surrounding text color — no per-theme
asset swap.

> Until this was fixed the slot was a hard 56×56 square with `width: 100%` on
> the child, which silently assumed every brand is square. A horizontal lock-up
> (mark plus two lines of type) was squeezed into the square and rendered as a
> scramble — visible in carapis, invisible in mls, whose mark happens to be
> square.

```tsx
<AuthLayout logo={<BrandMark className="text-foreground" />} … />
```

Supports: email OTP, phone OTP and GitHub OAuth. A 2FA challenge is not part of
this layout — see below.

**Consent, not a checkbox.** There is no opt-in terms checkbox — continuing *is*
the consent. When `termsUrl`/`privacyUrl` are set, a passive line ("By continuing
you agree to the Terms and Privacy Policy") renders under the submit button with
links that open in a new tab. The copy is intentionally hardcoded English (legal
document names stay in English across locales) — see `shared/AuthConsent`.

> **2FA is not a step of the sign-in flow.** When a sign-in step (OTP, password,
> OAuth callback) receives `requires_2fa`, it calls `beginTwoFactorChallenge` from
> `@djangocfg/api/auth` and nothing more. `TwoFactorChallengeDialog`
> (`snippets/TwoFactorDialog`, mounted by `AuthLayout`) opens over the page and
> owns code entry, the backup-code fallback and lockout hints. The form holds no
> 2FA state. *Configuring* 2FA (QR + backup codes) is `TwoFactorSetup`, used by
> **SettingsLayout** (`TwoFactorSection`); both live in `snippets/TwoFactor`.

**Fast code screen.** Submitting the email opens the code screen immediately and
rolls back to the identifier step if the request fails. The resend link counts
down from the server's `resend_in` (30s fallback).

**Session length.** Sign-ins are kept as long as the server's refresh-token
lifetime allows; there is no remember-me option.

## Usage

### Centered variant

```tsx
import { AuthLayout } from '@djangocfg/layouts';

<AuthLayout
  sourceUrl="https://myapp.com"
  redirectUrl="/private"
  termsUrl="/terms"
  privacyUrl="/privacy"
>
  {/* Optional: custom header shown only on the identifier step */}
  <div>
    <h1>Welcome to MyApp</h1>
    <p>Sign in to continue</p>
  </div>
</AuthLayout>
```

### Split variant (two-column)

```tsx
import { AuthLayout } from '@djangocfg/layouts';

<AuthLayout
  variant="split"
  sourceUrl="https://myapp.com"
  background={{
    imageUrl: '/assets/signup-bg.jpg',
    overlay: 'color-mix(in oklab, var(--background) 60%, transparent)',
    blur: '8px',
  }}
  sidebar={
    <div>
      <blockquote>"Amazing product!"</blockquote>
      <cite>— Jane Doe, CEO</cite>
    </div>
  }
>
  {/* Optional: custom header */}
  <div>
    <h1>Get started</h1>
    <p>Already have an account? <a href="/login">Login</a></p>
  </div>
</AuthLayout>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `variant` | `'centered' \| 'split' \| 'fullsplit'` | `'fullsplit'` | Shell layout variant |
| `mediaSide` | `'left' \| 'right'` | `'left'` | Which side the image half sits on (`fullsplit` only) |
| `background` | `AuthBackgroundConfig` | — | Background image/gradient/overlay/blur |
| `sidebar` | `ReactNode` | — | Media/side column content. On `fullsplit`, omitting it with `logo` set yields the default `AuthBrandPanel` |
| `sourceUrl` | `string` | — | App URL for analytics/tracking |
| `redirectUrl` | `string` | `/private` | Where to redirect after auth |
| `oauthProviders` | `('github' \| 'google')[]` | server list | Buttons come from the server (`GET /oauth/providers/`); this only narrows or orders them |
| `enableGithubAuth` | `boolean` | — | Deprecated, no effect |
| `enablePhoneAuth` | `boolean` | `false` | Allow phone number input |
| `logo` | `ReactNode` | — | Brand node. Placed by variant (see [Where the brand goes](#where-the-brand-goes)); the slot caps its height and keeps its aspect ratio |
| `termsUrl` | `string` | — | Terms link — rendered in the passive consent line (opens in a new tab) |
| `privacyUrl` | `string` | — | Privacy link — rendered in the passive consent line (opens in a new tab) |
| `supportUrl` | `string` | — | Support page link |
| `className` | `string` | — | Extra class on root element |
| `children` | `ReactNode` | — | Custom header (identifier step only) |

### AuthBackgroundConfig

| Prop | Type | Description |
|---|---|---|
| `imageUrl` | `string` | Background image URL (loaded via `useImageLoader`) |
| `gradient` | `string` | CSS gradient fallback |
| `overlay` | `string` | Overlay color with opacity |
| `blur` | `string` | Backdrop blur amount (default: `8px`) |

## Callbacks

```tsx
<AuthLayout
  onIdentifierSuccess={(identifier) => console.log('identifier:', identifier)}
  onOTPSuccess={() => console.log('otp verified')}
  onOAuthSuccess={(user, isNewUser, provider) => console.log(provider, user)}
  onError={(message) => console.error(message)}
/>
```

## Auth Steps

The sign-in flow walks these steps:

| Step | Description |
|---|---|
| `identifier` | Email or phone input |
| `otp` | 4-digit email OTP code entry |
| `success` | Full-screen confirmation → redirect (see below) |

`children` (custom header) are only rendered on the `identifier` step — hidden on all others.

## The success screen

A checkmark, the outcome, and what the wait is for:

```text
        ✓
  Signed in successfully
     Taking you in…
```

The mark is **always** the checkmark, never the brand. Rendering the logo
instead (the old behaviour when `logo` was set) produced a screen that never
actually said the sign-in worked — it read as a splash screen, which is what a
sign-in has just finished not being. The second line names the redirect, so the
pause before navigation reads as intent rather than a stall.

The overlay is one `role="status"` live region, so a screen reader hears the
confirmation and the redirect notice together. Timings live in `constants.ts`
(`REDIRECT_DELAY`, `ANIMATION_START_DELAY`).

The markup is exported separately as **`AuthSuccessScreen`** — no timer, no
router — so it can be rendered and reviewed on its own:

```tsx
<AuthSuccessScreen message="Signed in successfully" redirecting="Taking you in…" />
```

| Prop | Type | Description |
|---|---|---|
| `message` | `string` | The outcome |
| `redirecting` | `string?` | What the pause is for; omitted renders nothing |
| `visible` | `boolean?` | Drives the group fade. Default `true` |

That split exists because the screen previously had **no story at all**: the
only component that could draw it also navigated away 1.5s later, so nobody
could sit and look at it — which is how it kept showing the brand instead of a
confirmation. See `Success` in `AuthFlow.stories.tsx`.

## Provider sign-in stories

`AuthFlow.stories.tsx` runs the real hooks against a faked network. One place
fakes it: `oauthApiMock` (`@djangocfg/layouts/testing`, `testing/mockOAuthApi.ts`),
used as a story `beforeEach`. It answers `GET /oauth/providers/`, the two
`authorize` and `callback` POSTs (any of the 16 error codes, with its HTTP
status) at the `fetch` level, refuses every other request, and holds back
full-page navigations (the redirect to the provider, the redirect after
sign-in) so the iframe stays put; `getOAuthApiMock()` exposes the recorded
calls and navigations for `play` assertions. Pair it with
`MockAuthFormProvider oauthFromServer` for the button list, or run the whole
`AuthLayout` for a callback round trip. The callback stories put the provider's
parameters in the address bar and the stored state in `sessionStorage`
(`seedOAuthBrowser`), as a real return leaves them.

## A failed provider sign-in

A provider round trip that does not finish never blocks the page. `OAuthCallback`
strips `?provider=&code=&state=` from the address bar, puts the failure in
`AuthFormContext.oauthNotice`, and the visitor lands on the normal sign-in form
with a calm inline notice (`OAuthNotice`, `role="status"`) above the buttons. Only
the wait for the code exchange covers the page.

| Failure | The form says | One next step |
|---|---|---|
| Cancelled on the provider's page | nothing | the form itself |
| `link_not_allowed` (staff account) | "Use the email code for this address" + one sentence | **Continue with email**: closes the notice, focuses the email field |
| Expired or foreign state, exchange or token failure, provider down, unknown | one short sentence | **Try {provider} again** (email when the provider has no button here) |
| Email missing or unverified, domain refused | one sentence | **Continue with email** |
| Account disabled, rate limited | one sentence | none |
| `origin_not_allowed`, `missing_redirect_uri`, `oauth_disabled` (site not set up for the provider) | "not available on this site"; for `origin_not_allowed` also a developer line with the refused origin and the redirect URI to register | **Continue with email** |

The notice closes with its button or Escape. One table maps each code to its
sentence and next step: `components/oauth/errors/errorCopy.ts`; copy is `layouts.auth.oauth.error.*` and
`layouts.auth.oauth.notice.*` in `@djangocfg/i18n`. The strict-mode guard is
unchanged: one attempt per page load.

## Errors

The form never shows a raw transport string. `@djangocfg/api`'s
`resolveAuthError` (`auth/utils/errors.ts`) decides the copy in one place:

1. **Text the server wrote** (`error` / `detail` / `message`) — it knows the
   specific reason a status code cannot express ("This code has expired").
2. **Copy chosen from the status code**, translated, via keys that already
   exist in all 17 locales (`api.errors.*`, `ui.errors.*`).
3. A generic sentence.

`HTTP <code>:` strings are rejected on the way through: that is `APIError`
restating its own status line, and under HTTP/2 `statusText` is empty — which
is how a bare `HTTP 404:` once rendered under a sign-in field. The code still
reaches the console through `logAuthFailure`, where diagnosis belongs.

The message renders directly beneath the input it concerns, not at the foot of
the form.

## Architecture

AuthLayout is built on a **shell pattern** (inspired by PublicLayout's navbar/footer slots):

```
AuthLayout/
├── shells/
│   ├── AuthShell.tsx      — Orchestrator: loads bg image, dispatches variant
│   ├── CenteredShell.tsx  — Apple-style frameless layout
│   ├── SplitShell.tsx     — Floating frosted-glass card layout
│   ├── FullSplitShell.tsx — Full-bleed 50/50 layout
│   ├── context.tsx        — Shell context (variant, hasSidebar)
│   └── types.ts           — AuthShellVariant, AuthBackgroundConfig
├── components/steps/      — Auth step components (IdentifierStep, OTPStep, ...)
├── components/oauth/      — Provider sign-in, see its `index.ts` for the map:
│   ├── providers/         — registry (name + icon per provider), icons, which to show
│   ├── buttons/           — OAuthProviderButton, OAuthButtonList, OAuthButtons (hook)
│   ├── notice/            — inline message after a failed round trip
│   ├── callback/          — /auth?provider=<id>: URL parsing, wait overlay
│   └── errors/            — failure code -> copy and next step
├── components/shared/     — Reusable UI primitives (AuthButton, AuthConsent, ...)
│                          incl. AuthBrandPanel — the default `fullsplit` media content
├── styles/
│   ├── auth.css            — Shared form/button/input styles
│   ├── oauth.css           — Provider column, reserve while loading, developer hint
│   ├── centered-shell.css  — Centered variant layout
│   ├── split-shell.css     — Split variant layout
│   └── fullsplit-shell.css — Full-bleed split variant layout
```

Adding a new variant:
1. Add variant name to `AuthShellVariant` in `shells/types.ts`
2. Create `<NewShell>.tsx` in `shells/`
3. Add CSS in `styles/new-shell.css`
4. Wire it up in `AuthShell.tsx`

## Context

Step components can access form state via `useAuthFormContext()`:

```tsx
import { useAuthFormContext } from '@djangocfg/layouts';

const { step, identifier, isLoading } = useAuthFormContext();
```

Shell metadata is available via `useAuthShell()`:

```tsx
import { useAuthShell } from '@djangocfg/layouts';

const { variant, hasSidebar } = useAuthShell();
```

## Adding an OAuth provider

1. The backend adds the provider; `make generate` in `@djangocfg/api` extends `OAuthProviderId`.
2. Typecheck now fails in `components/oauth/providers/registry.ts`.
3. Draw `providers/icons/<Name>Icon.tsx` (20x20, `currentColor` unless the brand forbids recolouring).
4. Add one line to `OAUTH_PROVIDERS`: `{ name: 'Brand', Icon }`.

Nothing else changes: the label is `layouts.auth.identifier.oauth.continueWith` with
the brand name, the notices and error copy read the same table.
