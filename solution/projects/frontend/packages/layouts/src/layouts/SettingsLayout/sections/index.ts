export { buildBuiltinSections, BUILTIN_GROUP, PLATFORM_GROUP } from './builtins';
export { GeneralSection } from './GeneralSection';
export { AccountSection } from './AccountSection';
export { ApiKeysSection } from './ApiKeysSection';
// SettingRow/SettingsBlock now live in ui-core (universal). Re-export for
// backward compatibility with consumers importing them from @djangocfg/layouts.
export { SettingRow, SettingsBlock } from '@djangocfg/ui-core/components';
export { PreferencesRows } from './PreferencesRows';
