'use client';

import React from 'react';

import { Button, SettingRow, SettingsBlock } from '@djangocfg/ui-core/components';
import {
  getViewportHud,
  remeasureViewport,
  setViewportHud,
  subscribeViewportHud,
  viewportSnapshot,
} from '@djangocfg/ui-core/hooks';

import { useSettingsCopy } from '../i18n';

/** Re-reads `viewportSnapshot()` twice a second while the section is open. */
function useSnapshot(): string {
  const [text, setText] = React.useState('');
  React.useEffect(() => {
    const read = () => setText(viewportSnapshot());
    read();
    const id = window.setInterval(read, 500);
    return () => window.clearInterval(id);
  }, []);
  return text;
}

/**
 * Built-in "Debug" section (`builtins.debug`). The switch turns the on-screen viewport HUD on or off (kept in
 * localStorage); the HUD itself is drawn by `UiProviders` over the whole app, so it stays when this dialog closes.
 */
export const DebugSection: React.FC = () => {
  const copy = useSettingsCopy();
  const on = React.useSyncExternalStore(subscribeViewportHud, () => getViewportHud() !== 'off', () => false);
  const snapshot = useSnapshot();
  const [, bump] = React.useReducer((n: number) => n + 1, 0);

  return (
    <div className="space-y-8">
      <SettingsBlock>
        <SettingRow
          label={copy.debug.hud}
          description={copy.debug.hudHint}
          toggle
          checked={on}
          onToggle={(next) => setViewportHud(next ? 'small' : 'off')}
        />
        <SettingRow
          label={copy.debug.remeasureNow}
          action={<Button variant="outline" size="sm" onClick={() => { remeasureViewport(); bump(); }}>{copy.debug.remeasureNow}</Button>}
        />
      </SettingsBlock>
      <SettingsBlock title={copy.debug.readout}>
        <pre data-testid="viewport-readout" className="whitespace-pre-wrap break-all font-mono text-xs">{snapshot}</pre>
      </SettingsBlock>
    </div>
  );
};
