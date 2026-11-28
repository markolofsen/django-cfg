#!/usr/bin/env node
/**
 * README catalogue vs. component folders.
 *
 * Every folder under src/components/<group>/<name>/ (and every file in
 * select/) must be named in README.md, by its PascalCase or kebab-case name,
 * ignoring case and hyphens. Folders whose public name differs from the folder
 * go in ALIASES. Fails with the list of undocumented folders.
 */
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const components = join(root, 'src/components');
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, '');
const readme = norm(readFileSync(join(root, 'README.md'), 'utf8'));

// folder name -> the name the README uses
const ALIASES = {
  sonner: 'Toast',
  otp: 'OTPInput',
  'input-otp': 'InputOTP',
  'time-picker': 'TimePicker',
  'datetime-field': 'DateTimeField',
  'button-download': 'DownloadButton',
  'multi-select-pro-async': 'MultiSelectPro',
  'combobox-async': 'ComboboxAsync',
  swap: 'Swap',
  copy: 'CopyButton',
  primitive: 'Primitive',
  'visually-hidden-input': 'VisuallyHidden',
  'aspect-ratio': 'AspectRatio',
  'avatar-group': 'AvatarGroup',
  'badge-overflow': 'BadgeOverflow',
  'image-with-fallback': 'ImageWithFallback',
  'toggle-group': 'ToggleGroup',
  'circular-progress': 'CircularProgress',
  'radio-group': 'RadioGroup',
  'checkbox-group': 'CheckboxGroup',
  'input-group': 'InputGroup',
  'input-affix': 'InputAffix',
  'mask-input': 'MaskInput',
  'segmented-input': 'SegmentedInput',
  'tags-input': 'TagsInput',
  'phone-input': 'PhoneInput',
  'popover-action-button': 'PopoverActionButton',
  'popover-row-button': 'PopoverRowButton',
  'responsive-sheet': 'ResponsiveSheet',
  'side-panel': 'SidePanel',
  'alert-dialog': 'AlertDialog',
  'hover-card': 'HoverCard',
  'scroll-area': 'ScrollArea',
  'key-value': 'KeyValue',
  'filter-bar': 'FilterBar',
  'filter-button': 'FilterButton',
  'filter-menu': 'FilterMenu',
  'setting-row': 'SettingRow',
  'money-field': 'MoneyField',
  'relative-time-card': 'RelativeTimeCard',
  'token-icon': 'TokenIcon',
  'context-menu': 'ContextMenu',
  'dropdown-menu': 'DropdownMenu',
  'navigation-menu': 'NavigationMenu',
  menu: 'MenuBuilder',
};
// folders that are internals, not a component a consumer reaches for
const SKIP = new Set(['TouchSafeInput', 'primitives', 'Gallery', 'portal', 'presence', 'item', 'chart', 'label', 'field', 'form', 'button-group']);

const names = [];
for (const group of readdirSync(components)) {
  const dir = join(components, group);
  if (!statSync(dir).isDirectory()) continue;
  for (const entry of readdirSync(dir)) {
    if (entry.startsWith('.') || /\.(stories|test)\./.test(entry)) continue;
    const full = join(dir, entry);
    const base = statSync(full).isDirectory() ? entry : entry.replace(/\.(tsx|ts)$/, '');
    if (!statSync(full).isDirectory() && !/\.(tsx|ts)$/.test(entry)) continue;
    if (['index', 'helpers', 'types', 'trigger', 'README'].includes(base) || base.startsWith('_')) continue;
    names.push([`${group}/${base}`, base]);
  }
}

const missing = names
  .filter(([, base]) => !SKIP.has(base))
  .filter(([, base]) => !readme.includes(norm(ALIASES[base] ?? base)))
  .map(([path]) => path);

if (missing.length) {
  console.error('README.md catalogue is missing:\n  ' + missing.join('\n  '));
  console.error('\nAdd each to its group row in README.md (or to ALIASES / SKIP in scripts/check-docs.mjs).');
  process.exit(1);
}
console.log(`README catalogue covers ${names.length} component folders.`);
