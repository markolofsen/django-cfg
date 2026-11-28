import { beforeAll, describe, expect, it } from 'vitest';

import { DiagramIncompleteError, diagramPlugin } from './plugin';

const render = (source: string) =>
  diagramPlugin.getMermaid().render('mermaid-test', source);

// The plugin defers the parser behind a dynamic import, so whichever test calls
// it first pays for loading 2.5 MB — enough to push that one case past the
// default timeout while every other case runs in milliseconds. Warming it here
// keeps each test measuring its own behaviour rather than its position in the
// file. It is not a workaround for slowness: the deferral is the FEATURE, and
// `cost.test.ts` is what asserts it is still in place.
beforeAll(async () => {
  await import('./render');
}, 60_000);

describe('the streamdown plugin contract', () => {
  it('declares itself as the mermaid diagram plugin', () => {
    // Streamdown routes a fence by `language` and reads `type`/`name` to place
    // the block. A wrong value here renders nothing and throws nothing.
    expect(diagramPlugin.language).toBe('mermaid');
    expect(diagramPlugin.type).toBe('diagram');
    expect(diagramPlugin.name).toBe('mermaid');
  });

  it('resolves a finished diagram to an SVG', async () => {
    await expect(render('graph TD\n  A[Start] --> B[End]')).resolves.toMatchObject({
      svg: expect.stringContaining('<svg'),
    });
  });

  it('needs no configuring', () => {
    // The contract mirrors the mermaid runtime, which does. Ours reads the
    // theme from CSS variables in the SVG, so a call must be harmless rather
    // than merely unnecessary — streamdown calls it on every download.
    expect(() => diagramPlugin.getMermaid({ theme: 'dark' }).initialize({})).not.toThrow();
  });
});

describe('the guard streamdown does not apply', () => {
  // Streamdown computes whether a fence is still open and forwards it to the
  // code-block branch, but drops it on the mermaid branch and keys its render
  // effect on the chart alone. So every streamed token arrives here.
  it('rejects a half-arrived diagram rather than drawing it', async () => {
    await expect(render('graph TD\n  A[Start] --> ')).rejects.toBeInstanceOf(
      DiagramIncompleteError,
    );
  });

  it('rejects for a REASON the renderer itself would not give', async () => {
    // The control that makes the case above mean something: the renderer does
    // not fail on this input, it returns a wrong picture. Were the guard
    // removed, the promise would resolve and nothing else would notice.
    const { renderDiagram } = await import('./render');
    expect(renderDiagram('graph TD\n  A[Start] --> ').ok).toBe(true);
  });

  it('rejects an unsupported diagram type', async () => {
    // `pie` is outside the parser's five families. Distinct from the partial
    // case: this one is final, and the surface shows the source for both.
    await expect(render('pie title Votes\n  "A" : 10')).rejects.toBeInstanceOf(Error);
  });

  it('rejects empty source instead of resolving to an empty diagram', async () => {
    await expect(render('   \n  ')).rejects.toBeInstanceOf(DiagramIncompleteError);
  });
});
