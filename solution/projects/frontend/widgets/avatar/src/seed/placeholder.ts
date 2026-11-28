import { pickFromSeed } from "./hash";

/**
 * The tile a face occupies before its drawing arrives.
 *
 * Character styles are loaded on demand, so there is one frame with nothing to
 * paint. Three options were weighed: nothing (the row jumps when the face
 * lands), a spinner (motion in a dozen roster rows, for something that resolves
 * in milliseconds), or a flat colour. The colour wins — the tile is the right
 * size and a plausible hue from the start, so the arrival reads as detail
 * appearing rather than as content replacing content.
 *
 * SEEDED, not a neutral grey: a grey column would flash uniform and then become
 * varied, which is the opposite of the property this whole package is for.
 *
 * It deliberately does NOT try to predict the style's own background. That would
 * mean reimplementing each style's palette here, and a wrong guess flashes one
 * colour and settles on another — worse than a colour that was never a claim.
 */

/**
 * Muted enough to sit under any drawing without competing with it, and distinct
 * enough that neighbouring rows differ. Fixed rather than derived from the theme
 * because it is visible for one frame; a token lookup would couple this package
 * to a design system it otherwise knows nothing about.
 */
const PLACEHOLDER_COLOURS = [
  "#c8d8e4",
  "#e4d5c8",
  "#d6d9c4",
  "#dcd0e0",
  "#c9dcd8",
  "#e0d3cc",
] as const;

export function placeholderColour(seed: string): string {
  // A DIFFERENT salt from the style pick, so the two choices are independent:
  // sharing one hash would tie every notionists face to one colour and make the
  // placeholder a preview of the style rather than of the row.
  return pickFromSeed(PLACEHOLDER_COLOURS, `bg:${seed}`);
}
