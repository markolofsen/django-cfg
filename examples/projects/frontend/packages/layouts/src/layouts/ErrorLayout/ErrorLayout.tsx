/**
 * ErrorLayout - Universal Error Display
 *
 * Minimalist error page with customizable content
 * Works with Next.js error pages (404.tsx, 500.tsx, error.tsx)
 *
 * Usage:
 * ```tsx
 * // pages/404.tsx
 * import { ErrorLayout } from '@djangocfg/layouts/AppLayout';
 *
 * export default function NotFound() {
 *   return (
 *     <ErrorLayout
 *       code="404"
 *       title="Page Not Found"
 *       description="The page you're looking for doesn't exist."
 *     />
 *   );
 * }
 * ```
 */

'use client';

import React from 'react';
import { useRouter } from 'next/router';
import { Button } from '@djangocfg/ui/components';
import { getErrorContent } from './errorConfig';

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
}

/**
 * ErrorLayout Component
 *
 * Clean, minimal error display with semantic colors
 * Standalone layout - doesn't depend on AppLayout context
 *
 * Smart auto-configuration:
 * - Pass only `code` prop and everything is configured automatically
 * - Or override with custom title/description/illustration
 */
export function ErrorLayout({
  code,
  title,
  description,
  actions,
  showDefaultActions = true,
  illustration,
  supportEmail = 'support@example.com',
}: ErrorLayoutProps) {
  const router = useRouter();

  // Auto-configure content from error code if not provided
  const autoContent = code && (!title || !description || !illustration)
    ? getErrorContent(code)
    : null;

  // Use provided values or fall back to auto-generated
  const finalTitle = title || autoContent?.title || 'Error';
  const finalDescription = description || autoContent?.description;
  const finalIllustration = illustration || autoContent?.icon;

  const handleGoBack = () => {
    if (window.history.length > 1) {
      router.back();
    } else {
      router.push('/');
    }
  };

  const handleGoHome = () => {
    router.push('/');
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center space-y-8">
        {/* Error Code */}
        {code && (
          <div className="relative">
            <h1
              className="text-[12rem] font-bold leading-none text-muted/20 select-none"
              aria-hidden="true"
            >
              {code}
            </h1>
          </div>
        )}

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
                className="min-w-[140px]"
              >
                Go Back
              </Button>
              <Button
                variant="default"
                size="lg"
                onClick={handleGoHome}
                className="min-w-[140px]"
              >
                Go Home
              </Button>
            </>
          )}
        </div>

        {/* Additional Info */}
        <div className="pt-8 text-sm text-muted-foreground">
          <p>
            Need help? Contact{' '}
            <a
              href={`mailto:${supportEmail}`}
              className="text-primary hover:underline"
            >
              support
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
