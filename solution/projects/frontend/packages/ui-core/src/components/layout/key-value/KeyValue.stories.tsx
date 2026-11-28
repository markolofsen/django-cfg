import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  KeyValue,
  KeyValueAdd,
  KeyValueError,
  KeyValueItem,
  KeyValueKeyInput,
  KeyValueList,
  KeyValueRemove,
  KeyValueValueInput,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/KeyValue',
  component: KeyValue,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A key-value editor with add/remove, paste support, and validation.',
      },
    },
  },
} satisfies Meta<typeof KeyValue>;

export default meta;
type Story = StoryObj<typeof meta>;

function KeyValueHost(props: {
  defaultValue?: { id: string; key: string; value: string }[];
  allowDuplicateKeys?: boolean;
  minItems?: number;
  maxItems?: number;
}) {
  const [value, setValue] = useState(props.defaultValue ?? [{ id: '1', key: '', value: '' }]);
  return (
    <KeyValue
      value={value}
      onValueChange={setValue}
      allowDuplicateKeys={props.allowDuplicateKeys}
      minItems={props.minItems}
      maxItems={props.maxItems}
    >
      <KeyValueList>
        <KeyValueItem>
          <KeyValueKeyInput placeholder="Key" />
          <KeyValueValueInput placeholder="Value" />
          <KeyValueRemove />
        </KeyValueItem>
      </KeyValueList>
      <KeyValueAdd />
    </KeyValue>
  );
}

export const Default: Story = {
  render: () => (
    <KeyValueHost
      defaultValue={[
        { id: '1', key: 'name', value: 'John Doe' },
        { id: '2', key: 'email', value: 'john@example.com' },
      ]}
    />
  ),
};

export const Empty: Story = {
  render: () => <KeyValueHost />,
};

export const MinMaxItems: Story = {
  render: () => (
    <KeyValueHost
      defaultValue={[{ id: '1', key: 'key1', value: 'value1' }]}
      minItems={1}
      maxItems={3}
    />
  ),
};

export const AllowDuplicates: Story = {
  render: () => (
    <KeyValueHost
      defaultValue={[
        { id: '1', key: 'tag', value: 'a' },
        { id: '2', key: 'tag', value: 'b' },
      ]}
      allowDuplicateKeys
    />
  ),
};

export const WithErrors: Story = {
  render: () => (
    <KeyValue
      defaultValue={[{ id: '1', key: '', value: '' }]}
      onKeyValidate={(key) => (key.length < 2 ? 'Key must be at least 2 characters' : undefined)}
    >
      <KeyValueList>
        <KeyValueItem>
          <div className="flex flex-col gap-1">
            <KeyValueKeyInput placeholder="Key" />
            <KeyValueError field="key" />
          </div>
          <KeyValueValueInput placeholder="Value" />
          <KeyValueRemove />
        </KeyValueItem>
      </KeyValueList>
      <KeyValueAdd />
    </KeyValue>
  ),
};
