'use client';

import React, { memo } from 'react';

import { useAppT } from '@djangocfg/i18n';
import { Link } from '@djangocfg/ui-core/components';

import { AUTH } from '../../constants';

export interface AuthBrandPanelProps {
  /** The brand node the app already passes to `AuthLayout` as `logo`. */
  logo: React.ReactNode;
  /** One line under the mark. Omitted by default — the photo carries the mood. */
  tagline?: React.ReactNode;
  className?: string;
}

/**
 * AuthBrandPanel — what the `fullsplit` media half shows when the app gives it
 * nothing.
 *
 * WHY A DEFAULT EXISTS
 *
 * `fullsplit` is the default variant and its left half is a full-height photo.
 * The content over that photo is the `sidebar` slot, which the package left
 * entirely to the consumer — so an app passing `logo` + `background` and no
 * `sidebar` rendered a large photograph with nothing on it, while the brand
 * crowded the form column opposite. Four of the nine call sites were in exactly
 * that state; Storybook never showed it because the story harness supplied a
 * sidebar of its own, so the broken configuration had no story.
 *
 * The brand belongs here rather than above the form: the photo half is the
 * half with room, and a sign-in form reads fastest when it carries only the
 * task. An app that wants something richer (a quote, a testimonial) still
 * passes its own `sidebar` and this never renders.
 *
 * Text is light because it sits on the scrim `fullsplit-shell.css` paints over
 * the photo, not on a theme surface — so it does not follow `--foreground`.
 *
 * The mark is the way OUT. A sign-in screen is otherwise a dead end: arrive by
 * a direct link or get bounced here by an expired session and there is no
 * route back to the site — Back has nowhere to go either. A brand mark in the
 * corner is where people already click to leave, so it is the control to make
 * real rather than a second one to add. It always links to `AUTH.HOME_URL`;
 * nothing to configure.
 */
function AuthBrandPanelRaw({ logo, tagline, className = '' }: AuthBrandPanelProps) {
  /*
   * The label is read from the shared navigation catalogue rather than taken
   * as a prop: it is the same word in all 17 locales, and a `logo` is an
   * opaque node this component cannot read a name out of — a brand that is a
   * bare SVG would otherwise announce as an unnamed link.
   */
  const t = useAppT();

  return (
    <div className={`auth-brand-panel ${className}`}>
      <Link
        href={AUTH.HOME_URL}
        className="auth-brand-panel__mark"
        aria-label={t('layouts.navigation.home')}
      >
        {logo}
      </Link>
      {tagline && <p className="auth-brand-panel__tagline">{tagline}</p>}
    </div>
  );
}

export const AuthBrandPanel = memo(AuthBrandPanelRaw);
