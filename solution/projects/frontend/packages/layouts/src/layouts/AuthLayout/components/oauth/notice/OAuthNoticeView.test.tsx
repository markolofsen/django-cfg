// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it, vi } from 'vitest';

import { OAuthNoticeView, type OAuthNoticeViewProps } from './OAuthNoticeView';

vi.mock('@djangocfg/i18n', () => ({
  useAppT: () => (key: string, params?: Record<string, string>) =>
    params ? `${key} ${JSON.stringify(params)}` : key,
}));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

function render(props: Partial<OAuthNoticeViewProps> = {}) {
  const host = document.createElement('div');
  document.body.append(host);
  const root = createRoot(host);
  const handlers = { onDismiss: vi.fn(), onRetry: vi.fn() };
  act(() => root.render(<OAuthNoticeView provider="github" code="invalid_state" {...handlers} {...props} />));
  return { host, ...handlers, buttons: () => [...host.querySelectorAll('button')] };
}

describe('OAuthNoticeView', () => {
  it('says nothing for a cancelled sign-in', () => {
    expect(render({ code: 'cancelled' }).host.innerHTML).toBe('');
  });

  it('is a polite status, not an alert', () => {
    expect(render().host.querySelector('[role="status"]')).not.toBeNull();
  });

  it('offers a retry that runs the provider again', () => {
    const { buttons, onRetry } = render();
    const retry = buttons().find((b) => b.textContent!.includes('notice.retry'))!;
    act(() => retry.click());
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it('offers no retry when the provider has no button, and never a button for email', () => {
    const { buttons } = render({ onRetry: undefined });
    expect(buttons().some((b) => b.textContent!.includes('notice.retry'))).toBe(false);
    expect(render({ code: 'link_not_allowed' }).buttons().map((b) => b.getAttribute('aria-label'))).toEqual([
      'layouts.auth.oauth.notice.dismiss',
    ]);
  });

  it('uses one layout for every kind of notice: icon, text, close', () => {
    for (const code of ['invalid_state', 'link_not_allowed', 'origin_not_allowed', 'rate_limited'] as const) {
      const { host } = render({ code, origin: 'https://app.example.com' });
      const notice = host.querySelector('.auth-oauth-notice')!;
      expect(notice.querySelector('.auth-oauth-notice-icon')).not.toBeNull();
      expect(notice.querySelector('.auth-oauth-notice-text .auth-oauth-notice-body')).not.toBeNull();
      expect(notice.querySelector('.auth-oauth-notice-close')!.getAttribute('aria-label')).toBe(
        'layouts.auth.oauth.notice.dismiss',
      );
    }
  });

  it('closes with the dismiss button and with Escape', () => {
    const { buttons, onDismiss } = render();
    act(() => buttons().find((b) => b.getAttribute('aria-label') === 'layouts.auth.oauth.notice.dismiss')!.click());
    act(() => {
      document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
    });
    expect(onDismiss).toHaveBeenCalledTimes(2);
  });

  it('gives a developer the origin to allow when the origin is refused', () => {
    const { host } = render({ code: 'origin_not_allowed', origin: 'https://app.example.com' });
    expect(host.querySelector('.auth-oauth-hint')!.textContent).toContain('"origin":"https://app.example.com"');
    expect(host.querySelector('.auth-oauth-hint')!.textContent).toContain('"id":"github"');
  });

  it('shows no developer hint for other failures', () => {
    expect(render({ origin: 'https://app.example.com' }).host.querySelector('.auth-oauth-hint')).toBeNull();
  });
});
