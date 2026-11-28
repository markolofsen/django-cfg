import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Label,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Forms/Select',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'Radix-based select with theme-aware trigger and listbox. For a searchable variant use `<Combobox>`.',
      },
    },
  },
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <div className="w-64">
      <Select defaultValue="apple">
        <SelectTrigger>
          <SelectValue placeholder="Pick a fruit" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="apple">Apple</SelectItem>
          <SelectItem value="banana">Banana</SelectItem>
          <SelectItem value="cherry">Cherry</SelectItem>
        </SelectContent>
      </Select>
    </div>
  ),
};

export const WithLabel: Story = {
  render: () => (
    <div className="grid w-64 gap-1.5">
      <Label htmlFor="lang">Language</Label>
      <Select defaultValue="ru-RU">
        <SelectTrigger id="lang">
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="en-US">English (US)</SelectItem>
          <SelectItem value="ru-RU">Русский</SelectItem>
          <SelectItem value="ko-KR">한국어</SelectItem>
        </SelectContent>
      </Select>
    </div>
  ),
};

export const Disabled: Story = {
  render: () => (
    <div className="w-64">
      <Select disabled>
        <SelectTrigger>
          <SelectValue placeholder="Disabled" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="a">A</SelectItem>
        </SelectContent>
      </Select>
    </div>
  ),
};
