// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import { isChrome } from './chrome-filter';

afterEach(() => {
  document.body.innerHTML = '';
});

function el(html: string): HTMLElement {
  document.body.innerHTML = html;
  return document.body.firstElementChild as HTMLElement;
}

describe('isChrome', () => {
  it('flags landmark chrome tags', () => {
    expect(isChrome(el('<nav>links</nav>'))).toBe(true);
    expect(isChrome(el('<header>top</header>'))).toBe(true);
    expect(isChrome(el('<footer>bottom</footer>'))).toBe(true);
    expect(isChrome(el('<aside>side</aside>'))).toBe(true);
  });

  it('flags landmark chrome roles', () => {
    expect(isChrome(el('<div role="navigation">x</div>'))).toBe(true);
    expect(isChrome(el('<div role="banner">x</div>'))).toBe(true);
  });

  it('flags chrome by class/id name pattern', () => {
    expect(isChrome(el('<div class="sidebar">x</div>'))).toBe(true);
    expect(isChrome(el('<div id="app-navbar">x</div>'))).toBe(true);
    expect(isChrome(el('<div class="breadcrumb">x</div>'))).toBe(true);
  });

  it('never flags content landmarks', () => {
    expect(isChrome(el('<main>content</main>'))).toBe(false);
    expect(isChrome(el('<div role="main">content</div>'))).toBe(false);
  });

  it('does not flag a plain content div', () => {
    expect(isChrome(el('<div class="card-body">data</div>'))).toBe(false);
  });

  it('content-named element wins over an unlikely token', () => {
    // "main-content" contains "content" → not chrome despite layout-ish name
    expect(isChrome(el('<div class="main-content">x</div>'))).toBe(false);
  });
});
