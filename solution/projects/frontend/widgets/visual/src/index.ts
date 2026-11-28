/**
 * Presentation pieces: colour, motion, a code symbol, and two ways to show
 * media that are not a viewer.
 *
 * The residue of the retired ui-tools' `visual/` and `media/` folders after the parts with
 * a real home left — the image viewer and the players are
 * `@djangocfg/widget-media` and `@djangocfg/widget-player`, the charts are
 * `@djangocfg/widget-charts`, the overlays `@djangocfg/widget-overlay`.
 *
 * What is left genuinely belongs together: each puts something on screen for
 * its own sake, and none owns state a host has to drive.
 */
export * from './design/ColorPicker';
export * from './design/ColorPalette';
export * from './marquee';
export * from './qrcode';
export * from './gallery';
export * from './lottie';
