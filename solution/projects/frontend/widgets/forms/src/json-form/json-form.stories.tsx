import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import { LazyJsonSchemaForm as JsonSchemaForm } from './lazy';
import { ObjectFieldTemplate, evaluateDisabledWhen } from '.';
import type { RJSFSchema, UiSchema } from '@rjsf/utils';

const simpleSchema: RJSFSchema = {
  title: 'Account',
  type: 'object',
  required: ['email'],
  properties: {
    name: { type: 'string', title: 'Display name' },
    email: { type: 'string', title: 'Email', format: 'email' },
    age: { type: 'integer', title: 'Age', minimum: 13, maximum: 120 },
    newsletter: {
      type: 'boolean',
      title: 'Subscribe to the newsletter',
      default: true,
    },
  },
};

const nestedSchema: RJSFSchema = {
  title: 'Project',
  type: 'object',
  required: ['name'],
  properties: {
    name: { type: 'string', title: 'Project name' },
    visibility: {
      type: 'string',
      title: 'Visibility',
      enum: ['public', 'private', 'internal'],
      default: 'private',
    },
    members: {
      type: 'array',
      title: 'Members',
      items: {
        type: 'object',
        properties: {
          email: { type: 'string', format: 'email' },
          role: { type: 'string', enum: ['admin', 'editor', 'viewer'] },
        },
      },
    },
  },
};

const nestedUi: UiSchema = {
  'ui:submitButtonOptions': { submitText: 'Save project' },
  members: { 'ui:options': { orderable: false } },
};

const allWidgetsSchema: RJSFSchema = {
  title: 'All Widgets',
  type: 'object',
  properties: {
    text: { type: 'string', title: 'Text' },
    description: { type: 'string', title: 'Description' },
    count: { type: 'integer', title: 'Count', minimum: 0, maximum: 100 },
    progress: { type: 'integer', title: 'Progress', minimum: 0, maximum: 100, default: 40 },
    color: { type: 'string', title: 'Color', default: '#3b82f6' },
    plan: {
      type: 'string',
      title: 'Plan',
      enum: ['free', 'pro', 'enterprise'],
      default: 'pro',
    },
    enabled: { type: 'boolean', title: 'Enabled', default: true },
    accept: { type: 'boolean', title: 'Accept terms' },
  },
};

const allWidgetsUi: UiSchema = {
  description: { 'ui:widget': 'textarea' },
  progress: { 'ui:widget': 'slider', 'ui:options': { unit: '%', step: 5 } },
  color: { 'ui:widget': 'color' },
  enabled: { 'ui:widget': 'switch' },
  accept: { 'ui:widget': 'checkbox' },
};

const conditionalSchema: RJSFSchema = {
  title: 'Contact',
  type: 'object',
  required: ['firstName'],
  properties: {
    firstName: { type: 'string', title: 'First name' },
    email: { type: 'string', title: 'Email', format: 'email' },
    subscribe: { type: 'boolean', title: 'Subscribe to newsletter' },
    phone: { type: 'string', title: 'Phone' },
  },
};

const conditionalUi: UiSchema = {
  email: { 'ui:disabledWhen': { path: 'firstName', falsy: true } },
  subscribe: { 'ui:widget': 'switch' },
  phone: { 'ui:disabledWhen': { path: 'subscribe', falsy: true } },
};

interface FormHostProps {
  schema: RJSFSchema;
  uiSchema?: UiSchema;
  formData?: unknown;
  liveValidate?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  showErrorList?: false | 'top' | 'bottom';
}

function FormHost({
  schema,
  uiSchema,
  formData,
  liveValidate,
  disabled,
  readonly,
  showErrorList,
}: FormHostProps) {
  return (
    <div className="w-[520px] rounded-lg border border-border bg-card p-4 text-card-foreground">
      <JsonSchemaForm
        schema={schema}
        uiSchema={uiSchema}
        formData={formData}
        liveValidate={liveValidate}
        disabled={disabled}
        readonly={readonly}
        showErrorList={showErrorList}
        onSubmit={(data) => {
          alert(JSON.stringify(data.formData, null, 2));
        }}
      />
    </div>
  );
}

const meta = {
  title: 'Widgets/Forms/JSON form/Overview',
  component: FormHost,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'Schema-driven dynamic form (RJSF) wrapped with ui-core widgets. Supply a JSON Schema; the form renders inputs, validation, and a submit button.',
      },
    },
  },
  argTypes: {
    liveValidate: {
      control: 'boolean',
      table: { category: 'Behaviour' },
      description: 'Validate on every change instead of only on submit.',
    },
    disabled: {
      control: 'boolean',
      table: { category: 'Behaviour' },
      description: 'Disable all inputs.',
    },
    readonly: {
      control: 'boolean',
      table: { category: 'Behaviour' },
      description: 'Render inputs as read-only.',
    },
    showErrorList: {
      control: 'select',
      options: [false, 'top', 'bottom'],
      table: { category: 'Behaviour' },
      description: 'Position of the aggregated error list.',
    },
  },
} satisfies Meta<typeof FormHost>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Playground: Story = {
  args: {
    schema: simpleSchema,
    liveValidate: false,
    disabled: false,
    readonly: false,
    showErrorList: false,
  },
};

export const Simple: Story = {
  args: { schema: simpleSchema, liveValidate: false },
};

export const Validated: Story = {
  args: { schema: simpleSchema, liveValidate: true, showErrorList: 'top' },
};

export const Nested: Story = {
  args: { schema: nestedSchema, uiSchema: nestedUi },
};

export const AllWidgets: Story = {
  args: { schema: allWidgetsSchema, uiSchema: allWidgetsUi },
  parameters: {
    docs: {
      description: {
        story:
          'Single schema exercising every custom widget: text, textarea, number, slider, color, select, switch, checkbox.',
      },
    },
  },
};

/**
 * `ui:disabledWhen` greys out a field based on another field's value.
 * `email` is disabled until `firstName` has a value; `phone` is disabled
 * until `subscribe` is toggled on. Demonstrates `evaluateDisabledWhen`
 * driving the conditional state inside the form.
 */
export const Conditional: Story = {
  args: { schema: conditionalSchema, uiSchema: conditionalUi },
  render: () => {
    function ConditionalHost() {
      const [data, setData] = useState<Record<string, unknown>>({
        firstName: '',
        subscribe: false,
      });
      const emailDisabled = evaluateDisabledWhen(
        { path: 'firstName', falsy: true },
        data,
      );
      return (
        <div className="w-[520px] space-y-3 rounded-lg border border-border bg-card p-4 text-card-foreground">
          <JsonSchemaForm
            schema={conditionalSchema}
            uiSchema={conditionalUi}
            formData={data}
            onChange={(e) => setData((e.formData as Record<string, unknown>) ?? {})}
            showSubmitButton={false}
          />
          <pre className="text-[11px] text-muted-foreground">
            {`emailDisabled (via evaluateDisabledWhen) = ${String(emailDisabled)}`}
          </pre>
        </div>
      );
    }
    return <ConditionalHost />;
  },
};

export const ReadOnly: Story = {
  args: {
    schema: simpleSchema,
    formData: {
      name: 'Ada Lovelace',
      email: 'ada@analytical-engine.io',
      age: 36,
      newsletter: true,
    },
    readonly: true,
  },
};

/**
 * Swap the `ObjectFieldTemplate` to render a card-style heading above
 * the fields. Public template exports allow consumers to extend the
 * default layout without touching internals.
 */
export const WithCustomTemplate: Story = {
  args: { schema: simpleSchema },
  render: () => (
    <div className="w-[520px] rounded-lg border border-border bg-card p-4 text-card-foreground">
      <JsonSchemaForm
        schema={simpleSchema}
        templates={{
          ObjectFieldTemplate: (props) => (
            <div className="space-y-3">
              <div className="rounded-md bg-muted/50 px-3 py-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Custom template wrapper
              </div>
              <ObjectFieldTemplate {...props} />
            </div>
          ),
        }}
      />
    </div>
  ),
};
