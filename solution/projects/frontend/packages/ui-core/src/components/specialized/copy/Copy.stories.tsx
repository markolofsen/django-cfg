import type { Meta, StoryObj } from '@storybook/react-vite';
import { CopyButton, CopyField } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Specialized/Copy',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Button: Story = {
  render: () => <CopyButton value="Hello, World!" />,
};

export const ButtonWithText: Story = {
  render: () => (
    <CopyButton value="npm install @djangocfg/ui-core">
      Copy command
    </CopyButton>
  ),
};

export const ButtonVariants: Story = {
  render: () => (
    <div className="flex gap-2">
      <CopyButton value="Text" variant="default" />
      <CopyButton value="Text" variant="outline" />
      <CopyButton value="Text" variant="ghost" />
    </div>
  ),
};

export const ButtonSizes: Story = {
  render: () => (
    <div className="flex items-center gap-2">
      <CopyButton value="Text" size="sm" />
      <CopyButton value="Text" size="default" />
      <CopyButton value="Text" size="icon" />
    </div>
  ),
};

export const Field: Story = {
  render: () => (
    <div className="w-96">
      <CopyField value="npm install @djangocfg/ui-core" />
    </div>
  ),
};

export const FieldWithLabel: Story = {
  render: () => (
    <div className="w-96 space-y-2">
      <label className="text-sm font-medium">Installation command</label>
      <CopyField value="npm install @djangocfg/ui-core" />
    </div>
  ),
};

export const ApiKey: Story = {
  render: () => (
    <div className="w-96 space-y-2">
      <label className="text-sm font-medium">API Key</label>
      <CopyField value="example-api-key-not-a-credential" />
    </div>
  ),
};

export const URLs: Story = {
  render: () => (
    <div className="w-[420px] space-y-4">
      <div className="space-y-2">
        <label className="text-sm font-medium">Share Link</label>
        <CopyField value="https://example.com/share/abc123" />
      </div>
      <div className="space-y-2">
        <label className="text-sm font-medium">Embed Code</label>
        <CopyField value='<iframe src="https://example.com/embed/abc123"></iframe>' />
      </div>
    </div>
  ),
};

export const InCard: Story = {
  render: () => (
    <div className="w-96 rounded-lg border p-4">
      <h4 className="mb-2 font-medium">Invite Link</h4>
      <p className="mb-4 text-sm text-muted-foreground">
        Share this link with your team.
      </p>
      <CopyField value="https://app.example.com/invite/team-abc123" />
    </div>
  ),
};
