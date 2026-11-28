import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  AspectRatio,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  KeyValue,
  KeyValueAdd,
  KeyValueItem,
  KeyValueKeyInput,
  KeyValueList,
  KeyValueRemove,
  KeyValueValueInput,
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
  ScrollArea,
  Section,
  SectionHeader,
  Separator,
  Skeleton,
  Stack,
  StackItem,
  Sticky,
} from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Layout/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Every layout primitive in `ui-core`, side by side. These do not overlap in ' +
          'appearance so much as in *purpose* — several are one-line wrappers whose ' +
          'value is invisible until you see what they solve. Grouped by the job: ' +
          '**shaping a box**, **dividing a page**, **handling overflow**, and ' +
          '**standing in for content that is not there yet**.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

/**
 * Most of this group is a container with no intrinsic size — `ScrollArea`,
 * `Sticky` and `Resizable` collapse to nothing without an explicit height, so
 * every cell below pins one. Same height across cells keeps the rows even.
 */
const CELL = 'h-40';

function AspectRatioDemo() {
  return (
    <div className="w-full">
      <AspectRatio ratio={16 / 9} className="bg-muted flex items-center justify-center rounded-md">
        <span className="text-muted-foreground text-xs">16 / 9</span>
      </AspectRatio>
    </div>
  );
}

function CardDemo() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Card title</CardTitle>
        <CardDescription>Bordered surface with header slots.</CardDescription>
      </CardHeader>
      <CardContent className="text-muted-foreground text-sm">Body content.</CardContent>
    </Card>
  );
}

function SectionDemo() {
  // `Section` ships page-scale vertical padding; scaled down so the cell stays
  // comparable to its neighbours rather than dwarfing them.
  return (
    <div className={`${CELL} overflow-hidden rounded-md border`}>
      <Section className="!py-6">
        <SectionHeader title="Section" subtitle="Page-level band with a centered header." />
      </Section>
    </div>
  );
}

function SeparatorDemo() {
  return (
    <div className="flex flex-col gap-3 text-sm">
      <span>Above</span>
      <Separator />
      <span>Below</span>
      <div className="flex h-5 items-center gap-3">
        <span>Blog</span>
        <Separator orientation="vertical" />
        <span>Docs</span>
        <Separator orientation="vertical" />
        <span>Source</span>
      </div>
    </div>
  );
}

function ScrollAreaDemo() {
  return (
    <ScrollArea className={`${CELL} rounded-md border`}>
      <div className="p-3">
        {Array.from({ length: 20 }, (_, i) => (
          <div key={i} className="py-1 text-sm">
            Row {i + 1}
          </div>
        ))}
      </div>
    </ScrollArea>
  );
}

function ResizableDemo() {
  return (
    <ResizablePanelGroup direction="horizontal" className={`${CELL} rounded-md border`}>
      <ResizablePanel defaultSize={40}>
        <div className="flex h-full items-center justify-center text-sm">Left</div>
      </ResizablePanel>
      <ResizableHandle withHandle />
      <ResizablePanel defaultSize={60}>
        <div className="flex h-full items-center justify-center text-sm">Right</div>
      </ResizablePanel>
    </ResizablePanelGroup>
  );
}

function StickyDemo() {
  return (
    <div className={`${CELL} overflow-y-auto rounded-md border`}>
      <div className="flex items-start" style={{ minHeight: 420 }}>
        {/* disableOnMobile={false}: the docs iframe is narrow enough to trip
            the mobile bail-out, which would show nothing sticking at all. */}
        <Sticky offsetTop={0} disableOnMobile={false}>
          <div className="bg-card m-2 rounded-md border px-3 py-2 text-xs font-medium">Pinned</div>
        </Sticky>
        <div className="flex-1 space-y-2 p-2">
          {Array.from({ length: 12 }, (_, i) => (
            <div key={i} className="text-muted-foreground text-xs">
              Scroll me — row {i + 1}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function StackDemo() {
  return (
    <Stack className={CELL} expandOnHover>
      <StackItem>Card 1</StackItem>
      <StackItem>Card 2</StackItem>
      <StackItem>Card 3</StackItem>
    </Stack>
  );
}

function SkeletonDemo() {
  return (
    <div className="flex items-center gap-3">
      <Skeleton className="h-12 w-12 rounded-full" />
      <div className="grid flex-1 gap-2">
        <Skeleton className="h-4 w-1/2" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  );
}

function KeyValueDemo() {
  return (
    <KeyValue
      defaultValue={[
        { id: '1', key: 'region', value: 'eu-west-1' },
        { id: '2', key: 'tier', value: 'pro' },
      ]}
    >
      <KeyValueList>
        <KeyValueItem>
          <KeyValueKeyInput placeholder="Key" />
          <KeyValueValueInput placeholder="Value" />
          <KeyValueRemove />
        </KeyValueItem>
      </KeyValueList>
      <KeyValueAdd />
    </KeyValue>
  );
}

/**
 * The whole group on one screen.
 *
 * Grouped by the job each primitive does, because alphabetical order files
 * `Separator` next to `Section` — near-identical names, unrelated purposes.
 */
export const AllLayout: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Shaping a box">
        <Gallery>
          <GalleryItem name="Card" hint="Bordered surface for grouped content.">
            <CardDemo />
          </GalleryItem>
          <GalleryItem name="AspectRatio" hint="Lock a ratio before media loads.">
            <AspectRatioDemo />
          </GalleryItem>
          <GalleryItem name="Stack" hint="Layered cards, fan out on hover.">
            <StackDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Dividing a page">
        <Gallery>
          <GalleryItem name="Section" hint="Full-width page band with header.">
            <SectionDemo />
          </GalleryItem>
          <GalleryItem name="Separator" hint="One rule between two things.">
            <SeparatorDemo />
          </GalleryItem>
          <GalleryItem name="Resizable" hint="Split panes the user can drag.">
            <ResizableDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Handling overflow">
        <Gallery>
          <GalleryItem name="ScrollArea" hint="Styled scrollbars in a fixed box.">
            <ScrollAreaDemo />
          </GalleryItem>
          <GalleryItem name="Sticky" hint="Pin a panel while siblings scroll.">
            <StickyDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Standing in for content">
        <Gallery>
          <GalleryItem name="Skeleton" hint="Placeholder shape while data loads.">
            <SkeletonDemo />
          </GalleryItem>
          <GalleryItem name="KeyValue" hint="Editable pair list with add/remove.">
            <KeyValueDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};
