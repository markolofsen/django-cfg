import { readFileSync } from 'node:fs';

import { renderMermaidSVG } from 'beautiful-mermaid';
import { describe, expect, it } from 'vitest';

import { isDiagramComplete, renderDiagram, TINT_TOKENS } from './render';

/**
 * These run with NO jsdom, which is the property that made this dependency the
 * right one: `beautiful-mermaid` touches no DOM, so the renderer is testable at
 * the cheapest rung instead of only in a browser.
 */

describe('renderDiagram', () => {
  it.each([
    ['flowchart', 'graph TD\n  A[Start] --> B{Choice}\n  B -->|yes| C[Do it]'],
    ['sequence', 'sequenceDiagram\n  Alice->>Bob: Hello\n  Bob-->>Alice: Hi'],
    ['state', 'stateDiagram-v2\n  [*] --> Idle\n  Idle --> Running'],
    ['entity relationship', 'erDiagram\n  USER ||--o{ ORDER : places'],
    ['class', 'classDiagram\n  class Foo { +bar() }'],
  ])('renders a %s diagram', (_name, source) => {
    const result = renderDiagram(source);

    expect(result.ok).toBe(true);
    if (result.ok) expect(result.svg).toContain('<svg');
  });

  it('reports an unsupported diagram type instead of throwing', () => {
    // `pie` is outside the parser's coverage. The caller shows the source, so
    // the agent's answer survives a renderer that cannot draw it.
    const result = renderDiagram('pie title X\n  "a" : 30');

    expect(result.ok).toBe(false);
  });

  it('carries theme variables into the SVG so one render serves both themes', () => {
    const result = renderDiagram('graph TD\n  A[Start] --> B[End]');

    expect(result.ok).toBe(true);
    if (result.ok) expect(result.svg).toContain('var(--');
  });
});

describe('isDiagramComplete', () => {
  it.each([
    ['a trailing edge', 'graph TD\n  A[Start] --> '],
    ['an unclosed node label', 'graph TD\n  A[Start] --> B[Choi'],
    ['an unclosed brace', 'graph TD\n  A --> B{Choice'],
    ['nothing yet', '   '],
  ])('holds back on %s', (_name, source) => {
    expect(isDiagramComplete(source)).toBe(false);
  });

  it.each([
    ['a finished flowchart', 'graph TD\n  A[Start] --> B[End]'],
    ['a labelled edge', 'graph TD\n  B -->|yes| C[Do it]'],
    ['a sequence diagram', 'sequenceDiagram\n  Alice->>Bob: Hello'],
  ])('draws %s', (_name, source) => {
    expect(isDiagramComplete(source)).toBe(true);
  });

  it('holds back on a partial source the renderer would happily draw wrong', () => {
    // The whole reason the guard exists: this input does NOT throw, so a
    // try/catch would let a wrong picture through. Both halves asserted
    // together, because either alone reads as a passing test of the other.
    const partial = 'graph TD\n  A[Start] --> ';

    expect(renderDiagram(partial).ok).toBe(true);
    expect(isDiagramComplete(partial)).toBe(false);
  });
});

describe('the dialect a model actually writes', () => {
  // Every case here was measured against a live answer, not invented. The
  // screenshot that found them showed a correct fenced block, correct chrome,
  // and no picture — the source was rejected one line in, and a rejection is
  // indistinguishable from an unsupported diagram from outside.
  it('accepts a semicolon after the header', () => {
    // `show_media`'s own description offers `'graph TD; A-->B'` as its example,
    // so this is the form the agent is being TAUGHT while the parser refused it.
    expect(renderDiagram('graph TD;\n  A[Start] --> B[End]').ok).toBe(true);
  });

  it('accepts the whole single-line form', () => {
    expect(renderDiagram('graph TD; A-->B').ok).toBe(true);
  });

  it('accepts a semicolon on other declarations too', () => {
    expect(renderDiagram('flowchart LR;\n  A[Start] --> B[End]').ok).toBe(true);
  });

  it('renders the exact chart from the live answer', () => {
    const chart = [
      'graph TD;',
      '    A[Начало] --> B{Нужна помощь?}',
      '    B -->|Да| C[Обратиться к сотруднику]',
      '    B -->|Нет| D[Продолжить работу]',
      '    C --> E[Решить проблему]',
      '    D --> E',
      '    E --> F{Все ли ок?}',
      '    F -->|Да| G[Завершить]',
      '    F -->|Нет| B',
    ].join('\n');

    expect(renderDiagram(chart).ok).toBe(true);
  });

  it('still rejects a header that is not a diagram at all', () => {
    // The control. Normalising the header must not turn every string into a
    // diagram — `pie` is still outside the five families the parser covers.
    expect(renderDiagram('pie title Votes;\n  "A" : 10').ok).toBe(false);
  });
});

describe('the diagram follows the THEME, not the model', () => {
  // A model asked for a flowchart routinely paints it. Those hex values used to
  // reach the SVG untouched while the label colour came from the palette, so a
  // pale authored fill carried near-white text in the dark theme.
  const PAINTED = [
    'graph TD;',
    '    A[Начало] --> B{Вопрос}',
    '    B -->|да| C[Решение А]',
    '    B -->|нет| D[Решение B]',
    '    C --> E[Финал]',
    '    D --> E',
    '    style A fill:#90EE90',
    '    style B fill:#FFD700',
    '    style C fill:#87CEEB',
    '    style D fill:#FFA07A',
    '    classDef done fill:#90EE90,stroke:#333',
    '    linkStyle 0 stroke:#ff0000',
  ].join('\n');

  it('keeps no authored colour in the output', () => {
    const result = renderDiagram(PAINTED);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.svg).not.toMatch(/#[0-9A-Fa-f]{6}/);
  });

  it('gives every re-tinted fill its PAIRED text colour', () => {
    // The half that was missing first time round, and the one a screenshot
    // showed rather than a test: a fill without its partner put dark text on
    // saturated blue in the light theme. Contrast is a property of the pair, so
    // a `fill` token appearing without its `-foreground` is the defect.
    const result = renderDiagram(PAINTED);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    for (const token of TINT_TOKENS) {
      if (result.svg.includes(`var(--${token})`)) {
        expect(result.svg).toContain(`var(--${token}-foreground)`);
      }
    }
  });

  it('keeps DISTINCT authored colours distinct', () => {
    // Deleting the directives would also pass "no hex" while flattening the
    // diagram to one colour — the emphasis the author drew has to survive.
    const result = renderDiagram(PAINTED);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const tints = TINT_TOKENS.map((token) => `var(--${token})`).filter((token) =>
      result.svg.includes(token),
    );
    expect(tints.length).toBeGreaterThan(1);
  });

  it('maps the SAME authored colour to the same token', () => {
    // `A` and `E` are both `#90EE90` in the live answer. Two nodes the model
    // painted alike must stay alike, or the re-tint invents a distinction.
    const result = renderDiagram(PAINTED);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const primaries = [...result.svg.matchAll(/fill="var\(--primary\)"/g)];
    expect(primaries.length).toBeGreaterThan(1);
  });

  it('detects an authored colour when the drop is not applied', () => {
    // The control. `beautiful-mermaid` honours these directives, so without it
    // the assertion above would pass on a renderer that ignores them anyway —
    // and prove nothing about our filter.
    //
    // The header carries no semicolon here on purpose: this call bypasses the
    // whole pipeline, so a `graph TD;` would fail on the header normalisation
    // instead and the control would be testing the wrong thing.
    const painted = PAINTED.replace('graph TD;', 'graph TD');

    expect(renderMermaidSVGDirectly(painted)).toMatch(/#[0-9A-Fa-f]{6}/);
  });

  it('still draws every node after the colour lines go', () => {
    // Dropping lines must not drop the diagram: a filter matching too widely
    // would leave an empty-but-valid SVG, which reads as a rendering bug.
    const result = renderDiagram(PAINTED);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    for (const label of ['Начало', 'Вопрос', 'Решение А', 'Финал']) {
      expect(result.svg).toContain(label);
    }
  });

  it('leaves a label containing the word "style" alone', () => {
    // Only whole directive LINES go. Editing inside a label would corrupt the
    // text the agent wrote.
    const result = renderDiagram('graph TD\n  A[style guide] --> B[fill:#fff in prose]');

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.svg).toContain('style guide');
  });
});

/**
 * The library, called with no filtering of ours.
 *
 * The control above needs to prove `beautiful-mermaid` HONOURS an authored
 * colour — otherwise "no hex in the output" is satisfied by a renderer that
 * never emitted one, and our filter is untested.
 */
function renderMermaidSVGDirectly(source: string): string {
  return renderMermaidSVG(source, {
    bg: 'var(--card)',
    fg: 'var(--card-foreground)',
    muted: 'var(--muted-foreground)',
    border: 'var(--border)',
    accent: 'var(--primary)',
    transparent: true,
  });
}

describe('every tint pair states a real figure/ground relationship', () => {
  // Two screenshots found what no assertion did: `--muted` paired with
  // `--muted-foreground` renders grey-on-grey and the label vanishes. The
  // suffix is not a promise — `--muted-foreground` means "de-emphasised text on
  // the ORDINARY ground", not "text on --muted".
  //
  // Read from the shipped theme rather than restated here, so a token whose
  // value moves is caught instead of a copy of it going stale.
  const THEME_DIR = new URL('../../../../packages/ui-core/src/styles/css/theme/', import.meta.url);

  const lightness = (colour: string): number | null => {
    const match = colour.match(/hsl\([\d.]+[^\d.]+[\d.]+%\s+([\d.]+)%/);
    return match?.[1] === undefined ? null : Number(match[1]);
  };

  const tokenValue = (css: string, name: string): string | null =>
    css.match(new RegExp(`--${name}:\\s*([^;]+);`))?.[1]?.trim() ?? null;

  it.each(['light', 'dark'])('keeps every pair legible in the %s theme', (theme) => {
    const css = readFileSync(new URL(theme + '.css', THEME_DIR), 'utf8');

    // The control: the parser must actually find values, or every distance
    // below is computed from null and the loop asserts nothing.
    expect(lightness(tokenValue(css, 'primary') ?? '')).not.toBeNull();

    // Read out of the module rather than restated: a second hand-kept list of
    // the same tokens drifts, and this one already did — a mutation run left
    // `muted` here after the source went back to `accent`, so the gate failed
    // on a pair the renderer no longer uses.
    for (const pair of TINT_TOKENS) {
      const fill = lightness(tokenValue(css, pair) ?? '');
      const text = lightness(tokenValue(css, `${pair}-foreground`) ?? '');
      if (fill === null || text === null) continue;
      expect(Math.abs(fill - text)).toBeGreaterThan(50);
    }
  });
});

describe('boxes a reader would call the same look the same', () => {
  // Found by eye, not by assertion: two peer decision boxes rendered as the
  // same blue but one carried grey text and the other white. The model had
  // written `#4285F4` for one and `#5C9EFF` for the other — hues 217 and 216,
  // one degree apart — and keying on the literal made them two groups.
  const PEERS = [
    'graph TD;',
    '    A[Start] --> B{Ask}',
    '    B -->|yes| C[Branch A]',
    '    B -->|no| D[Branch B]',
    '    style C fill:#5C9EFF',
    '    style D fill:#4285F4',
  ].join('\n');

  it('gives near-identical hues one tint', () => {
    const result = renderDiagram(PEERS);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const labelled = [...result.svg.matchAll(
      /data-label="Branch [AB]"[\s\S]{0,400}?fill="(var\(--[a-z-]+\))"/g,
    )].map((match) => match[1]);

    expect(labelled).toHaveLength(2);
    expect(labelled[0]).toBe(labelled[1]);
  });

  it('still separates hues a reader WOULD call different', () => {
    // The control. Collapsing everything to one tint would satisfy the case
    // above while throwing away the distinction the author drew.
    const distinct = [
      'graph TD;',
      '    A[Ok] --> B[Warn]',
      '    style A fill:#90EE90',
      '    style B fill:#FFD700',
    ].join('\n');

    const result = renderDiagram(distinct);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const fills = [...result.svg.matchAll(
      /data-label="(?:Ok|Warn)"[\s\S]{0,400}?fill="(var\(--[a-z-]+\))"/g,
    )].map((match) => match[1]);

    expect(fills).toHaveLength(2);
    expect(fills[0]).not.toBe(fills[1]);
  });

  it('treats a desaturated colour as grey whatever its hue', () => {
    // `#f5f5f5` has a nominal hue of 0, which would otherwise group it with red.
    const greys = [
      'graph TD;',
      '    A[One] --> B[Two]',
      '    style A fill:#f5f5f5',
      '    style B fill:#eeeeee',
    ].join('\n');

    const result = renderDiagram(greys);

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    const fills = [...result.svg.matchAll(
      /data-label="(?:One|Two)"[\s\S]{0,400}?fill="(var\(--[a-z-]+\))"/g,
    )].map((match) => match[1]);

    expect(fills).toHaveLength(2);
    expect(fills[0]).toBe(fills[1]);
  });
});
