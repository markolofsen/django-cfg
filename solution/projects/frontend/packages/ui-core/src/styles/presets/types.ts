/**
 * Names of the static CSS presets shipped by ui-core.
 *
 * Preset tokens are intentionally not represented as TypeScript maps. CSS is
 * the single source of truth and consumers select a preset with a stylesheet
 * import, e.g. `@djangocfg/ui-core/styles/presets/macos`.
 */
export type ThemeStylePresetId =
  | 'default'
  | 'django-cfg'
  | 'ios'
  | 'macos'
  | 'windows'
  | 'soft'
  | 'dense'
  | 'high-contrast'
  | 'notion';
