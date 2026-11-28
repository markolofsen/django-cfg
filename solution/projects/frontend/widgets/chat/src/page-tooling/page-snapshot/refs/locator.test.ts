// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import { computeLocator, resolveLocator } from './locator';

afterEach(() => {
  document.body.innerHTML = '';
});

describe('computeLocator', () => {
  it('builds an id selector when the element has a unique id', () => {
    const el = document.createElement('button');
    el.id = 'submit-btn';
    el.textContent = 'Submit';
    document.body.appendChild(el);

    const locator = computeLocator(el, 'button');
    expect(locator.selector).toBe('#submit-btn');
    expect(locator.role).toBe('button');
    expect(locator.name).toBe('Submit');
    expect(locator.tag).toBe('button');
  });

  it('prefers data-testid over a structural path', () => {
    const el = document.createElement('a');
    el.setAttribute('data-testid', 'nav-home');
    el.textContent = 'Home';
    document.body.appendChild(el);

    expect(computeLocator(el, 'link').selector).toBe('a[data-testid="nav-home"]');
  });

  it('falls back to a structural path when no stable attribute exists', () => {
    document.body.innerHTML = '<section><div></div><a>One</a><a>Two</a></section>';
    const second = document.body.querySelectorAll('a')[1] as HTMLElement;

    const locator = computeLocator(second, 'link');
    expect(locator.selector).toContain('nth-of-type');
    // The structural path must re-find the same element.
    expect(document.querySelector(locator.selector)).toBe(second);
  });
});

describe('resolveLocator', () => {
  it('resolves via selector when structure is intact', () => {
    const el = document.createElement('button');
    el.id = 'go';
    el.textContent = 'Go';
    document.body.appendChild(el);

    const locator = computeLocator(el, 'button');
    expect(resolveLocator(locator)).toBe(el);
  });

  it('resolves by role + name when the selector breaks', () => {
    // Capture with a structural path (no stable attribute).
    document.body.innerHTML = '<div><a>Browse Catalog</a></div>';
    const original = document.body.querySelector('a') as HTMLElement;
    const locator = computeLocator(original, 'link');

    // Re-render shifts the element: extra wrapper + sibling inserted, so
    // the captured nth-of-type path no longer matches it.
    document.body.innerHTML =
      '<header><nav><span>x</span><a>Browse Catalog</a></nav></header>';

    const resolved = resolveLocator(locator);
    expect(resolved).not.toBeNull();
    expect(resolved?.textContent).toBe('Browse Catalog');
  });

  it('returns null when the element is genuinely gone', () => {
    const el = document.createElement('a');
    el.textContent = 'Vanishing Link';
    document.body.appendChild(el);
    const locator = computeLocator(el, 'link');

    document.body.innerHTML = '';
    expect(resolveLocator(locator)).toBeNull();
  });

  /**
   * Rows are the case where role + name cannot decide: every row's button is
   * named "Delete". Position used to answer instead, and position names a
   * SLOT — delete a row and the slot holds the next row's button, still a
   * single match, so nothing detects it. Three refs into a three-row table
   * resolved to Beta, Gamma and Beta after the first row was removed.
   */
  describe('same-named peers in repeated rows', () => {
    const ROWS =
      '<table><tbody>' +
      '<tr><td>Alpha</td><td><button>Delete</button></td></tr>' +
      '<tr><td>Beta</td><td><button>Delete</button></td></tr>' +
      '<tr><td>Gamma</td><td><button>Delete</button></td></tr>' +
      '</tbody></table>';

    const rowOf = (el: HTMLElement | null): string =>
      el?.closest('tr')?.querySelector('td')?.textContent ?? 'null';

    const locatorsForRows = () => {
      document.body.innerHTML = ROWS;
      return Array.from(document.querySelectorAll('button')).map((b) =>
        computeLocator(b as HTMLElement, 'button'),
      );
    };

    it('each ref keeps its own row when nothing moves', () => {
      const [alpha, beta, gamma] = locatorsForRows();
      expect(rowOf(resolveLocator(alpha!))).toBe('Alpha');
      expect(rowOf(resolveLocator(beta!))).toBe('Beta');
      expect(rowOf(resolveLocator(gamma!))).toBe('Gamma');
    });

    it('survives React recreating every node', () => {
      const [alpha, , gamma] = locatorsForRows();
      // Re-parsing the same markup gives brand-new nodes with identical
      // structure — what React does on a re-render.
      const body = document.querySelector('tbody')!;
      const markup = body.innerHTML;
      body.replaceChildren();
      body.innerHTML = markup;

      expect(rowOf(resolveLocator(alpha!))).toBe('Alpha');
      expect(rowOf(resolveLocator(gamma!))).toBe('Gamma');
    });

    it('follows the surviving rows when one is deleted, and refuses the deleted one', () => {
      const [alpha, beta, gamma] = locatorsForRows();
      document.querySelector('tbody tr')!.remove();

      // The deleted row's ref must be null, not a live sibling: a wrong
      // element is worse than a missing one because nothing reports it.
      expect(resolveLocator(alpha!)).toBeNull();
      expect(rowOf(resolveLocator(beta!))).toBe('Beta');
      expect(rowOf(resolveLocator(gamma!))).toBe('Gamma');
    });
  });

  it('matches an ARIA-roled element by role + name', () => {
    document.body.innerHTML =
      '<div role="button" aria-label="Open menu">≡</div>';
    const original = document.body.firstElementChild as HTMLElement;
    const locator = computeLocator(original, 'button');

    // Recreate the node — same role + accessible name, new identity.
    document.body.innerHTML =
      '<span></span><div role="button" aria-label="Open menu">≡</div>';
    const fresh = document.body.querySelectorAll('[role="button"]')[0];

    expect(resolveLocator(locator)).toBe(fresh);
  });
});
