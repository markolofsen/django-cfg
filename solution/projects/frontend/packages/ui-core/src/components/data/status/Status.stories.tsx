import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Status,
  StatusIndicator,
  StatusLabel,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Data/Status',
  component: Status,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component: 'A status badge with animated indicator dot and label.',
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'success', 'error', 'warning', 'info'],
    },
  },
} satisfies Meta<typeof Status>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => (
    <Status>
      <StatusIndicator />
      <StatusLabel>Default</StatusLabel>
    </Status>
  ),
};

export const Variants: Story = {
  render: () => (
    <div className="flex flex-wrap gap-3">
      <Status variant="default">
        <StatusIndicator />
        <StatusLabel>Default</StatusLabel>
      </Status>
      <Status variant="success">
        <StatusIndicator />
        <StatusLabel>Success</StatusLabel>
      </Status>
      <Status variant="error">
        <StatusIndicator />
        <StatusLabel>Error</StatusLabel>
      </Status>
      <Status variant="warning">
        <StatusIndicator />
        <StatusLabel>Warning</StatusLabel>
      </Status>
      <Status variant="info">
        <StatusIndicator />
        <StatusLabel>Info</StatusLabel>
      </Status>
    </div>
  ),
};

export const WithoutIndicator: Story = {
  render: () => (
    <Status variant="success">
      <StatusLabel>Completed</StatusLabel>
    </Status>
  ),
};

export const CustomLabel: Story = {
  render: () => (
    <div className="flex flex-wrap gap-3">
      <Status variant="success">
        <StatusIndicator />
        <StatusLabel>Online</StatusLabel>
      </Status>
      <Status variant="warning">
        <StatusIndicator />
        <StatusLabel>Maintenance</StatusLabel>
      </Status>
      <Status variant="error">
        <StatusIndicator />
        <StatusLabel>Offline</StatusLabel>
      </Status>
      <Status variant="info">
        <StatusIndicator />
        <StatusLabel>Deploying</StatusLabel>
      </Status>
    </div>
  ),
};
