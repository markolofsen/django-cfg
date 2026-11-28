/// <reference types="vite/client" />
import { useEffect } from 'react';
import type { Decorator, Preview } from '@storybook/nextjs-vite';

import dense from '@djangocfg/ui-core/styles/presets/dense?raw';
import djangoCfg from '@djangocfg/ui-core/styles/presets/django-cfg?raw';
import highContrast from '@djangocfg/ui-core/styles/presets/high-contrast?raw';
import ios from '@djangocfg/ui-core/styles/presets/ios?raw';
import notion from '@djangocfg/ui-core/styles/presets/notion?raw';
import macos from '@djangocfg/ui-core/styles/presets/macos?raw';
import soft from '@djangocfg/ui-core/styles/presets/soft?raw';
import windows from '@djangocfg/ui-core/styles/presets/windows?raw';

/**
 * Preset toolbar. The catalogue loads no preset by default (base.css type scale
 * + theme/*.css ladder); picking one injects its stylesheet last in <head>, so
 * its `:root` / `.dark` blocks override the defaults exactly like the
 * `@import` a consuming app uses. Deep-link: `?globals=preset:macos`.
 */
const PRESET_CSS: Record<string, string> = {
  dense,
  'django-cfg': djangoCfg,
  'high-contrast': highContrast,
  ios,
  macos,
  notion,
  soft,
  windows,
};

export const presetGlobalType: NonNullable<Preview['globalTypes']>[string] = {
  description: 'ui-core preset',
  toolbar: {
    title: 'Preset',
    icon: 'paintbrush',
    dynamicTitle: true,
    items: [{ value: 'default', title: 'default' }, ...Object.keys(PRESET_CSS).map((v) => ({ value: v, title: v }))],
  },
};

const STYLE_ID = 'sb-preset';

export const withPreset: Decorator = (Story, context) => {
  const preset = (context.globals.preset as string | undefined) ?? 'default';

  useEffect(() => {
    document.getElementById(STYLE_ID)?.remove();
    const css = PRESET_CSS[preset];
    if (!css) return;
    const el = document.createElement('style');
    el.id = STYLE_ID;
    el.textContent = css;
    document.head.appendChild(el);
    return () => el.remove();
  }, [preset]);

  return <Story />;
};
