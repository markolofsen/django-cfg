'use client';

import { createContext, useContext } from 'react';

export interface AuthLayoutContextValue {
  /** True when the consumer passed custom children — step headers should be hidden */
  hideHeader: boolean;
  /**
   * True when the brand is already rendered on the media half, so the form
   * header must not repeat it.
   *
   * A statement about the DESKTOP layout only: `fullsplit` drops the media half
   * below 1024px, where the logo above the form is the only brand left. CSS
   * owns that half of the decision on the same breakpoint — see
   * `.auth-header[data-brand-elsewhere]` in `auth.css`.
   */
  hasBrandPanel: boolean;
}

export const AuthLayoutContext = createContext<AuthLayoutContextValue>({
  hideHeader: false,
  hasBrandPanel: false,
});

export const useAuthLayoutContext = (): AuthLayoutContextValue => useContext(AuthLayoutContext);
