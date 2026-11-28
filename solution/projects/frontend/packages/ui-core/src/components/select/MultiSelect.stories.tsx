import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Label, MultiSelect, type MultiSelectOption } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/MultiSelect',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Plain multi-select with search and badge-style display of picked values. For badges + icons + animations use `MultiSelectPro`.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

const TAGS: MultiSelectOption[] = [
  { value: 'react', label: 'React', description: 'UI library' },
  { value: 'vue', label: 'Vue', description: 'Progressive framework' },
  { value: 'svelte', label: 'Svelte', description: 'Compile-time' },
  { value: 'solid', label: 'Solid', description: 'Fine-grained reactivity' },
  { value: 'angular', label: 'Angular', description: 'Opinionated' },
  { value: 'qwik', label: 'Qwik', description: 'Resumable' },
];

function DefaultHost() {
  const [value, setValue] = useState<string[]>([]);
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Frameworks</Label>
      <MultiSelect
        options={TAGS}
        value={value}
        onChange={setValue}
        placeholder="Pick frameworks…"
      />
      <p className="text-xs text-muted-foreground">Selected: {value.join(', ') || '(none)'}</p>
    </div>
  );
}

export const Default: Story = {
  render: () => <DefaultHost />,
};

function WithMaxHost() {
  const MAX = 2;
  const [value, setValue] = useState<string[]>([]);
  const handleChange = (next: string[]) => {
    // Cap selection at MAX — drop additions past the cap.
    if (next.length > MAX) return;
    setValue(next);
  };
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Pick up to {MAX} frameworks</Label>
      <MultiSelect
        options={TAGS}
        value={value}
        onChange={handleChange}
        placeholder="Pick frameworks…"
      />
      <p className="text-xs text-muted-foreground">
        {value.length}/{MAX} selected
      </p>
    </div>
  );
}

export const WithMax: Story = {
  render: () => <WithMaxHost />,
};

function WithBadgesHost() {
  // `maxDisplay` controls how many badges render before "+N more" collapses the rest.
  const [value, setValue] = useState<string[]>(['react', 'vue', 'svelte', 'solid']);
  return (
    <div className="grid w-80 gap-1.5">
      <Label>maxDisplay = 2</Label>
      <MultiSelect
        options={TAGS}
        value={value}
        onChange={setValue}
        maxDisplay={2}
        placeholder="Pick frameworks…"
      />
    </div>
  );
}

export const WithBadges: Story = {
  render: () => <WithBadgesHost />,
};

export const Disabled: Story = {
  render: () => (
    <div className="grid w-80 gap-1.5">
      <Label>Frameworks (disabled)</Label>
      <MultiSelect
        options={TAGS}
        value={['react', 'vue']}
        disabled
        placeholder="Pick frameworks…"
      />
    </div>
  ),
};
