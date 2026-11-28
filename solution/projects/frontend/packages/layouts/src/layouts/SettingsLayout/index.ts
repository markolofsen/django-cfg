/**
 * SettingsLayout
 *
 * A Claude.ai-style settings surface: a searchable, grouped section rail on the
 * left and a scrollable detail panel on the right, available as a global dialog
 * (URL-hash driven, zustand-backed) or an inline form.
 *
 * Designed to eventually supersede ProfileLayout. Built in parallel — both
 * coexist for now.
 *
 *   // Mount once (PrivateLayout does this):
 *   <SettingsDialog sections={appSections} builtins={{ security: true }} />
 *
 *   // Open from anywhere:
 *   const settings = useSettingsDialog();
 *   settings.open('billing');          // or navigate to #settings/billing
 *
 *   // Inline page variant:
 *   <SettingsForm sections={appSections} />
 */

'use client';

// Top-level components
export { SettingsDialog } from './SettingsDialog';
export { SettingsForm } from './SettingsForm';
export { AccountMenuButton } from './components/AccountMenuButton';
export type { AccountMenuButtonProps } from './components/AccountMenuButton';

// Store + public hooks
export { useSettingsDialogStore } from './store';
export { useSettingsIntent } from './intent/useSettingsIntent';
export type { SettingsIntent } from './intent/useSettingsIntent';
export {
  useSettingsDialog,
  useSettingsUrl,
  useSettingsSections,
  useAccountMenuItems,
} from './hooks';
export type {
  UseSettingsDialogReturn,
  UseSettingsUrlOptions,
  ResolvedGroup,
} from './hooks';

// Typed section ids, the `#settings/<id>` address
export { defineSettingsSections, settingsHref, MCP_SECTION_ID } from './sectionIds';
export type { SettingsSectionId, BuiltinSettingsSectionId } from './sectionIds';

// Context (for advanced custom shells)
export { SettingsProvider, useSettingsContext } from './context';
export type { SettingsProviderProps } from './context';

// Shell parts (compose a bespoke layout if needed)
export { SettingsShell, SettingsNav, SettingsNavItem, SettingsPanel, SettingsSearch, SettingsTabs } from './components';

// Built-in sections + helpers (extend/replace the defaults)
export {
  buildBuiltinSections,
  BUILTIN_GROUP,
  AccountSection,
  ApiKeysSection,
  SettingRow,
  SettingsBlock,
} from './sections';

// Types
export type {
  SettingsSection,
  SettingsSectionContext,
  SettingsGroup,
  SettingsBuiltins,
  SettingsContent,
  SettingsFormProps,
  SettingsDialogProps,
} from './types';
