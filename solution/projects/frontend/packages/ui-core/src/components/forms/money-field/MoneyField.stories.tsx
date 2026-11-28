import { useId, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { MoneyField } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/MoneyField',
  component: MoneyField,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'An amount input that formats as you type and reports **minor units** — cents, not dollars. ' +
          'Entry is till-style: digits fill from the right, so `1` `9` `9` reads $1.99.',
      },
    },
  },
  argTypes: {
    currency: { control: 'text' },
    locale: { control: 'text' },
    showSymbol: { control: 'boolean' },
    max: { control: 'number' },
    disabled: { control: 'boolean' },
  },
  args: {
    currency: 'USD',
    showSymbol: true,
  },
} satisfies Meta<typeof MoneyField>;

export default meta;
type Story = StoryObj<typeof meta>;

/** Shows the raw stored value beside the field — the point of the component. */
function Host({
  initial = 0,
  label,
  ...props
}: React.ComponentProps<typeof MoneyField> & { initial?: number; label?: string }) {
  const [minor, setMinor] = useState(initial);
  // The symbol addon is aria-hidden, so the label IS the field's accessible
  // name — an unlinked <label> leaves it nameless to a screen reader.
  const id = useId();
  return (
    <div className="w-56 space-y-2">
      {label ? (
        <label htmlFor={id} className="text-sm font-medium">
          {label}
        </label>
      ) : null}
      <MoneyField {...props} id={id} value={minor} onValueChange={setMinor} />
      <p className="text-muted-foreground text-xs">
        stored: <code className="font-mono">{minor}</code>{" "}
        {props.fractionDigits === 0 ? "whole units" : "minor units"}
      </p>
    </div>
  );
}

export const Default: Story = {
  render: (args) => <Host {...args} initial={1999} label="Price" />,
};

/**
 * Type into this one. Digits fill from the right — press `1`, `9`, `9` and it
 * reads $1.99. There is never a caret sitting "before the decimal point",
 * which is the state that makes most currency inputs confusing.
 */
export const TillStyleEntry: Story = {
  render: (args) => <Host {...args} initial={0} label="Start empty and type" />,
};

/**
 * Cross 1,000 while typing and watch the caret. Inserting a thousands
 * separator shifts every character after it, so restoring the caret by string
 * offset moves it a place — the single most common defect in a currency input.
 * This restores by digit count instead, so the caret stays where it looks.
 */
export const CaretSurvivesGrouping: Story = {
  render: (args) => <Host {...args} initial={99999} label="Add a digit at the end" />,
};

/**
 * ¥500 is five hundred yen, not five. Formatting a zero-decimal currency with
 * two decimals inflates every amount by 100× — and the result still reads as a
 * plausible price, which is why it survives review.
 */
export const ZeroDecimalCurrency: Story = {
  render: () => (
    <div className="space-y-6">
      <Host currency="USD" initial={50000} label="USD — 50000 minor units" />
      <Host currency="JPY" locale="ja-JP" initial={50000} label="JPY — same 50000" />
    </div>
  ),
};

/**
 * The decimal mark is a comma across most of Europe. Separators come from
 * `Intl`, not from a constant — guessing means "1.234" reads as either 1.234
 * or 1234 depending on the user, with nothing on screen to say which.
 */
export const Locales: Story = {
  render: () => (
    <div className="space-y-6">
      <Host currency="USD" locale="en-US" initial={123456} label="en-US" />
      <Host currency="EUR" locale="de-DE" initial={123456} label="de-DE" />
      <Host currency="EUR" locale="fr-FR" initial={123456} label="fr-FR" />
      <Host currency="INR" locale="en-IN" initial={12345678} label="en-IN (lakh grouping)" />
    </div>
  ),
};

/** Entry beyond `max` is ignored rather than clamped after the fact. */
export const Capped: Story = {
  render: (args) => <Host {...args} max={10000} initial={0} label="Capped at $100.00" />,
};

/** Drop the symbol when the label already carries the unit. */
export const WithoutSymbol: Story = {
  render: (args) => (
    <Host {...args} showSymbol={false} initial={2500} label="Amount (USD)" />
  ),
};

/**
 * Whole amounts, for money that is large rather than paid.
 *
 * A property asking price has no cents: the two zeros are something the reader
 * looks past and, because entry is right-anchored, two extra keystrokes.
 * `fractionDigits={0}` also changes what `value` means — dollars here, not
 * cents — so the stored figure below reads 1400000, not 140000000.
 */
export const WholeAmounts: Story = {
  render: () => (
    <div className="space-y-6">
      <Host currency="USD" fractionDigits={0} initial={1400000} label="Asking price" />
      <Host currency="USD" initial={140000000} label="The same amount, with cents" />
    </div>
  ),
};

export const Disabled: Story = {
  render: (args) => <Host {...args} disabled initial={4999} label="Disabled" />,
};
