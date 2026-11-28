import * as React from 'react';
import { renderToString } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { Button, ButtonLink } from './index';

// Node environment: no window, so `useCanHover` is false, the same as the first client render and a phone.
describe('Button tooltip prop', () => {
  it('draws the bare button where the device cannot hover (server render, phones)', () => {
    const html = renderToString(<Button tooltip={{ content: 'Open', hotkey: 'mod+j' }}>Go</Button>);
    expect(html).toBe(renderToString(<Button>Go</Button>));
  });

  it('adds no wrapper for a disabled button on such a device either', () => {
    const html = renderToString(<Button disabled tooltip="Nope">Go</Button>);
    expect(html).not.toContain('<span');
  });

  it('ButtonLink takes the same prop', () => {
    const html = renderToString(<ButtonLink href="/a" tooltip="Home">Home</ButtonLink>);
    expect(html).toBe(renderToString(<ButtonLink href="/a">Home</ButtonLink>));
  });
});
