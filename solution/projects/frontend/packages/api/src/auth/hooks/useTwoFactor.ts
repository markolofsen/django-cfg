'use client';

import {
  useTwoFactorVerify,
  type UseTwoFactorVerifyOptions,
  type UseTwoFactorVerifyReturn,
} from './useTwoFactorVerify';
import {
  useTwoFactorSetup,
  type TwoFactorSetupData,
  type UseTwoFactorSetupOptions,
  type UseTwoFactorSetupReturn,
} from './useTwoFactorSetup';
import {
  useTwoFactorStatus,
  type TwoFactorDevice,
  type UseTwoFactorStatusReturn,
} from './useTwoFactorStatus';

export interface UseTwoFactorOptions {
  /** Options for the login-time verification namespace */
  verify?: UseTwoFactorVerifyOptions;
  /** Options for the setup (enable) namespace */
  setup?: UseTwoFactorSetupOptions;
}

export interface UseTwoFactorReturn {
  /** Verify a 2FA challenge during login (TOTP / backup code). */
  verify: UseTwoFactorVerifyReturn;
  /** Enable 2FA — QR provisioning → confirm → backup codes. */
  setup: UseTwoFactorSetupReturn;
  /** Read device list / enabled flag and disable 2FA. */
  status: UseTwoFactorStatusReturn;
}

/**
 * Single entry point for all two-factor authentication flows.
 *
 * The three concerns — **verify** (login), **setup** (enable) and **status**
 * (manage/disable) — are distinct verbs over the same `CfgTotp*` API, so each
 * is exposed as its own namespace with an independent loading/error surface:
 *
 * @example
 * ```tsx
 * const two = useTwoFactor({ verify: { redirectUrl: '/dashboard' } });
 *
 * await two.verify.verifyTOTP(sessionId, code); // login
 * await two.setup.startSetup('My iPhone');       // enable
 * await two.status.fetchStatus();                // manage
 * ```
 *
 * Consumers that only need one concern can compose the underlying hooks
 * directly (`useTwoFactorVerify` / `useTwoFactorSetup` / `useTwoFactorStatus`),
 * all re-exported alongside this one, to avoid mounting the others' state.
 */
export const useTwoFactor = (options: UseTwoFactorOptions = {}): UseTwoFactorReturn => {
  const verify = useTwoFactorVerify(options.verify);
  const setup = useTwoFactorSetup(options.setup);
  const status = useTwoFactorStatus();

  return { verify, setup, status };
};

// Namespaced sub-hooks — use directly when only one concern is needed.
export {
  useTwoFactorVerify,
  useTwoFactorSetup,
  useTwoFactorStatus,
  type UseTwoFactorVerifyOptions,
  type UseTwoFactorVerifyReturn,
  type UseTwoFactorSetupOptions,
  type UseTwoFactorSetupReturn,
  type UseTwoFactorStatusReturn,
  type TwoFactorSetupData,
  type TwoFactorDevice,
};
