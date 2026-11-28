/**
 * ErrorLayout - Universal Error Display
 *
 * Minimalist error page with customizable content
 * Works with Next.js error pages (404.tsx, 500.tsx, error.tsx)
 *
 * Usage:
 * ```tsx
 * // app/not-found.tsx
 * import { ErrorLayout } from '@djangocfg/layouts/components';
 *
 * export default function NotFound() {
 *   return <ErrorLayout code={404} supportEmail={settings.contact.email} />;
 * }
 * ```
 */

'use client';

import React, { useEffect, useMemo } from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { canAutoReloadForChunk, isChunkLoadError, reloadForChunkError } from '@djangocfg/ui-core/lib';
import { useAppT } from '@djangocfg/i18n';

import { getErrorContent } from './errorConfig';
import { getErrorIcon } from './errorGlyphs';

export interface ErrorLayoutProps {
  /** Error code (e.g., "404", "500", "403") - if provided, auto-configures title/description/icon */
  code?: string | number;
  /** Error title (auto-generated from code if not provided) */
  title?: string;
  /** Error description (auto-generated from code if not provided) */
  description?: string;
  /** Custom action buttons */
  actions?: React.ReactNode;
  /** Show default actions (back, home) */
  showDefaultActions?: boolean;
  /** Custom illustration/icon (auto-generated from code if not provided) */
  illustration?: React.ReactNode;
  /** Support email for contact link */
  supportEmail?: string;
  /**
   * Public service-status page (e.g. `https://status.example.com`).
   *
   * Rendered as a secondary recovery link beside the support line, answering
   * the question a 500 actually raises — "is it me or is it them?". No default:
   * this package is generic, so the URL belongs to the consuming product, and
   * an app that passes nothing gets exactly the previous behaviour.
   *
   * Pass this ONLY on server-fault pages (500/502/503/504, `global-error`).
   * Not on a 404: telling someone who mistyped a URL to check whether our
   * servers are down is noise, and it teaches people to ignore the link when
   * it finally matters.
   */
  statusUrl?: string;
  /**
   * The caught error (`global-error.tsx` / `error.tsx` receive it as `error`).
   * When it is a stale-chunk failure (ChunkLoadError, cancelled `/_next/static`
   * fetch after a deploy) the page reloads ONCE (sessionStorage loop guard) and
   * renders nothing meanwhile; if the reload already happened, the normal error
   * screen is shown.
   */
  error?: unknown;
}

/**
 * Error glyphs — inline SVG, stroke-based.
 *
 * Inline on purpose: `ErrorLayout` renders inside Next.js error boundaries
 * (`error.tsx`, `not-found.tsx`, `global-error.tsx`). When the root layout
 * or a provider throws, the React tree is partially blown out — external
 * icon libs (`lucide-react` et al.) may fail to resolve because their
 * provider-dependent runtime is gone. Inline SVG has zero dependencies
 * and ships in the same bundle as `ErrorLayout` itself, so it always renders.
 *
 * Design: 1.25px stroke, `currentColor`, no heavy filled circles. The visual
 * weight comes from a soft radial glow on the wrapper, not the icon itself.
 */

/**
 * ErrorLayout Component
 */
export function ErrorLayout({
  code,
  title,
  description,
  actions,
  showDefaultActions = true,
  illustration,
  supportEmail = 'support@example.com',
  statusUrl,
  error,
}: ErrorLayoutProps) {
  const t = useAppT();
  const staleChunk = error !== undefined && isChunkLoadError(error);
  useEffect(() => {
    if (staleChunk) reloadForChunkError();
  }, [staleChunk]);

  const labels = useMemo(() => ({
    goBack: t('layouts.errors.goBack'),
    goHome: t('layouts.errors.goHome'),
    needHelp: t('layouts.errors.needHelp'),
    contactSupport: t('layouts.errors.contactSupport'),
    checkStatus: t('layouts.errors.checkStatus'),
    error: t('layouts.errors.error'),
  }), [t]);

  // Get content (Title/Description) from config. Note: Illustration check removed.
  // The function getErrorContent MUST NOT return React components/functions.
  const autoContent = code && (!title || !description)
    ? getErrorContent(code, t)
    : null;

  // Fallback to auto-generated values
  const finalTitle = title || autoContent?.title || labels.error;
  const finalDescription = description || autoContent?.description;

  // ILLUSTRATION FIX: Use passed prop OR compute the icon locally using getErrorIcon.
  const finalIllustration = illustration ?? getErrorIcon(code);


  const handleGoBack = () => {
    if (document.referrer && document.referrer !== window.location.href) {
      window.location.href = document.referrer;
    } else {
      window.history.back();
      setTimeout(() => window.location.reload(), 100);
    }
  };

  const handleGoHome = () => {
    window.location.href = '/';
  };

  if (staleChunk && canAutoReloadForChunk()) return null;

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-background">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Illustration */}
        {finalIllustration && (
          <div className="flex justify-center py-8">
            {finalIllustration}
          </div>
        )}

        {/* Error Content */}
        <div className="space-y-4">
          <h2 className="text-4xl font-bold text-foreground">
            {finalTitle}
          </h2>

          {finalDescription && (
            <p className="text-lg text-muted-foreground max-w-md mx-auto">
              {finalDescription}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          {/* Custom actions */}
          {actions}

          {/* Default actions */}
          {showDefaultActions && !actions && (
            <>
              <Button
                variant="outline"
                size="lg"
                onClick={handleGoBack}
                style={{ minWidth: '140px', padding: '12px 32px' }}
              >
                {labels.goBack}
              </Button>
              <Button
                variant="default"
                size="lg"
                onClick={handleGoHome}
                style={{ minWidth: '140px', padding: '12px 32px' }}
              >
                {labels.goHome}
              </Button>
            </>
          )}
        </div>

        {/* Additional Info
          *
          * Both links are TERTIARY on purpose. The visitor's one real intent on
          * an error page is to get back to what they were doing, which is what
          * the buttons above serve; a third equal-weight button would make the
          * common case harder in order to serve the rare one. The status link
          * answers a secondary question for whoever is asking it, and is quiet
          * for everyone else. */}
        <div className="pt-8 text-sm text-muted-foreground">
          <p>
            {labels.needHelp}{' '}
            <a
              href={`mailto:${supportEmail}`}
              className="text-primary hover:underline"
            >
              {labels.contactSupport}
            </a>
          </p>

          {statusUrl && (
            <p className="mt-2">
              <a
                href={statusUrl}
                target="_blank"
                rel="noreferrer noopener"
                className="inline-flex items-center gap-1.5 text-primary hover:underline"
              >
                {labels.checkStatus}
                {/* Inline SVG, not an icon package. `ErrorLayout` renders inside
                  * Next.js error boundaries where the tree is partially blown
                  * out and a provider-dependent icon runtime may fail to
                  * resolve — see the glyph note above. */}
                <svg
                  className="size-3.5"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={1.5}
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M14 5h5v5" />
                  <path d="M19 5l-8 8" />
                  <path d="M18 14v4.5A1.5 1.5 0 0 1 16.5 20h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10" />
                </svg>
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

