/**
 * App icon: ONE definition of the picture an app shows in a tab, on a home screen and as a PWA icon.
 *
 * House style: a full-bleed tile in the product's hue (a two-stop gradient), a white lucide glyph in the inner ~46-58%,
 * and NO border near the edge. The OS cuts its own corner (iOS ~22%, Android a mask); anything drawn at the edge never
 * matches that curve.
 *
 * Pure: plain host elements only (`next/og` renders nothing else) and no `next/og` import, so a client bundle can use
 * the same gradient for an in-app tile. The route factory lives in `./next`.
 */

import { createElement, type ReactElement } from 'react';

/** What lucide stores for an icon: `[tag, attrs][]`; `attrs.key` is React's key. */
export type IconNode = [tag: string, attrs: Record<string, string>][];

/**
 * A glyph is a lucide icon MODULE, `import * as workflow from 'lucide-react/icons/workflow'` (a lucide component is a
 * client component and `next/og` cannot render it, so its drawing data is read from the module), or the node list itself.
 */
export type AppIconGlyph = object | IconNode;

export type AppIconShape = 'rounded' | 'square';

export interface AppIconOptions {
  glyph: AppIconGlyph;
  /** OKLCH hue, 0-360. The switcher tile should use `appIconGradient(hue)` so both agree. */
  hue: number;
  /** Side in px. */
  size: number;
  /** `rounded`: transparent corners (browser tab). `square`: full-bleed for iOS and maskable PWA icons. @default 'rounded' */
  shape?: AppIconShape;
}

/** OKLCH to sRGB hex. `next/og` does not parse `oklch()`; CSS does, and the two must show the same colour. */
export function oklchToHex(l: number, c: number, h: number): string {
  const a = c * Math.cos((h * Math.PI) / 180);
  const b = c * Math.sin((h * Math.PI) / 180);
  const l_ = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m_ = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s_ = (l - 0.0894841775 * a - 1.291485548 * b) ** 3;
  const lin = [
    4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
    -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
    -0.0041960863 * l_ - 0.7034186147 * m_ + 1.707614701 * s_,
  ];
  const hex = lin.map((v) => {
    const g = v <= 0.0031308 ? 12.92 * v : 1.055 * v ** (1 / 2.4) - 0.055;
    return Math.round(Math.min(1, Math.max(0, g)) * 255).toString(16).padStart(2, '0');
  });
  return `#${hex.join('')}`;
}

/** The gradient behind a glyph, two hex stops from one hue. */
export function appIconGradient(hue: number): string {
  return `linear-gradient(150deg, ${oklchToHex(0.66, 0.17, hue)}, ${oklchToHex(0.47, 0.18, hue + 22)})`;
}

function nodesOf(glyph: AppIconGlyph): IconNode {
  if (Array.isArray(glyph)) return glyph as IconNode;
  const node = (glyph as { __iconData?: { node?: IconNode } }).__iconData?.node;
  if (!node) throw new Error("app-icon: glyph is not a lucide icon module (expected `import * as x from 'lucide-react/icons/<name>'`)");
  return node;
}

/** The picture as plain JSX, for `new ImageResponse(...)`. */
export function appIconElement({ glyph, hue, size, shape = 'rounded' }: AppIconOptions): ReactElement {
  const square = shape === 'square';
  // A square icon is cropped by the OS: keep the glyph inside the maskable safe zone (the inner 60%).
  const side = Math.round(size * (square ? 0.46 : 0.58));
  const glyphSvg = createElement(
    'svg',
    { width: side, height: side, viewBox: '0 0 24 24', fill: 'none', stroke: '#ffffff', strokeWidth: 2.1, strokeLinecap: 'round', strokeLinejoin: 'round' },
    ...nodesOf(glyph).map(([tag, { key, ...attrs }]) => createElement(tag, { key, ...attrs })),
  );
  return createElement(
    'div',
    {
      style: {
        width: size,
        height: size,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundImage: appIconGradient(hue),
        borderRadius: square ? 0 : Math.round(size * 0.225),
      },
    },
    glyphSvg,
  );
}
