/**
 * Regenerates `src/fonts/index.ts` from the three `.woff` files beside it.
 *
 *   node scripts/generate-fonts.mjs
 *
 * Satori needs raw font bytes and a `.woff` next to a route file is not a
 * module import — nothing traces it into a standalone build, so `readFile` at
 * request time ENOENTs in production. Inlining as base64 puts the bytes in the
 * module graph, which is the one thing that guarantees they ship with the
 * route. See `src/fonts/index.ts` for the full rationale.
 */
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const dir = join(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'fonts');

const weights = [
  ['MEDIUM', 'Medium', 500],
  ['SEMIBOLD', 'SemiBold', 600],
  ['EXTRABOLD', 'ExtraBold', 800],
];

const consts = [];
const entries = [];
for (const [constName, file, weight] of weights) {
  const b64 = (await readFile(join(dir, `PlusJakartaSans-${file}.woff`))).toString('base64');
  consts.push(`const ${constName}_B64 =\n  '${b64}';`);
  entries.push(
    `    { name: OG_FONT_FAMILY, data: decode(${constName}_B64), weight: ${weight}, style: 'normal' as const },`,
  );
}

const header = `import type { ImageResponse } from 'next/og';

/**
 * The typeface for generated Open Graph cards.
 *
 * Satori has no access to the browser's font stack, so every face a card draws
 * with has to be handed to it as raw bytes. That rules out \`next/font\`, which
 * is what the rest of an app uses: it emits \`woff2\` and returns CSS class
 * names, and Satori reads neither.
 *
 * ── Why the bytes are inlined as base64 ───────────────────────────────────
 *
 * The obvious alternative is \`readFile\` at request time. It works in \`dev\` and
 * then fails in production, because a \`.woff\` beside a route file is not a
 * module import — nothing traces it, so the standalone build does not copy it
 * into the output and the route throws ENOENT on the first shared link.
 * Inlining makes the font part of the module graph, which is the one thing
 * that guarantees it ships wherever the route ships.
 *
 * The cost is roughly 64KB of source across the three weights. It is paid once
 * at build time and never reaches a visitor's browser — OG cards are rendered
 * on the server for crawlers.
 *
 * GENERATED — do not hand-edit the base64 below. The source of truth is the
 * three \`PlusJakartaSans-*.woff\` files in this directory; regenerate with
 * \`node scripts/generate-fonts.mjs\` if a weight ever changes.
 *
 * Plus Jakarta Sans is the display face the djangocfg apps set their pages in,
 * so a shared card and the page it links to are set in the same type. It is
 * licensed under the SIL Open Font License 1.1.
 */

export type OgFonts = NonNullable<ConstructorParameters<typeof ImageResponse>[1]>['fonts'];

/** Referenced by \`render.tsx\` as \`fontFamily\`; the two must not drift. */
export const OG_FONT_FAMILY = 'Jakarta';

`;

const body = `
/**
 * \`Buffer\` is available here (OG routes declare \`runtime = 'nodejs'\`) and is
 * markedly faster than the \`atob\` + charCodeAt loop for buffers this size.
 */
function decode(b64: string): ArrayBuffer {
  const bytes = Buffer.from(b64, 'base64');
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
}

let cached: OgFonts | undefined;

/**
 * The three weights \`render.tsx\` draws with. Decoded once per server process —
 * a card is regenerated on cache misses, and re-decoding 64KB on each of them
 * is pure waste.
 */
export function loadOgFonts(): Promise<OgFonts> {
  cached ??= [
${entries.join('\n')}
  ];
  return Promise.resolve(cached);
}
`;

await writeFile(join(dir, 'index.ts'), `${header}${consts.join('\n\n')}\n${body}`);
console.log('wrote src/fonts/index.ts');
