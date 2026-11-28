/**
 * AuthLayout configurator defaults, presets, and image catalogue.
 */

import type { AuthPlaygroundConfig, AuthCenteredConfig, AuthSplitConfig } from './types';

export const BG_IMAGES = [
  {
    label: 'Mountains',
    value: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80',
  },
  {
    label: 'Night City',
    value: 'https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=1920&q=80',
  },
  {
    label: 'Abstract Mesh',
    value: 'https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=1920&q=80',
  },
  {
    label: 'Ocean Waves',
    value: 'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=1920&q=80',
  },
  {
    label: 'Forest Fog',
    value: 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1920&q=80',
  },
] as const;

export const defaultCenteredConfig: AuthCenteredConfig = {
  background: {
    enabled: false,
    imageUrl: BG_IMAGES[0].value,
    gradient: 'linear-gradient(135deg, color-mix(in oklab, var(--primary) 8%, transparent) 0%, var(--background) 100%)',
    overlay: 'color-mix(in oklab, var(--background) 60%, transparent)',
    blur: '8px',
  },
  form: {
    showLogo: true,
    showTerms: true,
    showGithub: true,
    showGoogle: true,
    showSupport: true,
  },
};

export const defaultSplitConfig: AuthSplitConfig = {
  background: {
    enabled: true,
    imageUrl: BG_IMAGES[0].value,
    gradient: '',
    overlay: 'color-mix(in oklab, var(--background) 60%, transparent)',
    blur: '8px',
  },
  sidebar: {
    enabled: true,
    showQuote: true,
    showAuthor: true,
  },
  form: {
    showLogo: true,
    showTerms: true,
    showGithub: true,
    showGoogle: true,
    showSupport: true,
  },
};

/** Full config used when the caller still needs a single object (e.g. URL encode). */
export const defaultConfig: AuthPlaygroundConfig = {
  variant: 'centered',
  ...defaultCenteredConfig,
  sidebar: { enabled: false, showQuote: true, showAuthor: true },
};

export const presets = {
  centered: defaultCenteredConfig,
  split: defaultSplitConfig,
} as const;

export function detectPreset(config: AuthPlaygroundConfig): 'centered' | 'split' | 'custom' {
  if (deepEqual(config, { variant: 'centered', ...defaultCenteredConfig, sidebar: { enabled: false, showQuote: true, showAuthor: true } })) {
    return 'centered';
  }
  if (deepEqual(config, { variant: 'split', ...defaultSplitConfig })) {
    return 'split';
  }
  return 'custom';
}

function deepEqual(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (typeof a !== 'object' || typeof b !== 'object' || a === null || b === null) return false;
  const ak = Object.keys(a as Record<string, unknown>);
  const bk = Object.keys(b as Record<string, unknown>);
  if (ak.length !== bk.length) return false;
  for (const k of ak) {
    if (!deepEqual((a as Record<string, unknown>)[k], (b as Record<string, unknown>)[k])) {
      return false;
    }
  }
  return true;
}
