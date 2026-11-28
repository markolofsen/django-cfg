// ============================================================================
// @djangocfg/payments — Stripe Appearance builder (design-token driven)
// ============================================================================
// Maps the live ui-core design tokens (macos preset) onto Stripe's Appearance
// API so the Payment Element (rendered in a cross-origin iframe, un-styleable
// from the app) matches the surrounding dialog in BOTH light and dark themes.
//
// Why this file exists: without an `appearance`, Stripe uses its default light
// `theme: 'stripe'` and renders a WHITE form on our dark dialog. Only the
// Appearance API can touch the iframe, so we translate our tokens into it.
//
// Stripe constraint: the core color variables (colorPrimary/colorBackground/
// colorText/colorDanger/colorSuccess/colorWarning) must be CONCRETE colors —
// `var(...)` and `rgba(...)` are rejected there. ui-core's palette hooks return
// hex, so we read from that (passed in as `tokens`) rather than forwarding raw
// `hsl(var(--x))` token strings.

import type { Appearance } from '@stripe/stripe-js';

/** Concrete hex/color values read from the live theme (ui-core palette). */
export interface AppearanceTokens {
  /** Brand CTA / accent — `--primary`. */
  primary: string;
  /** Input fill — `--input` (falls back to `--background`). */
  input: string;
  /** Body text — `--foreground`. */
  foreground: string;
  /** Secondary text / placeholders — `--muted-foreground`. */
  mutedForeground: string;
  /** Control outline — `--border`. */
  border: string;
  /** Focus ring (blue, ui-core pattern) — `--ring`. */
  ring: string;
  /** Error color — `--destructive`. */
  destructive: string;
  /** Resolved font stack — `--font-sans`. */
  fontFamily?: string;
  /** Control radius, e.g. `0.625rem` — `--radius-control`. */
  borderRadius?: string;
}

/** Sensible dark defaults if the theme can't be read (SSR / probe failure). */
const DARK_FALLBACK: AppearanceTokens = {
  primary: '#0a84ff',
  input: '#1c1c1e',
  foreground: '#f5f5f7',
  mutedForeground: '#98989d',
  border: '#38383a',
  ring: '#0a84ff',
  destructive: '#ff453a',
};

/** Sensible light defaults if the theme can't be read. */
const LIGHT_FALLBACK: AppearanceTokens = {
  primary: '#0071e3',
  input: '#ffffff',
  foreground: '#1d1d1f',
  mutedForeground: '#6e6e73',
  border: '#d2d2d7',
  ring: '#0071e3',
  destructive: '#ff3b30',
};

/**
 * Build a Stripe {@link Appearance} from resolved design tokens.
 *
 * @param theme  'light' | 'dark' — picks the base Stripe theme + fallback set.
 * @param tokens Concrete color/typography values from the live theme. When
 *               omitted (SSR), a matching light/dark fallback is used so the
 *               form is never white-on-dark.
 */
export function buildStripeAppearance(
  theme: 'light' | 'dark',
  tokens?: Partial<AppearanceTokens>,
): Appearance {
  const base = theme === 'dark' ? DARK_FALLBACK : LIGHT_FALLBACK;
  const t: AppearanceTokens = { ...base, ...tokens };

  const fontFamily =
    t.fontFamily ||
    '-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, sans-serif';
  const borderRadius = t.borderRadius || '0.625rem';

  return {
    theme: theme === 'dark' ? 'night' : 'stripe',
    labels: 'above',
    variables: {
      colorPrimary: t.primary,
      colorBackground: t.input,
      colorText: t.foreground,
      colorTextSecondary: t.mutedForeground,
      colorTextPlaceholder: t.mutedForeground,
      colorDanger: t.destructive,
      colorIcon: t.mutedForeground,
      fontFamily,
      fontSizeBase: '16px', // ≥16px avoids mobile input auto-zoom
      spacingUnit: '4px',
      borderRadius,
    },
    rules: {
      '.Input': {
        border: `1px solid ${t.border}`,
        boxShadow: 'none',
      },
      // Apple-minimal focus: a clean 1px ring, no fat blue glow.
      '.Input:focus': {
        border: `1px solid ${t.ring}`,
        boxShadow: `0 0 0 1px ${t.ring}`,
        outline: 'none',
      },
      '.Input--invalid': {
        border: `1px solid ${t.destructive}`,
        boxShadow: `0 0 0 1px ${t.destructive}`,
      },
      '.Tab': {
        border: `1px solid ${t.border}`,
        boxShadow: 'none',
      },
      '.Tab:hover': {
        border: `1px solid ${t.border}`,
      },
      '.Tab--selected': {
        border: `1px solid ${t.primary}`,
        boxShadow: `0 0 0 1px ${t.primary}`,
      },
      '.Label': {
        color: t.mutedForeground,
      },
    },
  };
}
