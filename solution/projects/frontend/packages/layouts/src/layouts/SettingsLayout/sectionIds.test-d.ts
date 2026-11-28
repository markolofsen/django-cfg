/**
 * Type tests: tsc (vitest typecheck, and `pnpm check`) must accept the first block and reject every
 * `@ts-expect-error` line. A line that stops being an error fails the build.
 */

import type { ComponentType } from 'react';
import { describe, expectTypeOf, it } from 'vitest';

import { MCP_SECTION_ID, defineSettingsSections, settingsHref, type SettingsSectionId } from './sectionIds';
import { useSettingsDialog } from './hooks/useSettingsDialog';
import type { SettingsSection } from './types';

declare const mcpLike: { id: 'mcp'; label: string; content: null; icon: ComponentType<{ className?: string }> };

const sections = defineSettingsSections([mcpLike, { id: 'billing', label: 'Billing', content: null }]);
type AppId = SettingsSectionId<typeof sections>;

describe('typed settings section ids', () => {
  it('the id union is the declared ids plus the built-ins', () => {
    expectTypeOf<AppId>().toEqualTypeOf<'mcp' | 'billing' | 'account' | 'general' | 'api-keys'>();
    expectTypeOf(MCP_SECTION_ID).toEqualTypeOf<'mcp'>();
  });

  it('the result still goes where a SettingsSection[] goes', () => {
    expectTypeOf(sections).toMatchTypeOf<SettingsSection[]>();
  });

  it('useSettingsDialog<Id> accepts known ids only', () => {
    const typed = useSettingsDialog<AppId>();
    typed.open('billing');
    typed.setSection('mcp');
    // @ts-expect-error unknown id
    typed.open('biling');
    // @ts-expect-error unknown id
    typed.setSection('nope');
    expectTypeOf(typed.activeSection).toEqualTypeOf<AppId | null>();
  });

  it('the untyped default still takes any string', () => {
    const loose = useSettingsDialog();
    loose.open('anything');
    loose.setSection('else');
    expectTypeOf(loose.activeSection).toEqualTypeOf<string | null>();
  });

  it('settingsHref keeps the id in the type', () => {
    expectTypeOf(settingsHref('mcp')).toEqualTypeOf<`#${string}/mcp`>();
    // @ts-expect-error the helper for a typed id rejects other strings
    settingsHref<AppId>('biling');
  });
});
