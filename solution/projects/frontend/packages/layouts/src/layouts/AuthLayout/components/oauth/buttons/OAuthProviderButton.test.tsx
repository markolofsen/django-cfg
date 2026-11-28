// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it } from 'vitest';

import { OAUTH_PROVIDERS } from '../providers/registry';
import { OAuthProviderButton } from './OAuthProviderButton';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

function render(state: { loading?: boolean; disabled?: boolean } = {}) {
  const host = document.createElement('div');
  const root = createRoot(host);
  act(() =>
    root.render(
      <>
        <OAuthProviderButton Icon={OAUTH_PROVIDERS.github.Icon} label="GitHub" {...state} />
        <OAuthProviderButton Icon={OAUTH_PROVIDERS.google.Icon} label="Google" {...state} />
      </>,
    ),
  );
  return [...host.querySelectorAll('button')];
}

describe('OAuthProviderButton', () => {
  it('gives every provider the same classes', () => {
    const [a, b] = render();
    expect(a!.className).toBe(b!.className);
    expect(a!.className).toContain('hover:bg-accent');
    expect(a!.querySelector('[data-slot="oauth-icon"] svg')).not.toBeNull();
  });

  it('hides the mark from assistive tech: the label carries the name', () => {
    const [a] = render();
    expect(a!.querySelector('[data-slot="oauth-icon"]')!.getAttribute('aria-hidden')).toBe('true');
    expect(a!.textContent).toBe('GitHub');
  });

  it('marks loading as busy and disabled, without the provider icon', () => {
    for (const b of render({ loading: true })) {
      expect(b.getAttribute('aria-busy')).toBe('true');
      expect(b.disabled).toBe(true);
      expect(b.querySelector('[data-slot="oauth-icon"]')).toBeNull();
    }
  });

  it('disables both the same way', () => {
    for (const b of render({ disabled: true })) expect(b.disabled).toBe(true);
  });

  it('lets a long label wrap instead of clipping it', () => {
    const [a] = render();
    expect(a!.className).toContain('whitespace-normal');
    expect(a!.className).toContain('h-auto');
  });
});
