// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it, vi } from 'vitest';

import { AppErrorFallback } from './AppErrorFallback';

vi.mock('@djangocfg/i18n', () => ({
  getT: (key: string) => key,
}));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

function render(props = {}) {
  const host = document.createElement('div');
  act(() => createRoot(host).render(<AppErrorFallback {...props} />));
  return host;
}

describe('AppErrorFallback', () => {
  it('renders exactly one action button', () => {
    const host = render();
    const buttons = host.querySelectorAll('button');
    expect(buttons).toHaveLength(1);
    expect(buttons[0]!.textContent).toBe('layouts.errors.refreshPage');
  });

  it('keeps one button when a support email is shown', () => {
    const host = render({ supportEmail: 'help@example.com' });
    expect(host.querySelectorAll('button')).toHaveLength(1);
    expect(host.querySelector('a[href="mailto:help@example.com"]')).not.toBeNull();
  });
});
