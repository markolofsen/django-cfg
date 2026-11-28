/**
 * Data surfaces: the components that put rows, nodes and cards on screen.
 *
 * A root barrel EXISTS here, unlike in the retired ui-tools, and the reason
 * the ban was there does not apply: ui-tools mixed compiled `dist/` subpaths with raw
 * `src/` ones, so a root barrel and a subpath resolved the same module twice
 * and a `TreeProvider` context went missing. Every subpath here is source, so
 * there is one resolution and one module instance.
 *
 * It still costs: importing the root pulls all nine trees. Prefer a subpath —
 * `@djangocfg/widget-data/tree` — in an app that wants one.
 */
export * from './Tree';
export * from './FileIcon';
export * from './JsonTree';
export * from './DataGrid';
export * from './DataTable';
export * from './Kanban';
export * from './Listbox';
export * from './Masonry';
export * from './Timeline';
