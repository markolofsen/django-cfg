// @vitest-environment jsdom
import React, { act } from 'react';
import { createRoot } from 'react-dom/client';
import { Home, MessageCircle } from 'lucide-react';
import { describe, expect, it, vi } from 'vitest';

import { SidebarViews } from './SidebarViews';

// react-dom + jsdom only: the package declares no testing-library.
(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const views = [
  { id: 'home', label: 'Home', icon: Home, groups: [] },
  { id: 'chat', label: 'Chat', icon: MessageCircle, groups: [] },
];

describe('SidebarViews', () => {
  it('shows the label of the active view only, and reports a pick', () => {
    const onChange = vi.fn();
    const host = document.createElement('div');
    document.body.appendChild(host);
    const root = createRoot(host);
    act(() => root.render(<SidebarViews views={views} active="home" onChange={onChange} />));
    const [home, chat] = Array.from(host.querySelectorAll<HTMLElement>('[role=tab]'));
    expect(home.getAttribute('aria-selected')).toBe('true');
    expect(home.textContent).toBe('Home');
    expect(chat.textContent).toBe('');
    act(() => chat.click());
    expect(onChange).toHaveBeenCalledWith('chat');
    act(() => root.unmount());
    host.remove();
  });
});
