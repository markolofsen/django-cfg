/**
 * Typed section ids.
 *
 * The dialog is mounted once and driven through a global store, so its `sections` prop cannot type the hooks that
 * open it. Declare the sections with `defineSettingsSections` and hand the id union to the hook instead:
 *
 *   const sections = defineSettingsSections([mcpSettingsSection(), { id: 'billing', ... }]);
 *   type AppSection = SettingsSectionId<typeof sections>;       // 'mcp' | 'billing' | built-in ids
 *   useSettingsDialog<AppSection>().open('biling');             // compile error
 *
 * Nothing here is runtime weight beyond two one-line functions.
 */

import type { SettingsSection } from './types';

/** Ids of the sections the layout ships (`builtins`). They are openable whether or not the host switched one off. */
export type BuiltinSettingsSectionId = 'account' | 'general' | 'api-keys';

/**
 * The id of the MCP section. `@djangocfg/widget-mcp` (`mcpSettingsSection()`) uses the same literal; layouts cannot
 * import the widget (a package never depends on a widget), so the two agree by value and each side has a test on it.
 */
export const MCP_SECTION_ID = 'mcp' as const;

/** The ids of a section list: the host's own plus the built-ins. Collapses to `string` if any id is not a literal. */
export type SettingsSectionId<S extends readonly { id: string }[]> = S[number]['id'] | BuiltinSettingsSectionId;

/**
 * Identity function that keeps each section's `id` as a literal type, so `SettingsSectionId<typeof sections>` is a
 * closed union. Accepts the result of `mcpSettingsSection()` as is.
 */
export function defineSettingsSections<const S extends SettingsSection[]>(sections: S): S {
  return sections;
}

/**
 * The address that opens the dialog on a section: `settingsHref('mcp')` is `"#settings/mcp"`. For a plain link
 * (`href`, `<a>`), a route table or an email; `useSettingsUrl` opens the dialog when the page lands on it.
 * `urlKey` follows `SettingsDialog`'s `urlKey` prop.
 */
export function settingsHref<Id extends string = string>(id: Id, urlKey = 'settings'): `#${string}/${Id}` {
  return `#${urlKey}/${id}`;
}
