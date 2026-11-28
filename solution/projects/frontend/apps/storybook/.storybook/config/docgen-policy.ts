import type { StorybookConfig } from '@storybook/nextjs-vite';

/**
 * Keep automatic prop parsing disabled for the central library catalog.
 *
 * `react-docgen-typescript` was previously configured against the Storybook
 * app tsconfig, which intentionally excludes workspace package sources. The
 * result was 589 "outside the active TypeScript project" warnings while most
 * imported components received no TypeScript docgen output. Switching to
 * `react-docgen` made the same production build roughly four times slower.
 * Public controls and docs therefore use explicit `argTypes`, component prose,
 * and MDX. Re-enable automatic parsing only with a measured package-scoped
 * design that preserves the build budget.
 */
export const docgenPolicy: NonNullable<StorybookConfig['typescript']> = {
  reactDocgen: false,
};
