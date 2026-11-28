import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Label,
  RadioGroup,
  RadioGroupItem,
} from '@djangocfg/ui-core/components';

const meta: Meta<typeof RadioGroup> = {
  title: 'Packages/UI Core/Forms/RadioGroup',
  component: RadioGroup,
  tags: ['autodocs'],
};

export default meta;

type Story = StoryObj<typeof RadioGroup>;

export const Default: Story = {
  render: () => (
    <RadioGroup defaultValue="balanced" className="grid gap-2">
      {[
        { value: 'fast', label: 'Fast — less accurate' },
        { value: 'balanced', label: 'Balanced (default)' },
        { value: 'accurate', label: 'Accurate — slower' },
      ].map((o) => (
        <div key={o.value} className="flex items-center gap-2">
          <RadioGroupItem value={o.value} id={`r-${o.value}`} />
          <Label htmlFor={`r-${o.value}`}>{o.label}</Label>
        </div>
      ))}
    </RadioGroup>
  ),
};

export const Horizontal: Story = {
  render: () => (
    <RadioGroup defaultValue="card" className="flex gap-4">
      {[
        { value: 'card', label: 'Card' },
        { value: 'paypal', label: 'PayPal' },
        { value: 'apple', label: 'Apple Pay' },
      ].map((o) => (
        <div key={o.value} className="flex items-center space-x-2">
          <RadioGroupItem value={o.value} id={`h-${o.value}`} />
          <Label htmlFor={`h-${o.value}`}>{o.label}</Label>
        </div>
      ))}
    </RadioGroup>
  ),
};

export const Disabled: Story = {
  render: () => (
    <RadioGroup defaultValue="option-1" disabled className="grid gap-2">
      {['option-1', 'option-2'].map((v) => (
        <div key={v} className="flex items-center space-x-2">
          <RadioGroupItem value={v} id={`d-${v}`} />
          <Label htmlFor={`d-${v}`}>{v}</Label>
        </div>
      ))}
    </RadioGroup>
  ),
};

export const WithDescriptions: Story = {
  render: () => (
    <RadioGroup defaultValue="startup" className="space-y-4">
      {[
        { value: 'startup', label: 'Startup', desc: 'Perfect for small teams.' },
        { value: 'business', label: 'Business', desc: 'Growing businesses.' },
        { value: 'enterprise', label: 'Enterprise', desc: 'Custom for orgs.' },
      ].map((p) => (
        <div key={p.value} className="flex items-start space-x-3">
          <RadioGroupItem value={p.value} id={`p-${p.value}`} className="mt-1" />
          <div>
            <Label htmlFor={`p-${p.value}`} className="font-medium">
              {p.label}
            </Label>
            <p className="text-sm text-muted-foreground">{p.desc}</p>
          </div>
        </div>
      ))}
    </RadioGroup>
  ),
};
