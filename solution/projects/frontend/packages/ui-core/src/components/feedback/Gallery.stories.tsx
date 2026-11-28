import type { Meta, StoryObj } from '@storybook/react-vite';
import { AlertCircle, Inbox, Info, Plus } from 'lucide-react';
import { toast } from 'sonner';
import {
  Alert,
  AlertDescription,
  AlertTitle,
  Banner,
  BannerActions,
  BannerClose,
  BannerContent,
  BannerDescription,
  BannerIcon,
  BannerTitle,
  Button,
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
  Preloader,
  Spinner,
  Toaster,
} from '@djangocfg/ui-core/components';

import { Gallery, GalleryItem, GalleryPage, GallerySection } from '../_gallery';

const meta = {
  title: 'Packages/UI Core/Feedback/Gallery',
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Every feedback component in `ui-core`, side by side. They all say ' +
          '"something happened" or "something is happening", and the choice between ' +
          'them is really two questions: **does the message interrupt the user or sit ' +
          'in the page**, and **is this a state or an event**.',
      },
    },
  },
} satisfies Meta;

export default meta;
type Story = StoryObj;

function AlertDemo() {
  return (
    <div className="flex flex-col gap-2">
      <Alert>
        <Info className="h-4 w-4" />
        <AlertTitle>Heads up</AlertTitle>
        <AlertDescription>Update available — v2.0.4.</AlertDescription>
      </Alert>
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>Your session has expired.</AlertDescription>
      </Alert>
    </div>
  );
}

function BannerDemo() {
  // Inline form rather than the `Banners` queue: a gallery cell should show the
  // component, not a button that maybe produces one somewhere off-screen.
  return (
    <Banner variant="info">
      <BannerIcon>
        <Info />
      </BannerIcon>
      <BannerContent>
        <BannerTitle>Update available</BannerTitle>
        <BannerDescription>A new version is ready to install.</BannerDescription>
      </BannerContent>
      <BannerActions>
        <BannerClose />
      </BannerActions>
    </Banner>
  );
}

function EmptyDemo() {
  return (
    <Empty>
      <EmptyHeader>
        <EmptyMedia>
          <Inbox className="h-8 w-8" />
        </EmptyMedia>
        <EmptyTitle>No messages yet</EmptyTitle>
        <EmptyDescription>Threads appear here once teammates write.</EmptyDescription>
      </EmptyHeader>
      <EmptyContent>
        <Button size="sm">
          <Plus className="mr-1 h-4 w-4" /> Start a thread
        </Button>
      </EmptyContent>
    </Empty>
  );
}

function ToasterDemo() {
  return (
    <div className="flex flex-wrap gap-2">
      {/* The global preview harness mounts TooltipProvider and DialogProvider
          but NOT a Toaster, so the cell has to supply one or the buttons below
          fire into nothing. */}
      <Toaster position="top-right" />
      <Button size="sm" onClick={() => toast('Note saved')}>
        Toast
      </Button>
      <Button size="sm" variant="outline" onClick={() => toast.success('Profile updated')}>
        Success
      </Button>
      <Button
        size="sm"
        variant="outline"
        onClick={() => toast.error('Could not reach the server')}
      >
        Error
      </Button>
    </div>
  );
}

/**
 * The whole group on one screen.
 *
 * Grouped by where the message lives and what it describes — the two things
 * that actually decide which component you reach for.
 */
export const AllFeedback: Story = {
  render: () => (
    <GalleryPage>
      <GallerySection title="Messages inside the page">
        <Gallery>
          <GalleryItem name="Alert" hint="Static notice pinned to its context.">
            <AlertDemo />
          </GalleryItem>
          <GalleryItem name="Banner" hint="Dismissible notice, often page-wide.">
            <BannerDemo />
          </GalleryItem>
          <GalleryItem name="Empty" hint="Nothing here yet — plus a next step.">
            <EmptyDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Messages over the page">
        <Gallery>
          <GalleryItem name="Toaster" hint="Transient event, fired from anywhere.">
            <ToasterDemo />
          </GalleryItem>
        </Gallery>
      </GallerySection>

      <GallerySection title="Work in progress">
        <Gallery>
          <GalleryItem name="Spinner" hint="Bare glyph, inline in buttons.">
            <div className="flex items-center gap-3">
              <Spinner className="h-4 w-4" />
              <Spinner className="h-6 w-6" />
              <Spinner className="h-8 w-8" />
            </div>
          </GalleryItem>
          <GalleryItem name="Preloader" hint="Spinner plus label for whole regions.">
            <Preloader size="md" text="Loading data…" />
          </GalleryItem>
        </Gallery>
      </GallerySection>
    </GalleryPage>
  ),
};
