import type { Meta, StoryObj } from '@storybook/react-vite';
import { FileQuestion, Inbox, Plus, RefreshCw, Search } from 'lucide-react';
import {
  Button,
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Feedback/Empty',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

export const Default: Story = {
  render: () => (
    <Empty className="w-[420px]">
      <EmptyHeader>
        <EmptyMedia>
          <Inbox className="h-10 w-10" />
        </EmptyMedia>
        <EmptyTitle>No messages yet</EmptyTitle>
        <EmptyDescription>
          When teammates message you, their threads appear here.
        </EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button>
          <Plus className="mr-1 h-4 w-4" /> Start a thread
        </Button>
      </EmptyContent>
    </Empty>
  ),
};

export const SearchNoResults: Story = {
  render: () => (
    <Empty className="w-[420px]">
      <EmptyMedia>
        <Search className="h-10 w-10 text-muted-foreground" />
      </EmptyMedia>
      <EmptyHeader>
        <EmptyTitle>No results found</EmptyTitle>
        <EmptyDescription>
          We couldn&apos;t find anything matching your search.
        </EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button variant="outline">Clear filters</Button>
      </EmptyContent>
    </Empty>
  ),
};

export const ErrorState: Story = {
  render: () => (
    <Empty className="w-[420px]">
      <EmptyMedia>
        <FileQuestion className="h-10 w-10 text-muted-foreground" />
      </EmptyMedia>
      <EmptyHeader>
        <EmptyTitle>Something went wrong</EmptyTitle>
        <EmptyDescription>
          We encountered an error while loading the data.
        </EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Retry
        </Button>
      </EmptyContent>
    </Empty>
  ),
};

export const Simple: Story = {
  render: () => (
    <Empty className="w-[320px]">
      <EmptyHeader>
        <EmptyTitle>No data</EmptyTitle>
        <EmptyDescription>Start by adding some data.</EmptyDescription>
      </EmptyHeader>
    </Empty>
  ),
};

export const InCard: Story = {
  render: () => (
    <div className="w-[420px] rounded-lg border p-6">
      <Empty>
        <EmptyMedia>
          <Inbox className="h-8 w-8 text-muted-foreground" />
        </EmptyMedia>
        <EmptyHeader>
          <EmptyTitle className="text-base">Empty inbox</EmptyTitle>
          <EmptyDescription className="text-sm">
            No messages to display
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
    </div>
  ),
};
