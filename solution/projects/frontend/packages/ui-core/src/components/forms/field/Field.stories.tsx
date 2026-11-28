import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Field,
  FieldContent,
  FieldDescription,
  FieldError,
  FieldLabel,
  Input,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/Field',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Higher-level wrapper around an input — bundles label + description + error message. Use with the `Form` primitive when binding to react-hook-form.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Field className="w-80">
      <FieldLabel htmlFor="email">Email</FieldLabel>
      <FieldContent>
        <Input id="email" placeholder="you@example.com" />
        <FieldDescription>We&apos;ll send a confirmation link.</FieldDescription>
      </FieldContent>
    </Field>
  ),
};

export const WithError: Story = {
  render: () => (
    <Field className="w-80">
      <FieldLabel htmlFor="pwd">Password</FieldLabel>
      <FieldContent>
        <Input id="pwd" type="password" aria-invalid defaultValue="123" />
        <FieldError>Password must be at least 8 characters.</FieldError>
      </FieldContent>
    </Field>
  ),
};
