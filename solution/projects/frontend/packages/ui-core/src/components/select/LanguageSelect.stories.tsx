import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Label, LanguageSelect } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/LanguageSelect',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Built-in language picker. Uses ISO 639-1 codes and shows the country flag of the language origin. Single or multiple selection.',
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
      <Label>Language</Label>
      <LanguageSelect value={value} onChange={setValue} placeholder="Select language…" />
      <p className="text-xs text-muted-foreground">Selected: {value[0] ?? '(none)'}</p>
    </div>
  );
}

export const Default: Story = {
  render: () => <DefaultHost />,
};

function PreselectedHost() {
  const [value, setValue] = useState<string[]>(['en', 'ru', 'ko']);
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Supported languages (multi)</Label>
      <LanguageSelect
        multiple
        value={value}
        onChange={setValue}
        placeholder="Pick languages…"
        showNativeName
        maxDisplay={3}
      />
      <p className="text-xs text-muted-foreground">Selected: {value.join(', ')}</p>
    </div>
  );
}

export const Preselected: Story = {
  render: () => <PreselectedHost />,
};
