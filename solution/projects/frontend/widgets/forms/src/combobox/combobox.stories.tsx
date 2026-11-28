import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Combobox,
  ComboboxTrigger,
  ComboboxList,
  ComboboxItem,
  ComboboxEmpty,
} from '.';

const meta = {
  title: 'Widgets/Forms/Combobox',
  component: Combobox,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'An advanced combobox with filtering, multi-select, and custom rendering.',
      },
    },
  },
  args: {
    options: [],
    children: null,
  },
} satisfies Meta<typeof Combobox>;

export default meta;
type Story = StoryObj<typeof meta>;

const options = [
  { value: 'react', label: 'React', description: 'A JavaScript library for building user interfaces' },
  { value: 'vue', label: 'Vue' },
  { value: 'angular', label: 'Angular' },
  { value: 'svelte', label: 'Svelte' },
  { value: 'solid', label: 'Solid' },
  { value: 'preact', label: 'Preact' },
];

function ComboboxHost(props: {
  multiple?: boolean;
  placeholder?: string;
}) {
  const [value, setValue] = useState<string | string[] | null>(null);
  return (
    <div className="w-80 space-y-2">
      <Combobox
        options={options}
        value={value ?? undefined}
        onChange={setValue}
        multiple={props.multiple}
        placeholder={props.placeholder}
      >
        <ComboboxTrigger />
        <ComboboxList>
          <ComboboxEmpty>No frameworks found.</ComboboxEmpty>
          {options.map((opt, i) => (
            <ComboboxItem key={opt.value} option={opt} index={i} />
          ))}
        </ComboboxList>
      </Combobox>
      <p className="text-sm text-muted-foreground">
        Selected:{' '}
        <code className="font-mono">
          {Array.isArray(value) ? value.join(', ') || '—' : value || '—'}
        </code>
      </p>
    </div>
  );
}

export const Default: Story = {
  render: () => <ComboboxHost placeholder="Select a framework…" />,
};

export const MultiSelect: Story = {
  render: () => <ComboboxHost multiple placeholder="Select frameworks…" />,
};
