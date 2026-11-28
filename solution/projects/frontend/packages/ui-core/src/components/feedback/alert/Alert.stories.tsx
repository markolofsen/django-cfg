import type { Meta, StoryObj } from '@storybook/react-vite';
import { AlertCircle, AlertTriangle, CheckCircle2, Info, Terminal } from 'lucide-react';
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Feedback/Alert',
  component: Alert,
  tags: ['autodocs'],
  argTypes: {
    variant: { control: 'select', options: ['default', 'destructive'] },
  },
} satisfies Meta<typeof Alert>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Alert className="w-[420px]">
      <Terminal className="h-4 w-4" />
      <AlertTitle>Heads up!</AlertTitle>
      <AlertDescription>
        You can add components to your app using the CLI.
      </AlertDescription>
    </Alert>
  ),
};

export const Destructive: Story = {
  render: () => (
    <Alert variant="destructive" className="w-[420px]">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Error</AlertTitle>
      <AlertDescription>
        Your session has expired. Please log in again.
      </AlertDescription>
    </Alert>
  ),
};

export const Success: Story = {
  render: () => (
    <Alert className="w-[420px] border-success-border text-success-foreground [&>svg]:text-success-foreground">
      <CheckCircle2 className="h-4 w-4" />
      <AlertTitle>Success</AlertTitle>
      <AlertDescription>Your changes have been saved successfully.</AlertDescription>
    </Alert>
  ),
};

export const Warning: Story = {
  render: () => (
    <Alert className="w-[420px] border-warning-border text-warning-foreground [&>svg]:text-warning-foreground">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>Warning</AlertTitle>
      <AlertDescription>Your subscription will expire in 3 days.</AlertDescription>
    </Alert>
  ),
};

export const WithoutIcon: Story = {
  render: () => (
    <Alert className="w-[420px]">
      <AlertTitle>Note</AlertTitle>
      <AlertDescription>You can also use alerts without icons.</AlertDescription>
    </Alert>
  ),
};

export const Stack: Story = {
  render: () => (
    <div className="grid w-[420px] gap-3">
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Info</AlertTitle>
        <AlertDescription>Update available — v2.0.4.</AlertDescription>
      </Alert>
      <Alert>
        <CheckCircle2 className="h-4 w-4" />
        <AlertTitle>Success</AlertTitle>
        <AlertDescription>Profile saved.</AlertDescription>
      </Alert>
    </div>
  ),
};
