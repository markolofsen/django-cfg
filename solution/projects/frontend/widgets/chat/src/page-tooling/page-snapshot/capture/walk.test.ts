// @vitest-environment jsdom
import { afterEach, describe, expect, it } from 'vitest';

import { walkDOM } from './walk';
import type { CSTInteractiveNode } from '../cst/types';
import { isContainerNode, isInteractiveNode } from '../cst/types';

afterEach(() => {
  document.body.innerHTML = '';
});

/** Flatten a CST subtree to all interactive nodes. */
function allInteractive(root: HTMLElement) {
  const { children } = walkDOM(root);
  const out: CSTInteractiveNode[] = [];
  const visit = (nodes: ReturnType<typeof walkDOM>['children']) => {
    for (const n of nodes) {
      if (isInteractiveNode(n)) out.push(n);
      else if (isContainerNode(n) || n.type === 'root') visit(n.children);
    }
  };
  visit(children);
  return out;
}

describe('walkDOM', () => {
  it('captures interactive elements with refs', () => {
    document.body.innerHTML = `
      <form>
        <label for="c">Company</label>
        <input id="c" type="text" value="Acme" />
        <button type="submit">Save</button>
      </form>`;
    const result = walkDOM(document.body);

    const interactive = allInteractive(document.body);
    expect(interactive).toHaveLength(2);
    expect(interactive[0]?.ref).toBe('@e1');
    expect(interactive[1]?.ref).toBe('@e2');
    expect(result.refMap.size).toBe(2);
  });

  it('resolves accessible name from a <label for>', () => {
    document.body.innerHTML = `
      <label for="c">Company Name</label>
      <input id="c" type="text" />`;
    const [input] = allInteractive(document.body);
    expect(input?.name).toBe('Company Name');
  });

  it('captures input value and role', () => {
    document.body.innerHTML = `<input type="search" value="hello" />`;
    const [input] = allInteractive(document.body);
    expect(input?.role).toBe('searchbox');
    expect(input?.value).toBe('hello');
  });

  it('captures checkbox checked state, not value', () => {
    document.body.innerHTML = `<input type="checkbox" checked />`;
    const [cb] = allInteractive(document.body);
    expect(cb?.role).toBe('checkbox');
    expect(cb?.checked).toBe(true);
    expect(cb?.value).toBeUndefined();
  });

  it('captures disabled and required state', () => {
    document.body.innerHTML = `
      <input type="text" disabled required />`;
    const [input] = allInteractive(document.body);
    expect(input?.disabled).toBe(true);
    expect(input?.required).toBe(true);
  });

  it('excludes chrome (nav) from the walk', () => {
    document.body.innerHTML = `
      <nav><a href="/x">Nav Link</a></nav>
      <main><button>Real Button</button></main>`;
    const interactive = allInteractive(document.body);
    expect(interactive).toHaveLength(1);
    expect(interactive[0]?.name).toBe('Real Button');
  });

  it('skips script/style tags', () => {
    document.body.innerHTML = `
      <div>
        <script>var x = 1;</script>
        <style>.a{}</style>
        <p>Visible text</p>
      </div>`;
    const { children } = walkDOM(document.body);
    const json = JSON.stringify(children);
    expect(json).not.toContain('var x');
    expect(json).not.toContain('.a{}');
    expect(json).toContain('Visible text');
  });

  it('emits a placeholder for canvas/svg instead of descending', () => {
    document.body.innerHTML = `
      <canvas aria-label="Sales chart"></canvas>`;
    const { children } = walkDOM(document.body);
    expect(JSON.stringify(children)).toContain('[Sales chart]');
  });

  it('applies the redaction hook to values and text', () => {
    document.body.innerHTML = `
      <input type="text" value="secret-value" />
      <p>plain paragraph</p>`;
    const { children } = walkDOM(document.body, {
      redactValue: (v, ctx) => (ctx.kind === 'value' ? '‹redacted›' : v),
    });
    const json = JSON.stringify(children);
    expect(json).toContain('‹redacted›');
    expect(json).not.toContain('secret-value');
    expect(json).toContain('plain paragraph');
  });

  it('builds a container node for a form', () => {
    document.body.innerHTML = `<form><button>Go</button></form>`;
    const { children } = walkDOM(document.body);
    const form = children.find(isContainerNode);
    expect(form?.role).toBe('form');
  });

  it('honors maxNodes as a safety valve', () => {
    document.body.innerHTML = `<div><div><div><button>x</button></div></div></div>`;
    const result = walkDOM(document.body, { maxNodes: 2 });
    expect(result.nodesVisited).toBeLessThanOrEqual(2);
  });
});
