import type { Meta, StoryObj } from '@storybook/react-vite';
import { Section, SectionHeader } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/Section',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Section>
      <p className="text-center text-muted-foreground">
        A plain section with default padding and background.
      </p>
    </Section>
  ),
};

export const WithHeader: Story = {
  render: () => (
    <Section>
      <SectionHeader
        title="Build faster with djangocfg"
        subtitle="Compose backends with typed configs, generated SDKs, and a UI kit that gets out of the way."
      />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {['Config', 'SDK', 'UI'].map((label) => (
          <div
            key={label}
            className="rounded-lg border bg-card p-6 text-center"
          >
            <div className="text-lg font-semibold">{label}</div>
            <p className="mt-2 text-sm text-muted-foreground">
              Description for {label}.
            </p>
          </div>
        ))}
      </div>
    </Section>
  ),
};

export const Variants: Story = {
  render: () => (
    <div className="space-y-4">
      {(['default', 'dark', 'gradient', 'card'] as const).map((variant) => (
        <Section key={variant} variant={variant}>
          <SectionHeader
            title={`Variant: ${variant}`}
            subtitle="Same content, different background treatment."
          />
        </Section>
      ))}
    </div>
  ),
};
