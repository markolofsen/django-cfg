import type { Meta, StoryObj } from '@storybook/nextjs-vite';

/**
 * Phase 1 smoke story.
 *
 * Purpose: validate the whole pipeline boots end-to-end.
 *   - `bg-card` / `text-card-foreground` / `border-border` read CSS variables
 *     from `light.css` / `dark.css`
 *   - flipping the toolbar theme should visibly invert the card
 *   - if neither happens, the Tailwind import order or the addon-themes
 *     parentSelector is wrong; do not proceed to phase 2
 */
function Smoke() {
  return (
    <div className="flex min-h-[200px] flex-col items-center justify-center gap-3 rounded-lg border border-border bg-card p-8 text-card-foreground">
      <p className="text-base font-medium">Storybook is live.</p>
      <p className="text-sm text-muted-foreground">
        Toggle the theme from the toolbar — colours should flip.
      </p>
    </div>
  );
}

const meta = {
  title: '_smoke/Smoke',
  component: Smoke,
  tags: ['!dev', 'contract'],
  parameters: {
    a11y: { test: 'error' },
    docs: { disable: true },
  },
} satisfies Meta<typeof Smoke>;

export default meta;

export const Default: StoryObj<typeof meta> = {};
