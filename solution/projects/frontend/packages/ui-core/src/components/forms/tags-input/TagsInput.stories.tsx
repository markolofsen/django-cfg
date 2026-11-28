import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  TagsInput,
  TagsInputInput,
  TagsInputItem,
  TagsInputItemDelete,
  TagsInputItemText,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/TagsInput',
  component: TagsInput,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'An input component for entering multiple tags with keyboard navigation and validation.',
      },
    },
  },
} satisfies Meta<typeof TagsInput>;

export default meta;
type Story = StoryObj<typeof meta>;

function TagsHost(props: {
  defaultValue?: string[];
  addOnPaste?: boolean;
  addOnTab?: boolean;
  editable?: boolean;
  max?: number;
  blurBehavior?: 'add' | 'clear';
}) {
  const [value, setValue] = useState<string[]>(props.defaultValue ?? []);
  return (
    <div className="w-96 space-y-2">
      <TagsInput
        value={value}
        onChange={setValue}
        addOnPaste={props.addOnPaste}
        addOnTab={props.addOnTab}
        editable={props.editable}
        max={props.max}
        blurBehavior={props.blurBehavior}
      >
        {value.map((tag) => (
          <TagsInputItem key={tag} value={tag}>
            <TagsInputItemText />
            <TagsInputItemDelete />
          </TagsInputItem>
        ))}
        <TagsInputInput placeholder="Add tag..." />
      </TagsInput>
      <p className="text-sm text-muted-foreground">
        Tags: <code className="font-mono">{value.join(', ') || '—'}</code>
      </p>
    </div>
  );
}

export const Default: Story = {
  render: () => <TagsHost defaultValue={['react', 'typescript']} />,
};

export const Empty: Story = {
  render: () => <TagsHost />,
};

export const AddOnPaste: Story = {
  render: () => <TagsHost addOnPaste defaultValue={['apple', 'banana']} />,
};

export const AddOnTab: Story = {
  render: () => <TagsHost addOnTab />,
};

export const Editable: Story = {
  render: () => <TagsHost editable defaultValue={['editable', 'tag']} />,
};

export const WithMax: Story = {
  render: () => <TagsHost max={3} defaultValue={['one', 'two']} />,
};

export const BlurAdd: Story = {
  render: () => <TagsHost blurBehavior="add" />,
};

export const BlurClear: Story = {
  render: () => <TagsHost blurBehavior="clear" />,
};
