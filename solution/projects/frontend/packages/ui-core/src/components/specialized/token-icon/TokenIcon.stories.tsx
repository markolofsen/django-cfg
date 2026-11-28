import type { Meta, StoryObj } from '@storybook/react-vite';
import { TokenIcon } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Specialized/TokenIcon',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Crypto / token glyphs sourced from @web3icons/react with text fallback for unknown symbols.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

export const Btc: Story = {
  render: () => <TokenIcon symbol="BTC" size={64} />,
};

export const Eth: Story = {
  render: () => <TokenIcon symbol="ETH" size={64} />,
};

export const Usdt: Story = {
  render: () => <TokenIcon symbol="USDT" size={64} />,
};

export const Variants: Story = {
  render: () => (
    <div className="flex items-center gap-6">
      <div className="flex flex-col items-center gap-2">
        <TokenIcon symbol="BTC" size={48} variant="branded" />
        <span className="text-muted-foreground text-xs">branded</span>
      </div>
      <div className="flex flex-col items-center gap-2">
        <TokenIcon symbol="BTC" size={48} variant="mono" />
        <span className="text-muted-foreground text-xs">mono</span>
      </div>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex items-end gap-4">
      {[16, 24, 32, 48, 64, 96].map((s) => (
        <div key={s} className="flex flex-col items-center gap-2">
          <TokenIcon symbol="ETH" size={s} />
          <span className="text-muted-foreground text-xs">{s}px</span>
        </div>
      ))}
    </div>
  ),
};

const GRID_TOKENS = [
  'BTC',
  'ETH',
  'USDT',
  'BNB',
  'SOL',
  'USDC',
  'XRP',
  'DOGE',
  'ADA',
  'TRX',
  'AVAX',
  'DOT',
  'MATIC',
  'LINK',
  'UNI',
];

export const Grid: Story = {
  render: () => (
    <div className="grid grid-cols-5 gap-4">
      {GRID_TOKENS.map((symbol) => (
        <div
          key={symbol}
          className="flex flex-col items-center gap-2 rounded-md border p-3"
        >
          <TokenIcon symbol={symbol} size={40} />
          <span className="text-muted-foreground text-xs font-medium">
            {symbol}
          </span>
        </div>
      ))}
    </div>
  ),
};

export const UnknownFallback: Story = {
  render: () => (
    <div className="flex items-center gap-4">
      <TokenIcon symbol="ZZZZZ" size={48} />
      <span className="text-muted-foreground text-sm">
        Unknown symbol — falls back to first 3 chars.
      </span>
    </div>
  ),
};
