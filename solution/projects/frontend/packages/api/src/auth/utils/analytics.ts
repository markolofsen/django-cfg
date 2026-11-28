import { isDev } from "./env";
/**
 * Auth analytics — a dependency-free SINK, not an implementation.
 *
 * `@djangocfg/api` cannot depend on `@djangocfg/analytics`: analytics reads auth
 * state (to attribute events to a signed-in user), so importing it here would
 * close a dependency cycle. Instead this module owns the *interface* and lets a
 * real implementation be injected at runtime — `@djangocfg/analytics` calls
 * `setAnalyticsSink()` when its provider mounts.
 *
 * Before this, the object below was a hardcoded stub that console.logged in dev
 * and did NOTHING in production. Every auth event it "tracked" —
 * AUTH_LOGIN_SUCCESS, AUTH_OAUTH_FAIL, AUTH_SESSION_EXPIRED — was silently
 * discarded. The events were fired, the calls looked right, and nothing ever
 * arrived anywhere.
 */

export enum AnalyticsEvent {
  AUTH_OTP_REQUEST = 'auth_otp_request',
  AUTH_LOGIN_SUCCESS = 'auth_login_success',
  AUTH_OTP_VERIFY_FAIL = 'auth_otp_verify_fail',
  AUTH_PASSWORD_LOGIN_FAIL = 'auth_password_login_fail',
  AUTH_SESSION_EXPIRED = 'auth_session_expired',
  AUTH_TOKEN_REFRESH = 'auth_token_refresh',
  AUTH_TOKEN_REFRESH_FAIL = 'auth_token_refresh_fail',
  AUTH_LOGOUT = 'auth_logout',
  AUTH_OAUTH_START = 'auth_oauth_start',
  AUTH_OAUTH_FAIL = 'auth_oauth_fail',
}

export enum AnalyticsCategory {
  AUTH = 'auth',
}

export type AnalyticsEventType = `${AnalyticsEvent}`;
export type AnalyticsCategoryType = `${AnalyticsCategory}`;

/**
 * What an analytics backend can actually carry.
 *
 * GA4 and OpenPanel serialise a property to a scalar; an object or a function
 * arrives as "[object Object]" without erroring anywhere. Declaring the wider
 * `unknown` here promised a forwarding guarantee no implementation keeps, and
 * it made this sink incompatible with `AnalyticsEventProperties` in
 * `@djangocfg/analytics` — the two describe the same channel and must agree.
 * Kept as a local declaration rather than an import: `api` does not depend on
 * `analytics`, and one shared four-member union is not worth that edge.
 */
export type AnalyticsPropertyValue = string | number | boolean | null;

interface AnalyticsEventParams {
  category?: AnalyticsCategoryType;
  label?: string;
  value?: number;
  // Extra dimensions vary per event; the sink only forwards them.
  [key: string]: AnalyticsPropertyValue | undefined;
}

/** What an analytics implementation must provide to receive auth events. */
export interface AnalyticsSink {
  // `| undefined` in the value: an optional dimension that was not supplied
  // reaches the sink as an explicit `undefined`, which every backend already
  // treats as absent. Excluding it would reject the caller below.
  event(
    name: string,
    params?: Record<string, AnalyticsPropertyValue | undefined>,
  ): void;
  setUser(userId: string | null): void;
}

let sink: AnalyticsSink | null = null;

/**
 * Install the real analytics implementation.
 *
 * Called by `@djangocfg/analytics` when its provider mounts. Pass `null` to
 * uninstall (on unmount), so a torn-down provider does not keep receiving events.
 */
export function setAnalyticsSink(next: AnalyticsSink | null): void {
  sink = next;
}

export const Analytics = {
  /** Track an auth event. Delivered to the installed sink, if any. */
  event(eventName: AnalyticsEventType, params?: AnalyticsEventParams) {
    if (sink) {
      sink.event(eventName, params);
      return;
    }
    // No sink installed: the app is not using @djangocfg/analytics. Say so in
    // dev rather than pretending the event went somewhere.
    if (isDev) {
      console.log('[Analytics:no-sink]', eventName, params);
    }
  },

  /** Attach the signed-in user. Pass null on logout. */
  setUser(userId: string | null) {
    if (sink) {
      sink.setUser(userId);
      return;
    }
    if (isDev) {
      console.log('[Analytics:no-sink] Set user:', userId);
    }
  },
};
