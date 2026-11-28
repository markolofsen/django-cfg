import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  CheckboxGroup,
  CheckboxGroupDescription,
  CheckboxGroupItem,
  CheckboxGroupLabel,
  CheckboxGroupList,
  CheckboxGroupMessage,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/CheckboxGroup',
  component: CheckboxGroup,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A group of checkboxes with shared state and orientation support.',
      },
    },
  },
} satisfies Meta<typeof CheckboxGroup>;

export default meta;
type Story = StoryObj<typeof meta>;

const options = [
  { value: 'react', label: 'React' },
  { value: 'vue', label: 'Vue' },
  { value: 'angular', label: 'Angular' },
  { value: 'svelte', label: 'Svelte' },
];

function CheckboxHost(props: { defaultValue?: string[]; disabled?: boolean; orientation?: 'horizontal' | 'vertical' }) {
  const [value, setValue] = useState<string[]>(props.defaultValue ?? []);
  return (
    <CheckboxGroup value={value} onValueChange={setValue} disabled={props.disabled}>
      <CheckboxGroupLabel>Select frameworks</CheckboxGroupLabel>
      <CheckboxGroupList orientation={props.orientation}>
        {options.map((opt) => (
          <CheckboxGroupItem key={opt.value} value={opt.value}>
            {opt.label}
          </CheckboxGroupItem>
        ))}
      </CheckboxGroupList>
      <CheckboxGroupMessage>Selected: {value.join(', ') || 'None'}</CheckboxGroupMessage>
    </CheckboxGroup>
  );
}

export const Default: Story = {
  render: () => <CheckboxHost />,
};

export const WithDefaultValue: Story = {
  render: () => <CheckboxHost defaultValue={['react', 'vue']} />,
};

export const Horizontal: Story = {
  render: () => <CheckboxHost orientation="horizontal" />,
};

export const Disabled: Story = {
  render: () => <CheckboxHost disabled />,
};

export const WithDescription: Story = {
  render: () => (
    <CheckboxGroup>
      <CheckboxGroupLabel>Notifications</CheckboxGroupLabel>
      <CheckboxGroupDescription>Choose which notifications you want to receive.</CheckboxGroupDescription>
      <CheckboxGroupList>
        {options.map((opt) => (
          <CheckboxGroupItem key={opt.value} value={opt.value}>
            {opt.label}
          </CheckboxGroupItem>
        ))}
      </CheckboxGroupList>
    </CheckboxGroup>
  ),
};
