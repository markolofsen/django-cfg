import type { Meta, StoryObj } from '@storybook/react-vite';
import { Bell, ChevronRight, FileText, Folder, User } from 'lucide-react';
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Badge,
  Button,
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemMedia,
  ItemSeparator,
  ItemTitle,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Specialized/Item',
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          'List-item primitive with media / content / actions slots. Compose into ItemGroup for vertical lists.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <div className="w-[420px]">
      <Item>
        <ItemContent>
          <ItemTitle>Plain item</ItemTitle>
          <ItemDescription>
            A bare item with title and description, no media.
          </ItemDescription>
        </ItemContent>
      </Item>
    </div>
  ),
};

export const WithIcon: Story = {
  render: () => (
    <div className="w-[420px]">
      <Item variant="outline">
        <ItemMedia variant="icon">
          <Folder />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Projects</ItemTitle>
          <ItemDescription>12 folders, 84 files</ItemDescription>
        </ItemContent>
        <ItemActions>
          <ChevronRight className="text-muted-foreground size-4" />
        </ItemActions>
      </Item>
    </div>
  ),
};

export const WithAvatar: Story = {
  render: () => (
    <div className="w-[420px]">
      <Item variant="outline">
        <ItemMedia variant="image">
          <Avatar>
            <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
            <AvatarFallback>SC</AvatarFallback>
          </Avatar>
        </ItemMedia>
        <ItemContent>
          <ItemTitle>shadcn</ItemTitle>
          <ItemDescription>Building things on the web.</ItemDescription>
        </ItemContent>
        <ItemActions>
          <Button size="sm" variant="outline">
            Follow
          </Button>
        </ItemActions>
      </Item>
    </div>
  ),
};

export const WithBadge: Story = {
  render: () => (
    <div className="w-[420px]">
      <Item variant="outline">
        <ItemMedia variant="icon">
          <Bell />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>
            Notifications <Badge variant="secondary">3 new</Badge>
          </ItemTitle>
          <ItemDescription>You have unread notifications.</ItemDescription>
        </ItemContent>
      </Item>
    </div>
  ),
};

export const Variants: Story = {
  render: () => (
    <div className="flex w-[420px] flex-col gap-3">
      <Item variant="default">
        <ItemContent>
          <ItemTitle>Default</ItemTitle>
          <ItemDescription>Transparent background</ItemDescription>
        </ItemContent>
      </Item>
      <Item variant="outline">
        <ItemContent>
          <ItemTitle>Outline</ItemTitle>
          <ItemDescription>Bordered card-like item</ItemDescription>
        </ItemContent>
      </Item>
      <Item variant="muted">
        <ItemContent>
          <ItemTitle>Muted</ItemTitle>
          <ItemDescription>Subtle filled background</ItemDescription>
        </ItemContent>
      </Item>
    </div>
  ),
};

export const Sizes: Story = {
  render: () => (
    <div className="flex w-[420px] flex-col gap-3">
      <Item variant="outline" size="default">
        <ItemMedia variant="icon">
          <FileText />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Default size</ItemTitle>
          <ItemDescription>p-4, gap-4</ItemDescription>
        </ItemContent>
      </Item>
      <Item variant="outline" size="sm">
        <ItemMedia variant="icon">
          <FileText />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Small size</ItemTitle>
          <ItemDescription>px-4 py-3, gap-2.5</ItemDescription>
        </ItemContent>
      </Item>
    </div>
  ),
};

export const Group: Story = {
  render: () => (
    <ItemGroup className="w-[420px] overflow-hidden rounded-md border">
      <Item>
        <ItemMedia variant="icon">
          <User />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Profile</ItemTitle>
          <ItemDescription>Manage your account</ItemDescription>
        </ItemContent>
        <ItemActions>
          <ChevronRight className="text-muted-foreground size-4" />
        </ItemActions>
      </Item>
      <ItemSeparator />
      <Item>
        <ItemMedia variant="icon">
          <Bell />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Notifications</ItemTitle>
          <ItemDescription>Email, push, SMS</ItemDescription>
        </ItemContent>
        <ItemActions>
          <ChevronRight className="text-muted-foreground size-4" />
        </ItemActions>
      </Item>
      <ItemSeparator />
      <Item>
        <ItemMedia variant="icon">
          <Folder />
        </ItemMedia>
        <ItemContent>
          <ItemTitle>Storage</ItemTitle>
          <ItemDescription>4.2 GB of 15 GB used</ItemDescription>
        </ItemContent>
        <ItemActions>
          <ChevronRight className="text-muted-foreground size-4" />
        </ItemActions>
      </Item>
    </ItemGroup>
  ),
};

export const AsLink: Story = {
  render: () => (
    <div className="w-[420px]">
      <Item variant="outline" asChild>
        <a href="#item-link">
          <ItemMedia variant="icon">
            <FileText />
          </ItemMedia>
          <ItemContent>
            <ItemTitle>Whole row clickable</ItemTitle>
            <ItemDescription>
              Item rendered as anchor via asChild
            </ItemDescription>
          </ItemContent>
          <ItemActions>
            <ChevronRight className="text-muted-foreground size-4" />
          </ItemActions>
        </a>
      </Item>
    </div>
  ),
};
