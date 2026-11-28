'use client';

import type { ReactNode } from 'react';

import { useAuth, useCfgRouter } from '@djangocfg/api/auth';
import { Button } from '@djangocfg/ui-core/components';

import { useAssistantCopy } from '../../../i18n/assistant';
import { AssistantLocked } from './assistant-locked';

/** What the signed-out view says and does. Every field is optional: the bundled words and the framework's sign-in page are the defaults. */
export interface AssistantLockOptions {
  title?: string;
  body?: string;
  /** Label of the sign-in button. */
  signInLabel?: string;
  /** The big icon in the centre; absent: a lock. */
  icon?: ReactNode;
  /** Where "Sign in" goes. Absent: the auth route of django-cfg (`useAuth().routes.auth`), after saving the current page as the return address. A host with its own router (locale prefix) passes its own. */
  onSignIn?: () => void;
  /** Replaces the whole view (icon, words, button) with the host's own block. */
  content?: ReactNode;
}

/** `checking`: the client is still reading the session (draw nothing, never flash the lock). `allowed`: signed in. `guest`: not signed in. */
export type AssistantAccess = 'checking' | 'allowed' | 'guest';

/** Who is looking, from the django-cfg auth state (`useAuth`). Outside an `AuthProvider` it reads as `guest`. */
export function useAssistantAccess(): AssistantAccess {
  const { status, isAuthenticated } = useAuth();
  if (isAuthenticated) return 'allowed';
  return status === 'resolving' ? 'checking' : 'guest';
}

/** The way to the sign-in page: saves where the reader was, so the sign-in comes back to the same page, then goes to the framework's auth route. */
export function useSignIn(override?: () => void): () => void {
  const { saveRedirectUrl, routes } = useAuth();
  const router = useCfgRouter();
  return () => {
    if (override) return override();
    saveRedirectUrl(`${window.location.pathname}${window.location.search}`);
    router.push(routes.auth);
  };
}

interface Props {
  lock?: AssistantLockOptions;
  children: ReactNode;
}

/**
 * Shows the assistant's body to a signed-in reader and the signed-out view to everyone else: a big icon, one short reason, a "Sign in" button. `AssistantFrame` and `ChatDock` wrap their body in it with `requireAuth`, so a
 * host writes no wrapper of its own; use it directly for any other surface.
 */
export function AssistantAuthGate({ lock, children }: Props) {
  const access = useAssistantAccess();
  const copy = useAssistantCopy();
  const signIn = useSignIn(lock?.onSignIn);
  if (access === 'allowed') return <>{children}</>;
  if (access === 'checking') return <div className="min-h-0 flex-1" aria-busy="true" />;
  if (lock?.content) return <>{lock.content}</>;
  return (
    <AssistantLocked
      icon={lock?.icon}
      title={lock?.title}
      body={lock?.body}
      action={<Button onClick={signIn}>{lock?.signInLabel ?? copy.signIn}</Button>}
    />
  );
}

/** The body as the frame and the dock draw it: gated only when the host asked for it. */
export function GatedBody({ requireAuth, lock, children }: Props & { requireAuth?: boolean }) {
  return requireAuth ? <AssistantAuthGate lock={lock}>{children}</AssistantAuthGate> : <>{children}</>;
}
