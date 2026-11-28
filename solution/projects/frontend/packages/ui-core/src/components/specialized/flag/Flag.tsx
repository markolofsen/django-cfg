'use client';

import * as React from 'react';

import { cn } from '../../../lib/utils';

import { FLAG_LOADERS } from './flag-map';
import { getLanguageCountryCode } from './language-to-country';

/**
 * Presentational attributes only.
 */
export interface FlagProps {
  /** ISO 3166-1 alpha-2 country code (e.g. `'US'`, `'JP'`). Case-insensitive. */
  countryCode: string;
  /** Optional rounded corners — common for tile / chip presentations. */
  rounded?: boolean;
  className?: string;
  width?: number | string;
  height?: number | string;
  title?: string;
}

/** Loaded SVG strings, shared by every `Flag` on the page. */
const loaded = new Map<string, string>();

/**
 * SVG country flag (3:2 aspect), loaded on demand — one small chunk per code.
 * Renders an empty box of the same size until it arrives, and nothing for an
 * unknown code.
 */
export function Flag({ countryCode, rounded, className, width, height, title }: FlagProps) {
  const code = countryCode?.toUpperCase();
  const load = code ? FLAG_LOADERS[code] : undefined;
  const [svg, setSvg] = React.useState(() => (code ? loaded.get(code) : undefined));

  React.useEffect(() => {
    if (!code || !load) return;
    const cached = loaded.get(code);
    if (cached) {
      setSvg(cached);
      return;
    }
    let live = true;
    load().then((m) => {
      loaded.set(code, m.default);
      if (live) setSvg(m.default);
    });
    return () => {
      live = false;
    };
  }, [code, load]);

  if (!load) return null;
  return (
    <span
      className={cn(
        'inline-block shrink-0 select-none [&>svg]:block [&>svg]:h-full [&>svg]:w-full',
        rounded && 'overflow-hidden rounded-[2px]',
        className,
      )}
      style={{ width, height }}
      title={title}
      aria-hidden="true"
      // Static SVG from `country-flag-icons`, never user input.
      dangerouslySetInnerHTML={svg ? { __html: svg } : undefined}
    />
  );
}

export interface LanguageFlagProps extends Omit<FlagProps, 'countryCode'> {
  /** Locale / language code (`'en'`, `'pt-BR'`, `'zh_CN'`, …). */
  code: string;
}

/**
 * Convenience wrapper — resolves a locale to a country code and renders `Flag`.
 * Returns `null` when the locale has no country mapping.
 */
export function LanguageFlag({ code, ...props }: LanguageFlagProps) {
  const country = getLanguageCountryCode(code);
  if (!country) return null;
  return <Flag countryCode={country} {...props} />;
}
