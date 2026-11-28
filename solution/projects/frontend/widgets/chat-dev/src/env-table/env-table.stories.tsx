import type { Meta, StoryObj } from '@storybook/react-vite';
import { EnvTable, type EnvVariable } from '.';

const SAMPLE: EnvVariable[] = [
  {
    key: 'DATABASE_URL',
    value: 'postgresql://demo:example@db.internal:5432/app',
    environment: 'production',
    description: 'Primary Postgres connection string.',
    required: true,
  },
  {
    key: 'STRIPE_SECRET_KEY',
    value: 'example-stripe-secret-not-a-credential',
    environment: 'production',
    required: true,
  },
  {
    key: 'NEXT_PUBLIC_API_URL',
    value: 'https://api.example.com',
    environment: 'preview',
    description: 'Exposed to the browser bundle.',
  },
  {
    key: 'DEBUG',
    value: 'app:*',
    environment: 'development',
  },
  {
    key: 'FEATURE_X',
    value: 'on',
  },
];

const SECRETS: EnvVariable[] = [
  {
    key: 'AWS_SECRET_ACCESS_KEY',
    value: 'example-aws-secret-not-a-credential',
    environment: 'production',
    required: true,
  },
  {
    key: 'OPENAI_API_KEY',
    value: 'example-api-key-not-a-credential',
    environment: 'production',
    required: true,
    description: 'Used by the chat agent. Rotate every 90 days.',
  },
  {
    key: 'JWT_SIGNING_SECRET',
    value: 'super-long-jwt-signing-secret-value-do-not-leak',
    environment: 'production',
    required: true,
  },
];

const meta = {
  title: 'Widgets/Chat Dev/EnvTable',
  component: EnvTable,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Read-only environment variable table with masked values, click-to-reveal, and per-row copy. Semantic tokens only; secrets stay in JS until reveal — the raw value is never written to the DOM in masked state. Requires `<UiProviders>` at the host root.',
      },
    },
  },
  argTypes: {
    title: { control: 'text' },
    defaultRevealed: { control: 'boolean' },
    emptyLabel: { control: 'text' },
  },
} satisfies Meta<typeof EnvTable>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    title: 'Environment',
    variables: SAMPLE,
  },
};

export const WithSecrets: Story = {
  args: {
    title: 'Production secrets',
    variables: SECRETS,
  },
};

export const AllRevealed: Story = {
  args: {
    title: 'Environment (revealed)',
    variables: SAMPLE,
    defaultRevealed: true,
  },
};

export const Empty: Story = {
  args: {
    variables: [],
    emptyLabel: 'No environment variables configured.',
  },
};
