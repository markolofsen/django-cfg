import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Label, TimezoneSelect } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/TimezoneSelect',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'IANA time zone picker built on Combobox. Options come from `Intl.supportedValuesOf` (no data dependency), show the current UTC offset and are ordered by it. `null` means "Automatic" — follow the browser.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

function Host({ initial, allowAuto = true }: { initial: string | null; allowAuto?: boolean }) {
  const [value, setValue] = useState<string | null>(initial);
  return (
    <div className="grid w-80 gap-1.5">
      <Label>Time zone</Label>
      <TimezoneSelect value={value} onChange={setValue} allowAuto={allowAuto} />
      <p className="text-xs text-muted-foreground">Value: {value ?? 'null (automatic)'}</p>
    </div>
  );
}

export const Automatic: Story = { render: () => <Host initial={null} /> };
export const Preselected: Story = { render: () => <Host initial="Asia/Seoul" /> };
export const WithoutAuto: Story = { render: () => <Host initial="Europe/Madrid" allowAuto={false} /> };
