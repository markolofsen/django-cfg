import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  AlignCenter,
  AlignLeft,
  AlignRight,
  Bold,
  ChevronDown,
  Italic,
  Underline,
} from 'lucide-react';
import {
  Button,
  ButtonGroup,
  ButtonGroupSeparator,
  ButtonGroupText,
} from '@djangocfg/ui-core/components';

const meta: Meta<typeof ButtonGroup> = {
  title: 'Packages/UI Core/Forms/ButtonGroup',
  component: ButtonGroup,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Group of buttons rendered with connected styling. Compose with `ButtonGroupSeparator` and `ButtonGroupText` for split actions and labels.',
      },
    },
  },
};

export default meta;

type Story = StoryObj<typeof ButtonGroup>;

export const Default: Story = {
  render: () => (
    <ButtonGroup>
      <Button variant="outline" size="icon">
        <Bold className="h-4 w-4" />
      </Button>
      <Button variant="outline" size="icon">
        <Italic className="h-4 w-4" />
      </Button>
      <Button variant="outline" size="icon">
        <Underline className="h-4 w-4" />
      </Button>
    </ButtonGroup>
  ),
};

export const WithSeparator: Story = {
  render: () => (
    <ButtonGroup>
      <Button variant="outline" size="icon">
        <AlignLeft className="h-4 w-4" />
      </Button>
      <Button variant="outline" size="icon">
        <AlignCenter className="h-4 w-4" />
      </Button>
      <Button variant="outline" size="icon">
        <AlignRight className="h-4 w-4" />
      </Button>
      <ButtonGroupSeparator />
      <Button variant="outline">
        Save
        <ChevronDown className="ml-1 h-4 w-4" />
      </Button>
    </ButtonGroup>
  ),
};

export const WithText: Story = {
  render: () => (
    <ButtonGroup>
      <ButtonGroupText>https://</ButtonGroupText>
      <Button variant="outline">example.com</Button>
      <ButtonGroupSeparator />
      <Button variant="outline">Copy</Button>
    </ButtonGroup>
  ),
};

export const Vertical: Story = {
  render: () => (
    <ButtonGroup orientation="vertical">
      <Button variant="outline">Top</Button>
      <Button variant="outline">Middle</Button>
      <Button variant="outline">Bottom</Button>
    </ButtonGroup>
  ),
};
