import type { ApiEndpoint } from '../../types';
import { relativePath } from '../../utils/url';

/**
 * Given a list of full endpoint paths, return the longest ``/``-aligned
 * prefix they all share. Used to strip the redundant group prefix
 * (``/api/v3/pet``) from sidebar labels so the meaningful tail is visible.
 *
 * Works on full URLs too — if every path begins with the same origin,
 * the origin is part of the common prefix and gets stripped.
 */
export function longestCommonPrefix(paths: string[]): string {
    if (paths.length === 0) return '';
    if (paths.length === 1) return '';

    const segments = paths.map((p) => p.split('/'));
    const minLen = Math.min(...segments.map((s) => s.length));

    const shared: string[] = [];
    for (let i = 0; i < minLen; i++) {
        const first = segments[0]![i];
        if (segments.every((s) => s[i] === first)) {
            shared.push(first!);
        } else {
            break;
        }
    }
    // Don't strip everything — we always want at least a leading "/" or
    // the method on the visible side. If the group has one endpoint,
    // the caller guards with paths.length check already.
    const joined = shared.join('/');
    // Trim trailing slash so the tail is clean (``/foo`` not ``foo``).
    return joined;
}

/**
 * Compute the label to show in the sidebar for a given endpoint.
 *
 * Priority:
 *   1. ``ep.summary`` — human-readable, from OpenAPI ``operation.summary``.
 *   2. The tail of ``ep.path`` after stripping the group's common prefix.
 *   3. Full ``ep.path`` if the group has a single endpoint (no prefix to strip).
 */
export function sidebarLabel(ep: ApiEndpoint, groupCommonPrefix: string): string {
    if (ep.summary) return ep.summary;

    if (groupCommonPrefix && ep.path.startsWith(groupCommonPrefix)) {
        const tail = ep.path.slice(groupCommonPrefix.length) || '/';
        return tail;
    }
    return relativePath(ep.path);
}

/** Tooltip text: always the definitive ``METHOD relative/path``. */
export function sidebarTooltip(ep: ApiEndpoint): string {
    return `${ep.method} ${relativePath(ep.path)}`;
}
