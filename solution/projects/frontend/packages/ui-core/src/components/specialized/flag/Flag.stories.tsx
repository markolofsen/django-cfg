import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { Flag, Input, LanguageFlag } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Specialized/Flag',
  component: Flag,
  tags: ['autodocs'],
  args: { countryCode: 'US', className: 'h-6 w-9' },
} satisfies Meta<typeof Flag>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Rounded: Story = {
  render: () => (
    <div className="flex items-center gap-3">
      <Flag countryCode="US" className="h-6 w-9" />
      <Flag countryCode="US" rounded className="h-6 w-9" />
    </div>
  ),
};

function LanguageFlagHost() {
  const [code, setCode] = useState('pt-BR');
  return (
    <div className="w-80 space-y-3">
      <div className="flex items-center gap-3 text-sm">
        <LanguageFlag code={code} rounded className="h-6 w-9" />
        <span className="font-mono text-muted-foreground">{code}</span>
      </div>
      <Input
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Locale (en, pt-BR, zh-CN, …)"
      />
    </div>
  );
}

export const LanguageInteractive: Story = { render: () => <LanguageFlagHost /> };

export const Grid: Story = {
  render: () => {
    const codes = [
      'US', 'GB', 'CA', 'BR', 'DE', 'FR', 'IT', 'ES', 'PT',
      'NL', 'SE', 'NO', 'DK', 'FI', 'PL', 'CZ', 'GR', 'TR',
      'RU', 'UA', 'JP', 'KR', 'CN', 'IN', 'TH', 'VN', 'ID', 'IL', 'SA',
    ];
    return (
      <div className="grid grid-cols-6 gap-3">
        {codes.map((c) => (
          <div key={c} className="flex flex-col items-center gap-1">
            <Flag countryCode={c} rounded className="h-6 w-9" />
            <span className="font-mono text-xs text-muted-foreground">{c}</span>
          </div>
        ))}
      </div>
    );
  },
};

export const UnknownCode: Story = {
  render: () => (
    <div className="text-sm text-muted-foreground">
      Unknown code renders nothing:{' '}
      <span className="inline-flex items-center gap-1.5">
        <Flag countryCode="ZZ" className="h-3 w-4" />
        <span>(no flag here →)</span>
      </span>
    </div>
  ),
};
