'use client';

import { useCallback } from 'react';

import { usePageSnapshot } from './use-page-snapshot';

/**
 * The opt-in toggle's current state and click handler.
 *
 * Deliberately framework-/component-agnostic: it returns plain values,
 * not a `ComposerAction`. The host wires these into whatever toggle
 * control its composer uses — this keeps `page-snapshot` decoupled from
 * the chat's component types.
 */
export interface PageSnapshotToggle {
  /** Whether page-context sharing is currently on. */
  pressed: boolean;
  /** Flip the opt-in. */
  toggle: () => void;
  /** Suggested control label / tooltip — reflects the current state. */
  label: string;
}

/**
 * Drive an opt-in toggle for page-context sharing.
 *
 * @example
 *   const snap = usePageSnapshotToggle();
 *   // feed into a composer action:
 *   { id: 'page-context', icon: <MonitorUp />, label: snap.label,
 *     pressed: snap.pressed, onClick: snap.toggle }
 */
export function usePageSnapshotToggle(): PageSnapshotToggle {
  const { isLinked, setIsLinked } = usePageSnapshot();

  const toggle = useCallback(() => {
    setIsLinked(!isLinked);
  }, [isLinked, setIsLinked]);

  return {
    pressed: isLinked,
    toggle,
    label: isLinked
      ? 'Stop sharing page context'
      : 'Share page context with the assistant',
  };
}
