import type { Meta, StoryObj } from '@storybook/react-vite';
import { ChevronRight, Mail, Plus, Send, Trash2 } from 'lucide-react';
import { expect, fn, userEvent, within } from 'storybook/test';
import { Button, ButtonLink } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/Button',
  component: Button,
  tags: ['autodocs', 'contract'],
  parameters: {
    a11y: { test: 'error' },
    docs: {
      description: {
        component:
          'Token-driven button. All variants react to the theme toggle — flip it from the toolbar to see dark mode.',
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'xs', 'lg', 'huge', 'icon'],
    },
    loading: { control: 'boolean' },
    disabled: { control: 'boolean' },
    elevated: {
      control: 'boolean',
      description:
        'Keep the variant’s baked-in shadow. Set false to flatten controls grouped inside a card/panel (e.g. table pagination).',
    },
  },
  args: {
    children: 'Click me',
    variant: 'default',
    size: 'default',
  },
} satisfies Meta<typeof Button>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: { onClick: fn() },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button', { name: 'Click me' }));
    await expect(args.onClick).toHaveBeenCalledOnce();
  },
};

export const Destructive: Story = {
  args: { variant: 'destructive', children: 'Delete' },
  // Shared destructive token is 3.65:1 in the current macOS preset.
  parameters: { a11y: { test: 'todo' } },
};

export const Outline: Story = {
  args: { variant: 'outline', children: 'Outline' },
};

export const Variants: Story = {
  parameters: { a11y: { test: 'todo' } },
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Button variant="default">Default</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="outline">Outline</Button>
      <Button variant="ghost">Ghost</Button>
      <Button variant="link">Link</Button>
      <Button variant="destructive">Destructive</Button>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <Button size="xs">XS</Button>
      <Button size="sm">SM</Button>
      <Button size="default">Default</Button>
      <Button size="lg">LG</Button>
      <Button size="huge">Huge</Button>
      <Button size="icon" aria-label="Add">
        <Plus />
      </Button>
    </div>
  ),
};

export const Elevation: Story = {
  parameters: { a11y: { test: 'todo' } },
  render: () => (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className="w-28 text-sm text-muted-foreground">elevated (default)</span>
        <Button variant="default">Default</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="outline">Outline</Button>
        <Button variant="destructive">Destructive</Button>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <span className="w-28 text-sm text-muted-foreground">elevated={'{false}'}</span>
        <Button variant="default" elevated={false}>
          Default
        </Button>
        <Button variant="secondary" elevated={false}>
          Secondary
        </Button>
        <Button variant="outline" elevated={false}>
          Outline
        </Button>
        <Button variant="destructive" elevated={false}>
          Destructive
        </Button>
      </div>
    </div>
  ),
};

export const Loading: Story = {
  args: { loading: true, children: 'Saving…' },
};

export const Disabled: Story = {
  args: { disabled: true, children: 'Disabled' },
};

export const WithIcons: Story = {
  parameters: { a11y: { test: 'todo' } },
  render: () => (
    <div className="flex flex-wrap gap-2">
      <Button>
        <Mail />
        Login with Email
      </Button>
      <Button variant="secondary">
        Send
        <Send />
      </Button>
      <Button variant="outline">
        Next
        <ChevronRight />
      </Button>
      <Button variant="destructive">
        <Trash2 />
        Delete
      </Button>
    </div>
  ),
};

export const AsLink: Story = {
  render: () => (
    <div className="flex flex-wrap gap-2">
      <ButtonLink href="https://example.com">External Link</ButtonLink>
      <ButtonLink href="/dashboard" variant="secondary">
        Dashboard
      </ButtonLink>
      <ButtonLink href="/settings" variant="outline">
        Settings
      </ButtonLink>
    </div>
  ),
};

/**
 * `ButtonLink` is an `<a>`, which has no native `disabled`. We emulate the
 * shadcn pattern: `aria-disabled` + `tabIndex={-1}` + `pointer-events-none
 * opacity-50` and the click is cancelled, so it can't navigate. `loading` adds
 * the same inert state plus a spinner — parity with `<Button>`.
 */
export const LinkStates: Story = {
  name: 'AsLink — disabled / loading',
  render: () => (
    <div className="flex flex-wrap items-center gap-2">
      <ButtonLink href="/dashboard">Enabled</ButtonLink>
      <ButtonLink href="/dashboard" disabled>
        Disabled
      </ButtonLink>
      <ButtonLink href="/dashboard" loading>
        Loading…
      </ButtonLink>
      <ButtonLink href="/dashboard" variant="outline" disabled>
        Disabled outline
      </ButtonLink>
    </div>
  ),
};
