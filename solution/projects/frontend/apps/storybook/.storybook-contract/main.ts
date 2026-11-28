import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

import type { StorybookConfig } from '@storybook/nextjs-vite';

import mainConfig from '../.storybook/main.ts';

/**
 * Small, blocking catalog for pull-request browser tests.
 *
 * Storybook's Vitest plugin indexes the `stories` field before tag filtering,
 * so this explicit catalog is what keeps the contract gate fast. Add a file
 * only after its stories are deterministic and carry the `contract` tag.
 *
 * EXPLICIT PATHS FAIL SILENTLY, so they are asserted below rather than trusted.
 * A glob that matches nothing is indistinguishable here from a glob whose
 * stories all pass: three entries pointed at `stories/ui-tools/` for months
 * after that directory was retired, and the gate went on reporting green while
 * testing six files instead of nine. The one thing a blocking gate must never
 * do is shrink without saying so.
 */
const CONTRACT_STORIES = [
  '../stories/_smoke/**/*.stories.@(ts|tsx)',
  // Retitled successors of the retired `ui-tools` entries. Both kept the
  // `contract` tag through the move, so they were meant to be here all along.
  '../../../widgets/data/src/stories/tree-Interaction.stories.tsx',
  '../../../widgets/forms/src/speech/VoiceControls.stories.tsx',
  // Package stories now live beside their source, so these are package paths.
  // ui-core nests each component in its own directory, hence the extra level.
  '../../../packages/ui-core/src/components/forms/button/Button.stories.tsx',
  '../../../packages/ui-core/src/components/navigation/disclosure/Disclosure.stories.tsx',
  '../../../packages/ui-core/src/components/overlay/dialog/Dialog.stories.tsx',
  '../../../packages/layouts/src/layouts/AuthLayout/AuthFlow.stories.tsx',
  '../../../packages/payments/src/components/PaymentStatusBadge.stories.tsx',
  '../../../packages/payments/src/components/CheckoutDialog.stories.tsx',
  '../../../packages/payments/src/components/UpdateCardDialog.stories.tsx',
];

/**
 * Every literal path must exist. Globs are skipped — `_smoke/**` is allowed to
 * match a varying number of files, which is exactly why it is a glob.
 */
for (const entry of CONTRACT_STORIES) {
  if (entry.includes('*')) continue;
  const path = fileURLToPath(new URL(entry, import.meta.url));
  if (!existsSync(path)) {
    throw new Error(
      `Contract catalog names a story that does not exist: ${entry}\n` +
        'Re-point it at the file that replaced it, or delete the entry — ' +
        'leaving it shrinks the blocking gate without failing it.',
    );
  }
}

const config: StorybookConfig = {
  ...mainConfig,
  stories: CONTRACT_STORIES,
};

export default config;
