import type { Meta, StoryObj } from '@storybook/react-vite';
import { Download, Settings2, X } from 'lucide-react';
import { Button, PopoverActionButton, PopoverRowButton } from '@djangocfg/ui-core/components';

/**
 * The two reusable macOS list/action row buttons:
 *
 * - `PopoverActionButton` — full-width icon+label footer/link row
 *   ("Connection settings…", "Manage providers…").
 * - `PopoverRowButton` — selectable picker row with a trailing-leading check
 *   (model / machine / provider pickers).
 *
 * For an icon-only ghost button (close/cancel), use the existing core
 * `Button variant="ghost" size="icon"` — no dedicated component needed.
 */
const meta = {
  title: 'Packages/UI Core/Forms/PopoverButtons',
  component: PopoverActionButton,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Low-level macOS list/action controls for popover footers and pickers. Token-driven — flip the theme toggle to see dark mode.',
      },
    },
  },
} satisfies Meta<typeof PopoverActionButton>;

export default meta;

type Story = StoryObj<typeof meta>;

export const ActionButton: Story = {
  render: () => (
    <div className="w-64 rounded border border-border p-2">
      <PopoverActionButton icon={<Settings2 className="h-3.5 w-3.5" />}>
        Connection settings…
      </PopoverActionButton>
      <PopoverActionButton icon={<Download className="h-3.5 w-3.5" />} className="mt-1">
        Download voice models
      </PopoverActionButton>
    </div>
  ),
};

export const RowButton: Story = {
  render: () => (
    <div className="w-64 rounded border border-border p-1">
      <PopoverRowButton selected>GPT-4o</PopoverRowButton>
      <PopoverRowButton>Claude Opus</PopoverRowButton>
      <PopoverRowButton>Llama 3.1 (local)</PopoverRowButton>
      <PopoverRowButton disabled>Gemini (unavailable)</PopoverRowButton>
    </div>
  ),
};

export const IconOnlyGhost: Story = {
  render: () => (
    <div className="flex flex-col gap-2">
      <p className="text-xs text-muted-foreground">
        Icon-only ghost = existing <code>Button variant=&quot;ghost&quot; size=&quot;icon&quot;</code> — no new
        component.
      </p>
      <Button variant="ghost" size="icon" aria-label="Close">
        <X className="h-4 w-4" />
      </Button>
    </div>
  ),
};
