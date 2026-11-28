import { useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import { ArrowRight, AtSign, Copy, Eye, EyeOff, Mail, Search } from 'lucide-react';
import {
  Button,
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupInput,
  InputGroupText,
  InputGroupTextarea,
  Kbd,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/InputGroup',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Composite input — addons (icons / prefix / suffix / inline button) glued onto an `<Input>` without breaking focus ring.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const WithIcon: Story = {
  render: () => (
    <InputGroup className="w-80">
      <InputGroupAddon>
        <Search className="h-4 w-4 text-muted-foreground" />
      </InputGroupAddon>
      <InputGroupInput placeholder="Search the docs…" />
    </InputGroup>
  ),
};

export const WithPrefix: Story = {
  render: () => (
    <InputGroup className="w-80">
      <InputGroupText>https://</InputGroupText>
      <InputGroupInput placeholder="djangocfg.com" />
    </InputGroup>
  ),
};

function PasswordToggleHost() {
  const [show, setShow] = useState(false);
  return (
    <InputGroup className="w-80">
      <InputGroupInput
        type={show ? 'text' : 'password'}
        placeholder="Enter password"
      />
      <InputGroupAddon align="inline-end">
        <InputGroupButton size="icon-xs" onClick={() => setShow(!show)}>
          {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  );
}

export const PasswordToggle: Story = { render: () => <PasswordToggleHost /> };

export const CopyInput: Story = {
  render: () => (
    <InputGroup className="w-96">
      <InputGroupInput value="npm install @djangocfg/ui-core" readOnly />
      <InputGroupAddon align="inline-end">
        <InputGroupButton size="icon-xs">
          <Copy className="h-4 w-4" />
        </InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  ),
};

export const WithKbd: Story = {
  render: () => (
    <InputGroup className="w-80">
      <InputGroupAddon>
        <Search className="h-4 w-4" />
      </InputGroupAddon>
      <InputGroupInput placeholder="Search…" />
      <InputGroupAddon align="inline-end">
        <Kbd size="xs">⌘K</Kbd>
      </InputGroupAddon>
    </InputGroup>
  ),
};

export const Email: Story = {
  render: () => (
    <InputGroup className="w-80">
      <InputGroupAddon>
        <AtSign className="h-4 w-4" />
      </InputGroupAddon>
      <InputGroupInput type="email" placeholder="you@example.com" />
    </InputGroup>
  ),
};

export const WithTextarea: Story = {
  render: () => (
    <InputGroup className="w-96">
      <InputGroupAddon align="block-start">
        <InputGroupText>Description</InputGroupText>
      </InputGroupAddon>
      <InputGroupTextarea placeholder="Enter description…" rows={4} />
    </InputGroup>
  ),
};

export const BothSides: Story = {
  render: () => (
    <InputGroup className="w-80">
      <InputGroupAddon>
        <Mail className="h-4 w-4" />
      </InputGroupAddon>
      <InputGroupInput placeholder="Enter email" />
      <InputGroupAddon align="inline-end">
        <InputGroupButton>Send</InputGroupButton>
      </InputGroupAddon>
    </InputGroup>
  ),
};

export const WithInlineButton: Story = {
  render: () => (
    <InputGroup className="w-80">
      <InputGroupAddon>
        <Mail className="h-4 w-4 text-muted-foreground" />
      </InputGroupAddon>
      <InputGroupInput placeholder="you@example.com" />
      <InputGroupButton>
        <Button size="sm">
          Send <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      </InputGroupButton>
    </InputGroup>
  ),
};
