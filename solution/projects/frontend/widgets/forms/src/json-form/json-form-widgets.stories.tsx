import type { Meta, StoryObj } from '@storybook/react-vite';
import { LazyJsonSchemaForm as JsonSchemaForm } from './lazy';
import type { RJSFSchema, UiSchema } from '@rjsf/utils';

interface WidgetHostProps {
  schema: RJSFSchema;
  uiSchema?: UiSchema;
  formData?: unknown;
}

function WidgetHost({ schema, uiSchema, formData }: WidgetHostProps) {
  return (
    <div className="w-[420px] rounded-lg border border-border bg-card p-4 text-card-foreground">
      <JsonSchemaForm
        schema={schema}
        uiSchema={uiSchema}
        formData={formData}
        showSubmitButton={false}
      />
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/JSON form/Widgets',
  component: WidgetHost,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Standalone showcase for each custom widget shipped with `JsonSchemaForm`. Every story uses a single-property schema so the widget renders in isolation.',
      },
    },
  },
} satisfies Meta<typeof WidgetHost>;

export default meta;

type Story = StoryObj<typeof meta>;

const wrap = (
  prop: RJSFSchema,
  name: string = 'value',
  uiSchema?: UiSchema,
): { schema: RJSFSchema; uiSchema?: UiSchema } => ({
  schema: {
    type: 'object',
    properties: { [name]: prop },
  },
  uiSchema: uiSchema ? { [name]: uiSchema } : undefined,
});

export const Text: Story = {
  args: wrap({ type: 'string', title: 'Display name' }, 'name'),
};

export const Textarea: Story = {
  args: wrap(
    { type: 'string', title: 'Description' },
    'description',
    { 'ui:widget': 'textarea' },
  ),
};

export const Number: Story = {
  args: wrap(
    { type: 'integer', title: 'Count', minimum: 0, maximum: 100 },
    'count',
  ),
};

export const Slider: Story = {
  args: wrap(
    { type: 'integer', title: 'Progress', minimum: 0, maximum: 100, default: 40 },
    'progress',
    { 'ui:widget': 'slider', 'ui:options': { unit: '%', step: 5 } },
  ),
};

export const Select: Story = {
  args: wrap(
    {
      type: 'string',
      title: 'Plan',
      enum: ['free', 'pro', 'enterprise'],
      default: 'pro',
    },
    'plan',
  ),
};

export const Radio: Story = {
  args: wrap(
    {
      type: 'string',
      title: 'Plan',
      enum: ['free', 'pro', 'enterprise'],
      default: 'pro',
    },
    'plan',
    { 'ui:widget': 'radio' },
  ),
};

export const Checkbox: Story = {
  args: wrap(
    { type: 'boolean', title: 'Accept terms' },
    'accept',
    { 'ui:widget': 'checkbox' },
  ),
};

export const Switch: Story = {
  args: wrap(
    { type: 'boolean', title: 'Enable notifications', default: true },
    'notifications',
    { 'ui:widget': 'switch' },
  ),
};

export const Color: Story = {
  args: wrap(
    { type: 'string', title: 'Accent color', default: '#3b82f6' },
    'color',
    { 'ui:widget': 'color' },
  ),
};
