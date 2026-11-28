import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Listbox,
  ListboxItem,
  ListboxItemIndicator,
  ListboxGroup,
  ListboxGroupLabel,
} from '../Listbox';

const meta = {
  title: 'Widgets/Data/Listbox',
  component: Listbox,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A keyboard-navigable listbox with single and multi-selection support.',
      },
    },
  },
} satisfies Meta<typeof Listbox>;

export default meta;
type Story = StoryObj<typeof meta>;

const frameworks = [
  { value: 'react', label: 'React' },
  { value: 'vue', label: 'Vue' },
  { value: 'angular', label: 'Angular' },
  { value: 'svelte', label: 'Svelte' },
];

const languages = [
  { value: 'ts', label: 'TypeScript' },
  { value: 'js', label: 'JavaScript' },
  { value: 'py', label: 'Python' },
  { value: 'go', label: 'Go' },
];

function ListboxHost(props: {
  multiple?: boolean;
  defaultValue?: string | string[];
  orientation?: 'horizontal' | 'vertical' | 'mixed';
}) {
  const [value, setValue] = useState<string | string[] | undefined>(props.defaultValue);
  return (
    <div className="w-64 space-y-2">
      <Listbox
        value={value}
        onValueChange={setValue}
        multiple={props.multiple}
        orientation={props.orientation}
        className="rounded-md border p-1"
      >
        {frameworks.map((fw) => (
          <ListboxItem key={fw.value} value={fw.value}>
            <ListboxItemIndicator />
            {fw.label}
          </ListboxItem>
        ))}
      </Listbox>
      <p className="text-sm text-muted-foreground">
        Selected: <code className="font-mono">{Array.isArray(value) ? value.join(', ') || '—' : value || '—'}</code>
      </p>
    </div>
  );
}

export const Default: Story = {
  render: () => <ListboxHost />,
};

export const WithDefaultValue: Story = {
  render: () => <ListboxHost defaultValue="react" />,
};

export const MultiSelect: Story = {
  render: () => <ListboxHost multiple defaultValue={['react', 'vue']} />,
};

export const Horizontal: Story = {
  render: () => <ListboxHost orientation="horizontal" />,
};

export const WithGroups: Story = {
  render: () => (
    <Listbox className="rounded-md border p-1 w-64">
      <ListboxGroup>
        <ListboxGroupLabel>Frameworks</ListboxGroupLabel>
        {frameworks.map((fw) => (
          <ListboxItem key={fw.value} value={fw.value}>
            <ListboxItemIndicator />
            {fw.label}
          </ListboxItem>
        ))}
      </ListboxGroup>
      <ListboxGroup>
        <ListboxGroupLabel>Languages</ListboxGroupLabel>
        {languages.map((lang) => (
          <ListboxItem key={lang.value} value={lang.value}>
            <ListboxItemIndicator />
            {lang.label}
          </ListboxItem>
        ))}
      </ListboxGroup>
    </Listbox>
  ),
};
