import type { Meta, StoryObj } from '@storybook/react-vite';
import { CalendarDays } from 'lucide-react';
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Button,
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Overlay/HoverCard',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Simple: Story = {
  render: () => (
    <HoverCard>
      <HoverCardTrigger asChild>
        <span className="cursor-pointer text-sm underline">What is this?</span>
      </HoverCardTrigger>
      <HoverCardContent>
        <p className="text-sm">
          A hover card appears when you hover over the trigger.
        </p>
      </HoverCardContent>
    </HoverCard>
  ),
};

export const UserProfile: Story = {
  render: () => (
    <HoverCard>
      <HoverCardTrigger asChild>
        <Button variant="link" className="p-0">
          John Doe
        </Button>
      </HoverCardTrigger>
      <HoverCardContent className="w-72">
        <div className="flex space-x-4">
          <Avatar className="h-12 w-12">
            <AvatarImage src="https://github.com/shadcn.png" />
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <h4 className="text-sm font-semibold">John Doe</h4>
            <p className="text-sm text-muted-foreground">
              Software Engineer at Acme Inc.
            </p>
            <div className="flex gap-4 pt-2 text-xs text-muted-foreground">
              <span>
                <strong>128</strong> Following
              </span>
              <span>
                <strong>512</strong> Followers
              </span>
            </div>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  ),
};

export const WithStats: Story = {
  render: () => (
    <HoverCard>
      <HoverCardTrigger asChild>
        <Button variant="outline" size="sm">
          View project
        </Button>
      </HoverCardTrigger>
      <HoverCardContent className="w-64">
        <div className="space-y-2">
          <h4 className="text-sm font-semibold">djangocfg</h4>
          <p className="text-sm text-muted-foreground">
            TypeScript + Django, end-to-end.
          </p>
          <div className="flex gap-4 pt-2 text-xs">
            <span className="flex items-center gap-1">
              {/* eslint-disable-next-line no-restricted-syntax -- GitHub's
                  language dot: yellow means TypeScript, not a warning state.
                  `bg-warning` would render the same colour and say the wrong
                  thing, and would follow a theme change this dot must not. */}
              <span className="h-2 w-2 rounded-full bg-yellow-500" />
              TypeScript
            </span>
            <span>1.2k ★</span>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  ),
};

export const Default: Story = {
  render: () => (
    <HoverCard>
      <HoverCardTrigger asChild>
        <Button variant="link">@markolofsen</Button>
      </HoverCardTrigger>
      <HoverCardContent className="w-72">
        <div className="flex gap-3">
          <Avatar>
            <AvatarImage src="https://github.com/markolofsen.png" />
            <AvatarFallback>MK</AvatarFallback>
          </Avatar>
          <div className="space-y-1">
            <div className="text-sm font-semibold">@markolofsen</div>
            <p className="text-sm text-muted-foreground">
              Building djangocfg. Open-source TypeScript + Django.
            </p>
            <div className="flex items-center text-xs text-muted-foreground">
              <CalendarDays className="mr-1 h-3 w-3" />
              Joined September 2024
            </div>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  ),
};
