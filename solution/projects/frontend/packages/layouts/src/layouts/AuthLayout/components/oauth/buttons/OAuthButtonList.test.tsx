// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { describe, expect, it, vi } from 'vitest';

import { OAuthButtonList, type OAuthButtonListProps } from './OAuthButtonList';

vi.mock('@djangocfg/i18n', () => ({
  useAppT: () => (key: string, params?: Record<string, string>) =>
    key === 'layouts.auth.identifier.oauth.continueWith' ? `Continue with ${params?.provider}` : key,
}));

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

function render(props: Partial<OAuthButtonListProps> = {}) {
  const host = document.createElement('div');
  const root = createRoot(host);
  const onSelect = vi.fn();
  act(() => root.render(<OAuthButtonList providers={['github', 'google']} onSelect={onSelect} {...props} />));
  return { group: host.querySelector('[role="group"]')!, buttons: [...host.querySelectorAll('button')], onSelect };
}

describe('OAuthButtonList', () => {
  it('renders one named button per provider inside a labelled group', () => {
    const { group, buttons } = render();
    expect(group.getAttribute('aria-label')).toBe('layouts.auth.identifier.oauth.groupLabel');
    expect(buttons.map((b) => b.textContent)).toEqual(['Continue with GitHub', 'Continue with Google']);
  });

  it('reports the clicked provider', () => {
    const { buttons, onSelect } = render();
    act(() => buttons[1]!.click());
    expect(onSelect).toHaveBeenCalledExactlyOnceWith('google');
  });

  it('shows progress on one provider and disables the other', () => {
    const { buttons } = render({ loadingProvider: 'github' });
    expect(buttons[0]!.getAttribute('aria-busy')).toBe('true');
    expect(buttons[0]!.disabled).toBe(true);
    expect(buttons[1]!.getAttribute('aria-busy')).toBeNull();
    expect(buttons[1]!.disabled).toBe(true);
  });

  it('disables everything when told to, and nothing otherwise', () => {
    expect(render({ disabled: true }).buttons.every((b) => b.disabled)).toBe(true);
    expect(render().buttons.every((b) => !b.disabled)).toBe(true);
  });

  it('renders nothing but the group for an empty list', () => {
    expect(render({ providers: [] }).buttons).toEqual([]);
  });
});
