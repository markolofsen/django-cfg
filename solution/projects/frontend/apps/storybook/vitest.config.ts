import path from 'node:path';
import { fileURLToPath } from 'node:url';

import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';
import { playwright } from '@vitest/browser-playwright';
import { defineConfig } from 'vitest/config';

const dirname = path.dirname(fileURLToPath(import.meta.url));

function storybookProject({
  name,
  include,
  configDir,
}: {
  name: string;
  include: string[];
  configDir: string;
}) {
  return {
    extends: true as const,
    optimizeDeps: {
      include: [
        '@storybook/addon-themes',
        'storybook/test',
        'storybook/theming',
        // CJS package consumed with named imports by accessibility test setup.
        'aria-query',
        // CJS default export consumed by Testing Library's role suggestions.
        'lz-string',
      ],
    },
    plugins: [
      storybookTest({
        configDir: path.join(dirname, configDir),
        storybookScript: 'pnpm dev',
        tags: {
          include,
          exclude: ['manual', 'experimental'],
        },
      }),
    ],
    test: {
      name,
      browser: {
        enabled: true,
        provider: playwright({}),
        headless: true,
        instances: [{ browser: 'chromium' as const }],
      },
    },
  };
}

/*
 * There is no `onConsoleLog` here on purpose.
 *
 * One lived in this file, throwing on any browser stderr, and it never ran: in
 * browser mode the preview iframe's console is forwarded by Vite (the terminal
 * lines read `[vite] (client) [console.error] …`) and never reaches that hook,
 * which sees only Node-side process streams. Probed directly — a deliberate
 * `console.error` inside a play function printed and the run exited 0.
 *
 * The gate that does work runs in the browser, as a preview `afterEach`:
 * `.storybook/preview/console-gate.ts`. It also attributes the failure to the
 * story that caused it, which the Node-side hook could not do.
 */
export default defineConfig({
  test: {
    projects: [
      storybookProject({
        name: 'storybook-contract',
        include: ['contract'],
        configDir: '.storybook-contract',
      }),
      storybookProject({
        name: 'storybook-all',
        include: ['test'],
        configDir: '.storybook',
      }),
    ],
  },
});
