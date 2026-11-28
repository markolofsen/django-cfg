// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import {
  hasIncludeAnnotation,
  hasRedactAnnotation,
  heuristicRedactKind,
} from './heuristics';

afterEach(() => {
  document.body.innerHTML = '';
});

function el(html: string): HTMLElement {
  document.body.innerHTML = html;
  return document.body.firstElementChild as HTMLElement;
}

describe('heuristicRedactKind', () => {
  it('flags a password input', () => {
    expect(heuristicRedactKind(el('<input type="password" />'))).toBe(
      'password',
    );
  });

  it('flags fields named like secrets', () => {
    expect(heuristicRedactKind(el('<input name="api_key" />'))).toBe(
      'sensitive-name',
    );
    expect(heuristicRedactKind(el('<input id="stripe-secret" />'))).toBe(
      'sensitive-name',
    );
    expect(heuristicRedactKind(el('<input class="cvv-field" />'))).toBe(
      'sensitive-name',
    );
  });

  it('flags sensitive autocomplete values', () => {
    expect(
      heuristicRedactKind(el('<input autocomplete="current-password" />')),
    ).toBe('autocomplete');
    expect(
      heuristicRedactKind(el('<input autocomplete="cc-number" />')),
    ).toBe('autocomplete');
  });

  it('does not flag a normal text field', () => {
    expect(heuristicRedactKind(el('<input name="company" />'))).toBeNull();
    expect(heuristicRedactKind(el('<input id="search" />'))).toBeNull();
  });
});

describe('hasRedactAnnotation', () => {
  it('detects data-ai-redact on the element', () => {
    expect(hasRedactAnnotation(el('<div data-ai-redact></div>'))).toBe(true);
  });

  it('detects data-ai-redact on an ancestor', () => {
    document.body.innerHTML = `<div data-ai-redact><span id="c">x</span></div>`;
    expect(hasRedactAnnotation(document.getElementById('c')!)).toBe(true);
  });

  it('is false on an un-annotated element', () => {
    expect(hasRedactAnnotation(el('<div></div>'))).toBe(false);
  });
});

describe('hasIncludeAnnotation', () => {
  it('detects data-ai-include', () => {
    expect(hasIncludeAnnotation(el('<input data-ai-include />'))).toBe(true);
    expect(hasIncludeAnnotation(el('<input />'))).toBe(false);
  });
});
