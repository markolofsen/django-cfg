import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Brain,
  Clock,
  FileText,
  Globe,
  ImagePlus,
  Lightbulb,
  MoreHorizontal,
  Paperclip,
  Plus,
  Telescope,
  Trash2,
} from 'lucide-react';
import {
  Button,
  MenuBuilder,
  type MenuItem,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Navigation/MenuBuilder',
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Declarative menu — pass a `MenuItem[]` tree and a trigger. Renders items, submenus, radio groups, checkboxes, sections, separators, shortcuts and descriptions through the Radix dropdown primitives.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

// ---------------------------------------------------------------------------
// ChatGPT-style composer menu — the canonical test case
// ---------------------------------------------------------------------------

export const ComposerMenu: Story = {
  name: 'Composer Menu (ChatGPT-style)',
  render: () => {
    const items: MenuItem[] = [
      {
        kind: 'section',
        id: 'attach',
        items: [
          {
            kind: 'item',
            id: 'add-files',
            label: 'Add photos & files',
            icon: Paperclip,
            shortcut: '⌘U',
            onSelect: () => undefined,
          },
          {
            kind: 'submenu',
            id: 'recent-files',
            label: 'Recent files',
            icon: Clock,
            items: [
              { kind: 'item', id: 'rf-1', label: 'report.pdf', icon: FileText, onSelect: () => undefined },
              { kind: 'item', id: 'rf-2', label: 'design.png', icon: FileText, onSelect: () => undefined },
            ],
          },
        ],
      },
      {
        kind: 'section',
        id: 'tools',
        items: [
          { kind: 'item', id: 'create-image', label: 'Create image', icon: ImagePlus, onSelect: () => undefined },
          { kind: 'item', id: 'thinking', label: 'Thinking', icon: Brain, onSelect: () => undefined },
          { kind: 'item', id: 'deep-research', label: 'Deep research', icon: Telescope, onSelect: () => undefined },
          { kind: 'item', id: 'web-search', label: 'Web search', icon: Globe, onSelect: () => undefined },
        ],
      },
      {
        kind: 'submenu',
        id: 'more',
        label: 'More',
        icon: MoreHorizontal,
        items: [
          { kind: 'item', id: 'canvas', label: 'Canvas', icon: Lightbulb, onSelect: () => undefined },
        ],
      },
    ];

    return (
      <MenuBuilder items={items} side="top" align="start">
        <Button variant="outline" size="icon" aria-label="Add files and more">
          <Plus className="size-4 text-foreground" />
        </Button>
      </MenuBuilder>
    );
  },
};

// ---------------------------------------------------------------------------
// Stateful rows — checkbox + radio group
// ---------------------------------------------------------------------------

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function StatefulDemo() {
  const [model, setModel] = useState('auto');
  const [wrap, setWrap] = useState(true);

  const items: MenuItem[] = [
    {
      kind: 'radio-group',
      id: 'model',
      label: 'Model',
      value: model,
      onValueChange: setModel,
      options: [
        { id: 'm-auto', value: 'auto', label: 'Auto' },
        { id: 'm-fast', value: 'fast', label: 'Fast' },
        {
          id: 'm-think',
          value: 'think',
          label: 'Thinking',
          description: 'Slower, more thorough',
        },
      ],
    },
    { kind: 'separator', id: 's1' },
    {
      kind: 'checkbox',
      id: 'wrap',
      label: 'Wrap long lines',
      checked: wrap,
      onCheckedChange: setWrap,
    },
    { kind: 'separator', id: 's2' },
    {
      kind: 'item',
      id: 'delete',
      label: 'Delete conversation',
      icon: Trash2,
      variant: 'destructive',
      onSelect: () => undefined,
    },
  ];

  return (
    <MenuBuilder items={items} align="start">
      <Button variant="outline">Options</Button>
    </MenuBuilder>
  );
}

export const Stateful: Story = {
  render: () => <StatefulDemo />,
};
