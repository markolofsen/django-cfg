'use client';

import { TreeRoot } from './TreeRoot';
import type { TreeRootProps } from './types';

/**
 * `<FinderTree>` — opinionated Finder/Explorer-style preset.
 *
 * Equivalent to `<TreeRoot>` with multi-selection, double-click activation,
 * inline rename, indent guides, and a cozy appearance turned on. Pass an
 * `adapter` to get the built-in CRUD menu wired to `window.dialog.*`.
 *
 * Override any preset default by simply passing the same prop:
 *
 * ```tsx
 * <FinderTree<FsNode>
 *   data={data}
 *   getItemName={(n) => n.data.name}
 *   adapter={fsAdapter}
 *   // override one preset default — everything else stays Finder-y:
 *   activationMode="single-click-preview"
 * />
 * ```
 */
export function FinderTree<T>(props: TreeRootProps<T>) {
  return (
    <TreeRoot<T>
      // Finder/Explorer defaults — every one is overridable via `props`.
      selectionMode="multiple"
      activationMode="double-click"
      enableInlineRename
      enableFinderHotkeys
      enableDnD
      enableTypeAhead
      showIndentGuides
      appearance={{ density: 'cozy' }}
      {...props}
    />
  );
}

export default FinderTree;
