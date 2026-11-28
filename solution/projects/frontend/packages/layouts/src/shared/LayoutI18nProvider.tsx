/**
 * LayoutI18nProvider — single source of truth for locale plumbing inside layouts.
 *
 * Mounted by `BaseApp` when `i18n` is passed. Every locale-aware component
 * inside layouts (footer, navbar controls, mobile drawer, private sidebar
 * account, UserMenu, LocaleSwitcher) reads from here instead of receiving
 * `i18n` as a prop.
 *
 * Components that may render outside the provider (e.g. raw shells used in
 * playground previews) should call `useLayoutI18nOptional()` and gracefully
 * hide locale-related UI when it returns `null`.
 */

'use client';

import * as React from 'react';

import type { I18nLayoutConfig } from '../layouts/types/layout.types';

const LayoutI18nContext = React.createContext<I18nLayoutConfig | null>(null);

export interface LayoutI18nProviderProps {
  value: I18nLayoutConfig | null | undefined;
  children: React.ReactNode;
}

/**
 * Provider — mount once at the app root (handled automatically by `BaseApp`).
 * Passing `null`/`undefined` is fine: consumers fall back to "no locale switcher".
 */
export function LayoutI18nProvider({ value, children }: LayoutI18nProviderProps) {
  // `null` keeps the context discriminator simple — `useLayoutI18nOptional`
  // returns `null` whether the provider is missing or `value` is empty.
  const stable = value ?? null;
  return <LayoutI18nContext.Provider value={stable}>{children}</LayoutI18nContext.Provider>;
}

/**
 * Throws when used outside the provider. Use for components that strictly
 * require locale plumbing (the locale picker dialog, for instance).
 */
export function useLayoutI18n(): I18nLayoutConfig {
  const ctx = React.useContext(LayoutI18nContext);
  if (!ctx) {
    throw new Error(
      'useLayoutI18n must be used inside <LayoutI18nProvider> — pass `i18n` to <BaseApp> / <AppLayout>.',
    );
  }
  return ctx;
}

/**
 * Optional accessor — returns `null` outside the provider or when no `i18n`
 * was configured. Use for opt-in mounts (footer locale switcher, navbar
 * locale dropdown) that should silently disappear when locale support is off.
 */
export function useLayoutI18nOptional(): I18nLayoutConfig | null {
  return React.useContext(LayoutI18nContext);
}
