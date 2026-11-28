'use client';

// Public surface — re-exports from each feature folder.
//
// Each folder owns one "scope" of keyboard interaction:
//   - keyboard/        arrow / home / end / enter / esc / mod+a
//   - type-ahead/      printable-keys rolling buffer
//   - finder-hotkeys/  Finder/Explorer shortcuts wired to adapter actions
//
// Adding a new scope = adding a new folder, not editing this barrel.

export { useTreeKeyboard } from './keyboard';
export type {
  UseTreeKeyboardOptions,
  UseTreeKeyboardReturn,
} from './keyboard';

export { useTreeTypeAhead } from './type-ahead';
export type { UseTreeTypeAheadOptions } from './type-ahead';

export { useTreeFinderHotkeys } from './finder-hotkeys';
export type {
  UseTreeFinderHotkeysOptions,
  UseTreeFinderHotkeysReturn,
} from './finder-hotkeys';
