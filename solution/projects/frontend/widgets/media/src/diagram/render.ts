// Mermaid source → SVG string. No React, no DOM.
//
// May import: beautiful-mermaid.

import { renderMermaidSVG } from 'beautiful-mermaid';

/**
 * The palette, as CSS variables rather than resolved colours.
 *
 * `beautiful-mermaid` writes these straight into the SVG's `fill`/`stroke`, so
 * passing variables makes one rendered diagram correct in BOTH themes and
 * follow a theme switch with no re-render. Resolving them here would need
 * `getComputedStyle`, which is a DOM call in a module whose whole value is that
 * it does not need one.
 */
const PALETTE = {
  bg: 'var(--card)',
  fg: 'var(--card-foreground)',
  muted: 'var(--muted-foreground)',
  border: 'var(--border)',
  accent: 'var(--primary)',
  transparent: true,
} as const;

export type DiagramResult =
  | { readonly ok: true; readonly svg: string }
  | { readonly ok: false; readonly error: string };

/**
 * Render a diagram, or say why not.
 *
 * A Result rather than a throw because BOTH outcomes are renderable: an
 * unsupported diagram type falls back to its own source, which is still the
 * answer the agent gave. `pie` is the measured example — the parser covers
 * flowchart, sequence, state, class and ER, and rejects the rest by header.
 */
export function renderDiagram(source: string): DiagramResult {
  try {
    return { ok: true, svg: renderMermaidSVG(retintToTheme(normalize(source)), PALETTE) };
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : String(error) };
  }
}

/** A `style`/`classDef`/`linkStyle` line, which is where authored colour lives. */
const COLOUR_DIRECTIVE = /^\s*(style|classDef|linkStyle)\s+/;

/**
 * A literal colour: hex, `rgb(...)`, `hsl(...)`, or a CSS named colour.
 *
 * Named colours are matched as a bare word after `fill:`/`stroke:` rather than
 * against a list of 148 names — the position is what makes it a colour, and a
 * list would go stale the moment a model reaches for one it lacks.
 */
const LITERAL_COLOUR = /(fill|stroke|color)\s*:\s*(#[0-9A-Fa-f]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\)|[A-Za-z]+)/g;

/**
 * Which token PAIR a literal fill becomes.
 *
 * A fill alone is half a decision. The design system ships every surface token
 * with its own foreground precisely because contrast is a property of the
 * PAIR — `--primary` is a saturated blue in both themes while
 * `--card-foreground` flips, so a fill taken without its partner puts dark text
 * on that blue in the light theme and reads as unstyled.
 *
 * Three pairs, cycled by order of appearance, so a diagram that painted its
 * nodes differently still READS differently — the distinction the author drew
 * survives even though their exact hue does not. All six are semantic tokens,
 * so both themes stay correct and a theme switch needs no re-render.
 *
 * `--primary` leads because a model's first colour is usually its emphasis.
 *
 * `--muted` is deliberately NOT among them, and the reason is that its
 * `-foreground` does not mean what the others' do. Measured as lightness
 * distance INSIDE each pair against the shipped theme:
 *
 * | pair | light | dark |
 * |---|---|---|
 * | `primary` | 55.0 | 51.0 |
 * | `secondary` | 89.5 | 78.6 |
 * | `accent` | 84.5 | 73.0 |
 * | `muted` | **47.0** | **47.2** |
 *
 * `--muted-foreground` is the token for de-emphasised text on the ORDINARY
 * ground, not for text sitting on `--muted` — so a node tinted with it renders
 * grey-on-grey and its label disappears in both themes. Every other pair states
 * a real figure/ground relationship.
 *
 * `--accent` is pale against the page in the light theme, which is what the
 * stroke is for: the outline gives the shape an edge the fill alone does not.
 */
const FILL_PAIRS = [
  { fill: 'var(--primary)', text: 'var(--primary-foreground)' },
  { fill: 'var(--secondary)', text: 'var(--secondary-foreground)' },
  { fill: 'var(--accent)', text: 'var(--accent-foreground)' },
] as const;

type FillPair = (typeof FILL_PAIRS)[number];

/**
 * The token NAMES behind `FILL_PAIRS`, for the gate that measures their
 * contrast against the shipped theme.
 *
 * Derived rather than restated: a second hand-kept copy of this list drifted
 * within a day of being written, leaving the gate asserting over a pair the
 * renderer had stopped using.
 */
export const TINT_TOKENS = FILL_PAIRS.map(({ fill }) =>
  fill.replace(/^var\(--|\)$/g, ''),
);

/** An outline is structure, not emphasis, so every stroke follows one token. */
const STROKE_TOKEN = 'var(--border)';

/**
 * Re-tint the model's own colours onto theme tokens.
 *
 * A model asked for a flowchart routinely paints it — `style A fill:#90EE90`,
 * a yellow decision diamond, a salmon branch. Those literals reach the SVG
 * untouched while the frame and the LABEL come from the palette above, so the
 * two halves answer to different themes: pale fills carry light-theme
 * assumptions, and the label on them is `var(--card-foreground)`, near-white in
 * the dark theme. White text on pale green.
 *
 * The palette cannot win that by being better chosen — one side is a literal on
 * the shape, the other a variable on the text, so whichever theme is active one
 * of the two is wrong.
 *
 * DELETING the directives fixes the contrast and flattens the diagram to one
 * colour, which throws away a distinction the author drew. Measured instead:
 * `style A fill:var(--primary)` passes through the parser intact. So each
 * distinct authored colour is mapped to a distinct semantic token, in order of
 * appearance and consistently across the diagram — the emphasis survives, the
 * hue does not, and both themes stay correct with no re-render.
 *
 * Only inside a `style`/`classDef`/`linkStyle` LINE, never `fill:` wherever it
 * appears: a node label may contain the word, and editing inside a label would
 * corrupt the text the agent wrote.
 */
function retintToTheme(source: string): string {
  if (!source.includes('style') && !source.includes('classDef')) return source;

  // One counter across the whole diagram, so the SAME authored fill maps to the
  // same token everywhere — two nodes the model painted alike stay alike.
  const assigned = new Map<string, FillPair>();

  return source
    .split('\n')
    .map((line) => (COLOUR_DIRECTIVE.test(line) ? retint(line, assigned) : line))
    .join('\n');
}

/**
 * Rewrite one directive's literal colours onto theme tokens.
 *
 * A rewritten `fill` carries its partner `color` along, because the authored
 * line rarely states one: the model picked a pale fill and left the text at the
 * default, which is correct for its own palette and wrong for ours.
 */
function retint(line: string, assigned: Map<string, FillPair>): string {
  // Resolved from the FILL first, so an authored `color:` in the same directive
  // becomes this fill's partner. Reading them in source order instead lets a
  // `color:` that precedes — or simply arrives before the fill is known — draw
  // the next tint in the cycle, which is a pair from a different node: measured
  // as `fill="var(--primary)"` carrying `var(--secondary-foreground)`, grey
  // text on saturated blue.
  // Undefined when the directive sets no fill — a `linkStyle 0 stroke:#f00`
  // colours an EDGE and has no box to pair with. Its stroke is still ours to
  // take: left alone, a model's red arrow stays red in both themes, which was
  // the one literal that survived the first version of this.
  const pair = pairFor(line, assigned);

  const rewritten = line.replace(LITERAL_COLOUR, (whole, property: string, value: string) => {
    // `fill:none` and `stroke:transparent` are structural, not palette — a node
    // deliberately left hollow must stay hollow.
    if (value === 'none' || value === 'transparent') return whole;
    if (property === 'stroke') return `${property}:${STROKE_TOKEN}`;
    if (pair === undefined) return whole;
    // An authored `color:` is honoured as the pair's text, not as its own
    // choice — a literal there has the same contrast problem as a literal fill.
    return `${property}:${property === 'color' ? pair.text : pair.fill}`;
  });

  if (pair === undefined) return rewritten;
  return /(^|,)\s*color\s*:/.test(rewritten) ? rewritten : `${rewritten},color:${pair.text}`;
}

/**
 * The token pair this directive's fill maps to, or undefined when it sets none.
 *
 * Keyed on the colour's HUE FAMILY, not its exact value. A model painting two
 * peer nodes reaches for two neighbouring blues without meaning a distinction —
 * measured on a live answer, `#4285F4` and `#5C9EFF` are hues 217 and 216, one
 * degree apart and identical to a reader. Keyed on the literal, those became
 * two different tokens and the two peer boxes rendered with different label
 * colours, which is a difference the diagram never claimed.
 *
 * So near hues collapse to one pair, and genuinely different ones (green 120
 * against yellow 51) still separate.
 */
function pairFor(line: string, assigned: Map<string, FillPair>): FillPair | undefined {
  const fill = new RegExp(LITERAL_COLOUR.source, 'g')
    .exec(line.replace(/(stroke|color)\s*:/g, 'x:'))
    ?.[2];
  if (fill === undefined || fill === 'none' || fill === 'transparent') return undefined;

  const key = hueFamily(fill);
  const known = assigned.get(key);
  if (known !== undefined) return known;

  const pair = FILL_PAIRS[assigned.size % FILL_PAIRS.length] as FillPair;
  assigned.set(key, pair);
  return pair;
}

/** How far apart two hues must sit to read as different colours, in degrees. */
const HUE_BUCKET = 30;

/** Below this saturation a colour reads as grey, whatever its hue says. */
const GREY_SATURATION = 15;

/**
 * A key that groups colours a reader would call the same.
 *
 * Hex only: a named colour or an `rgb()` would need a parser this module has no
 * reason to carry, and falling back to the literal is correct for them — an
 * exact repeat still groups, and only near-misses lose their grouping.
 */
function hueFamily(colour: string): string {
  const hex = /^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.exec(colour.trim())?.[1];
  if (hex === undefined) return colour.toLowerCase();

  const full = hex.length === 3 ? [...hex].map((c) => c + c).join('') : hex;
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(full.slice(i, i + 2), 16) / 255) as [
    number,
    number,
    number,
  ];

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const span = max - min;
  const lightness = (max + min) / 2;
  const saturation = span === 0 ? 0 : span / (1 - Math.abs(2 * lightness - 1));
  if (saturation * 100 < GREY_SATURATION) return 'grey';

  let hue: number;
  if (max === r) hue = ((g - b) / span) % 6;
  else if (max === g) hue = (b - r) / span + 2;
  else hue = (r - g) / span + 4;
  hue *= 60;
  if (hue < 0) hue += 360;

  return `hue-${Math.round(hue / HUE_BUCKET)}`;
}

/**
 * Accept the dialect models actually write.
 *
 * `graph TD;` is valid mermaid and the parser rejects it — it matches the
 * header exactly and a trailing `;` misses. Semicolons ELSEWHERE are already
 * fine (`A --> B;` parses), so the gap is one line wide and invisible from the
 * source: a diagram written the ordinary way simply never draws.
 *
 * Worth normalising rather than reporting, because we are the ones teaching the
 * dialect — `show_media`'s own description offers `'graph TD; A-->B'` as its
 * example, so the agent is being shown a form its renderer refuses.
 *
 * The single-line form (`graph TD; A-->B`) splits: the header ends at the
 * semicolon and the rest is a statement, which is what mermaid means by it.
 */
function normalize(source: string): string {
  const trimmed = source.trimStart();
  const firstBreak = trimmed.indexOf('\n');
  const header = firstBreak === -1 ? trimmed : trimmed.slice(0, firstBreak);
  const rest = firstBreak === -1 ? '' : trimmed.slice(firstBreak);

  const semicolon = header.indexOf(';');
  if (semicolon === -1) return source;

  const declaration = header.slice(0, semicolon).trimEnd();
  const inlined = header.slice(semicolon + 1).trim();
  return inlined === ''
    ? `${declaration}${rest}`
    : `${declaration}\n  ${inlined}${rest}`;
}

/**
 * Whether a diagram is finished enough to draw.
 *
 * The guard exists because the renderer does NOT throw on a partial source — it
 * draws a plausible wrong picture. `graph TD\n A[Start] --> ` renders an
 * arrow into nothing, and the next token changes it, so a streaming diagram
 * would flicker through several confident-looking lies before settling.
 *
 * Same class of defect as a typeset math prefix, and the same cure: show the
 * source until the shape is closed, then draw once.
 *
 * Balance is counted on the bracket pairs a mermaid node uses for its label.
 * Quotes are ignored deliberately — a label may legitimately contain a lone
 * bracket, and being wrong about a closed diagram costs a frame while being
 * wrong about an open one costs the flicker this guard removes.
 */
export function isDiagramComplete(source: string): boolean {
  const trimmed = source.trimEnd();
  if (trimmed === '') return false;

  // A trailing edge (`-->`, `---`, `-.->`) means the next node has not arrived.
  if (/(--+>?|-\.-+>?|==+>?)\s*\|?[^|]*$/.test(trimmed) && /[-=>]$/.test(trimmed)) {
    return false;
  }

  for (const [open, close] of [
    ['[', ']'],
    ['(', ')'],
    ['{', '}'],
  ] as const) {
    if (count(trimmed, open) !== count(trimmed, close)) return false;
  }

  return true;
}

function count(text: string, char: string): number {
  let total = 0;
  for (const candidate of text) if (candidate === char) total += 1;
  return total;
}
