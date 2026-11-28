import { cn } from '../../lib/utils';

/**
 * The one height ladder every field-like control and `Button` reads.
 *
 * A row of `<Input/> <Select/> <Button/>` only lines up if each of them gets
 * its height for the same size name from the same place. Two ladders drifting
 * apart is invisible per component and obvious the moment they share a row, so
 * a control never spells `h-9` / `h-10` itself — it reads this map.
 *
 * Tailwind reads complete class tokens only, so every entry is a literal
 * string; never build one by interpolation.
 *
 * - `height` / `minHeight`: the shared token. `minHeight` is for triggers that
 *   grow with their content (chips, tags) and must still never be shorter than
 *   the fixed control of the same size.
 * - Touch floor: every rung except `huge` also carries `pointer-coarse:min-h-11`
 *   (44px), so a finger gets a 44px control at any size while a mouse keeps the
 *   dense ladder. It is a utility on the control, not a token override: presets
 *   redefine `--control-h-*` unlayered and would win over a token override in
 *   the base layer. `min-height` beats `height`, so every rung rises together
 *   and a row of `Input` / `Select` / `Button` still lines up on a phone.
 * - `button`: horizontal padding and type size of a `Button` at this size.
 * - `field`: horizontal and vertical padding and type size of a text field.
 *   `default` keeps `text-base md:text-sm` so a phone does not zoom on focus.
 *
 * `huge` exists for `Button` only; no field has one.
 */
export const CONTROL_SIZE = {
  xs: {
    height: 'h-(--control-h-xs) pointer-coarse:min-h-11',
    minHeight: 'min-h-(--control-h-xs) pointer-coarse:min-h-11',
    button: 'px-2 py-1 text-xs',
    field: 'px-2 py-0.5 text-xs',
  },
  sm: {
    height: 'h-(--control-h-sm) pointer-coarse:min-h-11',
    minHeight: 'min-h-(--control-h-sm) pointer-coarse:min-h-11',
    button: 'px-3 text-sm',
    field: 'px-2.5 py-1 text-sm',
  },
  default: {
    height: 'h-(--control-h-default) pointer-coarse:min-h-11',
    minHeight: 'min-h-(--control-h-default) pointer-coarse:min-h-11',
    button: 'px-4 py-2',
    field: 'px-3 py-1 text-base md:text-sm',
  },
  lg: {
    height: 'h-(--control-h-lg) pointer-coarse:min-h-11',
    minHeight: 'min-h-(--control-h-lg) pointer-coarse:min-h-11',
    button: 'px-8',
    field: 'px-4 py-2 text-base',
  },
  huge: {
    height: 'h-(--control-h-huge)',
    minHeight: 'min-h-(--control-h-huge)',
    button: 'px-10 text-lg',
  },
} as const;

/** Every size name on the ladder. */
export type ControlSize = keyof typeof CONTROL_SIZE;

/** The sizes a text field offers — the ladder without `huge`. */
export type FieldControlSize = Exclude<ControlSize, 'huge'>;

/** Height, padding and type size of a fixed-height field at `size`. */
export const fieldSizeClass = (size: FieldControlSize = 'default'): string =>
  cn(CONTROL_SIZE[size].height, CONTROL_SIZE[size].field);

/** Height, padding and type size of a `Button` at `size`. */
export const buttonSizeClass = (size: ControlSize = 'default'): string =>
  cn(CONTROL_SIZE[size].height, CONTROL_SIZE[size].button);
