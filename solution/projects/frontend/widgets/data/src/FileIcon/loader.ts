'use client';

/**
 * Back-compat shim for the former `material-file-icons` lazy loader.
 *
 * File icons are now resolved synchronously from a vendored static data
 * module — see `./get-file-icon`. The async API is kept so existing callers
 * of `loadMaterialIcons` / `getMaterialIconsSync` keep working; both resolve
 * immediately to the local resolver.
 *
 * @deprecated Import {@link getFileIcon} from `./get-file-icon` instead.
 */

import { getFileIcon } from './get-file-icon';

/** Returns an inline SVG string for a file name, or `undefined`. */
type GetIconFn = (name: string) => { svg?: string } | undefined;

const localGetIcon: GetIconFn = (name) => ({ svg: getFileIcon(name).svg });

/** @deprecated Use {@link getFileIcon} — resolution is now synchronous. */
export function loadMaterialIcons(): Promise<GetIconFn> {
  return Promise.resolve(localGetIcon);
}

/** @deprecated Use {@link getFileIcon} — resolution is now synchronous. */
export function getMaterialIconsSync(): GetIconFn {
  return localGetIcon;
}
