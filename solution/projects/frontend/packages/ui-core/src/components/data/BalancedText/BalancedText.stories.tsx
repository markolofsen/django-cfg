import type { Meta, StoryObj } from '@storybook/react-vite';
import { BalancedText } from '@djangocfg/ui-core/components';

const SAMPLE_HEADING =
  'Pretext-powered balanced text that produces deterministic line breaks across browsers';

const SAMPLE_PARAGRAPH =
  'CSS text-wrap: balance only works up to about six lines and is inconsistent across browsers. BalancedText uses pretext to binary-search the narrowest width that preserves the natural line count.';

const meta = {
  title: 'Packages/UI Core/Data/BalancedText',
  component: BalancedText,
  tags: ['autodocs'],
  argTypes: {
    maxWidth: { control: { type: 'number', min: 100, max: 1200, step: 20 } },
    maxLines: { control: { type: 'number', min: 1, max: 8 } },
    font: { control: 'text' },
  },
  args: {
    children: SAMPLE_HEADING,
    maxWidth: 480,
  },
} satisfies Meta<typeof BalancedText>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: (args) => (
    <div className="border border-border/40 p-4 bg-muted/20">
      <BalancedText
        {...args}
        as="h2"
        className="text-2xl font-semibold text-foreground leading-tight"
      />
    </div>
  ),
};

export const MaxLinesCap: Story = {
  args: {
    children: SAMPLE_PARAGRAPH,
    maxWidth: 600,
    maxLines: 2,
  },
  render: (args) => (
    <div className="border border-border/40 p-4 bg-muted/20">
      <BalancedText
        {...args}
        as="p"
        className="text-base text-foreground leading-relaxed"
      />
    </div>
  ),
};

export const ComparisonWithCss: Story = {
  args: { children: SAMPLE_HEADING, maxWidth: 480 },
  render: (args) => (
    <div className="flex flex-col gap-6">
      <div>
        <p className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
          Plain (no balancing)
        </p>
        <p
          className="text-2xl font-semibold text-foreground leading-tight"
          style={{ maxWidth: args.maxWidth }}
        >
          {args.children}
        </p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
          CSS text-wrap: balance
        </p>
        <p
          className="text-2xl font-semibold text-foreground leading-tight"
          style={{ maxWidth: args.maxWidth, textWrap: 'balance' }}
        >
          {args.children}
        </p>
      </div>
      <div>
        <p className="text-xs uppercase tracking-wider text-muted-foreground mb-2">
          Pretext (BalancedText)
        </p>
        <BalancedText
          {...args}
          as="h2"
          className="text-2xl font-semibold text-foreground leading-tight"
        />
      </div>
    </div>
  ),
};

export const HeadingScales: Story = {
  render: () => (
    <div className="flex flex-col gap-6">
      <BalancedText
        as="h1"
        font="48px ui-sans-serif, system-ui, sans-serif"
        maxWidth={720}
        className="text-5xl font-bold text-foreground leading-none"
      >
        Deterministic line balancing for long-form headlines and hero sections
      </BalancedText>
      <BalancedText
        as="h3"
        font="20px ui-sans-serif, system-ui, sans-serif"
        maxWidth={520}
        className="text-xl font-semibold text-foreground leading-snug"
      >
        Works at any heading scale because pretext measures glyphs, not lines
      </BalancedText>
    </div>
  ),
};
