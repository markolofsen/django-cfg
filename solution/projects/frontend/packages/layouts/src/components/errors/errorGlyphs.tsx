'use client';

import React from 'react';

interface GlyphSpec {
  /** Accent tint used for the glow and the gradient stop. */
  accent: string;
  /** viewBox for the inner SVG. Default 24 24. */
  viewBox?: string;
  /** Inner SVG children. Must use `currentColor` for stroke. */
  paths: React.ReactNode;
}

const GLYPH_SPECS: Record<string, GlyphSpec> = {
  // 404 — magnifier over a page corner (not-found)
  '404': {
    accent: 'rgb(139 92 246)', // violet-500
    paths: (
      <>
        <path d="M13.5 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7.5" />
        <path d="M13.5 3 19 8.5" />
        <path d="M13 3v4a2 2 0 0 0 2 2h4" />
        <circle cx="11" cy="14.5" r="2.5" />
        <path d="m13 16.5 2 2" />
      </>
    ),
  },
  // 500 — server stack with a warning bolt (server-side failure)
  '500': {
    accent: 'rgb(239 68 68)', // red-500
    paths: (
      <>
        <rect x="3" y="4" width="18" height="6" rx="1.5" />
        <rect x="3" y="14" width="18" height="6" rx="1.5" />
        <path d="M7 7h.01" />
        <path d="M7 17h.01" />
        <path d="m15 6-2 4h3l-2 4" strokeLinejoin="round" />
      </>
    ),
  },
  // 502 — two servers with a broken link between
  '502': {
    accent: 'rgb(249 115 22)', // orange-500
    paths: (
      <>
        <rect x="3" y="4" width="8" height="16" rx="1.5" />
        <rect x="13" y="4" width="8" height="16" rx="1.5" />
        <path d="M6 8h.01" />
        <path d="M16 8h.01" />
        <path d="M11 11.5h-1" />
        <path d="M14 12.5h-1" />
        <path d="m11 10 2 4" strokeLinejoin="round" />
      </>
    ),
  },
  // 503 — power off / plug pulled
  '503': {
    accent: 'rgb(249 115 22)', // orange-500
    paths: (
      <>
        <path d="M12 2v10" />
        <path d="M18.4 6.6a9 9 0 1 1-12.77 0" />
      </>
    ),
  },
  // 504 — clock with slash (gateway timeout)
  '504': {
    accent: 'rgb(234 179 8)', // yellow-500
    paths: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
  },
  // 408 — clock (request timeout)
  '408': {
    accent: 'rgb(234 179 8)', // yellow-500
    paths: (
      <>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </>
    ),
  },
  // 403 — shield with a prohibition line (forbidden)
  '403': {
    accent: 'rgb(239 68 68)', // red-500
    paths: (
      <>
        <path d="M12 2 4 5v6c0 5 3.5 9 8 11 4.5-2 8-6 8-11V5l-8-3Z" />
        <path d="m9 9 6 6" strokeLinejoin="round" />
      </>
    ),
  },
  // 401 — key (auth required)
  '401': {
    accent: 'rgb(59 130 246)', // blue-500
    paths: (
      <>
        <circle cx="8" cy="15" r="4" />
        <path d="m10.8 12.2 8.2-8.2" />
        <path d="m17 5 3 3" />
        <path d="m15 7 2 2" />
      </>
    ),
  },
  // 400 — general alert triangle (bad request)
  '400': {
    accent: 'rgb(234 179 8)', // yellow-500
    paths: (
      <>
        <path d="m12 3 10 18H2L12 3Z" strokeLinejoin="round" />
        <path d="M12 9v5" />
        <path d="M12 17.5h.01" />
      </>
    ),
  },
};

const DEFAULT_GLYPH: GlyphSpec = {
  accent: 'rgb(113 113 122)', // zinc-500
  paths: (
    <>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v4" />
      <path d="M12 16h.01" />
    </>
  ),
};

/**
 * Render the glyph for a given code, wrapped in a container with a soft radial
 * glow behind the icon. Returns `null` if nothing should be shown.
 */
export function getErrorIcon(code?: string | number): React.ReactNode {
  if (code === undefined || code === null || code === '') return null;
  const c = String(code);
  const spec = GLYPH_SPECS[c] ?? DEFAULT_GLYPH;

  return (
    <div
      className="relative mx-auto flex size-28 items-center justify-center"
      aria-hidden="true"
    >
      {/* soft radial glow */}
      <div
        className="pointer-events-none absolute inset-0 rounded-full blur-2xl opacity-60"
        style={{
          background: `radial-gradient(circle at 50% 50%, ${spec.accent} 0%, transparent 65%)`,
        }}
      />
      {/* icon */}
      <svg
        className="relative size-20"
        viewBox={spec.viewBox ?? '0 0 24 24'}
        fill="none"
        stroke="currentColor"
        strokeWidth={1.25}
        strokeLinecap="round"
        style={{ color: spec.accent }}
      >
        {spec.paths}
      </svg>
    </div>
  );
}
