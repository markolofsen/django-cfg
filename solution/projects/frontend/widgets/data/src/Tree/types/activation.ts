'use client';

/**
 * How a node becomes "activated" (i.e. opened) on pointer interaction.
 *
 *   - `'single-click'` (default): single click activates a leaf immediately;
 *     double-click also activates. Folders always toggle on single click.
 *   - `'double-click'`: single click only selects + focuses; double-click is
 *     required to activate. Mirrors classic file-manager behaviour.
 *   - `'single-click-preview'`: VSCode Explorer / Cursor behaviour. Single
 *     click activates with `{ preview: true }` (consumer renders a preview
 *     tab); double-click activates with `{ preview: false }` (pinned tab).
 *
 * Folders ignore this setting — they always toggle on single click and
 * never call `onActivate`.
 */
export type TreeActivationMode =
  | 'single-click'
  | 'double-click'
  | 'single-click-preview';

export interface TreeActivateOptions {
  /**
   * `true` when the activation came from a single click in
   * `'single-click-preview'` mode. `false` for double-click and for
   * non-preview modes. Consumers typically map this to a
   * preview-tab vs pinned-tab distinction.
   */
  preview: boolean;
}
