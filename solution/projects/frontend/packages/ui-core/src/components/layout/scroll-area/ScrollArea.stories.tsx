import type { Meta, StoryObj } from '@storybook/react-vite';
import { ScrollArea, Separator } from '@djangocfg/ui-core/components';

const meta = {
  title: 'Packages/UI Core/Layout/ScrollArea',
  tags: ['autodocs'],
} satisfies Meta;

export default meta;

type Story = StoryObj;

const tags = Array.from({ length: 50 }, (_, i) => `tag-${i + 1}`);

export const Vertical: Story = {
  render: () => (
    <ScrollArea className="h-72 w-48 rounded-md border border-border">
      <div className="p-4">
        <h4 className="mb-3 text-sm font-medium">Tags</h4>
        {tags.map((t) => (
          <div key={t}>
            <div className="text-sm">{t}</div>
            <Separator className="my-2" />
          </div>
        ))}
      </div>
    </ScrollArea>
  ),
};

const works = [
  { artist: 'Ornella Binni', art: 'Sunset Dreams' },
  { artist: 'Tom Byrom', art: 'Mountain Peak' },
  { artist: 'Vladimir Malyavko', art: 'City Lights' },
  { artist: 'Fabio Fistarol', art: 'Ocean Blue' },
  { artist: 'Anthony Intraversato', art: 'Forest Path' },
  { artist: 'Ash Edmonds', art: 'Desert Storm' },
];

export const Horizontal: Story = {
  render: () => (
    <ScrollArea
      className="w-96 whitespace-nowrap rounded-md border"
      orientation="horizontal"
    >
      <div className="flex w-max space-x-4 p-4">
        {works.map((w) => (
          <figure key={w.artist} className="shrink-0">
            <div className="flex h-[150px] w-[150px] items-center justify-center overflow-hidden rounded-md bg-muted">
              <span className="text-sm text-muted-foreground">{w.art}</span>
            </div>
            <figcaption className="pt-2 text-xs text-muted-foreground">
              Photo by{' '}
              <span className="font-semibold text-foreground">{w.artist}</span>
            </figcaption>
          </figure>
        ))}
      </div>
    </ScrollArea>
  ),
};

export const Both: Story = {
  render: () => (
    <ScrollArea className="h-72 w-72 rounded-md border" orientation="both">
      <div className="p-4">
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className="whitespace-nowrap py-2">
            Long line of text requiring horizontal scrolling. Item {i + 1}
          </div>
        ))}
      </div>
    </ScrollArea>
  ),
};

export const Chat: Story = {
  render: () => (
    <div className="w-[420px] rounded-lg border">
      <div className="border-b p-4">
        <h4 className="font-medium">Chat</h4>
      </div>
      <ScrollArea className="h-64 p-4">
        <div className="space-y-4">
          {Array.from({ length: 15 }).map((_, i) => (
            <div
              key={i}
              className={`flex ${i % 2 === 0 ? 'justify-start' : 'justify-end'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-3 py-2 ${
                  i % 2 === 0
                    ? 'bg-muted'
                    : 'bg-primary text-primary-foreground'
                }`}
              >
                <p className="text-sm">Message {i + 1}</p>
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  ),
};
