// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { OTPStep } from './OTPStep';

const form = vi.hoisted(() => ({
  identifier: 'fixture@example.com',
  otp: '1234',
  isLoading: false,
  error: 'Invalid verification code',
  isRateLimited: false,
  rateLimitLabel: '',
  resendSeconds: 0,
  resendLabel: '',
  webmail: null,
  setOtp: vi.fn(),
  handleOTPSubmit: vi.fn(async (event: React.FormEvent) => event.preventDefault()),
  handleResendOTP: vi.fn(),
  handleBackToIdentifier: vi.fn(),
  isAutoSubmittingFromUrl: { current: false },
}));

vi.mock('../../context', () => ({ useAuthFormContext: () => form }));
vi.mock('../../../../utils', () => ({ config: { isDevelopment: true } }));
vi.mock('@djangocfg/api/auth', () => ({
  AUTH_CONSTANTS: { EMAIL_OTP_LENGTH: 4, TOTP_LENGTH: 6, BACKUP_CODE_MAX_LENGTH: 12 },
}));
vi.mock('@djangocfg/i18n', () => ({
  useAppT: () => (key: string) => key === 'layouts.auth.dev.anyCodeWorks'
    ? 'Dev Mode: Any code works'
    : key,
}));
vi.mock('@djangocfg/ui-core/components', () => ({
  Link: ({ children }: { children: React.ReactNode }) => <a href="/">{children}</a>,
  OTPInput: ({ value, onChange }: { value: string; onChange: (value: string) => void }) =>
    <input aria-label="Verification code" value={value} onChange={e => onChange(e.target.value)} />,
}));
vi.mock('../shared', async () => ({
  ...(await import('../shared/AuthContainer')),
  ...(await import('../shared/AuthHeader')),
  ...(await import('../shared/AuthButton')),
  ...(await import('../shared/AuthLink')),
  ...(await import('../shared/AuthError')),
  ...(await import('../shared/AuthOTPInput')),
  WebmailIcon: () => null,
}));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let cleanup: (() => void) | undefined;
afterEach(() => {
  cleanup?.();
  cleanup = undefined;
  form.handleOTPSubmit.mockClear();
});

function render() {
  const host = document.createElement('div');
  document.body.append(host);
  const root = createRoot(host);
  act(() => root.render(<OTPStep />));
  cleanup = () => { act(() => root.unmount()); host.remove(); };
  return host;
}

describe('OTPStep server-owned verification', () => {
  it('does not claim a development frontend can bypass OTP verification', () => {
    const host = render();
    expect(host.querySelector('.auth-dev-notice')).toBeNull();
    expect(host.textContent).not.toContain('Any code works');
  });

  it('keeps the backend error and verification action visible', () => {
    const host = render();
    expect(host.querySelector('[role="alert"]')?.textContent).toContain(form.error);
    const submit = host.querySelector<HTMLButtonElement>('button[type="submit"]')!;
    expect(submit.disabled).toBe(false);
    act(() => submit.click());
    expect(form.handleOTPSubmit).toHaveBeenCalledOnce();
  });
});
