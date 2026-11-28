/**
 * Code surfaces: an editor, a diff, a JSON editor and
 * the markdown renderer that embeds them.
 *
 * No root barrel worth importing — Monaco alone is ~550 KB and `json-edit-react`
 * and Prism sit behind their own subpaths. Import the one you want:
 * `@djangocfg/widget-code/editor`, `/diff-viewer`,
 * `/json-editor`, `/markdown-message`.
 */
export { ANCHOR, TOGGLE } from './role-tokens';
