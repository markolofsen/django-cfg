import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  Button,
  Input,
  Label,
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/Popover',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const WithForm: Story = {
  render: () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button>Update settings</Button>
      </PopoverTrigger>
      <PopoverContent className="w-72">
        <div className="grid gap-4">
          <div>
            <h4 className="text-sm font-medium">Settings</h4>
            <p className="text-xs text-muted-foreground">
              Configure your preferences.
            </p>
          </div>
          <div className="grid gap-3">
            <div className="grid gap-1.5">
              <Label htmlFor="dname">Display Name</Label>
              <Input id="dname" placeholder="Enter name" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="demail">Email</Label>
              <Input id="demail" type="email" placeholder="Enter email" />
            </div>
            <Button className="w-full">Save</Button>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  ),
};

export const Simple: Story = {
  render: () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm">
          Info
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-64">
        <p className="text-sm">Simple popover with text only.</p>
      </PopoverContent>
    </Popover>
  ),
};

export const Default: Story = {
  render: () => (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline">Open popover</Button>
      </PopoverTrigger>
      <PopoverContent className="w-72">
        <div className="grid gap-3">
          <div>
            <div className="text-sm font-medium">Dimensions</div>
            <p className="text-xs text-muted-foreground">
              Set the canvas size in pixels.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="grid gap-1.5">
              <Label htmlFor="w">Width</Label>
              <Input id="w" defaultValue="1024" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="h">Height</Label>
              <Input id="h" defaultValue="768" />
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  ),
};
