'use client';

import { createContext, useContext } from 'react';

/**
 * The composer's control scale. Defined here rather than in the chat package
 * because both sides of the slot bridge need it: chat's own action-bar
 * controls AND this widget's slot components (e.g. `VoiceComposerSlot`). Keeping it
 * beside the registry is what lets a slot inherit the size without importing
 * from chat — one of the cycles the package split removed.
 */
export type ComposerSize = 'sm' | 'md' | 'lg';

/**
 * Propagates the composer's `size` to slot components placed in
 * `composerSlots.inlineStart` / `inlineEnd` (`ComposerMenuButton`,
 * `ComposerModelPicker`, `ComposerToolPill`). Without this a host has
 * to repeat `size` on every slotted control to keep the action bar
 * visually aligned; with it, an explicit `size` prop on the slot
 * component still wins, but omitting it inherits the composer's size.
 */
const ComposerSizeContext = createContext<ComposerSize | null>(null);

export const ComposerSizeProvider = ComposerSizeContext.Provider;

/**
 * Resolve the effective size for a slotted control: an explicit prop
 * always wins; otherwise inherit from the composer; final fallback `md`.
 */
export function useResolvedComposerSize(explicit?: ComposerSize): ComposerSize {
  const inherited = useContext(ComposerSizeContext);
  return explicit ?? inherited ?? 'md';
}
