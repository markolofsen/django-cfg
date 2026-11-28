import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Editable,
  EditableInput,
  EditablePreview,
  EditableTextarea,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/Editable',
  component: Editable,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'An inline editable text component that toggles between preview and input modes.',
      },
    },
  },
} satisfies Meta<typeof Editable>;

export default meta;
type Story = StoryObj<typeof meta>;

function EditableHost(props: {
  defaultValue?: string;
  placeholder?: string;
  disabled?: boolean;
  readOnly?: boolean;
  submitOnBlur?: boolean;
  selectAllOnFocus?: boolean;
}) {
  const [value, setValue] = useState(props.defaultValue ?? '');
  return (
    <Editable
      value={value}
      onValueChange={setValue}
      placeholder={props.placeholder}
      disabled={props.disabled}
      readOnly={props.readOnly}
      submitOnBlur={props.submitOnBlur}
      selectAllOnFocus={props.selectAllOnFocus}
    >
      <EditablePreview />
      <EditableInput />
    </Editable>
  );
}

export const Default: Story = {
  render: () => <EditableHost defaultValue="Click to edit this text" />,
};

export const Placeholder: Story = {
  render: () => <EditableHost placeholder="Enter your name..." />,
};

export const Disabled: Story = {
  render: () => <EditableHost defaultValue="Cannot edit this" disabled />,
};

export const ReadOnly: Story = {
  render: () => <EditableHost defaultValue="Read-only value" readOnly />,
};

export const NoSubmitOnBlur: Story = {
  render: () => <EditableHost defaultValue="Press Enter to save" submitOnBlur={false} />,
};

export const NoSelectAll: Story = {
  render: () => <EditableHost defaultValue="Cursor at end on focus" selectAllOnFocus={false} />,
};

/**
 * Story bodies live in components, not in `render`.
 *
 * `render` is a plain callback with no identity of its own in React, so hooks
 * called there belong to whatever tree Storybook happens to mount and their
 * state survives or resets in ways nothing here controls. That is what
 * `react-hooks/rules-of-hooks` is flagging.
 */
function TextareaDemo() {
  const [value, setValue] = useState('Click to edit\nThis supports multiple lines');
  return (
    <Editable value={value} onValueChange={setValue}>
      <EditablePreview />
      <EditableTextarea />
    </Editable>
  );
}

export const Textarea: Story = {
  render: () => <TextareaDemo />,
};
