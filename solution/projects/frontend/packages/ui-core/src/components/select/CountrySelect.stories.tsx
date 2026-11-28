import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { CountrySelect, Label, type TCountryCode } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/CountrySelect',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Built-in country picker. Uses ISO 3166-1 alpha-2 codes and ships with SVG flags. Supports single/multiple and dropdown/inline variants.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

function DefaultHost() {
  const [value, setValue] = useState<string[]>([]);
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Country</Label>
      <CountrySelect value={value} onChange={setValue} placeholder="Select country…" />
      <p className="text-xs text-muted-foreground">Selected: {value[0] ?? '(none)'}</p>
    </div>
  );
}

export const Default: Story = {
  render: () => <DefaultHost />,
};

function PreselectedHost() {
  const [value, setValue] = useState<string[]>(['US', 'DE', 'JP']);
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Markets (multi)</Label>
      <CountrySelect
        multiple
        value={value}
        onChange={setValue}
        placeholder="Pick markets…"
        maxDisplay={3}
      />
      <p className="text-xs text-muted-foreground">Selected: {value.join(', ')}</p>
    </div>
  );
}

export const Preselected: Story = {
  render: () => <PreselectedHost />,
};

function FilteredHost() {
  const ALLOWED: TCountryCode[] = ['US', 'CA', 'MX', 'BR', 'AR', 'CL'];
  const [value, setValue] = useState<string[]>([]);
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Americas only</Label>
      <CountrySelect
        value={value}
        onChange={setValue}
        allowedCountries={ALLOWED}
        placeholder="Select a country…"
        showNativeName
      />
      <p className="text-xs text-muted-foreground">
        Restricted to: {ALLOWED.join(', ')}
      </p>
    </div>
  );
}

export const Filtered: Story = {
  render: () => <FilteredHost />,
};
