/**
 * Select Components - Unified Collection
 * 
 * All select-based components in one place:
 * - Select: Radix UI primitives with icon/badge support
 * - Combobox: Searchable single-select with icon/badge support
 * - MultiSelectPro: Multi-select with badges, icons, animations
 * - MultiSelectProAsync: Async multi-select with all features
 */

// Radix Select primitives (enhanced)
export {
  Select,
  SelectGroup,
  SelectValue,
  SelectTrigger,
  SelectContent,
  SelectLabel,
  SelectItem,
  SelectSeparator,
  SelectScrollUpButton,
  SelectScrollDownButton,
} from './select';

// Combobox
export { Combobox } from './combobox';
export type { ComboboxOption, ComboboxProps } from './combobox';

// Combobox Async (single-select with parent-owned async search)
export { ComboboxAsync } from './combobox-async';
export type { ComboboxAsyncOption, ComboboxAsyncProps } from './combobox-async';

// MultiSelect
export { MultiSelect } from './multi-select';
export type { MultiSelectOption, MultiSelectProps } from './multi-select';

// MultiSelectPro
export { MultiSelectPro } from './multi-select-pro';
export type {
  MultiSelectProOption,
  MultiSelectProGroup,
  MultiSelectProProps,
  MultiSelectProRef,
  AnimationConfig,
  ResponsiveConfig,
} from './multi-select-pro';

// MultiSelectPro Async
export { MultiSelectProAsync } from './multi-select-pro-async';
export type {
  MultiSelectProAsyncProps,
  MultiSelectProAsyncOption,
  MultiSelectProAsyncGroup,
  MultiSelectProAsyncRef,
} from './multi-select-pro-async';

// Helpers
export { createOption, createOptions } from './helpers';
export type { OptionBuilderConfig } from './helpers';

// CountrySelect
export { CountrySelect } from './country-select';
export type { CountrySelectProps, CountryOption } from './country-select';
export type { TCountryCode } from 'countries-list';

// TimezoneSelect
export { TimezoneSelect, detectTimezone, timezoneOffsetLabel } from './timezone-select';
export type { TimezoneSelectProps } from './timezone-select';

// LanguageSelect
export { LanguageSelect } from './language-select';
export type {
  LanguageSelectProps,
  LanguageSelectSize,
  LanguageSelectVariant,
  LanguageOption,
  TLanguageCode,
} from './language-select';

// Shared types
export type {
  BaseSelectOption,
  SelectOptionGroup,
  BadgeStyle,
  SelectAnimationConfig,
} from './types';
