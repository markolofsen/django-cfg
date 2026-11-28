import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Copy, Share, Highlighter } from 'lucide-react';
import {
  SelectionToolbar,
  SelectionToolbarContent,
  SelectionToolbarAction,
} from '.';

const meta = {
  title: 'Widgets/Overlay/SelectionToolbar',
  component: SelectionToolbar,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A toolbar that appears when text is selected within its container.',
      },
    },
  },
  args: {
    children: null,
  },
} satisfies Meta<typeof SelectionToolbar>;

export default meta;
type Story = StoryObj<typeof meta>;

function ToolbarDemo() {
  const [lastAction, setLastAction] = useState('');
  return (
    <div className="space-y-4">
      <SelectionToolbar minSelectionLength={2}>
        <div className="rounded-lg border p-6 leading-relaxed">
          <p>
            Select any text in this paragraph to see the selection toolbar appear.
            The toolbar is positioned near the selection and provides quick actions.
          </p>
          <p className="mt-4">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
            eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim
            ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
            aliquip ex ea commodo consequat.
          </p>
        </div>
        <SelectionToolbarContent>
          <SelectionToolbarAction
            label="Copy"
            onClick={() => setLastAction('Copied')}
          >
            <Copy className="h-3.5 w-3.5" />
          </SelectionToolbarAction>
          <SelectionToolbarAction
            label="Share"
            onClick={() => setLastAction('Shared')}
          >
            <Share className="h-3.5 w-3.5" />
          </SelectionToolbarAction>
          <SelectionToolbarAction
            label="Highlight"
            onClick={() => setLastAction('Highlighted')}
          >
            <Highlighter className="h-3.5 w-3.5" />
          </SelectionToolbarAction>
        </SelectionToolbarContent>
      </SelectionToolbar>
      {lastAction && (
        <p className="text-sm text-muted-foreground">
          Last action: <span className="font-medium">{lastAction}</span>
        </p>
      )}
    </div>
  );
}

export const Default: Story = {
  render: () => <ToolbarDemo />,
};
