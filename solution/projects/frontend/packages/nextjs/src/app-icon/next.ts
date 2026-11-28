/**
 * Route handlers for Next's icon file conventions, from one glyph and one hue.
 *
 *   // app/icon.tsx
 *   import * as workflow from 'lucide-react/icons/workflow';
 *   import { createAppIcon } from '@djangocfg/nextjs/app-icon/next';
 *   const icon = createAppIcon({ glyph: workflow, hue: 55 });
 *   export const generateImageMetadata = icon.generateImageMetadata;
 *   export default icon.icon;
 *
 *   // app/apple-icon.tsx
 *   export const size = { width: 180, height: 180 };
 *   export const contentType = 'image/png';
 *   export default icon.appleIcon;   // same createAppIcon call, or call it again
 *
 * Served at `/icon/tab` (64, rounded), `/icon/192`, `/icon/384`, `/icon/512` (square) and `/apple-icon` (180, square).
 */

import { ImageResponse } from 'next/og';

import { appIconElement, type AppIconGlyph } from './element';

export const appIconSizes = { tab: 64, '192': 192, '384': 384, '512': 512 } as const;
export const appleIconSize = { width: 180, height: 180 } as const;

export function createAppIcon({ glyph, hue }: { glyph: AppIconGlyph; hue: number }) {
  return {
    generateImageMetadata() {
      return Object.entries(appIconSizes).map(([id, side]) => ({
        id,
        size: { width: side, height: side },
        contentType: 'image/png',
      }));
    },
    async icon({ id }: { id: Promise<string | number> }) {
      const key = String(await id) as keyof typeof appIconSizes;
      const side = appIconSizes[key] ?? appIconSizes.tab;
      return new ImageResponse(appIconElement({ glyph, hue, size: side, shape: key === 'tab' ? 'rounded' : 'square' }), {
        width: side,
        height: side,
      });
    },
    appleIcon() {
      return new ImageResponse(appIconElement({ glyph, hue, size: appleIconSize.width, shape: 'square' }), appleIconSize);
    },
  };
}
