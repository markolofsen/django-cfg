/**
 * Forbidden State
 *
 * Shown when a signed-in user lacks the privilege a route requires
 * (`requireStaff`). Deliberately NOT a redirect to the sign-in form: the
 * session is valid, so signing in again changes nothing — and since the guard
 * saves the current URL first, a redirect would loop straight back here.
 *
 * It renders before any request fires, so the operator sees "wrong account"
 * instead of a screen full of 403s indistinguishable from a backend outage.
 * Sign out is the only action that helps: it lets them switch accounts.
 */

'use client';

import React from 'react';

import { ShieldAlert } from 'lucide-react';

import { useAuth } from '@djangocfg/api/auth';
import { Button } from '@djangocfg/ui-core/components';

export interface ForbiddenStateProps {
  /** Heading. Defaults to a staff-access message. */
  title?: string;
  /** Explanation under the heading. */
  description?: string;
}

export function ForbiddenState({
  title = 'Staff access required',
  description = 'Your account is signed in but does not have staff permissions for this area. Sign out and use a staff account, or ask an administrator to grant access.',
}: ForbiddenStateProps) {
  const { user, logout } = useAuth();

  return (
    <div
      role="alert"
      className="flex min-h-[var(--app-height,100svh)] flex-col items-center justify-center gap-4 p-6 text-center"
    >
      <div className="flex size-12 items-center justify-center rounded-full bg-destructive/10">
        <ShieldAlert className="size-6 text-destructive" />
      </div>

      <div className="space-y-2">
        <h1 className="text-lg font-semibold">{title}</h1>
        <p className="max-w-md text-sm text-muted-foreground">{description}</p>
        {/* Naming the account is the fastest way to spot the usual cause:
            signed in on the right site with the wrong account. */}
        {user?.email && (
          <p className="text-xs text-muted-foreground">
            Signed in as <span className="font-medium">{user.email}</span>
          </p>
        )}
      </div>

      <Button variant="outline" size="sm" onClick={logout}>
        Sign out
      </Button>
    </div>
  );
}
