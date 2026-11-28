import type { ThemeStylePresetId } from './types';

export const THEME_STYLE_PRESET_ORDER = [
  'default',
  'django-cfg',
  'notion',
  'ios',
  'macos',
  'windows',
  'soft',
  'dense',
  'high-contrast',
] as const satisfies readonly ThemeStylePresetId[];
