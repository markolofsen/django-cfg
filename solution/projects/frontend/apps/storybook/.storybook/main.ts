import { fileURLToPath } from "node:url";
import { dirname } from "node:path";
import type { StorybookConfig } from '@storybook/nextjs-vite';

import { docgenPolicy } from './config/docgen-policy.ts';

/**
 * Storybook 10.5 + Vite + Next.js framework.
 *
 * Conscious omissions vs. typical 8.x boilerplate:
 *   - no `addon-essentials` — folded into core in 9.x
 *   - no `addon-interactions` — replaced by addon-vitest
 *   - `addon-vitest` runs a tagged Vitest 4 browser project on Playwright
 *
 * See @plans/plan1-storybook/reports/03-storybook-upstream.md.
 */
const config: StorybookConfig = {
  framework: {
    name: getAbsolutePath("@storybook/nextjs-vite"),
    options: {},
  },
  stories: [
    '../stories/**/*.mdx',
    // Discovery and presentation are separate concerns. Test-only and manual
    // stories stay discoverable and use tags to control sidebar/test inclusion.
    '../stories/**/*.stories.@(ts|tsx)',
    // Widget stories live beside the component they cover, so a story is part
    // of the widget's own contract and moves with it.
    '../../../widgets/*/src/**/*.mdx',
    '../../../widgets/*/src/**/*.stories.@(ts|tsx)',
    // Same rule for packages. The single `*` is load-bearing: `packages/@archive`
    // and `packages/@sources` hold *nested* projects and have no `src/` at this
    // depth, so they never match — no explicit ignore needed.
    '../../../packages/*/src/**/*.mdx',
    '../../../packages/*/src/**/*.stories.@(ts|tsx)',
  ],
  tags: {
    manual: { defaultFilterSelection: 'exclude' },
    experimental: { defaultFilterSelection: 'exclude' },
  },
  addons: [
    getAbsolutePath("@storybook/addon-docs"),
    getAbsolutePath("@storybook/addon-a11y"),
    getAbsolutePath("@storybook/addon-themes"),
    getAbsolutePath("@storybook/addon-vitest"),
  ],
  docs: {
    defaultName: 'Docs',
  },
  typescript: docgenPolicy,
  staticDirs: ['../public'],
  // The Vite WebSocket shares Storybook's HTTP server. Its browser-facing
  // address must follow the page origin, not the container's listen port.
  async viteFinal(config) {
    const hmr = config.server?.hmr;
    if (hmr && typeof hmr === 'object' && hmr.server) {
      delete hmr.port;
    }
    return config;
  },
};

export default config;

function getAbsolutePath(value: string): any {
  return dirname(fileURLToPath(import.meta.resolve(`${value}/package.json`)));
}
