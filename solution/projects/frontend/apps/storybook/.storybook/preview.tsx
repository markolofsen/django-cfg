import './preview-globals.css';
import type { Preview } from '@storybook/nextjs-vite';
import { withThemeByClassName } from '@storybook/addon-themes';
import { presetGlobalType, withPreset } from './preview/preset-switcher';
import { deviceGlobalType, displayModeGlobalType, safeAreaGlobalType, withDisplayMode } from './preview/display-mode-switcher';
import { withStoryHarness } from './preview/story-harness';
import { ThemedDocsContainer } from './preview/theme-docs-container';
import { storyLifecycle } from './preview/lifecycle';
import { disableMediaCaptureUnderTest } from './preview/headless-media';
import { beginConsoleCapture, endConsoleCapture } from './preview/console-gate';

disableMediaCaptureUnderTest();

/**
 * Storybook preview config — global parameters + decorators.
 *
 * Provider strategy:
 *   - `withThemeByClassName` is the SINGLE source of truth for theme. It
 *     toggles the `.dark` class on `<html>`, and our token CSS does the rest.
 *   - We intentionally do NOT mount `@djangocfg/ui-core/theme#ThemeProvider`
 *     in the global decorator. It also writes to `html.className` from
 *     localStorage and would race against addon-themes. Stories that need
 *     `useThemeContext()` should wrap themselves locally.
 *   - `TooltipProvider` + `DialogProvider` are required by lots of ui-core
 *     components and have no side effects — safe at the global level.
 *
 * MSW loader is added in phase 4 (demo migration).
 */

const preview: Preview = {
  beforeEach: (context) => {
    beginConsoleCapture();
    return storyLifecycle(context);
  },
  // `afterEach`, not the `beforeEach` cleanup: Storybook runs this inside the
  // story's own lifecycle, so a console write fails the story that made it
  // rather than the one that happens to run next.
  afterEach: endConsoleCapture,
  parameters: {
    layout: 'padded',
    backgrounds: { disabled: true },
    // Phone presets for the PWA / drawer review (see the Display mode and Safe area toolbar items).
    viewport: {
      options: {
        iphone14: { name: 'iPhone 14 (390x844)', styles: { width: '390px', height: '844px' }, type: 'mobile' },
        iphoneSe: { name: 'iPhone SE (375x667)', styles: { width: '375px', height: '667px' }, type: 'mobile' },
        iphone16: { name: 'iPhone 16 Pro (402x874)', styles: { width: '402px', height: '874px' }, type: 'mobile' },
        iphone14ProMax: { name: 'iPhone Pro Max (430x932)', styles: { width: '430px', height: '932px' }, type: 'mobile' },
        iphone13mini: { name: 'iPhone mini (375x812)', styles: { width: '375px', height: '812px' }, type: 'mobile' },
      },
    },
    nextjs: { appDirectory: true },
    a11y: { test: 'todo' },
    docs: {
      codePanel: true,
      // Theme the autodocs page to match the preview toolbar toggle.
      container: ThemedDocsContainer,
    },
    options: {
      storySort: {
        order: [
          'Welcome',
          'UI Core',
          'UI Tools',
          'Layouts',
          'Payments',
          'Devtools',
          'API Client',
          'i18n',
          'Next.js Utils',
          '_smoke',
        ],
      },
    },
  },
  initialGlobals: { preset: 'default', device: 'off', displayMode: 'auto', safeArea: 'none' },
  globalTypes: { preset: presetGlobalType, device: deviceGlobalType, displayMode: displayModeGlobalType, safeArea: safeAreaGlobalType },
  decorators: [
    withPreset,
    withDisplayMode,
    withThemeByClassName({
      themes: { light: '', dark: 'dark' },
      defaultTheme: 'dark',
      parentSelector: 'html',
    }),
    withStoryHarness,
  ],
};

export default preview;
