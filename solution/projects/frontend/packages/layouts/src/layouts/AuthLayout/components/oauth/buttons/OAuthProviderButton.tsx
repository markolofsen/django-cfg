'use client';

import React, { memo } from 'react';

import { Button } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

export interface OAuthProviderButtonProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  /** Provider mark (an svg component); hidden while loading. */
  Icon: React.FC;
  label: string;
  loading?: boolean;
}

/**
 * The one button every OAuth provider uses. Border, height, radius, type,
 * hover, focus, active, disabled and loading are the same for all; only the
 * icon and the label change. Theme tokens only, so it follows light and dark.
 *
 * Full width, at least `--auth-oauth-height` tall (above the 44px touch
 * minimum). The label may wrap to a second line on a narrow screen or in a
 * long translation; the button grows instead of clipping it.
 */
function OAuthProviderButtonRaw({ Icon, label, loading = false, className, ...props }: OAuthProviderButtonProps) {
  return (
    <Button
      type="button"
      variant="outline"
      loading={loading}
      aria-busy={loading || undefined}
      className={cn(
        'auth-oauth-button h-auto min-h-[var(--auth-oauth-height)] w-full gap-2.5 whitespace-normal px-4 py-2 text-center text-sm font-medium shadow-none',
        'hover:bg-accent hover:text-accent-foreground active:bg-accent/70',
        'focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        'disabled:opacity-50',
        className,
      )}
      {...props}
    >
      {!loading && (
        <span data-slot="oauth-icon" className="inline-flex shrink-0" aria-hidden="true">
          <Icon />
        </span>
      )}
      {label}
    </Button>
  );
}

export const OAuthProviderButton = memo(OAuthProviderButtonRaw);
