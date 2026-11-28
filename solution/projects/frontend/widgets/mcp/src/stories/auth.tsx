import { useMemo, type ReactNode } from "react";

import { AuthContext, useAuth, type UserProfile } from "@djangocfg/api/auth";

export type StorySession = "signedOut" | "signedIn" | "checking";

/**
 * Gives `useAuth()` one fixed answer, so a story shows a single session state
 * with no backend. The rest of the context is `useAuth`'s own outside-provider
 * default.
 */
export function StoryAuth({ session, children }: { session: StorySession; children: ReactNode }) {
  const base = useAuth();
  const value = useMemo(
    () => ({
      ...base,
      user: session === "signedIn" ? ({ id: 1, email: "jane.cooper@example.com" } as UserProfile) : null,
      isLoading: session === "checking",
      isAuthenticated: session === "signedIn",
      routes: { auth: "/auth", defaultCallback: "/", defaultAuthCallback: "/auth" },
      getToken: () => "story-token",
      saveRedirectUrl: () => {},
    }),
    [base, session],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
