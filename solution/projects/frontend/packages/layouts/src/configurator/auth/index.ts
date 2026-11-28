/**
 * AuthLayout configurator — schemas, defaults, and presets.
 *
 * Two independent schemas are provided:
 *   - `authCenteredSchema` + `authCenteredUiSchema` — Apple-style frameless
 *   - `authSplitSchema` + `authSplitUiSchema` — two-column card with sidebar
 *
 * Use `defaultCenteredConfig` / `defaultSplitConfig` as safe initial values.
 */

export type {
  AuthPlaygroundConfig,
  AuthCenteredConfig,
  AuthSplitConfig,
  AuthShellVariant,
  PresetKind,
  AuthBackgroundConfig,
  AuthSidebarConfig,
  AuthFormConfig,
} from './types';

export {
  BG_IMAGES,
  defaultCenteredConfig,
  defaultSplitConfig,
  defaultConfig,
  presets,
  detectPreset,
} from './defaults';

export {
  authCenteredSchema,
  authCenteredUiSchema,
  authSplitSchema,
  authSplitUiSchema,
} from './schema';
